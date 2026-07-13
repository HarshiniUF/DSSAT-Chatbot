
"""
Zone-Based Cultivar Dataset Generator
======================================
Features:
- Variable cultivar counts per zone (0 to N)
- Added major_crop_areas field
- Comprehensive summary statistics
- Overlap analysis across zones

Usage:
    python generate_dataset.py

Global constants (COUNTRY, CROP_CODE, ZONES) are defined at the top of this file.
"""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Set
from collections import defaultdict

from dotenv import load_dotenv
# Single project-root .env (dssat_project/.env) -- see run_cli.py
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from agents.cultivar_agent import CultivarAgent


# ============================================================================
# GLOBAL CONSTANTS — Edit these before running
# ============================================================================

COUNTRY = "Kenya"
CROP_CODE = "MZ"
GENERATOR_MODEL = "gpt-5"
VERBOSE = False
BASE_OUTPUT_DIR = "data/cultivar_db"  # Changed from "outputs"

ZONES = [
    "Coastal Lowland",
    "Inner Lowland",
    "Lower Highland",
    "Lower Midland",
    "Upper Midland",
    "Upper Highland",
    "Tropical Alpine",
    "Nairobi"
]


# ============================================================================
# CROP CODE -> NAME MAPPING
# ============================================================================

CROP_MAP = {
    "MZ": "Maize",
    "WH": "Wheat",
    "BA": "Barley",
    "RI": "Rice",
    "SB": "Soybean",
    "PN": "Peanut",
    "SG": "Sorghum",
    "ML": "Millet",
    "SC": "Sugarcane",
    "TN": "Sunflower",
    "PP": "Pigeonpea",
    "CH": "Chickpea",
    "BN": "Dry Bean",
    "CB": "Cabbage",
    "TM": "Tomato",
    "PT": "Potato",
}


# ============================================================================
# HELPER: DERIVE CROP NAME FROM CROP CODE
# ============================================================================

def derive_crop_name(crop_code: str) -> str:
    """Derive the common crop name from DSSAT crop code."""
    return CROP_MAP.get(crop_code.upper(), crop_code)


# ============================================================================
# NEW: HELPER TO BUILD OUTPUT PATH
# ============================================================================

def build_output_path(base_dir: str, country: str, crop_name: str, crop_code: str) -> Path:
    """
    Build the output path following the structure:
    data/cultivar_db/<country_name>/<crop_name>/<country>_<crop>_cultivars_list.json
    
    Args:
        base_dir: Base directory (e.g., "data/cultivar_db")
        country: Country name (e.g., "Kenya")
        crop_name: Crop name (e.g., "Maize")
        crop_code: Crop code (e.g., "MZ")
    
    Returns:
        Path object for the output file
    """
    # Normalize names for directory structure (lowercase, replace spaces with underscores)
    country_dir = country.lower().replace(" ", "_")
    crop_dir = crop_name.lower().replace(" ", "_")
    
    # Build directory path
    output_dir = Path(base_dir) / country_dir / crop_dir
    
    # Create directories if they don't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Build filename: <country>_<crop>_cultivars_list.json
    filename = f"{country}_{crop_code}_cultivars_list.json"
    
    return output_dir / filename


# ============================================================================
# HELPER: BUILD STATE DICT FOR AGENT
# ============================================================================

def build_agent_state(
    zone_name: str,
    country: str,
    crop_code: str,
    crop_name: str,
    generator_model: str,
) -> Dict[str, Any]:
    """
    Build a plain dictionary state for CultivarAgent.process().
    """
    state: Dict[str, Any] = {
        "config": {},
        "messages": [],
        "errors": [],
        "crop_code": crop_code,
        "crop_name_text": crop_name,
        "zone_name": zone_name,
        "country": country,
        "generator_model": generator_model,
    }
    return state


# ============================================================================
# HELPER: EXTRACT CULTIVAR OUTPUT FOR STORAGE
# ============================================================================

def extract_cultivar_output(cultivar_helper_output: Dict[str, Dict]) -> Dict[str, Any]:
    """
    Reformat the agent output into the storage format:
    { cultivar_name: { characteristics: {...}, coefficients: {...} }, ... }
    """
    result = {}
    for cultivar_name, data in cultivar_helper_output.items():
        result[cultivar_name] = {
            "characteristics": data.get("characteristics", {}),
            "coefficients": data.get("coefficients", {}),
        }
    return result


# ============================================================================
# NEW v2: SUMMARY CALCULATOR
# ============================================================================

class SummaryCalculator:
    """
    Calculates comprehensive summary statistics for zone-based cultivar data.
    Tracks:
    - Total cultivars per zone
    - Coefficient availability (local vs research)
    - Cultivar overlap across zones
    - Unique cultivar counts
    """

    def __init__(self):
        self.zone_data: Dict[str, Dict[str, Any]] = {}
        self.cultivar_to_zones: Dict[str, Set[str]] = defaultdict(set)
        self.total_cultivars_with_repeats = 0
        
    def add_zone_data(self, zone_name: str, cultivar_data: Dict[str, Any]):
        """
        Add data for a single zone.

        Args:
            zone_name: Name of the agro-ecological zone
            cultivar_data: Dictionary of {cultivar_name: {characteristics, coefficients}}
        """
        num_cultivars = len(cultivar_data)
        num_local_coeffs = 0
        num_web_coeffs = 0
        num_analog_coeffs = 0
        num_estimated_coeffs = 0

        # Count coefficient sources
        for cultivar_name, data in cultivar_data.items():
            coeffs = data.get("coefficients", {})
            if coeffs.get("found", False):
                source = coeffs.get("source", "")
                if "Local .CUL file" in source:
                    num_local_coeffs += 1
                elif "WebFetch" in source:
                    num_web_coeffs += 1
                elif source.startswith("analog:"):
                    num_analog_coeffs += 1
                elif source == "trait_estimated":
                    num_estimated_coeffs += 1

            # Track cultivar-to-zone mapping
            self.cultivar_to_zones[cultivar_name].add(zone_name)

        self.total_cultivars_with_repeats += num_cultivars

        # Store zone summary
        self.zone_data[zone_name] = {
            "num_cultivars": num_cultivars,
            "num_local_coefficients": num_local_coeffs,
            "num_web_coefficients": num_web_coeffs,
            "num_analog_coefficients": num_analog_coeffs,
            "num_estimated_coefficients": num_estimated_coeffs,
            "crop_suitability_note": self._generate_suitability_note(num_cultivars)
        }
    
    def _generate_suitability_note(self, num_cultivars: int) -> str:
        """Generate a suitability note based on cultivar count."""
        if num_cultivars == 0:
            return "Crop not typically grown in this zone"
        elif num_cultivars <= 3:
            return "Limited cultivation; few suitable cultivars"
        elif num_cultivars <= 6:
            return "Moderate cultivation with several suitable cultivars"
        else:
            return "Major cultivation zone with diverse cultivar options"
    
    def get_cultivar_overlap_stats(self) -> Dict[str, Any]:
        """
        Calculate cultivar overlap statistics.
        
        Returns:
            Dictionary with overlap metrics
        """
        total_unique = len(self.cultivar_to_zones)
        
        cultivars_in_single_zone = sum(
            1 for zones in self.cultivar_to_zones.values() if len(zones) == 1
        )
        
        cultivars_in_multiple_zones = sum(
            1 for zones in self.cultivar_to_zones.values() if len(zones) >= 2
        )
        
        return {
            "total_cultivars_with_repeats": self.total_cultivars_with_repeats,
            "total_unique_cultivars": total_unique,
            "cultivars_in_single_zone": cultivars_in_single_zone,
            "cultivars_in_multiple_zones": cultivars_in_multiple_zones
        }
    
    def get_cultivar_zone_mapping(self) -> Dict[str, List[str]]:
        """
        Get mapping of each cultivar to its zones.
        
        Returns:
            Dictionary of {cultivar_name: [zone1, zone2, ...]}
        """
        return {
            cultivar: sorted(list(zones))
            for cultivar, zones in self.cultivar_to_zones.items()
        }
    
    def get_zone_detailed_summary(self) -> Dict[str, Dict[str, Any]]:
        """
        Get detailed summary for each zone.
        
        Returns:
            Dictionary of zone summaries
        """
        return self.zone_data
    
    def generate_full_summary(self) -> Dict[str, Any]:
        """
        Generate complete summary structure for JSON output.
        
        Returns:
            Complete summary dictionary
        """
        return {
            "total_cultivars_identified": self.get_cultivar_zone_mapping(),
            "zone_detailed": self.get_zone_detailed_summary(),
            "cultivars_overlap_info": self.get_cultivar_overlap_stats()
        }


# ============================================================================
# INCREMENTAL JSON WRITER v2
# ============================================================================

class IncrementalJsonWriter:
    """
    Writes results incrementally to a JSON file with summary statistics.
    v2: Includes comprehensive summary section.
    """

    def __init__(self, output_path: Path, crop_code: str, country: str):
        self.output_path = output_path
        self.summary_calc = SummaryCalculator()
        
        self.data = {
            "crop": crop_code,
            "country": country,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_zones": 0,
            "processed": 0,
            "summary": {},  # Will be populated incrementally
            "zones": {},
        }
        self._flush()

    def set_total(self, total: int):
        """Set total zone count."""
        self.data["total_zones"] = total
        self._flush()

    def add_zone(self, zone_name: str, cultivar_data: Dict[str, Any]):
        """
        Add a single zone's cultivar data and update summary.
        
        Args:
            zone_name: Name of the zone
            cultivar_data: Dictionary of cultivar data
        """
        # Add to zones section
        self.data["zones"][zone_name] = cultivar_data
        self.data["processed"] = len(self.data["zones"])
        
        # Update summary calculator
        self.summary_calc.add_zone_data(zone_name, cultivar_data)
        
        # Regenerate summary
        self.data["summary"] = self.summary_calc.generate_full_summary()
        
        # Flush to disk
        self._flush()

    def _flush(self):
        """Write current state to disk."""
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("=" * 70)
    print("  Zone-Based Cultivar Dataset Generator v2")
    print("=" * 70)

    # ------------------------------------------------------------------
    # 1. Derive crop name from crop code
    # ------------------------------------------------------------------
    crop_name = derive_crop_name(CROP_CODE)
    print(f"🌾 Crop: {crop_name} ({CROP_CODE})")
    print(f"🌍 Country: {COUNTRY}")
    print(f"🤖 Model: {GENERATOR_MODEL}")
    print(f"🔊 Verbose: {VERBOSE}")
    print(f"📍 Total Zones: {len(ZONES)}")
    print()

    # ------------------------------------------------------------------
    # 2. Create output file with new directory structure
    # ------------------------------------------------------------------
    output_path = build_output_path(BASE_OUTPUT_DIR, COUNTRY, crop_name, CROP_CODE)

    print(f"💾 Output file: {output_path}")
    print(f"📁 Directory structure: {BASE_OUTPUT_DIR}/{COUNTRY.lower()}/{crop_name.lower()}/")
    print("-" * 70)

    writer = IncrementalJsonWriter(output_path, CROP_CODE, COUNTRY)
    writer.set_total(len(ZONES))

    # ------------------------------------------------------------------
    # 3. Process each zone
    # ------------------------------------------------------------------
    total = len(ZONES)
    total_start = time.time()

    for idx, zone_name in enumerate(ZONES):
        print(f"\n{'─' * 60}")
        print(f"[{idx + 1}/{total}] 🌍 Zone: {zone_name}")

        # ── Build state for agent ────────────────────────────────────
        state = build_agent_state(
            zone_name=zone_name,
            country=COUNTRY,
            crop_code=CROP_CODE,
            crop_name=crop_name,
            generator_model=GENERATOR_MODEL,
        )

        # ── Run the standalone agent ─────────────────────────────────
        agent_start = time.time()
        try:
            result_state = CultivarAgent.process(state, verbose=VERBOSE)
            agent_elapsed = time.time() - agent_start

            cultivar_helper_output = result_state.get("cultivar_helper_output", {})
            cultivar_data = extract_cultivar_output(cultivar_helper_output)

            errors = result_state.get("errors", [])

            if errors:
                print(f"[{idx + 1}/{total}] ⚠️ Completed with errors: {errors}")

            writer.add_zone(zone_name, cultivar_data)

            cultivar_count = len(cultivar_data)
            
            if cultivar_count == 0:
                print(f"[{idx + 1}/{total}] ✅ Zone unsuitable — 0 cultivars in {agent_elapsed:.1f}s")
            else:
                print(f"[{idx + 1}/{total}] ✅ Done — {cultivar_count} cultivars in {agent_elapsed:.1f}s")

        except Exception as e:
            agent_elapsed = time.time() - agent_start
            print(f"[{idx + 1}/{total}] ❌ Failed after {agent_elapsed:.1f}s: {e}")

            writer.add_zone(zone_name, {
                "error": str(e),
                "cultivars": {}
            })

    # ------------------------------------------------------------------
    # 4. Summary
    # ------------------------------------------------------------------
    total_elapsed = time.time() - total_start
    minutes = int(total_elapsed // 60)
    seconds = total_elapsed % 60

    print(f"\n{'=' * 70}")
    print(f"  Zone-based processing complete!")
    print(f"  Total zones processed: {total}")
    print(f"  Total time: {minutes}m {seconds:.1f}s")
    print(f"  Output saved to: {output_path}")
    
    # Display summary statistics
    summary = writer.data.get("summary", {})
    overlap_info = summary.get("cultivars_overlap_info", {})
    
    print(f"\n  📊 Summary Statistics:")
    print(f"     Total unique cultivars: {overlap_info.get('total_unique_cultivars', 0)}")
    print(f"     Cultivars in multiple zones: {overlap_info.get('cultivars_in_multiple_zones', 0)}")
    print(f"     Total cultivars (with repeats): {overlap_info.get('total_cultivars_with_repeats', 0)}")
    
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()

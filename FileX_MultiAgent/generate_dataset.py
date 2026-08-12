
"""
Crop + Location Cultivar Dataset Generator
===========================================
Features:
- Only two real inputs: a crop code and a location name
- Variable cultivar counts (0 to N) for the location
- Coefficients come only from LLM knowledge + web/paper search — no local
  .CUL file matching, no "analog" cultivar borrowing
- Per-coefficient min/max bounds attached from data/coefficients_db
- Locations accumulate over repeated runs into one file per crop

Usage:
    python generate_dataset.py

Global constants (CROP_CODE, LOCATION_NAME) are defined at the top of this file.
"""

from __future__ import annotations

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Set
from collections import defaultdict

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent / ".env")

from agents.cultivar_agent import CultivarAgent


# ============================================================================
# GLOBAL CONSTANTS — Edit these before running
# ============================================================================

CROP_CODE = "MZ"
LOCATION_NAME = "Kenya"
GENERATOR_MODEL = "gpt-5"
VERBOSE = False
BASE_OUTPUT_DIR = "data/cultivar_db"

# Optional: crop name used in LLM prompts / summary text, without changing the
# storage folder (which stays derived from CROP_MAP below, e.g. "peanut", so it
# keeps matching utils/helpers.py's _load_aez_database lookup). Use this to
# override the display name the LLM sees (e.g. "Corn" instead of "Maize")
# while the storage folder stays keyed off CROP_MAP. Leave as None to use the
# CROP_MAP name as-is.
CROP_DISPLAY_NAME_OVERRIDE = None


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
    "SU": "Sunflower",
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
# HELPER TO BUILD OUTPUT PATH
# ============================================================================

def build_output_path(base_dir: str, crop_name: str, crop_code: str) -> Path:
    """
    Build the output path following the structure:
    data/cultivar_db/<crop_name>/<crop_name>_<CR>_cultivars_list.json

    Must stay in exact sync with agents/cultivar_agent.py's _db_file_path —
    both are independently derived from the same crop_code so a run through
    generate_dataset.py and a direct CultivarAgent call land on one file.

    Args:
        base_dir: Base directory (e.g., "data/cultivar_db")
        crop_name: Crop name (e.g., "Peanut")
        crop_code: Crop code (e.g., "PN")

    Returns:
        Path object for the output file
    """
    crop_dir = crop_name.lower().replace(" ", "_")

    output_dir = Path(base_dir) / crop_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{crop_dir}_{crop_code}_cultivars_list.json"

    return output_dir / filename


# ============================================================================
# HELPER: BUILD STATE DICT FOR AGENT
# ============================================================================

def build_agent_state(
    location_name: str,
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
        "location_name": location_name,
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
# SUMMARY CALCULATOR
# ============================================================================

class SummaryCalculator:
    """
    Calculates comprehensive summary statistics across every location
    accumulated so far for one crop's DB file.
    Tracks:
    - Total cultivars per location
    - Coefficient source breakdown (llm_knowledge / web_paper / not_found)
    - Cultivar overlap across locations
    - Unique cultivar counts
    """

    def __init__(self):
        self.location_data: Dict[str, Dict[str, Any]] = {}
        self.cultivar_to_locations: Dict[str, Set[str]] = defaultdict(set)
        self.total_cultivars_with_repeats = 0

    def add_location_data(self, location_name: str, cultivar_data: Dict[str, Any]):
        """
        Add data for a single location.

        Args:
            location_name: Free-text location name
            cultivar_data: Dictionary of {cultivar_name: {characteristics, coefficients}}
        """
        num_cultivars = len(cultivar_data)
        num_llm_knowledge = 0
        num_web_paper = 0
        num_not_found = 0

        for cultivar_name, data in cultivar_data.items():
            coeffs = data.get("coefficients", {})
            if not coeffs.get("found", False):
                num_not_found += 1
            else:
                source = coeffs.get("source", "")
                if source.startswith("WebFetch"):
                    num_web_paper += 1
                elif source == "LLM knowledge":
                    num_llm_knowledge += 1
                else:
                    num_not_found += 1

            self.cultivar_to_locations[cultivar_name].add(location_name)

        self.total_cultivars_with_repeats += num_cultivars

        self.location_data[location_name] = {
            "num_cultivars": num_cultivars,
            "num_llm_knowledge_coefficients": num_llm_knowledge,
            "num_web_paper_coefficients": num_web_paper,
            "num_not_found_coefficients": num_not_found,
            "crop_suitability_note": self._generate_suitability_note(num_cultivars),
        }

    def _generate_suitability_note(self, num_cultivars: int) -> str:
        """Generate a suitability note based on cultivar count."""
        if num_cultivars == 0:
            return "Crop not typically grown in this location"
        elif num_cultivars <= 3:
            return "Limited cultivation; few suitable cultivars"
        elif num_cultivars <= 6:
            return "Moderate cultivation with several suitable cultivars"
        else:
            return "Major cultivation location with diverse cultivar options"

    def get_cultivar_overlap_stats(self) -> Dict[str, Any]:
        """Calculate cultivar overlap statistics across locations."""
        total_unique = len(self.cultivar_to_locations)

        cultivars_in_single_location = sum(
            1 for locations in self.cultivar_to_locations.values() if len(locations) == 1
        )

        cultivars_in_multiple_locations = sum(
            1 for locations in self.cultivar_to_locations.values() if len(locations) >= 2
        )

        return {
            "total_cultivars_with_repeats": self.total_cultivars_with_repeats,
            "total_unique_cultivars": total_unique,
            "cultivars_in_single_location": cultivars_in_single_location,
            "cultivars_in_multiple_locations": cultivars_in_multiple_locations,
        }

    def get_cultivar_location_mapping(self) -> Dict[str, List[str]]:
        """Get mapping of each cultivar to the locations it appears in."""
        return {
            cultivar: sorted(list(locations))
            for cultivar, locations in self.cultivar_to_locations.items()
        }

    def get_location_detailed_summary(self) -> Dict[str, Dict[str, Any]]:
        """Get detailed summary for each location."""
        return self.location_data

    def generate_full_summary(self) -> Dict[str, Any]:
        """Generate complete summary structure for JSON output."""
        return {
            "total_cultivars_identified": self.get_cultivar_location_mapping(),
            "location_detailed": self.get_location_detailed_summary(),
            "cultivars_overlap_info": self.get_cultivar_overlap_stats(),
        }


# ============================================================================
# SUMMARY WRITER
# ============================================================================

class SummaryWriter:
    """
    CultivarAgent already writes/updates the per-crop DB file's "locations"
    section directly. This recomputes the "summary" section from everything
    currently in that file (all locations accumulated across runs, not just
    the one just generated) and flushes it back to disk.
    """

    def __init__(self, output_path: Path):
        self.output_path = output_path

    def refresh_summary(self) -> Dict[str, Any]:
        with open(self.output_path, "r", encoding="utf-8") as f:
            db = json.load(f)

        calc = SummaryCalculator()
        for location_name, cultivar_data in db.get("locations", {}).items():
            calc.add_location_data(location_name, cultivar_data)

        db["summary"] = calc.generate_full_summary()
        db["generated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(db, f, indent=2, ensure_ascii=False)

        return db["summary"]


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("=" * 70)
    print("  Crop + Location Cultivar Dataset Generator v3")
    print("=" * 70)

    # ------------------------------------------------------------------
    # 1. Derive crop name from crop code
    # ------------------------------------------------------------------
    crop_name = derive_crop_name(CROP_CODE)  # drives storage folder — do not change
    crop_display_name = CROP_DISPLAY_NAME_OVERRIDE or crop_name  # what the LLM sees in prompts
    print(f"🌾 Crop: {crop_display_name} ({CROP_CODE}) [storage folder: {crop_name.lower()}]")
    print(f"📍 Location: {LOCATION_NAME}")
    print(f"🤖 Model: {GENERATOR_MODEL}")
    print(f"🔊 Verbose: {VERBOSE}")
    print()

    # ------------------------------------------------------------------
    # 2. Resolve output file path
    # ------------------------------------------------------------------
    output_path = build_output_path(BASE_OUTPUT_DIR, crop_name, CROP_CODE)
    print(f"💾 Output file: {output_path}")
    print("-" * 70)

    # ------------------------------------------------------------------
    # 3. Build state and run the standalone agent
    # ------------------------------------------------------------------
    state = build_agent_state(
        location_name=LOCATION_NAME,
        crop_code=CROP_CODE,
        crop_name=crop_display_name,
        generator_model=GENERATOR_MODEL,
    )

    start = time.time()
    try:
        result_state = CultivarAgent.process(state, verbose=VERBOSE)
        elapsed = time.time() - start

        cultivar_helper_output = result_state.get("cultivar_helper_output", {})
        cultivar_data = extract_cultivar_output(cultivar_helper_output)

        errors = result_state.get("errors", [])
        if errors:
            print(f"⚠️ Completed with errors: {errors}")

        cultivar_count = len(cultivar_data)
        if cultivar_count == 0:
            print(f"✅ Location unsuitable — 0 cultivars in {elapsed:.1f}s")
        else:
            print(f"✅ Done — {cultivar_count} cultivars in {elapsed:.1f}s")

    except Exception as e:
        elapsed = time.time() - start
        print(f"❌ Failed after {elapsed:.1f}s: {e}")
        return

    # ------------------------------------------------------------------
    # 4. Recompute summary across every location accumulated for this crop
    # ------------------------------------------------------------------
    if not output_path.exists():
        print(f"\n⚠️ No output file was written to {output_path} — skipping summary.")
        return

    summary = SummaryWriter(output_path).refresh_summary()

    print(f"\n{'=' * 70}")
    print("  Processing complete!")
    print(f"  Total time: {elapsed:.1f}s")
    print(f"  Output saved to: {output_path}")

    overlap_info = summary.get("cultivars_overlap_info", {})
    print("\n  📊 Summary Statistics (all locations in this crop's DB):")
    print(f"     Total unique cultivars: {overlap_info.get('total_unique_cultivars', 0)}")
    print(f"     Cultivars in multiple locations: {overlap_info.get('cultivars_in_multiple_locations', 0)}")
    print(f"     Total cultivars (with repeats): {overlap_info.get('total_cultivars_with_repeats', 0)}")

    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()

"""
StandaloneCultivarHelperAgent v2 - Enhanced zone-based cultivar discovery

Key improvements from v1:
- Removed fixed cultivar count constraints (allows 0 to N cultivars)
- Added major_crop_areas field to characteristics
- Enhanced field descriptions and validation
- Maintains same workflow structure as v1

Workflow per cultivar:
  1. Generate list of suitable cultivars for zone (variable count)
  2. LLM predicts agronomic characteristics for each cultivar
  3. Search local .CUL files for coefficients
  4. If not found locally, search research papers for coefficients
"""

from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple

import requests
from bs4 import BeautifulSoup

from utils.llm import get_llm
from utils.helpers import strip_markdown_fences

from prompts.standalone_cultivar_helper_agent_prompts import (
    generate_cultivar_list_prompt,
    extract_characteristics_prompt,
    parse_cul_file_coefficients_prompt,
    search_coefficients_in_research_prompt,
    extract_coefficients_from_paper_prompt,
    find_analog_cultivar_prompt,
)


# ============================================================================
# HELPER FUNCTIONS (unchanged from v1)
# ============================================================================

def find_cul_files(genotype_dir: Path, crop_code: str) -> List[Path]:
    """
    Find ALL .CUL files matching crop_code inside genotype_dir.

    For MZ/WH crops, only CERES model files (<crop_code>CER*.CUL) are selected.
    For all other crops, all <crop_code>*.CUL files are selected.
    """
    if not genotype_dir.exists():
        return []

    crop_code = (crop_code or "").strip().upper()
    if not crop_code:
        return []

    if crop_code in ["MZ", "WH"]:
        target_prefix = f"{crop_code}CER"
        matching_files = [
            p for p in genotype_dir.iterdir()
            if p.is_file()
            and p.name.upper().startswith(target_prefix)
            and p.name.upper().endswith(".CUL")
        ]
    else:
        matching_files = [
            p for p in genotype_dir.iterdir()
            if p.is_file()
            and p.name.upper().startswith(crop_code)
            and p.name.upper().endswith(".CUL")
        ]

    matching_files.sort()
    return matching_files


def get_all_cul_file_contents(genotype_dir: Path, crop_code: str) -> List[Tuple[Path, str]]:
    """
    Read content of ALL .CUL files for given crop code.
    Returns list of (Path, content) tuples.
    """
    cul_files = find_cul_files(genotype_dir, crop_code)
    if not cul_files:
        return []

    file_contents = []
    for cul_file in cul_files:
        try:
            content = cul_file.read_text(encoding="latin1")
            file_contents.append((cul_file, content))
        except Exception:
            continue

    return file_contents


def search_cultivar_in_all_cul_files(
    cultivar_name: str,
    file_contents: List[Tuple[Path, str]]
) -> Optional[Tuple[Path, str]]:
    """
    Search for cultivar name across multiple .CUL files.
    Returns (Path, content) for first file containing the cultivar, or None.
    """
    if not cultivar_name or not file_contents:
        return None

    cultivar_lower = cultivar_name.lower()

    for cul_file, content in file_contents:
        if cultivar_lower in content.lower():
            return (cul_file, content)

    return None


# ============================================================================
# STANDALONE CULTIVAR HELPER AGENT CLASS v2
# ============================================================================

class StandaloneCultivarHelperAgent:
    """
    Standalone agent for cultivar discovery and coefficient retrieval v2.
    
    Enhanced features:
    - Variable cultivar count per zone (0 to N)
    - Added major_crop_areas field
    - Improved field descriptions
    
    Output per cultivar:
        {
            "cultivar_name": "...",
            "characteristics": { ... with major_crop_areas ... },
            "coefficients": { ... }
        }
    """

    AGENT_NAME = "StandaloneCultivarHelperAgent_v2"

    # ========================================================================
    # CROP CODE -> NAME MAPPING
    # ========================================================================
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

    # ========================================================================
    # MAIN ENTRY POINT
    # ========================================================================

    @staticmethod
    def process(state: Dict[str, Any], verbose: bool = False) -> Dict[str, Any]:
        """
        Main processing function.

        Args:
            state: Plain dictionary containing:
                - config (dict, optional)
                - crop_code (str)
                - crop_name_text (str, optional)
                - zone_name (str): agro-ecological zone name
                - country (str): country name
                - generator_model (str, optional): LLM model name
            verbose: If True, print detailed logs. If False, print progress only.

        Returns:
            Updated state with "cultivar_helper_output" added.
        """
        agent = StandaloneCultivarHelperAgent.AGENT_NAME

        def log(msg: str, force: bool = False):
            if verbose or force:
                print(f"[{agent}] {msg}")

        def progress(msg: str):
            """Always printed to show progress."""
            print(f"[{agent}] {msg}")

        progress("Agent started")

        # ====================================================================
        # STEP 1: EXTRACT REQUIRED INPUTS FROM STATE
        # ====================================================================
        config = state.get("config", {}) or {}

        crop_code = state.get("crop_code", "")
        if not crop_code:
            crop_code = (config.get("cultivar", {}) or {}).get("CR", "MZ")
        crop_code = str(crop_code).strip() or "MZ"

        crop_name = state.get("crop_name_text", "")
        if not crop_name:
            crop_name = config.get("crop_name", "")
        if not crop_name:
            crop_name = StandaloneCultivarHelperAgent.CROP_MAP.get(crop_code, crop_code)

        zone_name = state.get("zone_name", "Unknown Zone")
        country = state.get("country", "Unknown Country")

        log(f"🌍 Country: {country}")
        log(f"📍 Zone: {zone_name}")
        log(f"🌾 Crop: {crop_name} ({crop_code})")

        # ====================================================================
        # STEP 2: RESOLVE GENOTYPE DIRECTORY
        # ====================================================================
        genotype_dir = Path(__file__).resolve().parents[1] / "Genotype"

        if not genotype_dir.exists():
            msg = f"Genotype directory not found at {genotype_dir}"
            state.setdefault("errors", []).append(f"{agent}: {msg}")
            progress(f"❌ {msg}")
            return state

        log(f"📁 Genotype directory: {genotype_dir}")

        # ====================================================================
        # STEP 3: GENERATE CULTIVAR LIST (v2: variable count)
        # ====================================================================
        progress("Step 1/4: Generating cultivar list for zone...")

        cultivar_list = StandaloneCultivarHelperAgent._generate_cultivar_list(
            state, crop_name, crop_code, zone_name, country, verbose=verbose
        )

        if cultivar_list is None:
            msg = "Failed to generate cultivar list"
            state.setdefault("errors", []).append(f"{agent}: {msg}")
            progress(f"❌ {msg}")
            return state

        # v2: Allow empty list if zone is unsuitable
        if len(cultivar_list) == 0:
            progress(f"✅ Zone unsuitable for {crop_name} - no cultivars generated")
            state["cultivar_helper_output"] = {}
            state.setdefault("messages", []).append(
                f"{agent}: Zone unsuitable - 0 cultivars"
            )
            return state

        progress(f"✅ Generated {len(cultivar_list)} cultivar candidates")
        log(f"   Cultivars: {cultivar_list}")

        # ====================================================================
        # STEP 4: LOAD ALL .CUL FILES
        # ====================================================================
        all_cul_files = get_all_cul_file_contents(genotype_dir, crop_code)

        if all_cul_files:
            file_names = [f.name for f, _ in all_cul_files]
            log(f"📄 Loaded {len(all_cul_files)} .CUL file(s): {', '.join(file_names)}")
        else:
            log(f"⚠️ No .CUL files found for {crop_code}")

        # ====================================================================
        # STEP 5: PROCESS EACH CULTIVAR
        # ====================================================================
        progress("Step 2/4: Processing each cultivar...")

        cultivar_results = {}

        for idx, cultivar_name in enumerate(cultivar_list, 1):
            progress(f"  [{idx}/{len(cultivar_list)}] Processing: {cultivar_name}")

            result = StandaloneCultivarHelperAgent._process_single_cultivar(
                state, cultivar_name, crop_name, crop_code,
                zone_name, country, all_cul_files, verbose=verbose
            )

            cultivar_results[cultivar_name] = result

            coeff_source = result.get("coefficients", {}).get("source", "none")
            log(f"    └─ Coefficients source: {coeff_source}")

        # ====================================================================
        # STEP 6: SAVE RESULTS TO STATE
        # ====================================================================
        state["cultivar_helper_output"] = cultivar_results
        state.setdefault("messages", []).append(
            f"{agent}: Processed {len(cultivar_list)} cultivars"
        )

        summary = StandaloneCultivarHelperAgent._summarize_results(cultivar_results)

        progress(
            f"📊 Summary: {summary['local']} local .CUL, "
            f"{summary['web']} web paper, "
            f"{summary['analog']} analog, "
            f"{summary['not_found']} not found"
        )

        progress("Agent completed")
        return state

    # ========================================================================
    # STEP 3: GENERATE CULTIVAR LIST (v2: variable count)
    # ========================================================================

    @staticmethod
    def _generate_cultivar_list(
        state: Dict[str, Any],
        crop_name: str,
        crop_code: str,
        zone_name: str,
        country: str,
        verbose: bool = False
    ) -> Optional[List[str]]:
        """
        Generate list of suitable cultivars using LLM.
        v2: Returns empty list if zone is unsuitable (not None).
        """
        agent = StandaloneCultivarHelperAgent.AGENT_NAME

        prompt = generate_cultivar_list_prompt(
            crop_name, crop_code, zone_name, country
        )

        gen_model = state.get("generator_model", "gpt-5")

        try:
            if verbose:
                print(f"[{agent}] 🤖 Calling LLM to generate cultivar list (model={gen_model})")

            llm = get_llm(mode="api", model=gen_model)
            response = llm.invoke(prompt)

            clean = strip_markdown_fences(response)
            cultivar_list = json.loads(clean)

            if not isinstance(cultivar_list, list):
                raise ValueError("LLM did not return a list")

            cultivar_list = [c for c in cultivar_list if c and isinstance(c, str)]
            
            # v2: Empty list is valid (zone unsuitable)
            return cultivar_list

        except Exception as e:
            if verbose:
                print(f"[{agent}] ❌ Error generating cultivar list: {e}")
            state.setdefault("errors", []).append(f"{agent}: Failed to generate cultivar list - {e}")
            return None

    # ========================================================================
    # STEP 5: PROCESS SINGLE CULTIVAR
    # ========================================================================

    @staticmethod
    def _process_single_cultivar(
        state: Dict[str, Any],
        cultivar_name: str,
        crop_name: str,
        crop_code: str,
        zone_name: str,
        country: str,
        all_cul_files: List[Tuple[Path, str]],
        verbose: bool = False
    ) -> Dict[str, Any]:
        """
        Process a single cultivar through the workflow:
          1. LLM predicts agronomic characteristics (always)
          2. Search local .CUL files for coefficients
          3. If not found locally, search research papers for coefficients

        Returns:
            {
                "cultivar_name": str,
                "characteristics": { ... },
                "coefficients": { ... }
            }
        """
        agent = StandaloneCultivarHelperAgent.AGENT_NAME

        # ==================================================================
        # STEP A: EXTRACT CHARACTERISTICS (ALWAYS RUNS FIRST)
        # ==================================================================
        if verbose:
            print(f"[{agent}]   ├─ Extracting agronomic characteristics...")

        characteristics = StandaloneCultivarHelperAgent._extract_characteristics(
            state, cultivar_name, crop_name, zone_name, country, verbose=verbose
        )

        # ==================================================================
        # STEP B: SEARCH LOCAL .CUL FILES FOR COEFFICIENTS
        # ==================================================================
        coefficients = None

        if all_cul_files:
            found_in_file = search_cultivar_in_all_cul_files(cultivar_name, all_cul_files)

            if found_in_file:
                cul_file, cul_content = found_in_file
                if verbose:
                    print(f"[{agent}]   ├─ Found in {cul_file.name}, parsing coefficients...")

                local_result = StandaloneCultivarHelperAgent._parse_local_cul_file(
                    state, cultivar_name, crop_code, cul_content, verbose=verbose
                )

                if local_result.get("found"):
                    coefficients = {
                        "found": True,
                        "source": f"Local .CUL file: {cul_file.name}",
                        "source_url": None,
                        "coefficients": local_result.get("coefficients", {}),
                        "notes": f"Parsed from local file {cul_file.name}. "
                                 f"INGENO: {local_result.get('ingeno', 'N/A')}. "
                                 f"Cultivar name in file: {local_result.get('cultivar_name', cultivar_name)}"
                    }
            else:
                if verbose:
                    print(f"[{agent}]   ├─ Not found in any local .CUL files")
        else:
            if verbose:
                print(f"[{agent}]   ├─ No .CUL files available to search")

        # ==================================================================
        # STEP C: REAL WEB SEARCH + FETCH (Step 2 of fallback chain)
        # ==================================================================
        if coefficients is None:
            if verbose:
                print(f"[{agent}]   ├─ Step 2: Searching web for published coefficients...")

            web_result = StandaloneCultivarHelperAgent._search_web_for_coefficients(
                state, cultivar_name, crop_name, crop_code, zone_name, country, verbose=verbose
            )

            if web_result:
                coefficients = web_result
                if verbose:
                    print(f"[{agent}]   ├─ ✅ Found via web: {coefficients['source']}")

        # ==================================================================
        # STEP D: ANALOG CULTIVAR FROM .CUL FILES (Step 3 of fallback chain)
        # ==================================================================
        if coefficients is None:
            if verbose:
                print(f"[{agent}]   ├─ Step 3: Looking for analog cultivar in .CUL files...")

            if all_cul_files:
                analog_result = StandaloneCultivarHelperAgent._find_analog_from_cul(
                    state, cultivar_name, characteristics, all_cul_files, crop_code, verbose=verbose
                )
                if analog_result:
                    coefficients = analog_result
                    if verbose:
                        print(f"[{agent}]   ├─ ✅ Analog found: {coefficients['source']}")

        # ==================================================================
        # ASSEMBLE FINAL OUTPUT
        # ==================================================================
        if coefficients is None:
            coefficients = {"found": False, "source": "not_found", "source_url": None, "coefficients": {}}

        return {
            "cultivar_name": cultivar_name,
            "characteristics": characteristics,
            "coefficients": coefficients,
        }

    # ========================================================================
    # EXTRACT CHARACTERISTICS (v2: includes major_crop_areas)
    # ========================================================================

    @staticmethod
    def _extract_characteristics(
        state: Dict[str, Any],
        cultivar_name: str,
        crop_name: str,
        zone_name: str,
        country: str,
        verbose: bool = False
    ) -> Dict[str, Any]:
        """Extract agronomic characteristics using LLM."""
        agent = StandaloneCultivarHelperAgent.AGENT_NAME

        prompt = extract_characteristics_prompt(crop_name, cultivar_name, zone_name, country)
        gen_model = state.get("generator_model", "gpt-5")

        try:
            llm = get_llm(mode="api", model=gen_model)
            response = llm.invoke(prompt)

            clean = strip_markdown_fences(response)
            result = json.loads(clean)

            # Normalize: ensure we return the nested structure expected
            return {
                "data": result.get("characteristics", {}),
                "source": result.get("source", "LLM prediction"),
                "source_url": result.get("source_url", None),
                "confidence": result.get("confidence", "medium"),
            }

        except Exception as e:
            if verbose:
                print(f"[{agent}]   └─ Error extracting characteristics: {e}")
            return {
                "data": {
                    "maturity_class": "unknown",
                    "error": str(e)
                },
                "source": "Error during extraction",
                "source_url": None,
                "confidence": "low",
            }

    # ========================================================================
    # PARSE LOCAL .CUL FILE (unchanged from v1)
    # ========================================================================

    @staticmethod
    def _parse_local_cul_file(
        state: Dict[str, Any],
        cultivar_name: str,
        crop_code: str,
        cul_content: str,
        verbose: bool = False
    ) -> Dict[str, Any]:
        """Parse coefficients for specific cultivar from .CUL file using LLM."""
        agent = StandaloneCultivarHelperAgent.AGENT_NAME

        prompt = parse_cul_file_coefficients_prompt(crop_code, cultivar_name, cul_content)
        gen_model = state.get("generator_model", "gpt-5")

        try:
            llm = get_llm(mode="api", model=gen_model)
            response = llm.invoke(prompt)

            clean = strip_markdown_fences(response)
            result = json.loads(clean)
            return result

        except Exception as e:
            if verbose:
                print(f"[{agent}]   └─ Error parsing .CUL file: {e}")
            return {"found": False, "reason": f"Parse error: {e}"}

    # ========================================================================
    # STEP C: REAL WEB SEARCH + FETCH FOR COEFFICIENTS
    # ========================================================================

    @staticmethod
    def _search_web_for_coefficients(
        state: Dict[str, Any],
        cultivar_name: str,
        crop_name: str,
        crop_code: str,
        zone_name: str,
        country: str,
        verbose: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Step 2 of fallback chain: Real web search + page fetch.
        Fires DuckDuckGo queries, fetches open-access pages, then asks
        the LLM to extract the coefficient table from the page text.
        Returns a coefficients dict on success, or None on failure.
        """
        agent = StandaloneCultivarHelperAgent.AGENT_NAME

        try:
            try:
                from ddgs import DDGS
            except ImportError:
                from duckduckgo_search import DDGS
        except ImportError:
            if verbose:
                print(f"[{agent}]   ├─ ddgs not installed, skipping web step")
            return None

        gen_model = state.get("generator_model", "gpt-5")

        queries = [
            f'DSSAT CERES {crop_name} "{cultivar_name}" genotypic coefficients P1 P2 P5',
            f'"{cultivar_name}" DSSAT calibration {country} coefficients',
            f'DSSAT {crop_name} calibration {country} {zone_name} coefficients table',
        ]

        # Domains where full text is freely accessible
        OPEN_ACCESS_DOMAINS = [
            "pmc.ncbi.nlm.nih.gov",
            "ncbi.nlm.nih.gov/pmc",
            "plos",
            "biorxiv.org",
            "mdpi.com",
            "frontiersin.org",
            "tandfonline.com",
            "researchgate.net",
        ]

        for query in queries:
            try:
                if verbose:
                    print(f"[{agent}]   ├─ Web search: {query}")

                with DDGS() as ddgs:
                    search_results = list(ddgs.text(query, max_results=5))

                time.sleep(1)  # avoid rate-limiting

                for result in search_results:
                    url = result.get("href", "")
                    if not url:
                        continue

                    is_open = any(domain in url for domain in OPEN_ACCESS_DOMAINS)
                    is_pdf = url.lower().endswith(".pdf")
                    if not is_open and not is_pdf:
                        continue

                    try:
                        resp = requests.get(
                            url, timeout=12,
                            headers={"User-Agent": "Mozilla/5.0 (compatible; research-bot/1.0)"}
                        )
                        if resp.status_code != 200:
                            continue

                        soup = BeautifulSoup(resp.text, "html.parser")
                        page_text = soup.get_text(separator=" ", strip=True)

                        # Pre-filter: page must mention the cultivar or DSSAT coefficients
                        has_cultivar = cultivar_name.lower() in page_text.lower()
                        has_coeffs = any(tok in page_text for tok in ["P1", "PHINT", "genotypic"])
                        if not (has_cultivar or has_coeffs):
                            continue

                        if verbose:
                            print(f"[{agent}]   ├─ Fetching: {url}")

                        prompt = extract_coefficients_from_paper_prompt(
                            crop_name, crop_code, cultivar_name, page_text
                        )
                        llm = get_llm(mode="api", model=gen_model)
                        response = llm.invoke(prompt)
                        clean = strip_markdown_fences(response)
                        parsed = json.loads(clean)

                        if parsed.get("found"):
                            return {
                                "found": True,
                                "source": f"WebFetch: {url}",
                                "source_url": url,
                                "coefficients": parsed.get("coefficients", {}),
                                "notes": parsed.get("notes", "Extracted from published paper"),
                            }

                    except Exception:
                        continue  # try next URL

            except Exception as e:
                if verbose:
                    print(f"[{agent}]   ├─ Web search error for query '{query}': {e}")
                continue  # try next query

        return None  # all queries exhausted without a hit

    # ========================================================================
    # STEP D: ANALOG CULTIVAR FROM .CUL FILES
    # ========================================================================

    @staticmethod
    def _find_analog_from_cul(
        state: Dict[str, Any],
        cultivar_name: str,
        characteristics: Dict[str, Any],
        all_cul_files: List[Tuple[Path, str]],
        crop_code: str,
        verbose: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Step 3 of fallback chain: Find the closest cultivar already in .CUL files
        based on matching traits (DTM, maturity class) and use its coefficients
        as a proxy for the unknown cultivar.
        Returns a coefficients dict on success, or None on failure.
        """
        agent = StandaloneCultivarHelperAgent.AGENT_NAME
        gen_model = state.get("generator_model", "gpt-5")
        crop_name = StandaloneCultivarHelperAgent.CROP_MAP.get(crop_code, crop_code)

        for cul_file, cul_content in all_cul_files:
            try:
                prompt = find_analog_cultivar_prompt(
                    crop_name, crop_code, cultivar_name, characteristics, cul_content
                )
                llm = get_llm(mode="api", model=gen_model)
                response = llm.invoke(prompt)
                clean = strip_markdown_fences(response)
                parsed = json.loads(clean)

                if parsed.get("found"):
                    analog_name = parsed.get("analog_cultivar_name", "unknown")
                    if verbose:
                        print(f"[{agent}]   ├─ Analog: '{analog_name}' from {cul_file.name}")
                    return {
                        "found": True,
                        "source": f"analog: {analog_name} from {cul_file.name}",
                        "source_url": None,
                        "coefficients": parsed.get("coefficients", {}),
                        "notes": parsed.get("match_reason", ""),
                    }

            except Exception as e:
                if verbose:
                    print(f"[{agent}]   ├─ Analog search error in {cul_file.name}: {e}")
                continue

        return None  # no analog found across all .CUL files

    # ========================================================================
    # SUMMARIZE RESULTS
    # ========================================================================

    @staticmethod
    def _summarize_results(cultivar_results: Dict[str, Dict]) -> Dict[str, int]:
        """Summarize results by coefficient source type (3-step fallback chain)."""
        summary = {
            "local": 0,
            "web": 0,
            "analog": 0,
            "not_found": 0,
        }

        for result in cultivar_results.values():
            coeff = result.get("coefficients", {})
            if not coeff.get("found", False):
                summary["not_found"] += 1
            else:
                source = coeff.get("source", "")
                if "Local .CUL file" in source:
                    summary["local"] += 1
                elif "WebFetch" in source:
                    summary["web"] += 1
                elif source.startswith("analog:"):
                    summary["analog"] += 1
                else:
                    summary["not_found"] += 1

        return summary

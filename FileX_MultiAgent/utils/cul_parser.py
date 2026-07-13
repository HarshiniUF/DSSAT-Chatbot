"""
CUL File Cultivar Matcher

Simplified approach — NO full CUL file parsing into JSON.
Instead, sends raw CUL file content directly to LLM and asks it
to find the INGENO (VAR#) and coefficients for a specific cultivar name.

Flow:
1. Filter AEZ cultivars to those with coefficients.found == True
2. If multiple, LLM picks the best/most-used for the area
3. Send raw CUL file content + chosen cultivar name to LLM → get INGENO + details
4. Fallback: if no AEZ cultivar found in CUL file, ask LLM for medium-season generic

Usage:
    from utils.cul_parser import parse_and_match_cultivar

    matched_name, details = parse_and_match_cultivar(
        cultivar_list=state["cultivar_list"],
        crop_code="MZ",
    )
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

from utils.llm import get_llm
from utils.helpers import strip_markdown_fences

# Reuse CUL file discovery helpers from the standalone cultivar helper agent
from agents.standalone_cultivar_helper_agent import (
    find_cul_files,
    get_all_cul_file_contents,
)


# ============================================================================
# CONSTANTS
# ============================================================================

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_DEFAULT_GENOTYPE_DIR = _PROJECT_ROOT / "Genotype"


# ============================================================================
# INTERNAL: Filter AEZ cultivars to only those with coefficients
# ============================================================================

def _split_cultivars_by_calibration(
    zone_cultivars_dict: dict,
) -> tuple[List[str], List[str]]:
    """
    Split zone cultivars into two priority groups based on coefficient source:
      - calibrated: source starts with "Local" (directly calibrated in CUL file)
      - analog:     source starts with "analog" (borrowed from a similar cultivar)

    Returns (calibrated_names, analog_names). Both lists contain only entries
    where coefficients["found"] == True.
    """
    calibrated: List[str] = []
    analog: List[str] = []
    for name, data in zone_cultivars_dict.items():
        coeff = data.get("coefficients", {})
        if not coeff.get("found", False):
            continue
        source = coeff.get("source", "")
        if source.lower().startswith("local"):
            calibrated.append(name)
        else:
            analog.append(name)
    return calibrated, analog


# ============================================================================
# INTERNAL: Extract analog CUL name from source string
# ============================================================================

def _extract_analog_cul_name(source: str) -> Optional[str]:
    """
    Parse e.g. 'analog: SWEET CORN from MZCER048.CUL' → 'SWEET CORN'.
    Returns None if source is not an analog entry.
    """
    m = re.match(r'analog:\s*(.+?)\s+from\s+\S+\.CUL', source, re.IGNORECASE)
    return m.group(1).strip() if m else None


# ============================================================================
# INTERNAL: LLM picks the best cultivar from a list for the location
# ============================================================================

def _select_best_cultivar(
    cultivar_names: List[str],
    crop_code: str,
    zone_name: str,
    model: str = "gpt-5",
) -> str:
    """
    When multiple AEZ cultivars have coefficients, use LLM to pick the
    best/most commonly used one for that crop in that zone/area.
    """
    prompt = f"""You are an agronomist expert in crop variety selection.

**Task**: From the list below, pick the ONE cultivar that is most commonly used
and best suited for {crop_code} crop production in the "{zone_name}" agro-ecological zone.

**Cultivar options** (all have DSSAT coefficients available):
{json.dumps(cultivar_names)}

**Selection criteria**:
1. Most widely grown/popular in the region
2. Most commonly used in DSSAT simulations for this area
3. Best documented with reliable coefficient data
4. If unsure, prefer the cultivar with the most research backing

**Output**: Return ONLY valid JSON:
{{
  "selected": "<exact cultivar name from the list>",
  "reason": "<brief explanation>"
}}

Rules:
- "selected" must be EXACTLY as it appears in the list
- Return only JSON, no markdown fences"""

    print(f"[cul_parser] Asking LLM to select best cultivar from {len(cultivar_names)} options...")
    llm = get_llm(mode="api", model=model)
    response = llm.invoke(prompt)

    clean = strip_markdown_fences(response)
    result = json.loads(clean)

    selected = result.get("selected", "")
    reason = result.get("reason", "")

    if selected not in cultivar_names:
        lower_map = {n.lower(): n for n in cultivar_names}
        if selected.lower() in lower_map:
            selected = lower_map[selected.lower()]
        else:
            print(f"[cul_parser] LLM selected '{selected}' which is not in the list. Using first: {cultivar_names[0]}")
            selected = cultivar_names[0]

    print(f"[cul_parser] Selected cultivar: '{selected}' — {reason}")
    return selected


# ============================================================================
# INTERNAL: Send raw CUL content + cultivar name to LLM to get INGENO
# ============================================================================

def _lookup_cultivar_in_cul(
    cul_file_contents: List[Tuple[Path, str]],
    cultivar_name: str,
    crop_code: str,
    model: str = "gpt-5",
) -> Optional[dict]:
    """
    Send raw CUL file content to LLM and ask it to find the INGENO (VAR#)
    and all coefficient values for a specific cultivar name.

    Returns dict with keys: VAR#, ECO#, EXPNO, + all coefficients, or None if not found.
    """
    file_sections = []
    for file_path, content in cul_file_contents:
        file_sections.append(
            f"--- BEGIN FILE: {file_path.name} ---\n{content}\n--- END FILE: {file_path.name} ---"
        )
    combined_content = "\n\n".join(file_sections)

    prompt = f"""You are a DSSAT file reading expert. I need you to find a specific cultivar
in the .CUL file below and return its data.

**Cultivar name to find**: "{cultivar_name}"
**Crop code**: {crop_code}

**CUL File Content**:
{combined_content}

**How CUL files work**:
- Lines starting with "!" are comments
- Lines starting with "@" are column headers (e.g. @VAR#  VRNAME.......... EXPNO   ECO#    P1    P2    P5    G2    G3 PHINT)
- Data lines have: VAR# (cols 1-6), VRNAME (cols 7-22), then EXPNO, ECO#, and numeric coefficients
- The VRNAME column is the cultivar name — search for "{cultivar_name}" in this column
- Match should be case-insensitive and ignore extra whitespace

**Task**: Find the data line where VRNAME matches "{cultivar_name}" and extract ALL values.

**Output**: Return ONLY valid JSON:
{{
  "found": true,
  "cultivar_name": "<exact VRNAME as it appears in the file>",
  "VAR#": "<the 6-char genotype code from columns 1-6>",
  "ECO#": "<ecotype code>",
  "EXPNO": "<experiment number or null if '.'>",
  <for each coefficient column from the @ header line>
  "<COEFF_NAME>": <numeric_value_as_float>,
  ...
}}

If the cultivar is NOT found in the file, return:
{{
  "found": false,
  "cultivar_name": "{cultivar_name}",
  "message": "Not found in CUL file"
}}

Rules:
- VAR# is the INGENO code (e.g. "KY0011", "IB0001") — this is critical
- Numeric values must be floats, not strings
- If a value is "." use null
- Return ONLY JSON, no markdown fences"""

    print(f"[cul_parser] Asking LLM to find '{cultivar_name}' in CUL file (model={model})...")
    llm = get_llm(mode="api", model=model)
    response = llm.invoke(prompt)

    clean = strip_markdown_fences(response)
    result = json.loads(clean)

    if not result.get("found", False):
        print(f"[cul_parser] LLM says '{cultivar_name}' not found in CUL file.")
        return None

    print(f"[cul_parser] Found '{cultivar_name}' → VAR#={result.get('VAR#', '?')}, ECO#={result.get('ECO#', '?')}")
    return result


# ============================================================================
# INTERNAL: Fallback — ask LLM for medium-season generic from CUL file
# ============================================================================

def _lookup_medium_season_generic(
    cul_file_contents: List[Tuple[Path, str]],
    crop_code: str,
    model: str = "gpt-5",
) -> Tuple[str, dict]:
    """
    Fallback: ask LLM to find the medium-season generic cultivar in the CUL file
    and return its name + details.
    """
    file_sections = []
    for file_path, content in cul_file_contents:
        file_sections.append(
            f"--- BEGIN FILE: {file_path.name} ---\n{content}\n--- END FILE: {file_path.name} ---"
        )
    combined_content = "\n\n".join(file_sections)

    prompt = f"""You are a DSSAT file reading expert. I need you to find the **medium-season
generic** cultivar in the .CUL file below and return its data.

**Crop code**: {crop_code}

**CUL File Content**:
{combined_content}

**Context**: DSSAT .CUL files typically include generic cultivars like "MEDIUM SEASON",
"LONG SEASON", "SHORT SEASON". I need the medium-season one as a safe default.

**How CUL files work**:
- Lines starting with "@" are column headers
- Data lines have: VAR# (cols 1-6), VRNAME (cols 7-22), then EXPNO, ECO#, and coefficients
- Look for a VRNAME containing "MEDIUM" — this is the medium-season generic

**Output**: Return ONLY valid JSON:
{{
  "found": true,
  "cultivar_name": "<exact VRNAME>",
  "VAR#": "<genotype code>",
  "ECO#": "<ecotype code>",
  "EXPNO": "<value or null>",
  <coefficient columns>: <float values>,
  "reason": "<brief explanation of why this is the medium-season generic>"
}}

Rules:
- Avoid MINIMA/MAXIMA rows
- Prefer entries with "MEDIUM" in the name
- Numeric values as floats
- Return ONLY JSON, no markdown fences"""

    print(f"[cul_parser] Asking LLM for medium-season generic cultivar from CUL file...")
    llm = get_llm(mode="api", model=model)
    response = llm.invoke(prompt)

    clean = strip_markdown_fences(response)
    result = json.loads(clean)

    if not result.get("found", False):
        raise ValueError(f"LLM could not find a medium-season generic cultivar in the CUL file.")

    cultivar_name = result.get("cultivar_name", "")
    print(f"[cul_parser] Fallback: medium-season generic '{cultivar_name}' → VAR#={result.get('VAR#', '?')}")

    return (cultivar_name, result)


# ============================================================================
# PUBLIC: Main entry point
# ============================================================================

def parse_and_match_cultivar(
    cultivar_list: Tuple[str, dict],
    crop_code: str,
    genotype_dir: Optional[Path] = None,
    model: str = "gpt-5",
) -> Tuple[str, dict]:
    """
    Find a cultivar's INGENO and CNAME from the CUL file.

    Priority:
      1. Locally-calibrated cultivars (coefficients.source starts with 'Local') —
         looked up by their exact name in the CUL file.
      2. Analog cultivars (coefficients.source starts with 'analog') —
         the analog CUL entry name is extracted from the source string and looked
         up in the CUL file to get INGENO; the original cultivar name is preserved
         as CNAME.  e.g. "DKC 910" (source: analog: SWEET CORN …) →
         CNAME="DKC 910", INGENO=IB0037 (VAR# of SWEET CORN in CUL).
      3. Medium-season generic fallback if nothing resolves.

    Args:
        cultivar_list: Tuple (zone_name, zone_cultivars_dict) from state["cultivar_list"].
        crop_code: DSSAT 2-letter crop code.
        genotype_dir: Path to Genotype/ directory. Defaults to version_3/Genotype/.
        model: LLM model name. Default "gpt-5".

    Returns:
        Tuple of (cname, details_dict).
        details_dict contains at minimum: VAR# (INGENO), ECO#, and coefficient values.
    """
    if genotype_dir is None:
        genotype_dir = _DEFAULT_GENOTYPE_DIR

    crop_code = (crop_code or "").strip().upper()
    if not crop_code:
        raise ValueError("crop_code must be a non-empty string (e.g. 'MZ', 'WH').")

    # -----------------------------------------------------------------------
    # Step 1: Load raw CUL file content
    # -----------------------------------------------------------------------
    print(f"[cul_parser] Fetching .CUL files for crop code '{crop_code}'...")
    cul_file_contents = get_all_cul_file_contents(genotype_dir, crop_code)

    if not cul_file_contents:
        raise FileNotFoundError(
            f"No .CUL files found for crop code '{crop_code}' in {genotype_dir}."
        )

    file_names = [f.name for f, _ in cul_file_contents]
    print(f"[cul_parser] Found {len(cul_file_contents)} CUL file(s): {', '.join(file_names)}")

    # -----------------------------------------------------------------------
    # Step 2: Split AEZ cultivars into calibrated (Local) vs analog groups
    # -----------------------------------------------------------------------
    zone_name, zone_cultivars_dict = cultivar_list

    if not zone_cultivars_dict:
        raise ValueError(f"cultivar_list has no cultivars for zone '{zone_name}'.")

    calibrated_names, analog_names = _split_cultivars_by_calibration(zone_cultivars_dict)

    print(f"[cul_parser] Zone '{zone_name}': {len(zone_cultivars_dict)} total, "
          f"{len(calibrated_names)} locally-calibrated, {len(analog_names)} analog")

    # -----------------------------------------------------------------------
    # Step 3: Try calibrated cultivars first, then analog as fallback
    # -----------------------------------------------------------------------
    def _resolve_one(cname: str, is_analog: bool) -> Optional[dict]:
        """
        Look up a single cultivar in the CUL file.

        For calibrated cultivars: search by the cultivar name directly.
        For analog cultivars: search by the analog entry name extracted from
        coefficients.source (e.g. 'SWEET CORN' from 'analog: SWEET CORN from …').
        Returns the CUL details dict (with VAR#) or None.
        """
        # Try the cultivar name directly first (works for calibrated, and
        # occasionally for analog cultivars that share a CUL entry name).
        details = _lookup_cultivar_in_cul(cul_file_contents, cname, crop_code, model=model)
        if details:
            return details

        if not is_analog:
            return None

        # Extract the analog CUL name and look that up instead.
        source = zone_cultivars_dict.get(cname, {}).get("coefficients", {}).get("source", "")
        analog_cul_name = _extract_analog_cul_name(source)
        if not analog_cul_name:
            return None

        print(f"[cul_parser] '{cname}' not in CUL directly; trying analog '{analog_cul_name}'...")
        return _lookup_cultivar_in_cul(cul_file_contents, analog_cul_name, crop_code, model=model)

    def _try_cultivar_list(candidates: List[str], is_analog: bool, label: str):
        if not candidates:
            return None, None

        if len(candidates) == 1:
            chosen = candidates[0]
            print(f"[cul_parser] Only one {label} cultivar: '{chosen}'")
        else:
            chosen = _select_best_cultivar(candidates, crop_code, zone_name, model=model)

        details = _resolve_one(chosen, is_analog)
        if details:
            print(f"[cul_parser] Final cultivar ({label}): CNAME='{chosen}' VAR#={details.get('VAR#')}")
            return chosen, details

        for name in [n for n in candidates if n != chosen]:
            print(f"[cul_parser] Trying {label} alternative: '{name}'...")
            details = _resolve_one(name, is_analog)
            if details:
                print(f"[cul_parser] Final cultivar ({label}): CNAME='{name}' VAR#={details.get('VAR#')}")
                return name, details

        print(f"[cul_parser] No {label} cultivar resolved in CUL file.")
        return None, None

    chosen_name, details = _try_cultivar_list(calibrated_names, is_analog=False, label="calibrated")

    if chosen_name is None:
        chosen_name, details = _try_cultivar_list(analog_names, is_analog=True, label="analog")

    if chosen_name is not None:
        return (chosen_name, details)

    print(f"[cul_parser] No cultivar with coefficients found in CUL file.")

    # -----------------------------------------------------------------------
    # Step 4: Fallback to medium-season generic
    # -----------------------------------------------------------------------
    print(f"[cul_parser] Falling back to medium-season generic cultivar.")
    name, details = _lookup_medium_season_generic(cul_file_contents, crop_code, model=model)

    print(f"[cul_parser] Final cultivar (fallback): '{name}' → VAR#={details.get('VAR#')}")
    return (name, details)

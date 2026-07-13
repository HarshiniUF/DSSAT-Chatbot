"""
Helper utility functions
"""

from __future__ import annotations

import json
from datetime import datetime, date
from typing import Optional, Tuple

from utils.llm import get_llm

from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter


def convert_date_to_dssat_date(date_str: str) -> date:
    """Convert date from YYYY-MM-DD string to Python date object"""
    try:
        return datetime.strptime(str(date_str), "%Y-%m-%d").date()
    except Exception as e:
        raise ValueError(
            f"convert_date_to_dssat_date: could not parse {date_str!r} as "
            f"YYYY-MM-DD"
        ) from e


def parse_codebook_section(file_path, section_name):
    """Parse DSSAT codebook sections"""
    codes = {}
    in_section = False
    with open(file_path, "r", encoding="latin1") as f:
        for line in f:
            line = line.strip()
            if line.startswith(f"*{section_name}"):
                in_section = True
                continue
            if in_section and line.startswith("*") and not line.startswith(f"*{section_name}"):
                break
            if in_section and line and not line.startswith("!") and not line.startswith("@"):
                parts = line.split()
                if len(parts) > 1:
                    code = parts[0]
                    desc = " ".join(parts[1:])
                    codes[code] = desc
    return codes


def make_code_options_text(codes_dict):
    """Converts code dictionary to a readable string for LLM prompt."""
    return "\n".join([f"{code}: {desc}" for code, desc in codes_dict.items()])


def strip_markdown_fences(text: str) -> str:
    """
    Remove ```json ... ``` or ``` ... ``` fences if the LLM wrapped JSON output in a code block.
    """
    if text is None:
        return ""
    s = str(text).strip()
    if s.startswith("```"):
        lines = s.splitlines()
        lines = lines[1:]  # drop ```json / ```
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        s = "\n".join(lines).strip()
    return s


def get_crop_name(cr: str, cultivar_cr_codes_text: str, model: Optional[str] = None) -> str:
    """
    Get crop name from crop code.
    Now supports optional `model` so Streamlit can control it.
    """
    llm = get_llm(mode="api", model=(model or "gpt-5"))

    prompt = f"""
What is the crop name for this CR code {cr} according to DSSAT/agronomy?
Return only the crop name, no formatting.

Context containing crop codes and their names:
{cultivar_cr_codes_text}
""".strip()

    crop_name = llm.invoke(prompt)
    return str(crop_name).strip()


# def get_location(lat: float, long: float, model: Optional[str] = None) -> str:
#     """
#     Get location name from coordinates (short).
#     Now supports optional `model`.
#     """
#     llm = get_llm(mode="api", model=(model or "gpt-5"))

#     prompt = f"""
# What is the location name for this latitude {lat} and longitude {long}?
# Give output like: "Iowa, USA"
# No extra text.
# """.strip()

#     location = llm.invoke(prompt)
#     return str(location).strip()


# Create a single global geolocator to reuse across calls
_geolocator = Nominatim(user_agent="dssat_helper_app")
_reverse = RateLimiter(_geolocator.reverse, min_delay_seconds=1)  # be polite to the API


def get_location(lat: float, long: float, model: Optional[str] = None) -> str:
    """
    Get location name from coordinates (short).
    Now uses geopy reverse geocoding instead of LLM.
    Returns a short string like: "Iowa, USA"
    """
    try:
        location = _reverse((lat, long), language="en")
        if not location:
            return ("Unknown location","Unknown country")

        addr = location.raw.get("address", {})

        # Try to build something like "City, State, CountryCode" or "State, CountryCode"
        city = (
            addr.get("city")
            or addr.get("town")
            or addr.get("village")
            or addr.get("hamlet")
        )
        state = addr.get("state")
        country = addr.get("country")
        country_code = addr.get("country_code", "").upper() if addr.get("country_code") else ""

        parts = []

        # Prefer city then state (if available)
        if city:
            parts.append(city)
        if state and state not in parts:
            parts.append(state)

        # Add country code or country
        if country:
                parts.append(country)

        # If we managed to build a short name, return it
        if parts:
            return (", ".join(parts),country)

        # Fallback to full address string if nothing else works
        return (location.address,country or "Unknown location")

    except Exception:
        # In production, you'd probably log the error
        return ("Unknown location","Unknown country")

# utils/helpers.py

import subprocess
import os
import sys
from pathlib import Path

def validate_xfile_with_xb2(input_file_path, output_file_path):
    """
    Validate and process FileX files using the Java FileXCustomScriptV1.
    
    Args:
        input_file_path (str): Absolute or relative path to the input FileX file
        output_file_path (str): Absolute or relative path where the output file should be saved
    
    Returns:
        dict: {
            'success': bool,
            'stdout': str,
            'stderr': str,
            'exit_code': int,
            'output_file': str (absolute path if successful)
        }
    
    Raises:
        FileNotFoundError: If input file doesn't exist
        RuntimeError: If Java compilation or execution fails
    """
    
    try:
        # Convert to absolute paths
        input_file_path = os.path.abspath(input_file_path)
        output_file_path = os.path.abspath(output_file_path)
        
        # Validate input file exists
        if not os.path.exists(input_file_path):
            raise FileNotFoundError(f"Input file not found: {input_file_path}")
        
        # Get the xb2 directory (sibling to utils)
        utils_dir = Path(__file__).parent  # utils folder
        project_root = utils_dir.parent     # parent of utils
        xb2_dir = project_root / 'XB2' / 'src'
        
        if not xb2_dir.exists():
            raise FileNotFoundError(f"XB2/src directory not found at: {xb2_dir}")
        
        java_file = 'FileXCustomScriptV1.java'
        java_file_path = xb2_dir / java_file
        
        if not java_file_path.exists():
            raise FileNotFoundError(f"Java file not found: {java_file_path}")
        
        # Ensure output directory exists
        output_dir = os.path.dirname(output_file_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        print(f"Compiling Java file: {java_file}")
        print(f"Working directory: {xb2_dir}")
        
        # Compile the Java file
        compile_process = subprocess.run(
            ['javac', java_file],
            capture_output=True,
            text=True,
            cwd=str(xb2_dir)
        )
        
        if compile_process.returncode != 0:
            error_msg = f"Java compilation failed:\n{compile_process.stderr}"
            print(error_msg, file=sys.stderr)
            return {
                'success': False,
                'stdout': compile_process.stdout,
                'stderr': compile_process.stderr,
                'exit_code': compile_process.returncode,
                'output_file': None
            }
        
        print("Compilation successful!")
        print(f"\nRunning validation on: {input_file_path}")
        print(f"Output will be saved to: {output_file_path}")
        
        # Run the compiled Java class with file paths as arguments
        class_name = java_file.replace('.java', '')
        run_process = subprocess.run(
            ['java', class_name, input_file_path, output_file_path],
            capture_output=True,
            text=True,
            cwd=str(xb2_dir),
            timeout=60  # 60 second timeout
        )
        
        # Print the Java output
        print("\n" + "="*60)
        print("JAVA VALIDATION OUTPUT:")
        print("="*60)
        print(run_process.stdout)
        
        if run_process.stderr:
            print("\nJava Errors/Warnings:", file=sys.stderr)
            print(run_process.stderr, file=sys.stderr)
        
        # Check if validation passed (exit code 0 means success)
        success = run_process.returncode == 0
        
        if success:
            print(f"\n✓ Validation PASSED - Output saved to: {output_file_path}")
        else:
            print(f"\n✗ Validation FAILED - File not saved", file=sys.stderr)
        
        return {
            'success': success,
            'stdout': run_process.stdout,
            'stderr': run_process.stderr,
            'exit_code': run_process.returncode,
            'output_file': output_file_path if success else None
        }
        
    except subprocess.TimeoutExpired:
        error_msg = "Java process timed out after 60 seconds"
        print(error_msg, file=sys.stderr)
        return {
            'success': False,
            'stdout': '',
            'stderr': error_msg,
            'exit_code': -1,
            'output_file': None
        }
    
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        return {
            'success': False,
            'stdout': '',
            'stderr': str(e),
            'exit_code': -1,
            'output_file': None
        }
    
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(error_msg, file=sys.stderr)
        return {
            'success': False,
            'stdout': '',
            'stderr': error_msg,
            'exit_code': -1,
            'output_file': None
        }



from pathlib import Path  # if not already imported at top of helpers.py

# Project root: .../version_3/
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# AEZ database JSON path relative to project root
AEZ_DB_PATH = PROJECT_ROOT / "data" / "cultivar_db"

# Maps DSSAT crop codes to full crop names (must match generate_dataset.py)
_CROP_CODE_TO_NAME = {
    "MZ": "maize", "WH": "wheat", "BA": "barley", "RI": "rice",
    "SB": "soybean", "PN": "peanut", "SG": "sorghum", "ML": "millet",
    "SC": "sugarcane", "TN": "sunflower", "PP": "pigeonpea",
    "CH": "chickpea", "BN": "dry_bean", "CB": "cabbage",
    "TM": "tomato", "PT": "potato",
}


# def _load_aez_database(db_path: Path = AEZ_DB_PATH) -> dict:
#     """
#     Internal helper to load the AEZ database JSON.

#     Args:
#         db_path (Path): Path to AEZ_Database_GPT5.json.

#     Returns:
#         dict: Parsed JSON content.

#     Raises:
#         FileNotFoundError: If file is missing.
#         json.JSONDecodeError: If file is not valid JSON.
#     """
#     with open(db_path, "r", encoding="utf-8") as f:
#         return json.load(f)
    

def _load_aez_database(
    country: str,
    crop_code: str,
    db_path: Path = AEZ_DB_PATH
) -> dict:
    """
    Internal helper to load the AEZ database JSON for a specific country and crop.

    Args:
        country (str): Country name (e.g., "Kenya", "Ethiopia").
        crop_code (str): Crop code (e.g., "MZ", "WH").
        db_path (Path): Base path to AEZ database directory.

    Returns:
        dict: Parsed JSON content.

    Raises:
        FileNotFoundError: If file is missing.
        json.JSONDecodeError: If file is not valid JSON.
        ValueError: If multiple or no JSON files found in the directory.
    """
    # Try crop-name-based path first (generated by generate_dataset.py),
    # fall back to crop-code-based path for backwards compatibility.
    crop_name = _CROP_CODE_TO_NAME.get(crop_code.upper(), crop_code.lower())
    crop_dir = db_path / country.lower() / crop_name

    if not crop_dir.exists():
        crop_dir = db_path / country.lower() / crop_code.lower()

    if not crop_dir.exists():
        return {
            "error": f"AEZ database directory not found for {country}/{crop_code} "
                     f"(tried '{crop_name}' and '{crop_code.lower()}')"
        }
    
    # Find all JSON files in the directory
    json_files = list(crop_dir.glob("*.json"))
    
    if len(json_files) == 0:
        return {
            "error":f"No JSON file found in: {crop_dir}"
        }
    
    if len(json_files) > 1:
        return {
            "error":f"Multiple JSON files found in {crop_dir}: {[f.name for f in json_files]}. "
        }
    
    # Load the single JSON file
    json_file = json_files[0]
    
    with open(json_file, "r", encoding="utf-8") as f:
        return json.load(f)




def get_zone_by_location(location_name: str, country: str,model: Optional[str] = None) -> str:
    """
    Infer the Kenyan agro-ecological zone (AEZ) for a given location name
    using the LLM.

    Args:
        location_name (str): Human-readable location (e.g. "Machakos, Kenya").
        model (Optional[str]): Optional model name override for get_llm.
                               Defaults to gpt-4o in get_llm.

    Returns:
        str: One of the AEZ zone names:
             ["Coastal Lowland", "Inner Lowland", "Lower Highland",
              "Lower Midland", "Upper Midland", "Upper Highland",
              "Tropical Alpine", "Nairobi"]

    Notes:
        - Returns a best-guess zone string.
        - If the LLM output is not recognized, it will throw an error "No Zone Found By LLM"
    """
    from utils.llm import get_llm  # local import to avoid circular issues

    zones_file = Path("data/zones_list.json")
    
    if not zones_file.exists():
        return f"Zones file not found: {zones_file}"
    
    with open(zones_file, "r", encoding="utf-8") as f:
        zones_data = json.load(f)
    
    
    # Get zones for the detected country
    zones = zones_data.get(country, [])
    
    if not zones:
        return f"No zones found for country: {country}"

    zones_text = "\n".join(f"- {z}" for z in zones)


    
    llm = get_llm(mode="api", model=(model or "gpt-5"))


    prompt = f"""
You are an agronomist familiar with {country}'s agro-ecological zones (AEZs).

Given a location in {country} (county, sub-county, town, or general place name),
assign it to the SINGLE most appropriate agro-ecological zone from this list:

{zones_text}

Rules:
- Return ONLY the zone name, exactly as written above.
- Do NOT explain your reasoning.
- Do NOT add any extra words.
- If you are unsure, choose the best approximate zone based on altitude,
  climate and common agronomic usage.

Location: "{location_name}"
""".strip()

    raw_zone = llm.invoke(prompt)
    candidate = (raw_zone or "").strip()

    # Exact match first
    if candidate in zones:
        return candidate

    # Case-insensitive match
    lower_map = {z.lower(): z for z in zones}
    if candidate.lower() in lower_map:
        return lower_map[candidate.lower()]

    # Try to detect zone name inside longer LLM output
    for z in zones:
        if z.lower() in candidate.lower():
            return z

    # Fallback: neutral mid-altitude region
    return "No Zone Found By LLM"


def get_cultivar_list_by_location(
    location_name: str,
    country:str,
    crop_code:str,
    model: Optional[str] = None,
) -> Tuple[str, dict]:
    """
    Given a human-readable location name, infer the AEZ zone using the LLM
    and then return the cultivar information for that zone from the
    AEZ_Database_GPT5.json file.

    Args:
        location_name (str): e.g. "Machakos, Kenya" or "Makueni".
        model (Optional[str]): Optional model name for zone inference.

    Returns:
        Tuple[str, dict]:
            - zone_name (str): The inferred AEZ zone name.
            - zone_cultivars (dict): The entry from AEZ_Database_GPT5["zones"][zone_name],
              i.e. a mapping of cultivar name -> {characteristics, coefficients}.

    Raises:
        FileNotFoundError: If AEZ database file is not found.
        KeyError: If the inferred zone is not present in the database.
        json.JSONDecodeError: If the AEZ database JSON is invalid.
    """
    print("started cultivart list fetching.....")
    if not model:
        model = "gpt-5"
    # 1. Infer zone from location using LLM
    zone_name = get_zone_by_location(location_name,country,model=model)
    if "Zone file not" in zone_name:
        return ("",{})
    
    print(f"zone name fetched.....{zone_name}")
    # 2. Load AEZ database JSON
    data = _load_aez_database(country,crop_code)

    print(f"cultivar list loaded from database....")
    zones_dict = data.get("zones", {})
    if zone_name not in zones_dict:
        # This means your AEZ database does not have that zone key.
        # Raising helps you catch data/config problems early.
        return (f"Inferred zone '{zone_name}' not found in AEZ database.","")

    zone_cultivars = zones_dict[zone_name]

    return (zone_name, zone_cultivars)




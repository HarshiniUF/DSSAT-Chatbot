"""
Experiment Configuration
Central configuration for experiment design and constraints
"""

import json
from pathlib import Path

# ============================================================================
# Workflow Inputs (external JSON -- single source of truth for the values
# that used to be hardcoded here or computed from date.today())
# ============================================================================

_WORKFLOW_INPUTS_PATH = Path(__file__).resolve().parent / "workflow_inputs.json"


def _load_workflow_inputs() -> dict:
    if not _WORKFLOW_INPUTS_PATH.exists():
        raise FileNotFoundError(
            f"workflow_inputs.json not found at {_WORKFLOW_INPUTS_PATH}. "
            "This file is required -- it's the single source for location, "
            "crop, and season-year inputs used by the whole workflow."
        )
    with open(_WORKFLOW_INPUTS_PATH, "r") as f:
        data = json.load(f)
    required = ["latitude", "longitude", "location_name", "crop_name", "season_year"]
    missing = [k for k in required if k not in data]
    if missing:
        raise ValueError(f"workflow_inputs.json is missing required key(s): {missing}")
    return data


_workflow_inputs = _load_workflow_inputs()

# Fixed project location. Every generated experiment uses this single
# location regardless of what region the user's question mentions.
DEFAULT_LATITUDE = _workflow_inputs["latitude"]
DEFAULT_LONGITUDE = _workflow_inputs["longitude"]
DEFAULT_LOCATION_NAME = _workflow_inputs["location_name"]

# Fixed project crop. Every generated experiment uses this single crop
# regardless of what crop the user's question mentions.
DEFAULT_CROP_NAME = _workflow_inputs["crop_name"]

# Fixed season year -- drives SDATE, the weather fetch window, and the
# harvest-window cap, all derived the same way date.today().year used to be.
DEFAULT_SEASON_YEAR = int(_workflow_inputs["season_year"])

# ============================================================================
# Experiment Design Parameters
# ============================================================================

# Maximum number of treatments per experiment
MAX_TREATMENTS = 12

# Minimum number of treatments per experiment
MIN_TREATMENTS = 3

# Yield difference threshold for meaningful treatment difference (%)
YIELD_DIFFERENCE_THRESHOLD = 5.0

# ============================================================================
# Critic Agent Parameters
# ============================================================================

# Maximum iterations for critic feedback loop
MAX_CRITIC_ITERATIONS = 6

# Minimum score for experiment approval (0-10)
# NOTE: This is a threshold for "good" designs. However, we still generate SNX
# files even if score is below this, to allow exploratory simulations.
# The critic will provide feedback for improvement regardless of approval status.
MIN_APPROVAL_SCORE = 7.0

# Minimum score to generate SNX files (can be lower than MIN_APPROVAL_SCORE)
# This allows us to generate files for exploratory simulations
MIN_SCORE_FOR_SNX_GENERATION = 3.0  # NEW: Much more lenient for SNX generation

# ============================================================================
# Fertilizer Parameters
# ============================================================================

# Common fertilizer codes in DSSAT
FERTILIZER_CODES = {
    "DAP": "FE001",      # Diammonium Phosphate
    "MAP": "FE002",      # Monoammonium Phosphate
    "CAN": "FE003",      # Calcium Ammonium Nitrate
    "UREA": "FE004",     # Urea
    "KCl": "FE005",      # Potassium Chloride
}

# Fertilizer application methods
APPLICATION_METHODS = {
    "broadcast": "AP001",      # Broadcast
    "topdress": "AP002",       # Topdress
    "furrow": "AP003",         # Furrow
    "foliar": "AP004",         # Foliar
}

# ============================================================================
# Planting Parameters
# ============================================================================

# Typical planting window (YYYDD format)
PLANTING_WINDOW_START = 25060  # June 1
PLANTING_WINDOW_END = 25150    # May 30 (next year)

# ============================================================================
# Crop Parameters
# ============================================================================

# Crop codes in DSSAT
CROP_CODES = {
    "MZ": "Maize",
    "PN": "Peanut",
    "WH": "Wheat",
    "RI": "Rice",
    "SB": "Sorghum",
    "CO": "Cotton",
}

# ============================================================================
# Configuration Functions
# ============================================================================

def get_max_treatments() -> int:
    """Get maximum number of treatments per experiment"""
    return MAX_TREATMENTS


def get_min_treatments() -> int:
    """Get minimum number of treatments per experiment"""
    return MIN_TREATMENTS


def get_yield_difference_threshold() -> float:
    """Get yield difference threshold for meaningful treatment difference (%)"""
    return YIELD_DIFFERENCE_THRESHOLD


def get_max_critic_iterations() -> int:
    """Get maximum iterations for critic feedback loop"""
    return MAX_CRITIC_ITERATIONS


def get_min_approval_score() -> float:
    """Get minimum score for experiment approval (0-10)"""
    return MIN_APPROVAL_SCORE


def get_fertilizer_code(fertilizer_name: str) -> str:
    """Get DSSAT fertilizer code for given fertilizer name"""
    return FERTILIZER_CODES.get(fertilizer_name.upper(), "FE001")


def get_application_method_code(method: str) -> str:
    """Get DSSAT application method code"""
    return APPLICATION_METHODS.get(method.lower(), "AP001")


def get_crop_name(crop_code: str) -> str:
    """Get crop name for given DSSAT crop code"""
    return CROP_CODES.get(crop_code.upper(), "Unknown")


# ============================================================================
# Validation Functions
# ============================================================================

def is_valid_treatment_count(count: int) -> bool:
    """Check if treatment count is within valid range"""
    return MIN_TREATMENTS <= count <= MAX_TREATMENTS


def is_meaningful_yield_difference(yield_diff: float) -> bool:
    """Check if yield difference is meaningful"""
    return abs(yield_diff) >= YIELD_DIFFERENCE_THRESHOLD


def is_approved_score(score: float) -> bool:
    """Check if score meets approval threshold"""
    return score >= MIN_APPROVAL_SCORE


# ============================================================================
# Configuration Info
# ============================================================================

def get_config_info() -> dict:
    """Get all configuration parameters as dictionary"""
    return {
        "max_treatments": MAX_TREATMENTS,
        "min_treatments": MIN_TREATMENTS,
        "yield_threshold": YIELD_DIFFERENCE_THRESHOLD,
        "max_critic_iterations": MAX_CRITIC_ITERATIONS,
        "min_approval_score": MIN_APPROVAL_SCORE,
        "default_location": DEFAULT_LOCATION_NAME,
        "fertilizers": FERTILIZER_CODES,
        "crops": CROP_CODES,
    }

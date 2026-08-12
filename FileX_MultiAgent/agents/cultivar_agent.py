"""
CultivarAgent - Standalone cultivar database builder.

NOT part of the LangGraph workflow.  Used by generate_dataset.py
(and can be called directly) to build / update the local cultivar JSON
database under  data/cultivar_db/<crop>/<crop>_<CR>_cultivars_list.json

Per-location workflow:
  1. Check whether the location already has an entry in the DB JSON file.
     If yes  → load from DB and return (no LLM calls needed).
     If no   → delegate to StandaloneCultivarHelperAgent to generate
               cultivar data, then save the result to the DB file.

Interface (mirrors StandaloneCultivarHelperAgent so generate_dataset.py
can swap the import with no other changes):

    state in:
        crop_code       (str)  e.g. "PN"
        crop_name_text  (str)  e.g. "Peanut"  (optional, derived if absent)
        location_name   (str)  e.g. "Kaolack, Senegal"
        generator_model (str)  LLM model name  (default "gpt-5")

    state out (added):
        cultivar_helper_output  dict[cultivar_name → {characteristics, coefficients}]
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from agents.standalone_cultivar_helper_agent import StandaloneCultivarHelperAgent


# ============================================================================
# MODULE-LEVEL CONSTANTS
# ============================================================================

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_CULTIVAR_DB_BASE = _PROJECT_ROOT / "data" / "cultivar_db"


# ============================================================================
# INTERNAL HELPERS
# ============================================================================

def _db_file_path(crop_code: str) -> Path:
    """
    Return the canonical JSON path for this crop.
    Matches the structure produced by generate_dataset.py:
      data/cultivar_db/<crop_name_lower>/<crop_name_lower>_<CR>_cultivars_list.json
    """
    crop_name = StandaloneCultivarHelperAgent.CROP_MAP.get(crop_code.upper(), crop_code)
    crop_dir = crop_name.lower().replace(" ", "_")
    filename = f"{crop_dir}_{crop_code}_cultivars_list.json"
    return _CULTIVAR_DB_BASE / crop_dir / filename


def _load_db_json(crop_code: str) -> Dict[str, Any]:
    """Load the DB JSON for this crop, or return empty dict if the file is missing."""
    fp = _db_file_path(crop_code)
    if not fp.exists():
        return {}
    try:
        with open(fp, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_location_to_db(
    crop_code: str,
    location_name: str,
    location_data: Dict[str, Any],
) -> None:
    """
    Insert / update a single location entry in the DB JSON file.
    Creates the file and parent directories if they do not yet exist.
    All previously saved locations are preserved.
    """
    fp = _db_file_path(crop_code)
    fp.parent.mkdir(parents=True, exist_ok=True)

    # Load existing data (or start fresh)
    if fp.exists():
        try:
            with open(fp, "r", encoding="utf-8") as f:
                db = json.load(f)
        except Exception:
            db = {}
    else:
        db = {}

    if not db:
        db = {
            "crop": crop_code,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_locations": 0,
            "processed": 0,
            "locations": {},
        }

    db.setdefault("locations", {})[location_name] = location_data
    db["processed"] = len(db["locations"])
    db["total_locations"] = max(db.get("total_locations", 0), db["processed"])
    db["generated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(fp, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)


# ============================================================================
# AGENT
# ============================================================================

class CultivarAgent:
    """
    Standalone cultivar DB builder.

    Wraps StandaloneCultivarHelperAgent and adds a DB persistence layer:
    locations already present in the JSON database are returned from disk
    without any LLM calls; missing locations are generated and saved.

    Called by generate_dataset.py instead of StandaloneCultivarHelperAgent.
    """

    AGENT_NAME = "CultivarAgent"

    @staticmethod
    def process(state: Dict[str, Any], verbose: bool = False) -> Dict[str, Any]:
        """
        Build or load the cultivar DB entry for one location.

        Args:
            state:   dict with keys: crop_code, location_name,
                     crop_name_text (optional), generator_model (optional).
            verbose: if True, print detailed logs.

        Returns:
            Updated state with ``cultivar_helper_output`` added.
        """
        agent = CultivarAgent.AGENT_NAME

        def log(msg: str):
            if verbose:
                print(f"[{agent}] {msg}")

        def progress(msg: str):
            print(f"[{agent}] {msg}")

        crop_code = str(state.get("crop_code", "MZ")).strip().upper() or "MZ"
        location_name = state.get("location_name", "Unknown Location")
        gen_model = state.get("generator_model", "gpt-5")

        crop_name = state.get("crop_name_text", "")
        if not crop_name:
            crop_name = StandaloneCultivarHelperAgent.CROP_MAP.get(crop_code, crop_code)

        progress(f"Location: {location_name} | Crop: {crop_name} ({crop_code})")

        # ====================================================================
        # STEP 1: Check DB — return from disk if location already exists
        # ====================================================================
        db_data = _load_db_json(crop_code)
        locations_in_db = db_data.get("locations", {})

        if location_name in locations_in_db and locations_in_db[location_name]:
            existing_location = locations_in_db[location_name]
            progress(f"Location already in DB ({len(existing_location)} cultivar(s)) — skipping generation")
            log(f"Loaded from: {_db_file_path(crop_code)}")

            state["cultivar_helper_output"] = existing_location
            state.setdefault("messages", []).append(
                f"{agent}: Location '{location_name}' loaded from DB ({len(existing_location)} cultivar(s))"
            )
            return state

        # ====================================================================
        # STEP 2: Location not in DB — generate via StandaloneCultivarHelperAgent
        # ====================================================================
        progress("Location not in DB — generating now via StandaloneCultivarHelperAgent...")

        helper_state: Dict[str, Any] = {
            "config": {},
            "messages": [],
            "errors": [],
            "crop_code": crop_code,
            "crop_name_text": crop_name,
            "location_name": location_name,
            "generator_model": gen_model,
        }

        helper_result = StandaloneCultivarHelperAgent.process(helper_state, verbose=verbose)

        for err in helper_result.get("errors", []):
            state.setdefault("errors", []).append(f"{agent}: {err}")
        for msg in helper_result.get("messages", []):
            state.setdefault("messages", []).append(msg)

        raw_output: Dict[str, Any] = helper_result.get("cultivar_helper_output", {})

        # Reformat to DB storage format: {cultivar_name: {characteristics, coefficients}}
        location_data: Dict[str, Any] = {
            name: {
                "characteristics": data.get("characteristics", {}),
                "coefficients": data.get("coefficients", {}),
            }
            for name, data in raw_output.items()
        }

        # ====================================================================
        # STEP 3: Save to DB
        # ====================================================================
        _save_location_to_db(crop_code, location_name, location_data)
        progress(f"Saved {len(location_data)} cultivar(s) to DB for location '{location_name}'")
        log(f"DB file: {_db_file_path(crop_code)}")

        state["cultivar_helper_output"] = location_data
        state.setdefault("messages", []).append(
            f"{agent}: Location '{location_name}' generated and saved ({len(location_data)} cultivar(s))"
        )

        return state

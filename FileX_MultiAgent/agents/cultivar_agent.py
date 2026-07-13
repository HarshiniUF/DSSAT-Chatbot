"""
CultivarAgent - Standalone cultivar database builder.

NOT part of the LangGraph workflow.  Used by generate_dataset.py
(and can be called directly) to build / update the local cultivar JSON
database under  data/cultivar_db/<country>/<crop>/<Country>_<CR>_cultivars_list.json

Per-zone workflow:
  1. Check whether the zone already has an entry in the DB JSON file.
     If yes  → load from DB and return (no LLM calls needed).
     If no   → delegate to StandaloneCultivarHelperAgent to generate
               cultivar data, then save the result to the DB file.

Interface (mirrors StandaloneCultivarHelperAgent so generate_dataset.py
can swap the import with no other changes):

    state in:
        country         (str)  e.g. "Kenya"
        crop_code       (str)  e.g. "MZ"
        crop_name_text  (str)  e.g. "Maize"  (optional, derived if absent)
        zone_name       (str)  e.g. "Upper Midland"
        generator_model (str)  LLM model name  (default "gpt-5")

    state out (added):
        cultivar_helper_output  dict[cultivar_name → {characteristics, coefficients}]
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from agents.standalone_cultivar_helper_agent import StandaloneCultivarHelperAgent


# ============================================================================
# MODULE-LEVEL CONSTANTS
# ============================================================================

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_AEZ_DB_BASE  = _PROJECT_ROOT / "data" / "cultivar_db"


# ============================================================================
# INTERNAL HELPERS
# ============================================================================

def _db_file_path(country: str, crop_code: str) -> Path:
    """
    Return the canonical JSON path for this country + crop.
    Matches the structure produced by generate_dataset.py:
      data/cultivar_db/<country_lower>/<crop_name_lower>/<Country>_<CR>_cultivars_list.json
    """
    crop_name   = StandaloneCultivarHelperAgent.CROP_MAP.get(crop_code.upper(), crop_code)
    country_dir = country.lower().replace(" ", "_")
    crop_dir    = crop_name.lower().replace(" ", "_")
    filename    = f"{country}_{crop_code}_cultivars_list.json"
    return _AEZ_DB_BASE / country_dir / crop_dir / filename


def _load_db_json(country: str, crop_code: str) -> Dict[str, Any]:
    """Load the DB JSON for country + crop, or return empty dict if the file is missing."""
    fp = _db_file_path(country, crop_code)
    if not fp.exists():
        return {}
    try:
        with open(fp, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_zone_to_db(
    country: str,
    crop_code: str,
    zone_name: str,
    zone_data: Dict[str, Any],
) -> None:
    """
    Insert / update a single zone entry in the DB JSON file.
    Creates the file and parent directories if they do not yet exist.
    All previously saved zones are preserved.
    """
    fp = _db_file_path(country, crop_code)
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
            "crop":         crop_code,
            "country":      country,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_zones":  0,
            "processed":    0,
            "summary":      {},
            "zones":        {},
        }

    db.setdefault("zones", {})[zone_name] = zone_data
    db["processed"]    = len(db["zones"])
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
    zones already present in the JSON database are returned from disk
    without any LLM calls; missing zones are generated and saved.

    Called by generate_dataset.py instead of StandaloneCultivarHelperAgent.
    """

    AGENT_NAME = "CultivarAgent"

    @staticmethod
    def process(state: Dict[str, Any], verbose: bool = False) -> Dict[str, Any]:
        """
        Build or load the cultivar DB entry for one zone.

        Args:
            state:   dict with keys: country, crop_code, zone_name,
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

        country   = state.get("country", "Unknown")
        crop_code = str(state.get("crop_code", "MZ")).strip().upper() or "MZ"
        zone_name = state.get("zone_name", "Unknown Zone")
        gen_model = state.get("generator_model", "gpt-5")

        crop_name = state.get("crop_name_text", "")
        if not crop_name:
            crop_name = StandaloneCultivarHelperAgent.CROP_MAP.get(crop_code, crop_code)

        progress(f"Zone: {zone_name} | Country: {country} | Crop: {crop_name} ({crop_code})")

        # ====================================================================
        # STEP 1: Check DB — return from disk if zone already exists
        # ====================================================================
        db_data     = _load_db_json(country, crop_code)
        zones_in_db = db_data.get("zones", {})

        if zone_name in zones_in_db and zones_in_db[zone_name]:
            existing_zone = zones_in_db[zone_name]
            progress(f"Zone already in DB ({len(existing_zone)} cultivar(s)) — skipping generation")
            log(f"Loaded from: {_db_file_path(country, crop_code)}")

            state["cultivar_helper_output"] = existing_zone
            state.setdefault("messages", []).append(
                f"{agent}: Zone '{zone_name}' loaded from DB ({len(existing_zone)} cultivar(s))"
            )
            return state

        # ====================================================================
        # STEP 2: Zone not in DB — generate via StandaloneCultivarHelperAgent
        # ====================================================================
        progress("Zone not in DB — generating now via StandaloneCultivarHelperAgent...")

        helper_state: Dict[str, Any] = {
            "config":          {},
            "messages":        [],
            "errors":          [],
            "crop_code":       crop_code,
            "crop_name_text":  crop_name,
            "zone_name":       zone_name,
            "country":         country,
            "generator_model": gen_model,
        }

        helper_result = StandaloneCultivarHelperAgent.process(helper_state, verbose=verbose)

        for err in helper_result.get("errors", []):
            state.setdefault("errors", []).append(f"{agent}: {err}")
        for msg in helper_result.get("messages", []):
            state.setdefault("messages", []).append(msg)

        raw_output: Dict[str, Any] = helper_result.get("cultivar_helper_output", {})

        # Reformat to DB storage format: {cultivar_name: {characteristics, coefficients}}
        zone_data: Dict[str, Any] = {
            name: {
                "characteristics": data.get("characteristics", {}),
                "coefficients":    data.get("coefficients", {}),
            }
            for name, data in raw_output.items()
        }

        # ====================================================================
        # STEP 3: Save to DB
        # ====================================================================
        _save_zone_to_db(country, crop_code, zone_name, zone_data)
        progress(f"Saved {len(zone_data)} cultivar(s) to DB for zone '{zone_name}'")
        log(f"DB file: {_db_file_path(country, crop_code)}")

        state["cultivar_helper_output"] = zone_data
        state.setdefault("messages", []).append(
            f"{agent}: Zone '{zone_name}' generated and saved ({len(zone_data)} cultivar(s))"
        )

        return state

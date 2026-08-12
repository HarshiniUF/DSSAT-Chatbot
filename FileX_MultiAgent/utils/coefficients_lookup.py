"""
Deterministic lookup against the hardcoded coefficients database built by
scripts/build_coefficients_db.py (data/coefficients_db/<CROP_CODE>.json).

Used to replace LLM-based .CUL file parsing in cul_parser.py and
standalone_cultivar_helper_agent.py for the 13 crops that have an extracted
database. Crops without one (e.g. Barley, Pigeonpea, Chickpea — no DSSATTools
Crop class, so not simulation-ready anyway) fall back to the caller's
existing LLM-based path; load_coefficients_db returns None for those.
"""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_COEFF_DB_DIR = _PROJECT_ROOT / "data" / "coefficients_db"

_NAME_KEYS = ("vrname", "var-name")


def _normalize(name: str) -> str:
    return re.sub(r"\s+", " ", (name or "").strip()).lower()


def _entry_name(entry: dict) -> str:
    for key in _NAME_KEYS:
        if entry.get(key):
            return entry[key]
    return ""


@lru_cache(maxsize=None)
def load_coefficients_db(crop_code: str) -> Optional[Dict[str, Any]]:
    """Return the parsed coefficients_db dict for crop_code, or None if not built."""
    path = _COEFF_DB_DIR / f"{crop_code.strip().upper()}.json"
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def find_cultivar_by_name(db: Dict[str, Any], cultivar_name: str) -> Optional[Dict[str, Any]]:
    """
    Look up a cultivar by name (case/whitespace-insensitive exact match first,
    then substring match) against VRNAME/VAR-NAME in the coefficients_db.

    Returns a flattened dict: {"found", "cultivar_name", "VAR#", "ECO#",
    "EXPNO", <coefficient_name>: value, ...} — same shape the LLM-based
    lookups used to return, so callers don't need to change.
    """
    target = _normalize(cultivar_name)
    if not target:
        return None

    exact_match = None
    substring_match = None

    for code, entry in db.get("cultivars", {}).items():
        entry_name = _entry_name(entry)
        normalized_entry_name = _normalize(entry_name)
        if not normalized_entry_name:
            continue

        if normalized_entry_name == target:
            exact_match = (code, entry, entry_name)
            break
        if substring_match is None and (
            target in normalized_entry_name or normalized_entry_name in target
        ):
            substring_match = (code, entry, entry_name)

    code, entry, entry_name = exact_match or substring_match or (None, None, None)
    if code is None:
        return None

    result: Dict[str, Any] = {
        "found": True,
        "cultivar_name": entry_name,
        "VAR#": code,
        "ECO#": entry.get("eco#"),
        "EXPNO": entry.get("expno") or entry.get("exp#"),
    }
    result.update(entry.get("coefficients", {}))
    return result


def find_cultivar_by_code_or_name(
    db: Dict[str, Any], code: Optional[str] = None, name: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Resolve a cultivar with an exact VAR# code if given and valid (most
    reliable — used when a caller, e.g. an LLM analog match, names both a
    code and a display name), else fall back to name-based matching.
    """
    if code:
        entry = db.get("cultivars", {}).get(code.strip())
        if entry:
            result: Dict[str, Any] = {
                "found": True,
                "cultivar_name": _entry_name(entry),
                "VAR#": code.strip(),
                "ECO#": entry.get("eco#"),
                "EXPNO": entry.get("expno") or entry.get("exp#"),
            }
            result.update(entry.get("coefficients", {}))
            return result

    if name:
        return find_cultivar_by_name(db, name)

    return None


def find_generic_fallback(db: Dict[str, Any]) -> Optional[tuple]:
    """
    Deterministic replacement for the "medium-season generic" LLM fallback:
    prefer a cultivar whose name contains "MEDIUM"; otherwise fall back to
    the first cultivar in the file (stable JSON insertion order) as a safe
    default. Returns (cultivar_name, details_dict) or None if the crop has
    no cultivars at all.
    """
    cultivars = db.get("cultivars", {})
    if not cultivars:
        return None

    for code, entry in cultivars.items():
        entry_name = _entry_name(entry)
        if "MEDIUM" in entry_name.upper():
            return _build_result(code, entry, entry_name)

    code, entry = next(iter(cultivars.items()))
    entry_name = _entry_name(entry)
    return _build_result(code, entry, entry_name)


def _build_result(code: str, entry: dict, entry_name: str) -> tuple:
    result: Dict[str, Any] = {
        "found": True,
        "cultivar_name": entry_name,
        "VAR#": code,
        "ECO#": entry.get("eco#"),
        "EXPNO": entry.get("expno") or entry.get("exp#"),
    }
    result.update(entry.get("coefficients", {}))
    return (entry_name, result)

"""
Fix mislabeled coefficients in the existing data/cultivar_db/*.json files.

Bug: the old LLM-based generator stored every crop's coefficients under a
fixed maize-shaped key set (P1, P2, P5, G2, G3, PHINT) regardless of the
crop's real DSSAT model. For non-maize crops (e.g. Peanut's CROPGRO model:
CSDL, PPSEN, EM-FL, FL-SH, FL-SD, SD-PM, FL-LF, LFMAX, SLAVR, SIZLF, XFRT,
WTPSD, SFDUR, SDPDV, PODUR, THRSH, SDPRO, SDLIP) this silently mislabeled
real values under the wrong names and dropped the rest.

Fix: for every cultivar entry whose coefficients.source names a resolvable
local/analog cultivar in the crop's real .CUL file, re-derive the
coefficients dict from data/coefficients_db/<CROP>.json (extracted directly
from the .CUL file, correct schema, already verified against DSSATTools'
own parser) and overwrite the stored dict with the correctly-keyed values.

Entries whose source can't be resolved (e.g. "not_found", or a name/code
that isn't in the coefficients_db) are left untouched and reported.

Usage:
    python scripts/fix_cultivar_db_coefficients.py [--write]

Without --write, runs in dry-run mode and only reports what would change.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path
from typing import Any, Dict, Optional

from utils.coefficients_lookup import load_coefficients_db, find_cultivar_by_name

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CULTIVAR_DB_FILES = [
    PROJECT_ROOT / "data/cultivar_db/united_states/maize/United States_MZ_cultivars_list.json",
    PROJECT_ROOT / "data/cultivar_db/kenya/maize/Kenya_MZ_cultivars_list.json",
    PROJECT_ROOT / "data/cultivar_db/senegal/peanut/senegal_PN_cultivars_list.json",
]

_ANALOG_RE = re.compile(r"analog:\s*(.+?)\s+from\s+\S+\.CUL", re.IGNORECASE)


def _resolve_search_target(source: str, cultivar_name: str) -> Optional[str]:
    m = _ANALOG_RE.match(source or "")
    if m:
        return m.group(1).strip()
    if (source or "").lower().startswith("local"):
        return cultivar_name
    return None


def _lookup(db: dict, search_target: str) -> Optional[dict]:
    # Prefer an exact VAR# code match if the search text leads with one
    # (Kenya's analog strings often embed it, e.g. "IB0028 TAINAN-11").
    first_token = search_target.split()[0] if search_target.split() else ""
    if first_token in db.get("cultivars", {}):
        entry = db["cultivars"][first_token]
        name_key = "vrname" if "vrname" in entry else "var-name"
        result = {
            "found": True,
            "cultivar_name": entry.get(name_key, ""),
            "VAR#": first_token,
            "ECO#": entry.get("eco#"),
            "EXPNO": entry.get("expno") or entry.get("exp#"),
        }
        result.update(entry.get("coefficients", {}))
        return result
    return find_cultivar_by_name(db, search_target)


def fix_file(path: Path, write: bool) -> Dict[str, int]:
    data = json.loads(path.read_text(encoding="utf-8"))
    crop_code = data.get("crop", "")
    db = load_coefficients_db(crop_code)

    stats = {"checked": 0, "already_correct": 0, "fixed": 0, "unresolved": 0, "not_found": 0}

    if db is None:
        print(f"[SKIP] {path.name}: no coefficients_db for crop '{crop_code}'")
        return stats

    correct_keys = {k.upper() for k in next(iter(db["cultivars"].values()))["coefficients"].keys()}

    for zone_name, cultivars in data.get("zones", {}).items():
        for cname, entry in cultivars.items():
            coef = entry.get("coefficients", {})
            if not coef.get("found"):
                stats["not_found"] += 1
                continue

            stats["checked"] += 1
            stored_keys = {k.upper() for k in coef.get("coefficients", {}).keys()}

            if stored_keys == correct_keys:
                stats["already_correct"] += 1
                continue

            search_target = _resolve_search_target(coef.get("source", ""), cname)
            if not search_target:
                stats["unresolved"] += 1
                print(f"  [UNRESOLVED] {zone_name}/{cname}: source={coef.get('source')!r}")
                continue

            match = _lookup(db, search_target)
            if not match:
                stats["unresolved"] += 1
                print(f"  [UNRESOLVED] {zone_name}/{cname}: '{search_target}' not in {crop_code} coefficients_db")
                continue

            non_coef_keys = {"found", "cultivar_name", "VAR#", "ECO#", "EXPNO"}
            new_coefficients = {
                k.upper(): v for k, v in match.items() if k not in non_coef_keys
            }

            old_coefficients = coef.get("coefficients", {})
            print(
                f"  [FIX] {zone_name}/{cname}: {old_coefficients} -> {new_coefficients} "
                f"(VAR#={match['VAR#']}, matched via '{search_target}')"
            )
            coef["coefficients"] = new_coefficients
            stats["fixed"] += 1

    if write and stats["fixed"] > 0:
        backup_path = path.with_suffix(path.suffix + ".bak")
        shutil.copy2(path, backup_path)
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"  -> wrote fixes to {path} (backup: {backup_path.name})")

    return stats


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="Actually write fixes (default: dry-run)")
    args = parser.parse_args()

    for path in CULTIVAR_DB_FILES:
        if not path.exists():
            print(f"[MISSING] {path}")
            continue
        print(f"\n=== {path.relative_to(PROJECT_ROOT)} ===")
        stats = fix_file(path, write=args.write)
        print(f"  {stats}")


if __name__ == "__main__":
    main()

"""
Build a hardcoded coefficients database from the DSSAT .CUL genotype files
in Genotype/, for the crops that have a working DSSATTools Crop class
(i.e. are actually simulation-ready via FileAssemblerAgent).

Reuses DSSATTools' own per-crop column schema (cul_dtypes / cul_pars_fmt)
and fixed-width parsing (parse_pars_line) so the extracted values match
exactly what DSSATTools.crop.<Crop>(ingeno) would resolve at simulation
time — same file, same columns, same type coercion.

Output: data/coefficients_db/<CROP_CODE>.json, one file per crop:
    {
      "crop_code": "MZ", "crop_name": "Maize", "model_file": "MZCER048.CUL",
      "bounds": {"min": {...}, "max": {...}},
      "cultivars": {
        "IB0001": {"vrname": "...", "expno": "...", "eco#": "...",
                    "coefficients": {"p1": 110.0, ...}}
      }
    }

Usage:
    python scripts/build_coefficients_db.py
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from DSSATTools.DSSATTools.crop import (
    Maize, Wheat, Sorghum, PearlMillet, Rice, Soybean, Sunflower, Potato,
    Tomato, Cabbage, Sugarcane, DryBean, Peanut,
)
from DSSATTools.DSSATTools.base.partypes import parse_pars_line, clean_comments
from DSSATTools.DSSATTools.base.utils import detect_encoding

PROJECT_ROOT = Path(__file__).resolve().parents[1]
GENOTYPE_DIR = PROJECT_ROOT / "Genotype"
OUT_DIR = PROJECT_ROOT / "data" / "coefficients_db"

# Non-coefficient descriptor columns present in every crop's cul_pars_fmt.
_DESCRIPTOR_KEYS = {"vrname", "var-name", "expno", "exp#", "eco#"}

# crop_code -> (Crop class, human-readable crop name)
CROPS: Dict[str, tuple] = {
    "MZ": (Maize, "Maize"),
    "WH": (Wheat, "Wheat"),
    "SG": (Sorghum, "Sorghum"),
    "ML": (PearlMillet, "Millet"),
    "RI": (Rice, "Rice"),
    "SB": (Soybean, "Soybean"),
    "SU": (Sunflower, "Sunflower"),
    "PT": (Potato, "Potato"),
    "TM": (Tomato, "Tomato"),
    "CB": (Cabbage, "Cabbage"),
    "SC": (Sugarcane, "Sugarcane"),
    "BN": (DryBean, "Dry Bean"),
    "PN": (Peanut, "Peanut"),
}

_SENTINEL_CODES = {"999991": "min", "999992": "max"}


def _coerce(dtypes: dict, pars_fmt: dict, name: str, raw_value: str):
    """Mirror Record.__setitem__'s type coercion (NumberType/DescriptionType).

    'eco#' is special-cased in DSSATTools itself (Crop.__init__ stores it as
    the raw ecotype code string rather than instantiating its Record dtype
    marker) — mirrored here rather than calling dtypes['eco#'](...).
    """
    if name == "eco#":
        return raw_value.strip()
    typed = dtypes[name](name, raw_value, pars_fmt[name])
    if isinstance(typed, float):
        return None if typed != typed else float(typed)  # NaN -> None
    return str(typed)


def _parse_cul_file(cul_path: Path, dtypes: dict, pars_fmt: dict) -> Dict[str, Any]:
    encoding = detect_encoding(str(cul_path))
    with open(cul_path, "r", encoding=encoding) as f:
        lines = f.readlines()

    lines = clean_comments(lines)

    bounds: Dict[str, dict] = {"min": {}, "max": {}}
    cultivars: Dict[str, Any] = {}
    skipped: Dict[str, str] = {}

    for line in lines:
        if not line.strip() or line[0] in "@*$!":
            continue

        code = line[:6].strip()
        if not code:
            continue

        raw = parse_pars_line(line[7:], pars_fmt)

        try:
            record: Dict[str, Any] = {}
            coefficients: Dict[str, Any] = {}
            for name, value in raw.items():
                coerced = _coerce(dtypes, pars_fmt, name, value)
                if name in _DESCRIPTOR_KEYS:
                    record[name] = coerced
                else:
                    coefficients[name] = coerced
        except ValueError as e:
            # Malformed source row (e.g. a decimal point corrupted to a space
            # in the raw .CUL file) — skip this cultivar rather than abort
            # the whole file, and surface it for manual review.
            skipped[code] = f"{e} (raw row: {line.strip()!r})"
            continue

        if code in _SENTINEL_CODES:
            bounds[_SENTINEL_CODES[code]] = coefficients
            continue

        record["coefficients"] = coefficients
        cultivars[code] = record

    return {"bounds": bounds, "cultivars": cultivars, "skipped": skipped}


def build_all() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for crop_code, (crop_cls, crop_name) in CROPS.items():
        cul_filename = Path(crop_cls.spe_file).with_suffix(".CUL").name
        cul_path = GENOTYPE_DIR / cul_filename

        if not cul_path.exists():
            print(f"[SKIP] {crop_code} ({crop_name}): {cul_path} not found")
            continue

        parsed = _parse_cul_file(cul_path, crop_cls.cul_dtypes, crop_cls.cul_pars_fmt)

        out = {
            "crop_code": crop_code,
            "crop_name": crop_name,
            "model_file": cul_filename,
            **parsed,
        }

        out_path = OUT_DIR / f"{crop_code}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2, ensure_ascii=False)

        print(
            f"[OK] {crop_code} ({crop_name}): {len(parsed['cultivars'])} cultivars "
            f"-> {out_path.relative_to(PROJECT_ROOT)}"
        )
        for code, reason in parsed["skipped"].items():
            print(f"  [WARN] skipped {code}: {reason}")


if __name__ == "__main__":
    build_all()

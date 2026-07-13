"""
CLI adapter exposing main.run_workflow() to external callers via subprocess.

This project defines its own `agents`, `utils`, `prompts`, and `judge_agents`
packages, which collide by name with the parent chatbot project's own
`agents` package. Rather than importing this pipeline in-process, the parent
project invokes this script as an isolated subprocess (its own interpreter,
its own working directory), passing a config file in and reading the
generated FileX file back out.

Usage:
    python run_cli.py --config <path> --output <path> [--geonames-username <name>]
                       [--use-cache] [--enable-judge]
                       [--generator-model gpt-5] [--judge-model gpt-5]

Prints one JSON line to stdout: {"ok": bool, "output_path": str, "errors": [...]}

Baseline-discovery mode (--baseline-only, no --output needed): runs only
field -> planting -> fertilizer (main.run_baseline_discovery()) so
FertilizerAgent's own prompt can infer a real representative-practice total N
rate for the crop/location, instead of generating a full FileX. Prints one
JSON line: {"ok": bool, "pdate": str, "baseline_total_n_kg_ha": float,
"narrative": str, "errors": [...]}
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dotenv import load_dotenv

# Single project-root .env (dssat_project/.env) -- no .env files live under
# FileX_MultiAgent itself, so this works whether run_cli.py is invoked as a
# subprocess by the parent chatbot or standalone for testing.
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from main import run_workflow, run_baseline_discovery  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", required=False, default=None)
    parser.add_argument("--baseline-only", action="store_true",
                         help="Run only field->planting->fertilizer and print a discovered N baseline, no FileX output.")
    parser.add_argument("--geonames-username", default="")
    parser.add_argument("--use-cache", action="store_true")
    parser.add_argument("--enable-judge", action="store_true")
    parser.add_argument("--generator-model", default="gpt-5")
    parser.add_argument("--judge-model", default="gpt-5")
    args = parser.parse_args()

    if not args.baseline_only and not args.output:
        parser.error("--output is required unless --baseline-only is set")

    geonames_username = args.geonames_username or os.getenv("GEONAMES_USERNAME", "")
    if not geonames_username:
        print(json.dumps({"ok": False, "output_path": args.output,
                           "errors": ["GEONAMES_USERNAME not provided and not set in environment."]}))
        return 1

    if args.baseline_only:
        try:
            result = run_baseline_discovery(
                config_path=args.config,
                geonames_username=geonames_username,
                use_cache=args.use_cache,
                enable_judge=args.enable_judge,
                generator_model=args.generator_model,
                judge_model=args.judge_model,
            )
        except Exception as exc:
            print(json.dumps({"ok": False, "baseline_total_n_kg_ha": None, "pdate": None,
                               "narrative": "", "errors": [str(exc)]}))
            return 1

        print(json.dumps({
            "ok": result.get("ok", False),
            "pdate": result.get("pdate"),
            "baseline_total_n_kg_ha": result.get("baseline_total_n_kg_ha"),
            "narrative": result.get("narrative", ""),
            "errors": result.get("errors", []),
        }))
        return 0 if result.get("ok") else 1

    try:
        result = run_workflow(
            config_path=args.config,
            output_path=args.output,
            geonames_username=geonames_username,
            use_cache=args.use_cache,
            run_list=["ALL"],
            enable_judge=args.enable_judge,
            generator_model=args.generator_model,
            judge_model=args.judge_model,
        )
    except Exception as exc:
        print(json.dumps({"ok": False, "output_path": args.output, "errors": [str(exc)]}))
        return 1

    errors = result.get("errors", [])

    # Snapshot of the field/cultivar/planting/irrigation values this run
    # actually used, so a caller generating multiple treatments (e.g. the
    # parent chatbot's per-treatment loop) can lock every later treatment to
    # these same values and only vary its own focus variable (fertilizer).
    guidelines = None
    if not errors:
        fert_events = result.get("fertilizer_config") or []
        irrig_cfg = result.get("irrigation_config") or {}
        field_meta = result.get("field_metadata") or {}
        field_details = {
            k: field_meta.get(k)
            for k in ("id_field", "wsta", "id_soil", "flsa", "flob", "fldt", "sldp", "flname")
        }
        field_details["weather_duration_years"] = (field_meta.get("metadata") or {}).get("weather_duration_years")
        pdate = result.get("pdate")
        guidelines = {
            "cultivars": {
                "CR": result.get("crop_code"),
                "INGENO": result.get("cultivar_ingeno"),
                "CNAME": result.get("cultivar_name"),
            },
            "planting_details": result.get("planting_config") or {},
            "fertilizer_details": {
                "events": fert_events,
                "total_n": sum(float(e.get("FAMN") or 0) for e in fert_events),
            },
            "irrigation_details": {
                "strategy": irrig_cfg.get("strategy", "rainfed"),
                "header_row": irrig_cfg.get("header_row", {}),
                "events": irrig_cfg.get("irrigation_events", []),
            },
            "field_details": field_details,
            "initial_conditions": {},
            "simulation_controls": {"IRRIG": result.get("irrig")},
            "automatic_management": {"PLANTING": {"PFRST": pdate, "PLAST": pdate}},
        }

    print(json.dumps({"ok": not errors, "output_path": args.output, "errors": errors, "guidelines": guidelines}))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())

"""
Bridge to the FileX_MultiAgent creation pipeline.

FileX_MultiAgent/ defines its own `agents`, `utils`, `prompts`, and
`judge_agents` packages — names that collide with this project's own
chatbot `agents` package. Rather than importing it in-process, it is
invoked as an isolated subprocess (its own venv, its own working
directory) via FileX_MultiAgent/run_cli.py, passing a config JSON in and
reading the generated FileX (.SNX) file back out.

One subprocess call is made per treatment in `proposed_experiment.treatments`,
so each generated file reflects the nitrogen rate that treatment actually
calls for (via config["fertilizer"]["target_n_rate_kg_ha"], which
FileX_MultiAgent's FertilizerAgent prompt honors as a hard total-N target).
"""

import json
import os
import subprocess
import tempfile
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional

from experiment_config import (
    CROP_CODES, DEFAULT_LATITUDE, DEFAULT_LONGITUDE, DEFAULT_LOCATION_NAME,
    DEFAULT_CROP_NAME, DEFAULT_SEASON_YEAR,
)

_FILEX_DIR = Path(__file__).resolve().parent.parent / "FileX_MultiAgent"
_FILEX_PYTHON = _FILEX_DIR / "venv" / "bin" / "python"
_FILEX_RUNNER = _FILEX_DIR / "run_cli.py"

_CROP_NAME_TO_CODE = {name.upper(): code for code, name in CROP_CODES.items()}


def _crop_code_from_name(crop_name: str) -> str:
    return _CROP_NAME_TO_CODE.get((crop_name or "").strip().upper(), "MZ")


def _resolve_location() -> Dict[str, Any]:
    """Every generated experiment uses this one fixed location, regardless of
    what region (if any) the user's question mentions."""
    return {
        "Latitude": DEFAULT_LATITUDE,
        "Longitude": DEFAULT_LONGITUDE,
        "place": DEFAULT_LOCATION_NAME,
    }


def _build_filex_config(
    intent: Dict[str, Any],
    target_n_rate_kg_ha: Optional[float] = None,
) -> Dict[str, Any]:
    """Translate the chatbot's classified intent (+ a specific treatment's
    nitrogen rate) into the config schema FileX_MultiAgent's pipeline expects.
    Crop and season year are pinned from workflow_inputs.json (DEFAULT_CROP_NAME /
    DEFAULT_SEASON_YEAR) -- same as location -- regardless of what intent
    extracted from the question; intent["crop"] is still used for narrative only."""
    crop_code = _crop_code_from_name(DEFAULT_CROP_NAME)
    year = DEFAULT_SEASON_YEAR

    config: Dict[str, Any] = {
        "Location": _resolve_location(),
        "Year": {"start_year": year},
        "crop_growing_season": str(year),
        "weather": {
            "start_date": f"{year - 1}-01-01",
            "end_date": f"{year + 1}-12-31",
        },
        "cultivar": {"CR": crop_code},
    }
    if target_n_rate_kg_ha is not None:
        config["fertilizer"] = {"target_n_rate_kg_ha": target_n_rate_kg_ha}
    return config


def _launch_filex_cli(config_path: str, extra_args: List[str], timeout: int) -> subprocess.CompletedProcess:
    """Shared subprocess launch for run_cli.py, in either full-generation or
    --baseline-only mode. Raises FileNotFoundError/subprocess.TimeoutExpired
    on failure for the caller to translate into its own result shape."""
    if not _FILEX_PYTHON.exists() or not _FILEX_RUNNER.exists():
        raise FileNotFoundError(f"FileX_MultiAgent pipeline not found (expected {_FILEX_RUNNER}).")

    geonames_username = os.getenv("GEONAMES_USERNAME", "")
    enable_judge = os.getenv("FILEX_ENABLE_JUDGE", "").lower() in ("1", "true", "yes")

    cmd = [str(_FILEX_PYTHON), str(_FILEX_RUNNER), "--config", config_path, "--use-cache"] + extra_args
    if geonames_username:
        cmd += ["--geonames-username", geonames_username]
    if enable_judge:
        cmd += ["--enable-judge"]

    return subprocess.run(cmd, cwd=str(_FILEX_DIR), capture_output=True, text=True, timeout=timeout)


def _run_filex_multiagent(config: Dict[str, Any], treatment_id: str, fallback_name: str) -> Dict[str, Any]:
    """Invoke FileX_MultiAgent as a subprocess. The output filename follows
    FileX_MultiAgent's own convention (see streamlit_ui/app.py, which names
    downloads after the DSSAT experiment code on the file's own *EXP.DETAILS
    line, e.g. "KETR2601SN.SNX") -- with this treatment's id appended, e.g.
    "KETR2601SN_s01.SNX". The suffix is required, not cosmetic: that
    *EXP.DETAILS code depends only on field id + planting-season date, so
    every treatment in the same run shares the identical code -- without a
    per-treatment suffix, treatment 2's file would silently overwrite
    treatment 1's. Returns {"ok": bool, "path": str|None, "summary": str}."""
    with tempfile.TemporaryDirectory() as tmp:
        config_path = os.path.join(tmp, "runtime_config.json")
        tmp_output_path = os.path.join(tmp, "runtime_output.SNX")
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)

        try:
            proc = _launch_filex_cli(config_path, ["--output", tmp_output_path], timeout=600)
        except FileNotFoundError as exc:
            return {"ok": False, "path": None, "summary": str(exc)}
        except subprocess.TimeoutExpired:
            return {"ok": False, "path": None, "summary": "FileX generation timed out after 10 minutes."}

        if not os.path.exists(tmp_output_path):
            tail = "\n".join((proc.stdout + proc.stderr).splitlines()[-25:])
            return {"ok": False, "path": None, "summary": f"FileX generation failed:\n{tail}"}

        with open(tmp_output_path, "r") as f:
            content = f.read()

    first_line = content.strip().splitlines()[0] if content.strip() else ""
    if first_line.startswith("*EXP.DETAILS:"):
        exp_code = first_line.split(":", 1)[1].strip()
        output_name = f"{exp_code}_{treatment_id}.SNX"
    else:
        # Shouldn't normally happen -- FileAssemblerAgent always writes this
        # line first. Fall back to the caller's generic name rather than lose
        # the file.
        output_name = fallback_name

    with open(output_name, "w") as dst:
        dst.write(content)

    return {"ok": True, "path": output_name, "summary": f"Generated {output_name}"}


def _run_filex_baseline_discovery(config: Dict[str, Any]) -> Dict[str, Any]:
    """Invoke FileX_MultiAgent in --baseline-only mode (field->planting->
    fertilizer only, no forced N target) to discover a real representative-
    practice total N rate. Returns {"ok", "baseline_total_n_kg_ha", "pdate",
    "narrative", "summary"}."""
    with tempfile.TemporaryDirectory() as tmp:
        config_path = os.path.join(tmp, "runtime_config.json")
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)

        try:
            proc = _launch_filex_cli(config_path, ["--baseline-only"], timeout=300)
        except FileNotFoundError as exc:
            return {"ok": False, "baseline_total_n_kg_ha": None, "pdate": None, "narrative": "", "summary": str(exc)}
        except subprocess.TimeoutExpired:
            return {"ok": False, "baseline_total_n_kg_ha": None, "pdate": None, "narrative": "",
                    "summary": "Baseline discovery timed out after 5 minutes."}

    # run_cli.py prints exactly one JSON line as its last line of stdout.
    result = None
    for line in (proc.stdout or "").splitlines():
        line = line.strip()
        if line.startswith("{"):
            try:
                result = json.loads(line)
            except json.JSONDecodeError:
                continue

    if result is None:
        tail = "\n".join((proc.stdout + proc.stderr).splitlines()[-25:])
        return {"ok": False, "baseline_total_n_kg_ha": None, "pdate": None, "narrative": "",
                "summary": f"Baseline discovery failed:\n{tail}"}

    if not result.get("ok"):
        return {"ok": False, "baseline_total_n_kg_ha": None, "pdate": None, "narrative": "",
                "summary": f"Baseline discovery failed: {result.get('errors')}"}

    return {
        "ok": True,
        "baseline_total_n_kg_ha": result.get("baseline_total_n_kg_ha"),
        "pdate": result.get("pdate"),
        "narrative": result.get("narrative", ""),
        "summary": f"Discovered baseline: {result.get('baseline_total_n_kg_ha')} kg N/ha",
    }


def discover_fertilizer_baseline(intent: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ask FileX_MultiAgent's real Field->Planting->Fertilizer agents what a
    representative farmer-practice total N rate looks like for this crop and
    location, instead of guessing one with a generic prompt. Used by
    q_classifier for fertilizer_rate/fertilizer_timing questions, once per
    question -- the result is cached in intent_brief and reused across any
    a1_designer redesign iterations rather than looked up again.
    """
    config = _build_filex_config(intent, target_n_rate_kg_ha=None)
    return _run_filex_baseline_discovery(config)


def multiagent_xfile_node(state: Dict) -> Dict:
    """
    LangGraph node that generates a FileX (.SNX) per designed treatment by
    delegating to the FileX_MultiAgent pipeline.
    """
    intent = state.get("intent_brief", {}) or state.get("intent", {})
    experiment = state.get("proposed_experiment", {})
    treatments: List[Dict[str, Any]] = experiment.get("treatments", [])

    if not treatments:
        # No design available — fall back to a single generic file for the
        # classified crop/region.
        treatments = [{"id": "s01", "modifications": {}}]

    crop_code = _crop_code_from_name(DEFAULT_CROP_NAME)
    run_date = date.today().isoformat()

    generated_files = []
    summaries = []
    for t in treatments:
        treatment_id = t.get("id", "s01")
        rate = t.get("modifications", {}).get("basal_rate")
        config = _build_filex_config(intent, target_n_rate_kg_ha=rate)
        fallback_name = f"generated_{crop_code}_{treatment_id}_{run_date}.SNX"
        result = _run_filex_multiagent(config, treatment_id, fallback_name)
        if result["ok"]:
            generated_files.append(result["path"])
            rate_note = f" (target {rate} kg N/ha)" if rate is not None else ""
            summaries.append(f"{result['path']}{rate_note}")
        else:
            summaries.append(f"{treatment_id} FAILED: {result['summary']}")

    summary_text = "Generated FileX file(s):\n" + "\n".join(f"- {s}" for s in summaries)

    return {
        **state,
        "generated_files": generated_files,
        "generation_summary": summary_text,
    }

"""
Multi-Agent LangGraph Workflow for DSSAT FileX Generation using DSSATTools

- Same agents and edges as before
- Streamlit-friendly logging via utils.ui_logger (ui_event/ui_log)
- Still works as a CLI script too
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional, List

from dotenv import load_dotenv
from langgraph.graph import StateGraph, END

from utils.state import DSSATState
from utils.helpers import parse_codebook_section
from utils.cache_manager import SimpleCacheManager
from utils.geo_fetcher import geo_coordinates_search
from utils.ui_logger import ui_event, ui_log, ui_error

from agents.planting_agent import PlantingAgent
from agents.fertilizer_agent import FertilizerAgent
from agents.irrigation_agent import IrrigationAgent
from agents.residue_agent import ResidueAgent
from agents.field_agent import FieldAgent
from agents.initial_conditions_agent import InitialConditionsAgent
from agents.simulation_control_agent import SimulationControlAgent
from agents.file_assembler_agent import FileAssemblerAgent

# Single project-root .env (dssat_project/.env) -- see run_cli.py
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# ============================================================================
# DEFAULTS (script mode)
# ============================================================================
CONFIG_PATH = "Input_config_test1.json"
OUTPUT_PATH = "XFILE_OUTPUT_test1.SNX"

DEFAULT_GENERATOR_MODEL = "gpt-5"
DEFAULT_JUDGE_MODEL = "gpt-5"

DEFAULT_JUDGE_ENABLED = False
DEFAULT_MAX_JUDGE_ATTEMPTS = 2

DEFAULT_USE_CACHE = True
DEFAULT_RUN_LIST = ["ALL"]


# ============================================================================
# GRAPH CONSTRUCTION
# ============================================================================
def create_dssat_workflow():
    """
    Create the LangGraph workflow for DSSAT file generation using DSSATTools.
    Same nodes and edges as your current pipeline.
    """
    workflow = StateGraph(DSSATState)

    # FieldAgent: soil + weather + cultivar resolution (reads from pre-built AEZ DB).
    # CultivarAgent is standalone (not in this workflow) — run generate_dataset.py
    # or CultivarAgent directly to build the DB before running the workflow.
    workflow.add_node("field", FieldAgent.process)
    workflow.add_node("planting", PlantingAgent.process)
    workflow.add_node("fertilizer", FertilizerAgent.process)
    workflow.add_node("irrigation", IrrigationAgent.process)
    workflow.add_node("residue", ResidueAgent.process)
    workflow.add_node("initial_conditions", InitialConditionsAgent.process)
    workflow.add_node("simulation_control", SimulationControlAgent.process)
    workflow.add_node("assembler", FileAssemblerAgent.process)

    workflow.add_edge("field", "planting")
    workflow.add_edge("planting", "fertilizer")
    workflow.add_edge("fertilizer", "irrigation")
    workflow.add_edge("irrigation", "residue")
    workflow.add_edge("residue", "initial_conditions")
    workflow.add_edge("initial_conditions", "simulation_control")
    workflow.add_edge("simulation_control", "assembler")
    workflow.add_edge("assembler", END)

    workflow.set_entry_point("field")
    return workflow.compile()


def create_baseline_discovery_workflow():
    """
    Small graph used only to discover a representative-practice fertilizer
    baseline: field -> planting -> fertilizer, skipping every other section.
    Callers must omit config["fertilizer"]["target_n_rate_kg_ha"] so
    FertilizerAgent's own prompt is free to infer a real total N rate instead
    of hitting a caller-supplied target.
    """
    workflow = StateGraph(DSSATState)
    workflow.add_node("field", FieldAgent.process)
    workflow.add_node("planting", PlantingAgent.process)
    workflow.add_node("fertilizer", FertilizerAgent.process)
    workflow.add_edge("field", "planting")
    workflow.add_edge("planting", "fertilizer")
    workflow.add_edge("fertilizer", END)
    workflow.set_entry_point("field")
    return workflow.compile()


# ============================================================================
# STATE BUILDING
# ============================================================================
def _strict_irrigation_irop_codes() -> Dict[str, str]:
    """
    Your strict list (as you wanted).
    """
    return {
        "IR001": "Furrow, mm",
        "IR002": "Alternating furrows, mm",
        "IR003": "Flood, mm",
        "IR004": "Sprinkler, mm",
        "IR005": "Drip or trickle, mm",
        "IR006": "Flood depth, mm",
        "IR007": "Water table depth, cm",
        "IR008": "Percolation rate, mm day-1",
        "IR009": "Bund height, mm",
        "IR010": "Puddling (for Rice only)",
        "IR011": "Constant flood depth, mm",
    }


def build_initial_state(
    *,
    config: Dict[str, Any],
    config_path: str,
    geonames_username: str,
    use_cache: bool,
    run_list: List[str],
    enable_judge: bool,
    max_judge_attempts: int,
    generator_model: str,
    judge_model: str,
    ui_emit=None,
    ui_print: bool = False,
) -> Dict[str, Any]:
    """
    Build the state dict used by the LangGraph workflow.
    Safe to call from Streamlit.
    """

    # --- Location resolution ---
    location_cfg = config.get("Location", {}) or {}
    config["Location"] = location_cfg

    place_name = location_cfg.get("place") or location_cfg.get("Place") or location_cfg.get("name")
    if not place_name or not str(place_name).strip():
        raise ValueError("Location.place is required in config (e.g., 'Trans Nzoia').")

    existing_lat = location_cfg.get("Latitude") or location_cfg.get("latitude")
    existing_lon = location_cfg.get("Longitude") or location_cfg.get("longitude")

    if existing_lat is not None and existing_lon is not None:
        # Coordinates already known (e.g. supplied by a calling process) —
        # skip the live GeoNames lookup entirely.
        lat, lon = float(existing_lat), float(existing_lon)
        country = location_cfg.get("Country") or location_cfg.get("country") or ""
    else:
        lat, lon, country = geo_coordinates_search(
            str(place_name).strip(),
            max_rows=1,
            username=geonames_username,
        )
    location_text = f"{place_name}, {country}" if country else str(place_name)

    # Update config with resolved coords
    config["Location"]["place"] = str(place_name).strip()
    config["Location"]["Latitude"] = float(lat)
    config["Location"]["Longitude"] = float(lon)

    # Crop code from config (UI may override this before calling)
    crop_code = (config.get("cultivar", {}) or {}).get("CR") or "MZ"
    crop_code = str(crop_code).strip() or "MZ"

    # --- Cache manager ---
    cache_manager = SimpleCacheManager(cache_file="cache.json", use_cache=use_cache)
    cache_key = cache_manager.get_cache_key(config_path=config_path, crop_code=crop_code, lat=lat, lon=lon)

    # --- Codebooks ---
    fertilizer_FMCD_codes = parse_codebook_section("DETAIL.CDE", "Fertilizers, Inoculants and Amendments")
    fertilizer_FACD_codes = parse_codebook_section("DETAIL.CDE", "Methods - Fertilizer and Chemical Applications")
    planting_PLDS_codes = parse_codebook_section("DETAIL.CDE", "Plant Distribution")
    planting_PLME_codes = parse_codebook_section("DETAIL.CDE", "Planting Material/Method")
    cultivar_crop_codes = parse_codebook_section("DETAIL.CDE", "Crop and Weed Species")

    irrigation_IROP_codes = _strict_irrigation_irop_codes()

    # judge attempts
    max_attempts = int(max_judge_attempts) if enable_judge else 1

    state: Dict[str, Any] = {
        "config": config,

        "cultivar": None,
        "planting": None,
        "fertilizer": None,
        "irrigation": None,
        "residue": None,
        "field": None,
        "initial_conditions": None,
        "simulation_controls": None,
        "treatment": None,

        "messages": [],
        "errors": [],
        "complete_filex": "",

        "crop_code": crop_code,
        "cultivar_name": "",
        "cultivar_ingeno": "",
        "pdate": None,
        "irrig": "N",

        "xcrd": float(lat),
        "ycrd": float(lon),

        "location_text": location_text,
        "crop_name_text": "",

        "planting_PLDS_codes": planting_PLDS_codes,
        "planting_PLME_codes": planting_PLME_codes,
        "fertilizer_FMCD_codes": fertilizer_FMCD_codes,
        "fertilizer_FACD_codes": fertilizer_FACD_codes,
        "cultivar_crop_codes": cultivar_crop_codes,
        "irrigation_IROP_codes": irrigation_IROP_codes,

        "field_metadata": {},

        "planting_config": None,
        "planting_judge_feedback": None,
        "planting_judge_attempts": 0,

        "fertilizer_config": None,
        "fertilizer_judge_feedback": None,
        "fertilizer_judge_attempts": 0,

        "irrigation_config": None,
        "irrigation_judge_feedback": None,
        "irrigation_judge_attempts": 0,

        "max_judge_attempts": max_attempts,
        "enable_judge": bool(enable_judge),

        "cache_manager": cache_manager,
        "cache_key": cache_key,
        "run_list": run_list,
        "config_path": config_path,

        # models used by agents/judges
        "generator_model": generator_model,
        "judge_model": judge_model,

        # UI hooks
        "_ui": {
            "emit": ui_emit,        # Streamlit sets this
            "print": ui_print,      # enable terminal print if you want
            "events": [],
            "logs": {},
            "meta": {
                "cache_key": cache_key,
                "use_cache": use_cache,
                "run_list": run_list,
                "location": location_text,
            },
        },
    }

    ui_event(state, agent="Workflow", kind="info", message="Initial state built", data=state["_ui"]["meta"])
    ui_log(state, "Workflow", f"📍 {location_text} (lat={lat}, lon={lon})")
    ui_log(state, "Workflow", f"🌾 crop_code={crop_code}")
    ui_log(state, "Workflow", f"📦 cache_key={cache_key} use_cache={use_cache} run_list={run_list}")
    ui_log(state, "Workflow", f"🤖 generator_model={generator_model} judge_model={judge_model} judge={enable_judge}")

    return state


# ============================================================================
# WORKFLOW EXECUTION
# ============================================================================
def run_workflow(
    *,
    config_path: str,
    output_path: Optional[str] = None,
    geonames_username: str,
    use_cache: bool = DEFAULT_USE_CACHE,
    run_list: Optional[List[str]] = None,
    enable_judge: bool = DEFAULT_JUDGE_ENABLED,
    max_judge_attempts: int = DEFAULT_MAX_JUDGE_ATTEMPTS,
    generator_model: str = DEFAULT_GENERATOR_MODEL,
    judge_model: str = DEFAULT_JUDGE_MODEL,
    ui_emit=None,
    ui_print: bool = False,
) -> Dict[str, Any]:
    """
    Execute workflow and return final state dict.
    If output_path is provided, writes the generated FileX there.
    Safe to call from Streamlit.
    """
    run_list = run_list or ["ALL"]

    # Load config
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    # Build state (adds location coords, cache key, codebooks, model info)
    state = build_initial_state(
        config=config,
        config_path=config_path,
        geonames_username=geonames_username,
        use_cache=use_cache,
        run_list=run_list,
        enable_judge=enable_judge,
        max_judge_attempts=max_judge_attempts,
        generator_model=generator_model,
        judge_model=judge_model,
        ui_emit=ui_emit,
        ui_print=ui_print,
    )

    ui_event(state, agent="Workflow", kind="info", message="Compiling workflow graph")
    workflow = create_dssat_workflow()

    ui_event(state, agent="Workflow", kind="info", message="Invoking workflow")
    result = workflow.invoke(state)

    # Write output if requested
    if output_path:
        try:
            Path(output_path).write_text(result.get("complete_filex", ""), encoding="utf-8")
            ui_event(result, agent="Workflow", kind="output", message="FileX written", data={"output_path": output_path})
        except Exception as e:
            ui_error(result, "Workflow", f"Failed writing output file: {e}", data={"output_path": output_path})

    return result


def run_baseline_discovery(
    *,
    config_path: str,
    geonames_username: str,
    use_cache: bool = DEFAULT_USE_CACHE,
    enable_judge: bool = DEFAULT_JUDGE_ENABLED,
    max_judge_attempts: int = DEFAULT_MAX_JUDGE_ATTEMPTS,
    generator_model: str = DEFAULT_GENERATOR_MODEL,
    judge_model: str = DEFAULT_JUDGE_MODEL,
    ui_emit=None,
    ui_print: bool = False,
) -> Dict[str, Any]:
    """
    Run only field -> planting -> fertilizer, with no forced target_n_rate_kg_ha,
    so FertilizerAgent's own prompt (base_prompt_fertilizer_agent) is free to
    infer a real representative farmer-practice total N rate for this crop and
    location -- instead of the caller supplying one. Used by the chatbot to
    pick a genuine baseline *before* designing treatments, rather than guessing
    one with a generic prompt.

    Returns {"ok", "pdate", "baseline_total_n_kg_ha", "narrative",
    "fertilizer_events", "errors"}.
    """
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    # A baseline lookup must not carry a forced target -- that would defeat
    # the whole point of letting the prompt infer one freely.
    config.pop("fertilizer", None)

    state = build_initial_state(
        config=config,
        config_path=config_path,
        geonames_username=geonames_username,
        use_cache=use_cache,
        run_list=["ALL"],
        enable_judge=enable_judge,
        max_judge_attempts=max_judge_attempts,
        generator_model=generator_model,
        judge_model=judge_model,
        ui_emit=ui_emit,
        ui_print=ui_print,
    )

    ui_event(state, agent="Workflow", kind="info", message="Compiling baseline-discovery graph")
    workflow = create_baseline_discovery_workflow()

    ui_event(state, agent="Workflow", kind="info", message="Invoking baseline-discovery workflow")
    result = workflow.invoke(state)

    fertilizer_events = result.get("fertilizer_config") or []
    baseline_total_n = sum(float(ev.get("FAMN") or 0) for ev in fertilizer_events)

    return {
        "ok": not result.get("errors") and bool(fertilizer_events),
        "pdate": result.get("pdate"),
        "baseline_total_n_kg_ha": round(baseline_total_n, 2) if fertilizer_events else None,
        "narrative": result.get("fertilizer_narrative", ""),
        "fertilizer_events": fertilizer_events,
        "errors": result.get("errors", []),
    }


# ============================================================================
# SCRIPT MODE
# ============================================================================
if __name__ == "__main__":
    # Script mode defaults — still works like before, but cleaner.
    # (If you want terminal output, set ui_print=True.)
    try:
        res = run_workflow(
            config_path=CONFIG_PATH,
            output_path=OUTPUT_PATH,
            geonames_username="keerthikattamudi",
            use_cache=DEFAULT_USE_CACHE,
            run_list=DEFAULT_RUN_LIST,
            enable_judge=DEFAULT_JUDGE_ENABLED,
            max_judge_attempts=DEFAULT_MAX_JUDGE_ATTEMPTS,
            generator_model=DEFAULT_GENERATOR_MODEL,
            judge_model=DEFAULT_JUDGE_MODEL,
            ui_emit=None,
            ui_print=True,
        )

        print("\n" + "=" * 70)
        print("✓ DSSAT FileX generated successfully using DSSATTools + LangGraph!")
        print("=" * 70)
        print(f"Output: {OUTPUT_PATH}")
        if res.get("errors"):
            print("Errors:")
            for e in res["errors"]:
                print(" -", e)

    except Exception as e:
        print("Workflow failed:", e)

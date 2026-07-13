from __future__ import annotations
import json
from typing import Any, Dict, Optional

def safe_json(obj: Any) -> str:
    try:
        return json.dumps(obj, indent=2, ensure_ascii=False, default=str)
    except Exception:
        return str(obj)

def try_render_section_from_state(agent_name: str, state: Dict[str, Any]) -> Dict[str, Optional[str]]:
    """
    Best-effort extraction of:
      - DSSATTools object (stringified)
      - config JSON used by the agent
      - narrative text (if present)
      - judge feedback JSON (if present)
    Uses the state keys your agents already write today.
    """
    mapping = {
        "PlantingAgent": {
            "obj_key": "planting",
            "cfg_key": "planting_config",
            "narr_key": "planting_narrative",
            "judge_key": "planting_judge_feedback",
            "attempts_key": "planting_judge_attempts",
        },
        "FertilizerAgent": {
            "obj_key": "fertilizer",
            "cfg_key": "fertilizer_config",
            "narr_key": "fertilizer_narrative",
            "judge_key": "fertilizer_judge_feedback",
            "attempts_key": "fertilizer_judge_attempts",
        },
        "IrrigationAgent": {
            "obj_key": "irrigation",
            "cfg_key": "irrigation_config",
            "narr_key": "irrigation_narrative",
            "judge_key": "irrigation_judge_feedback",
            "attempts_key": "irrigation_judge_attempts",
        },
        "ResidueAgent": {"obj_key": "residue", "cfg_key": "residue_config", "narr_key": "residue_narrative", "judge_key": "residue_judge_feedback", "attempts_key": "residue_judge_attempts"},
        "FieldAgent": {"obj_key": "field", "cfg_key": "field_metadata", "narr_key": "cultivar_name", "judge_key": None, "attempts_key": None},
        "InitialConditionsAgent": {"obj_key": "initial_conditions", "cfg_key": "initial_conditions_config", "narr_key": "initial_conditions_narrative", "judge_key": "initial_conditions_judge_feedback", "attempts_key": "initial_conditions_judge_attempts"},
        "SimulationControlAgent": {"obj_key": "simulation_controls", "cfg_key": "simulation_controls_config", "narr_key": None, "judge_key": None, "attempts_key": None},
        "FileAssemblerAgent": {"obj_key": None, "cfg_key": None, "narr_key": None, "judge_key": None, "attempts_key": None},
    }

    m = mapping.get(agent_name, {})
    obj_key = m.get("obj_key")
    cfg_key = m.get("cfg_key")
    narr_key = m.get("narr_key")
    judge_key = m.get("judge_key")
    attempts_key = m.get("attempts_key")

    section_obj = state.get(obj_key) if obj_key else None
    cfg_obj = state.get(cfg_key) if cfg_key else None
    narrative = state.get(narr_key) if narr_key else None
    judge = state.get(judge_key) if judge_key else None
    attempts = state.get(attempts_key) if attempts_key else None

    section_text = None
    if section_obj is not None:
        # DSSATTools objects usually stringify nicely; if not, you still get something readable.
        section_text = str(section_obj)

    cfg_text = safe_json(cfg_obj) if cfg_obj is not None else None
    judge_text = safe_json(judge) if judge is not None else None

    return {
        "section_text": section_text,
        "config_text": cfg_text,
        "narrative": narrative,
        "judge_text": judge_text,
        "attempts": str(attempts) if attempts is not None else None,
    }

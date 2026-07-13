"""
State definition for the DSSAT workflow (Streamlit-ready).
"""

from __future__ import annotations
from typing import TypedDict, List, Dict, Any, Optional

from DSSATTools.DSSATTools.filex import (
    Cultivar, Planting, Fertilizer, Residue, Irrigation,
    Field, InitialConditions, SimulationControls, Treatment
)


class DSSATState(TypedDict, total=False):
    # Input configuration from JSON
    config: Dict[str, Any]

    # DSSATTools FileX objects
    cultivar: Optional[Cultivar]
    planting: Optional[Planting]
    fertilizer: Optional[Fertilizer]
    residue: Optional[Residue]
    irrigation: Optional[Irrigation]
    field: Optional[Field]
    initial_conditions: Optional[InitialConditions]
    simulation_controls: Optional[SimulationControls]
    treatment: Optional[Treatment]

    # Metadata and processing info
    messages: List[str]
    errors: List[str]

    # Final output
    complete_filex: str

    # Shared values
    crop_code: str
    cultivar_name: str
    cultivar_ingeno: str
    pdate: str
    irrig: str
    xcrd: Optional[float]
    ycrd: Optional[float]
    crop_name_text: str
    location_text: str

    planting_PLDS_codes: Dict[str, str]
    planting_PLME_codes: Dict[str, str]
    cultivar_crop_codes: Dict[str, str]
    fertilizer_name: str
    fertilizer_FMCD_codes: Dict[str, str]
    fertilizer_FACD_codes: Dict[str, str]
    irrigation_IROP_codes: Dict[str, str]

    field_metadata: Dict[str, Any]

    # Judge metadata
    planting_judge_feedback: Optional[Dict[str, Any]]
    planting_judge_attempts: int
    fertilizer_judge_feedback: Optional[Dict[str, Any]]
    fertilizer_judge_attempts: int
    irrigation_judge_feedback: Optional[Dict[str, Any]]
    irrigation_judge_attempts: int

    planting_config: Optional[Dict[str, Any]]
    fertilizer_config: Optional[List[Dict[str, Any]]]
    irrigation_config: Optional[Dict[str, Any]]

    max_judge_attempts: int
    enable_judge: bool

    cache_manager: Optional[Any]
    cache_key: str
    run_list: List[str]
    config_path: str

    # NEW: model switching
    generator_model: str
    judge_model: str

    # NEW: UI channel (callback + logs/events)
    _ui: Dict[str, Any]

    cultivar_list: Optional[Any]

    # Matched cultivar data from CUL file (set by FieldAgent via cul_parser)
    # Tuple of (matched_cultivar_name, cultivar_details_dict) or None
    matched_cultivar_data: Optional[Any]

    weather_duration_years: int

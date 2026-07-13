"""
Planting Agent - Handles planting details section
"""

from __future__ import annotations

import json
from typing import Any, Dict

from utils.state import DSSATState
from utils.llm import get_llm
from utils.helpers import (
    convert_date_to_dssat_date,
    make_code_options_text,
    get_crop_name,
    strip_markdown_fences,
)
from utils.ui_logger import ui_event, ui_log

from DSSATTools.DSSATTools.filex import Planting
from judge_agents.judge_planting_agent import JudgePlantingAgent
from prompts.planting_agent_prompts import base_prompt_planting_agent


class PlantingAgent:
    """
    Agent responsible for the PLANTING DETAILS section using DSSATTools.
    Reads: planting_details from JSON
    Fallback: LLM inference for missing parameters
    Creates Planting object with comprehensive single prompt approach.
    """

    @staticmethod
    def _record_judge_history(state: Dict[str, Any], feedback: Dict[str, Any]) -> None:
        state.setdefault("_ui", {}).setdefault("judge_history", {}).setdefault("PlantingAgent", []).append(feedback)
        ui_event(
            state,
            agent="PlantingAgent",
            kind="judge",
            message=f"Judge returned pass={feedback.get('pass')} score={feedback.get('score')}",
            data={"feedback": feedback},
        )

    @staticmethod
    def _apply_judge_suggestions(planting_config: Dict[str, Any], feedback: Dict[str, Any]) -> Dict[str, Any]:
        """
        Judge output schema (your current judge prompt) nests suggestions like:
          feedback["planting"]["PDATE"]["suggested_value"]
        We apply suggested_value only when non-null.
        """
        plant_block = feedback.get("planting") or {}
        for field, details in plant_block.items():
            if not isinstance(details, dict):
                continue
            suggested = details.get("suggested_value")
            if suggested is not None:
                planting_config[field] = suggested
        return planting_config

    @staticmethod
    def process(state: DSSATState) -> DSSATState:
        agent_name = "PlantingAgent"

        cache_manager = state.get("cache_manager")
        cache_key = state.get("cache_key")
        run_list = state.get("run_list")

        ui_event(state, agent=agent_name, kind="info", message="Starting PlantingAgent")

        # ============================================================================
        # STEP 1: Cache check
        # ============================================================================
        should_run = cache_manager.should_run_agent(agent_name, run_list)

        if not should_run:
            cached_data = cache_manager.get_cached_output(agent_name, cache_key)
            if cached_data:
                ui_event(
                    state,
                    agent=agent_name,
                    kind="cache",
                    message="Loaded from cache",
                    data={
                        "timestamp": cached_data.get("timestamp"),
                        "judge_approved": cached_data.get("judge_approved"),
                        "attempts": cached_data.get("attempts"),
                    },
                )
                ui_log(state, agent_name, f"📦 Cache hit (saved on {cached_data.get('timestamp')})")

                planting_config = cached_data.get("planting_config") or {}
                pdate = cached_data.get("pdate")

                pdate_obj = convert_date_to_dssat_date(pdate)
                planting = Planting(
                    pdate=pdate_obj,
                    ppop=float(planting_config.get("PPOP")),
                    ppoe=float(planting_config.get("PPOP")),
                    plme=planting_config.get("PLME"),
                    plds=planting_config.get("PLDS"),
                    plrs=float(planting_config.get("PLRS")),
                    plrd=int(planting_config.get("PLRD")),
                    pldp=float(planting_config.get("PLDP")),
                    plwt=-99,
                    page=-99,
                    penv=-99,
                    plph=-99,
                    sprl=-99,
                    plname=-99,
                )

                state["planting"] = planting
                state["pdate"] = pdate
                state["planting_config"] = planting_config
                state["messages"].append(f"{agent_name}: Loaded from cache (no LLM calls)")
                ui_event(state, agent=agent_name, kind="output", message="Planting restored from cache")
                return state

            ui_log(state, agent_name, "⚠️ No cache found — running agent")

        else:
            ui_event(state, agent=agent_name, kind="info", message="Forced run (in RUN_LIST)")

        # ============================================================================
        # STEP 2: Prepare context
        # ============================================================================
        config = state.get("config", {})
        base_planting_config = config.get("planting_details", {}) or {}

        crop_code = state.get("crop_code")
        cultivar_name = state.get("cultivar_name")
        xcrd = state.get("xcrd", None)
        ycrd = state.get("ycrd", None)

        cultivar_crop_codes = state.get("cultivar_crop_codes", {})
        planting_PLDS_codes = state.get("planting_PLDS_codes", {})
        planting_PLME_codes = state.get("planting_PLME_codes", {})

        cult_crop_codes_text = make_code_options_text(cultivar_crop_codes)
        plant_PLDS_options_text = make_code_options_text(planting_PLDS_codes)
        plant_PLME_options_text = make_code_options_text(planting_PLME_codes)

        crop_name = get_crop_name(crop_code, cult_crop_codes_text)
        location = state.get("location_text")

        state["crop_name_text"] = crop_name
        state["location_text"] = location

        #fetch crop growing season (start year)
        crop_growing_season = config['crop_growing_season']

        MAX_JUDGE_ATTEMPTS = state.get("max_judge_attempts")
        JUDGE_ENABLED = state.get("enable_judge")

        # local mutable copy
        planting_config: Dict[str, Any] = dict(base_planting_config)
        attempts = 0
        final_planting_obj = None
        planting_judge_feedback: Dict[str, Any] | str = ""

        # Determine if we need LLM
        needs_llm = (
            not planting_config
            or len(planting_config) == 0
            or any(
                planting_config.get(key) is None or planting_config.get(key) == ""
                for key in ["PDATE", "PPOP", "PLME", "PLDS", "PLRS", "PLDP", "PLRD"]
            )
        )

        # ============================================================================
        # STEP 3: Judge–Generator loop
        # ============================================================================
        while attempts < MAX_JUDGE_ATTEMPTS:
            attempts += 1
            state["planting_judge_attempts"] = attempts
            state["messages"].append(f"{agent_name}: Generation attempt {attempts}")
            ui_event(
                state,
                agent=agent_name,
                kind="step",
                message=f"Attempt {attempts}/{MAX_JUDGE_ATTEMPTS}",
            )

            if needs_llm:
                ui_log(state, agent_name, "🧠 Calling generator LLM for planting_details")
                prompt = base_prompt_planting_agent(
                    crop_code,
                    crop_name,
                    cultivar_name,
                    location,
                    xcrd,
                    ycrd,
                    planting_config,
                    planting_judge_feedback,
                    plant_PLME_options_text,
                    plant_PLDS_options_text,
                    crop_growing_season
                )

                try:
                    model = state.get("generator_model", "gpt-5")  # <<< NEW
                    llm = get_llm(mode="api", model=model)          # <<< NEW
                    llm_response = llm.invoke(prompt)

                    clean = strip_markdown_fences(llm_response)
                    result_json = json.loads(clean)

                    planting_config = result_json.get("planting_details", {}) or {}
                    narrative = result_json.get("narrative", "")

                    state["planting_narrative"] = narrative
                    state["messages"].append(f"{agent_name}: LLM suggested planting configuration")
                    ui_event(state, agent=agent_name, kind="step", message="Generator LLM returned JSON")
                except Exception as e:
                    state["errors"].append(f"{agent_name}: Could not parse LLM JSON output. Error: {e}")
                    ui_event(state, agent=agent_name, kind="error", message=f"Generator JSON parse failed: {e}")
                    raise
            else:
                ui_log(state, agent_name, "✅ Using provided planting_details from config (no LLM)")

            # Build Planting object (current candidate)
            pdate = planting_config.get("PDATE")
            ppop = planting_config.get("PPOP")
            plme = planting_config.get("PLME")
            plds = planting_config.get("PLDS")
            plrs = planting_config.get("PLRS")
            pldp = planting_config.get("PLDP")
            plrd = planting_config.get("PLRD")

            pdate_obj = convert_date_to_dssat_date(pdate)

            planting = Planting(
                pdate=pdate_obj,
                ppop=float(ppop),
                ppoe=float(ppop),
                plme=plme,
                plds=plds,
                plrs=float(plrs),
                plrd=int(plrd),
                pldp=float(pldp),
                plwt=-99,
                page=-99,
                penv=-99,
                plph=-99,
                sprl=-99,
                plname=-99,
            )

            final_planting_obj = planting
            state["planting"] = planting
            state["pdate"] = pdate
            state["planting_config"] = planting_config

            # --------------------
            # Judge
            # --------------------
            if not JUDGE_ENABLED:
                feedback = {"pass": True, "score": 5, "parameter": "planting", "planting": {}, "issues": [], "summary": "Judge disabled"}
                planting_judge_feedback = ""
                ui_log(state, agent_name, "🟨 Judge disabled — accepting candidate")
                PlantingAgent._record_judge_history(state, feedback)
            else:
                ui_log(state, agent_name, "🧑‍⚖️ Calling judge LLM for planting_details")
                state = JudgePlantingAgent.process(state)
                feedback = state.get("planting_judge_feedback") or {}
                planting_judge_feedback = feedback
                PlantingAgent._record_judge_history(state, feedback)

            if not feedback:
                state["errors"].append(f"{agent_name}: Judge returned empty feedback")
                ui_event(state, agent=agent_name, kind="error", message="Judge feedback empty")
                raise RuntimeError("JudgePlantingAgent: feedback is empty")

            passed = bool(feedback.get("pass"))

            if passed:
                state["messages"].append(f"{agent_name}: Judge accepted planting configuration on attempt {attempts}")
                ui_event(state, agent=agent_name, kind="step", message="✅ Judge passed")
                break

            # If failed: apply judge suggested values and loop
            ui_event(state, agent=agent_name, kind="step", message="❌ Judge failed — applying suggested fixes")
            planting_config = PlantingAgent._apply_judge_suggestions(planting_config, feedback)
            state["planting_config"] = planting_config
            needs_llm = True  # rerun generator using judge feedback

        # ============================================================================
        # STEP 4: Finalize + cache
        # ============================================================================
        if final_planting_obj is None:
            state["errors"].append(f"{agent_name}: Failed after {attempts} attempt(s)")
            ui_event(state, agent=agent_name, kind="error", message="Final planting object is None")
            raise RuntimeError(f"{agent_name}: final_planting_obj is None")

        cache_data = {
            "planting_config": planting_config,
            "pdate": planting_config.get("PDATE"),
            "judge_approved": True,
            "attempts": attempts,
        }
        cache_manager.save_agent_output(agent_name, cache_key, cache_data)
        ui_event(state, agent=agent_name, kind="cache", message="Saved to cache", data={"attempts": attempts})

        state["planting"] = final_planting_obj
        state["pdate"] = planting_config.get("PDATE")
        state["messages"].append(
            f"{agent_name}: Created Planting object (PDATE={planting_config.get('PDATE')}, PPOP={planting_config.get('PPOP')}) after {attempts} attempt(s)"
        )
        ui_event(state, agent=agent_name, kind="output", message="Planting section ready")
        return state

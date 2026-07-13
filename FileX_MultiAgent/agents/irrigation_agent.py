"""
Irrigation Agent - Handles irrigation and water management
"""

from __future__ import annotations

import json
from typing import Optional, List, Dict, Any

from utils.state import DSSATState
from utils.llm import get_llm
from utils.helpers import convert_date_to_dssat_date, strip_markdown_fences
from utils.ui_logger import ui_log, ui_event
from DSSATTools.DSSATTools.filex import Irrigation, IrrigationEvent
from prompts.irrigation_agent_prompts import base_irrigation_agent_prompts
from judge_agents.judge_irrigation_agent import JudgeIrrigationAgent


class IrrigationAgent:
    """
    Agent responsible for irrigation using DSSATTools.
    Uses LLM prompt to determine irrigation strategy and parameters,
    with QC loop through JudgeIrrigationAgent.
    """

    @staticmethod
    def process(state: DSSATState) -> DSSATState:
        agent_name = "IrrigationAgent"
        ui_event(state, agent=agent_name, kind="info", message="Irrigation agent started")

        # ============================================================================
        # STEP 1: Cache Check
        # ============================================================================
        cache_manager = state.get("cache_manager")
        cache_key = state.get("cache_key")
        run_list = state.get("run_list", ["ALL"])

        should_run = True
        if cache_manager is not None:
            should_run = cache_manager.should_run_agent(agent_name, run_list)

        if not should_run and cache_manager is not None:
            cached_data = cache_manager.get_cached_output(agent_name, cache_key)

            if cached_data:
                ui_event(
                    state,
                    agent=agent_name,
                    kind="cache",
                    message="Loaded from cache",
                    data={
                        "cache_key": cache_key,
                        "timestamp": cached_data.get("timestamp"),
                        "strategy": cached_data.get("strategy"),
                        "judge_approved": cached_data.get("judge_approved"),
                        "attempts": cached_data.get("attempts"),
                    },
                )
                ui_log(state, agent_name, f"📦 Cache hit (key={cache_key})")

                strategy = cached_data.get("strategy")
                irrigation_config = cached_data.get("irrigation_config") or {}
                irrig_flag = cached_data.get("irrig", "N")

                state["irrig"] = irrig_flag
                state["irrigation_config"] = irrigation_config

                if strategy == "rainfed" or irrig_flag == "N":
                    state["irrigation"] = None
                    state.setdefault("messages", []).append(f"{agent_name}: Loaded from cache (rainfed, no irrigation)")
                    ui_event(state, agent=agent_name, kind="output", message="Rainfed (from cache)")
                    return state

                # Recreate Irrigation object (irrigated)
                header_row = irrigation_config.get("header_row", {}) or {}
                irrigation_events_data = irrigation_config.get("irrigation_events", []) or []
                pdate = state.get("pdate")

                irrigation_events: List[IrrigationEvent] = []
                for app in irrigation_events_data:
                    idate_str = str(app.get("IDATE", "")).strip()
                    idate = convert_date_to_dssat_date(idate_str if idate_str else pdate)

                    irrigation_events.append(
                        IrrigationEvent(
                            idate=idate,
                            irval=float(app.get("IRVAL")),
                            irop=app.get("IROP"),
                        )
                    )

                irrigation_obj = Irrigation(
                    table=irrigation_events,
                    efir=float(header_row.get("EFIR", -99)),
                    idep=float(header_row.get("IDEP", -99)),
                    ithr=float(header_row.get("ITHR", -99)),
                    iept=float(header_row.get("IEPT", -99)),
                    ioff=header_row.get("IOFF", "GS000"),
                    iame=header_row.get("IAME", "IR001"),
                    iamt=float(header_row.get("IAMT", -99)),
                    irname=header_row.get("IRNAME", "-99"),
                )

                state["irrigation"] = irrigation_obj
                state.setdefault("messages", []).append(
                    f"{agent_name}: Loaded from cache ({len(irrigation_events)} irrigation events)"
                )
                ui_event(state, agent=agent_name, kind="output", message="Irrigation object restored from cache")
                return state

            ui_log(state, agent_name, "⚠️ No cache found; running agent fresh")
        else:
            ui_log(state, agent_name, "🚀 Running agent fresh")

        # ============================================================================
        # STEP 2: Run Agent
        # ============================================================================
        config = state.get("config", {})
        _ = config.get("irrigation_and_water_management", {}) or {}  # keep for future use

        MAX_JUDGE_ATTEMPTS = int(state.get("max_judge_attempts", 1))
        JUDGE_ENABLED = bool(state.get("enable_judge", False))

        # Context
        crop_code = state.get("crop_code")
        cultivar_name = state.get("cultivar_name")
        pdate = state.get("pdate")
        xcrd = state.get("xcrd", None)
        ycrd = state.get("ycrd", None)

        irrigation_irop_codes = state.get("irrigation_IROP_codes")
        crop_name = state.get("crop_name_text")
        location = state.get("location_text")

        ui_log(state, agent_name, f"Processing irrigation for {crop_code} - {crop_name} at {location}")

        attempts = 0
        final_irrigation_obj: Optional[Irrigation] = None
        irrigation_judge_feedback: Dict[str, Any] = {}
        irrigation_config: Dict[str, Any] = state.get("irrigation_config") or {}

        gen_model = state.get("generator_model", "gpt-5")

        while attempts < MAX_JUDGE_ATTEMPTS:
            attempts += 1
            state["irrigation_judge_attempts"] = attempts
            state.setdefault("messages", []).append(f"{agent_name}: Generation attempt {attempts}")

            ui_event(state, agent=agent_name, kind="step", message=f"Attempt {attempts} started")

            prompt = base_irrigation_agent_prompts(
                crop_code, crop_name, cultivar_name, location, xcrd, ycrd, pdate,
                irrigation_irop_codes, irrigation_config, irrigation_judge_feedback
            )

            # 1) Generator LLM
            try:
                ui_log(state, agent_name, f"Calling generator LLM (model={gen_model})")
                llm = get_llm(mode="api", model=gen_model)
                llm_response = llm.invoke(prompt)

                clean = strip_markdown_fences(llm_response)
                result_json = json.loads(clean)
            except json.JSONDecodeError as e:
                state.setdefault("errors", []).append(f"{agent_name}: Could not parse LLM JSON output. Error: {e}")
                ui_event(state, agent=agent_name, kind="error", message=f"Generator JSON parse failed: {e}")
                # original behavior: fall back to no irrigation
                state["irrig"] = "N"
                state["irrigation"] = None
                return state
            except Exception as e:
                state.setdefault("errors", []).append(f"{agent_name}: Unexpected error: {e}")
                ui_event(state, agent=agent_name, kind="error", message=f"Generator error: {e}")
                state["irrig"] = "N"
                state["irrigation"] = None
                return state

            irrigation_section = result_json.get("irrigation_section", {}) or {}
            strategy = irrigation_section.get("strategy")
            narrative = result_json.get("narrative", "")
            irrigation_events = irrigation_section.get("irrigation_events", []) or []
            header_row = irrigation_section.get("header_row", {}) or {}

            state["irrigation_narrative"] = narrative

            irrigation_config = {
                "strategy": strategy,
                "header_row": header_row,
                "irrigation_events": irrigation_events,
            }
            state["irrigation_config"] = irrigation_config

            ui_event(
                state,
                agent=agent_name,
                kind="step",
                message=f"LLM suggested strategy='{strategy}' events={len(irrigation_events)}",
                data={"strategy": strategy, "events": len(irrigation_events)},
            )

            # 2) Judge
            if not JUDGE_ENABLED:
                ui_log(state, agent_name, "Judge disabled — accepting configuration")
                feedback = {"pass": True, "score": 5, "issues": []}
                irrigation_judge_feedback = {}
            else:
                ui_event(state, agent=agent_name, kind="judge", message=f"Judge started (attempt {attempts})")
                state = JudgeIrrigationAgent.process(state)
                feedback = state.get("irrigation_judge_feedback") or {"error":"no feedback"}
                irrigation_judge_feedback = feedback

                state.setdefault("_ui", {}).setdefault("judge_history", {}).setdefault(agent_name, []).append(feedback)

                ui_event(
                    state,
                    agent=agent_name,
                    kind="judge",
                    message=f"Judge finished (attempt {attempts})",
                    data={"pass": bool(feedback.get("pass")), "score": feedback.get("score")},
                )

            if feedback is None:
                state.setdefault("messages", []).append(
                    f"{agent_name}: Judge returned no feedback; no irrigation section will be written."
                )
                ui_event(state, agent=agent_name, kind="error", message="Judge feedback missing")
                state["irrig"] = "N"
                state["irrigation"] = None
                return state

            passed = bool(feedback.get("pass"))

            if passed:
                ui_log(state, agent_name, f"✅ Judge passed on attempt {attempts}")

                strategy = irrigation_config.get("strategy")
                header_row = irrigation_config.get("header_row", {}) or {}
                irrigation_apps = irrigation_config.get("irrigation_events", []) or []

                # Build events
                events: List[IrrigationEvent] = []

                # If rainfed => no section
                if strategy == "rainfed":
                    state["irrig"] = "N"
                    
                    state.setdefault("messages", []).append(
                        f"{agent_name}: Final strategy rainfed; no irrigation events"
                    )
                    empty_irrigation_events = [
                        IrrigationEvent(
                        idate=None,
                        irval=0,
                        irop=None
                    )]
                    final_irrigation_obj = Irrigation(
                        table=empty_irrigation_events,
                        efir=float(header_row.get("EFIR", -99)),
                        idep=float(header_row.get("IDEP", -99)),
                        ithr=float(header_row.get("ITHR", -99)),
                        iept=float(header_row.get("IEPT", -99)),
                        ioff=header_row.get("IOFF", None),
                        iame=header_row.get("IAME", None),
                        iamt=float(header_row.get("IAMT", -99)),
                        irname=header_row.get("IRNAME", "-99"),
                    )

                    state["irrigation"] = final_irrigation_obj
                    break #exists the loop and doesnt go to below code

                if len(irrigation_apps) == 0:
                    raise RuntimeError("[IrrigationAgent] Strategy not rainfed but irrigation_events is empty.")

                
                for app in irrigation_apps:
                    idate_str = str(app.get("IDATE", "")).strip()
                    idate = convert_date_to_dssat_date(idate_str if idate_str else pdate)
                    events.append(
                        IrrigationEvent(
                            idate=idate,
                            irval=float(app.get("IRVAL")),
                            irop=app.get("IROP"),
                        )
                    )

                irrigation_obj = Irrigation(
                    table=events,
                    efir=float(header_row.get("EFIR", -99)),
                    idep=float(header_row.get("IDEP", -99)),
                    ithr=float(header_row.get("ITHR", -99)),
                    iept=float(header_row.get("IEPT", -99)),
                    ioff=header_row.get("IOFF", None),
                    iame=header_row.get("IAME", None),
                    iamt=float(header_row.get("IAMT", -99)),
                    irname=header_row.get("IRNAME", "-99"),
                )

                final_irrigation_obj = irrigation_obj
                state["irrigation"] = irrigation_obj
                state["irrig"] = "R"

                state.setdefault("messages", []).append(
                    f"{agent_name}: Created Irrigation object with {len(events)} event(s); strategy='{strategy}'"
                )
                break
            else:
                # FAIL: apply suggested_fix and retry
                suggested_fix = (feedback.get("suggested_fix") or {})
                global_fix = suggested_fix.get("global", {}) or {}
                events_fix = suggested_fix.get("events", []) or []

                ui_log(state, agent_name, f"❌ Judge failed on attempt {attempts}; applying patch and retrying")

                # Apply global strategy/header fixes
                if global_fix.get("strategy") is not None:
                    irrigation_config["strategy"] = global_fix.get("strategy")

                hdr_fix = global_fix.get("header_row", {}) or {}
                header_row = irrigation_config.get("header_row", {}) or {}
                for field in ["EFIR", "IDEP", "ITHR", "IEPT", "IOFF", "IAME", "IAMT", "IRNAME"]:
                    if hdr_fix.get(field) is not None:
                        header_row[field] = hdr_fix.get(field)
                irrigation_config["header_row"] = header_row

                # Apply per-event fixes
                irrigation_events = irrigation_config.get("irrigation_events", []) or []
                for ev_fix in events_fix:
                    idx_fix = ev_fix.get("index")
                    if idx_fix is None:
                        continue
                    if idx_fix < 0:
                        continue

                    # If patch references an event beyond current list, extend list
                    while idx_fix >= len(irrigation_events):
                        irrigation_events.append(
                            {"IDATE": None, "IROP": None, "IRVAL": None, "EFIR": None, "Assumptions_or_Notes": None}
                        )

                    ev = irrigation_events[idx_fix]
                    for field in ["IDATE", "IROP", "IRVAL", "EFIR", "Assumptions_or_Notes"]:
                        if ev_fix.get(field) is not None:
                            ev[field] = ev_fix.get(field)

                irrigation_config["irrigation_events"] = irrigation_events
                state["irrigation_config"] = irrigation_config

        # After loop
        if final_irrigation_obj is None:
            # If strategy ended up rainfed, this is OK. Only mark error if judge never passed and not rainfed.
            # We rely on state["irrig"] to indicate final.
            if state.get("irrig") != "R":
                state.setdefault("errors", []).append(
                    f"{agent_name}: Final irrigation object is None after {attempts} attempt(s)"
                )
            # For rainfed, keep irrigation None
            state.setdefault("messages", []).append(f"{agent_name}: Completed (rainfed or no irrigation object).")
            return state

        # ============================================================================
        # STEP 3: Save successful result to cache
        # ============================================================================
        if cache_manager is not None:
            cache_data = {
                "strategy": irrigation_config.get("strategy"),
                "irrigation_config": irrigation_config,
                "irrig": state.get("irrig"),
                "judge_approved": True,
                "attempts": attempts,
            }
            cache_manager.save_agent_output(agent_name, cache_key, cache_data)
            ui_event(
                state,
                agent=agent_name,
                kind="cache",
                message="Saved output to cache",
                data={"cache_key": cache_key, "attempts": attempts},
            )

        state.setdefault("messages", []).append(f"{agent_name}: Final Irrigation object set after {attempts} attempt(s)")
        ui_event(state, agent=agent_name, kind="output", message="Irrigation section complete")
        return state

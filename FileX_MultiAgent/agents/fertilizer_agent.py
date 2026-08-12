"""
Fertilizer Agent - Handles fertilizer applications
"""

from __future__ import annotations

import json
from typing import List, Dict, Any, Optional

from utils.state import DSSATState
from utils.llm import get_llm
from utils.helpers import convert_date_to_dssat_date, make_code_options_text, strip_markdown_fences
from utils.ui_logger import ui_event, ui_log

from DSSATTools.DSSATTools.filex import Fertilizer, FertilizerEvent
from judge_agents.judge_fertilizer_agent import JudgeFertilizerAgent
from prompts.fertilizer_agent_prompts import base_prompt_fertilizer_agent


class FertilizerAgent:
    """
    Agent responsible for fertilizer applications using DSSATTools.
    Creates Fertilizer objects with FertilizerEvent list.
    Uses judge loop (optional) and caching.
    """

    @staticmethod
    def process(state: DSSATState) -> DSSATState:
        agent_name = "FertilizerAgent"
        ui_event(state, agent=agent_name, kind="info", message="Fertilizer agent started")

        # ============================================================================
        # STEP 1: Cache Check
        # ============================================================================
        cache_manager = state.get("cache_manager")
        cache_key = state.get("cache_key")
        run_list = state.get("run_list")

        should_run = True
        if cache_manager is not None:
            should_run = cache_manager.should_run_agent(agent_name, run_list)

        if not should_run and cache_manager is not None:
            cached_data = cache_manager.get_cached_output(agent_name, cache_key)

            if cached_data:
                fertilizer_config = cached_data.get("fertilizer_config", []) or []

                ui_event(
                    state,
                    agent=agent_name,
                    kind="cache",
                    message="Loaded from cache",
                    data={
                        "cache_key": cache_key,
                        "timestamp": cached_data.get("timestamp"),
                        "events": len(fertilizer_config),
                        "judge_approved": cached_data.get("judge_approved"),
                        "attempts": cached_data.get("attempts"),
                    },
                )
                ui_log(state, agent_name, f"📦 Cache hit (events={len(fertilizer_config)})")

                # Recreate Fertilizer object
                fertilizer_events: List[FertilizerEvent] = []
                for idx, fert in enumerate(fertilizer_config, 1):
                    fdate = convert_date_to_dssat_date(fert["FDATE"])
                    fertilizer_events.append(
                        FertilizerEvent(
                            fdate=fdate,
                            fmcd=fert.get("FMCD"),
                            facd=fert.get("FACD"),
                            fdep=float(fert.get("FDEP")),
                            famn=float(fert.get("FAMN")),
                            famp=float(fert.get("FAMP")),
                            famk=float(fert.get("FAMK")),
                            fername=f"Fertilizer_{idx}",
                        )
                    )

                fertilizer_obj = Fertilizer(table=fertilizer_events)
                state["fertilizer"] = fertilizer_obj
                state["fertilizer_config"] = fertilizer_config
                state.setdefault("messages", []).append(
                    f"{agent_name}: Loaded from cache ({len(fertilizer_events)} fertilizer events)"
                )

                ui_event(state, agent=agent_name, kind="output", message="Fertilizer section restored from cache")
                return state

            ui_log(state, agent_name, "⚠️ No cache found; running agent fresh")
        else:
            ui_log(state, agent_name, "🚀 Running agent fresh")

        # ============================================================================
        # STEP 2: Run Agent
        # ============================================================================
        config = state.get("config", {})
        _ = config.get("fertilizers_inorganic", []) or []  # keep for later if you want to merge config+LLM
        target_n_rate_kg_ha = (config.get("fertilizer") or {}).get("target_n_rate_kg_ha")

        MAX_JUDGE_ATTEMPTS = int(state.get("max_judge_attempts", 1))
        JUDGE_ENABLED = bool(state.get("enable_judge", False))

        cultivar_crop_codes = state.get("cultivar_crop_codes", {})
        fertilizer_fmcd_codes = state.get("fertilizer_FMCD_codes", {})
        fertilizer_facd_codes = state.get("fertilizer_FACD_codes", {})

        _ = make_code_options_text(cultivar_crop_codes)  # kept, even if not currently used by your prompt

        crop_code = state.get("crop_code")
        crop_name = state.get("crop_name_text")
        cultivar_name = state.get("cultivar_name")
        pdate = state.get("pdate")

        xcrd = state.get("xcrd", None)
        ycrd = state.get("ycrd", None)
        location = state.get("location_text")

        ui_log(state, agent_name, f"Context: {crop_code} - {crop_name} at {location} (PDATE={pdate})")
        ui_event(
            state,
            agent=agent_name,
            kind="info",
            message="Entering generation/judge loop",
            data={"max_attempts": MAX_JUDGE_ATTEMPTS, "judge_enabled": JUDGE_ENABLED},
        )

        fertilizer_config: List[Dict[str, Any]] = []
        final_fertilizer_obj: Optional[Fertilizer] = None
        attempts = 0
        fertilizer_judge_feedback: Dict[str, Any] = {}

        gen_model = state.get("generator_model", "gpt-5")

        while attempts < MAX_JUDGE_ATTEMPTS:
            attempts += 1
            state["fertilizer_judge_attempts"] = attempts
            state.setdefault("messages", []).append(f"{agent_name}: Generation attempt {attempts}")

            ui_event(state, agent=agent_name, kind="step", message=f"Attempt {attempts} started")

            prompt = base_prompt_fertilizer_agent(
                crop_name,
                location,
                pdate,
                fertilizer_config,
                fertilizer_judge_feedback,
                fertilizer_fmcd_codes,
                fertilizer_facd_codes,
                target_n_rate_kg_ha=target_n_rate_kg_ha,
            )

            # 1) Generator
            try:
                ui_log(state, agent_name, f"Calling generator LLM (model={gen_model})")
                llm = get_llm(mode="api", model=gen_model)
                llm_response = llm.invoke(prompt)

                clean = strip_markdown_fences(llm_response)
                result_json = json.loads(clean)
            except Exception as e:
                state.setdefault("errors", []).append(f"{agent_name}: Could not parse LLM JSON output. Error: {e}")
                ui_event(state, agent=agent_name, kind="error", message=f"Generator JSON parse failed: {e}")
                raise

            fertilizer_section = result_json.get("fertilizer_section", []) or []
            state["fertilizer_narrative"] = result_json.get("narrative", "")

            # Convert to internal config list (calendar FDATE only)
            fertilizer_config = []
            for fert in fertilizer_section:
                fdate_str = str(fert.get("FDATE", "")).strip()
                fdate_calendar = fdate_str.split(",")[0].strip() if "," in fdate_str else fdate_str
                if not fdate_calendar:
                    fdate_calendar = pdate  # fallback

                fertilizer_config.append(
                    {
                        "FDATE": fdate_calendar,
                        "FMCD": fert.get("FMCD"),
                        "FACD": fert.get("FACD"),
                        "FDEP": fert.get("FDEP"),
                        "FAMN": fert.get("FAMN"),
                        "FAMP": fert.get("FAMP"),
                        "FAMK": fert.get("FAMK"),
                        "Assumptions_or_Notes": fert.get("Assumptions_or_Notes", ""),
                    }
                )

            state["fertilizer_config"] = fertilizer_config

            ui_event(
                state,
                agent=agent_name,
                kind="step",
                message=f"Generated fertilizer program (events={len(fertilizer_config)})",
                data={"events": len(fertilizer_config)},
            )

            # 2) Judge
            if not JUDGE_ENABLED:
                ui_log(state, agent_name, "Judge disabled — accepting configuration")
                feedback = {"pass": True, "score": 5, "issues": [], "suggested_fix": {"events": []}}
                fertilizer_judge_feedback = {}
            else:
                ui_event(state, agent=agent_name, kind="judge", message=f"Judge started (attempt {attempts})")
                state = JudgeFertilizerAgent.process(state)
                feedback = state.get("fertilizer_judge_feedback") or {}
                fertilizer_judge_feedback = feedback

                state.setdefault("_ui", {}).setdefault("judge_history", {}).setdefault(agent_name, []).append(feedback)

                ui_event(
                    state,
                    agent=agent_name,
                    kind="judge",
                    message=f"Judge finished (attempt {attempts})",
                    data={"pass": bool(feedback.get("pass")), "score": feedback.get("score")},
                )

            if feedback is None:
                ui_event(state, agent=agent_name, kind="error", message="Judge feedback is None")
                raise RuntimeError("JudgeFertilizerAgent: feedback is None")

            passed = bool(feedback.get("pass"))
            if passed:
                ui_log(state, agent_name, f"✅ Judge passed on attempt {attempts}")

                # Build DSSAT Fertilizer object
                fertilizer_events: List[FertilizerEvent] = []
                for idx, fert in enumerate(fertilizer_config, 1):
                    fdate = convert_date_to_dssat_date(fert["FDATE"])
                    fertilizer_events.append(
                        FertilizerEvent(
                            fdate=fdate,
                            fmcd=fert.get("FMCD"),
                            facd=fert.get("FACD"),
                            fdep=float(fert.get("FDEP")),
                            famn=float(fert.get("FAMN")),
                            famp=float(fert.get("FAMP")),
                            famk=float(fert.get("FAMK")),
                            fername=f"Fertilizer_{idx}",
                        )
                    )

                final_fertilizer_obj = Fertilizer(table=fertilizer_events)
                state["fertilizer"] = final_fertilizer_obj
                break

            # FAIL: apply patch and retry
            ui_log(state, agent_name, f"❌ Judge failed on attempt {attempts}; applying patch and retrying")

            suggested_fix = feedback.get("suggested_fix", {}) or {}
            events_fix = suggested_fix.get("events", []) or []

            # Apply corrections to fertilizer_config in-place
            for ev_fix in events_fix:
                idx_fix = ev_fix.get("index")
                if idx_fix is None or idx_fix < 0:
                    continue

                # Extend list if patch points beyond current events
                while idx_fix >= len(fertilizer_config):
                    fertilizer_config.append(
                        {"FDATE": pdate, "FMCD": None, "FACD": None, "FDEP": 0, "FAMN": 0, "FAMP": 0, "FAMK": 0}
                    )

                ev = fertilizer_config[idx_fix]
                for field in ["FDATE", "FMCD", "FACD", "FDEP", "FAMN", "FAMP", "FAMK"]:
                    if ev_fix.get(field) is not None:
                        ev[field] = ev_fix.get(field)

            state["fertilizer_config"] = fertilizer_config

        # ===== After loop =====
        if final_fertilizer_obj is None:
            state.setdefault("errors", []).append(
                f"{agent_name}: Failed to obtain acceptable fertilizer configuration after {attempts} attempt(s)"
            )
            ui_event(state, agent=agent_name, kind="error", message="Failed after max attempts")
            return state

        events_count = len(final_fertilizer_obj.table) if hasattr(final_fertilizer_obj, "table") else 0
        state.setdefault("messages", []).append(
            f"{agent_name}: Created Fertilizer object with {events_count} event(s) after {attempts} attempt(s)"
        )

        # ============================================================================
        # STEP 3: Save successful result to cache
        # ============================================================================
        if cache_manager is not None:
            cache_data = {
                "fertilizer_config": fertilizer_config,
                "judge_approved": True,
                "attempts": attempts,
            }
            cache_manager.save_agent_output(agent_name, cache_key, cache_data)
            ui_event(
                state,
                agent=agent_name,
                kind="cache",
                message="Saved output to cache",
                data={"cache_key": cache_key, "attempts": attempts, "events": len(fertilizer_config)},
            )

        ui_event(state, agent=agent_name, kind="output", message="Fertilizer section complete")
        return state

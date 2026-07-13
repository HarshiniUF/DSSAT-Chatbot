from __future__ import annotations

import json
from typing import Any, Dict, List

from utils.llm import get_judge_llm
from utils.helpers import strip_markdown_fences
from utils.ui_logger import ui_log, ui_event


class JudgeIrrigationAgent:
    """
    LLM Judge for the IrrigationAgent.

    Reads irrigation_config from state and returns minimal PATCH in suggested_fix.
    """

    @staticmethod
    def process(state: Dict[str, Any]) -> Dict[str, Any]:
        agent_name = "JudgeIrrigationAgent"
        ui_event(state, agent=agent_name, kind="judge", message="JudgeIrrigationAgent started")

        irrigation_section = state.get("irrigation_config", {}) or {}
        strategy = irrigation_section.get("strategy")
        header_row = irrigation_section.get("header_row", {}) or {}
        irrigation_events: List[Dict[str, Any]] = irrigation_section.get("irrigation_events", []) or []

        if strategy not in ("rainfed", "irrigated"):
            ui_event(state, agent=agent_name, kind="error", message="strategy invalid or missing")
            raise RuntimeError("irrigation_config.strategy must be 'rainfed' or 'irrigated'")

        crop_code = state.get("crop_code")
        crop_name = state.get("crop_name_text")
        cultivar_name = state.get("cultivar_name")
        location = state.get("location_text")
        xcrd = state.get("xcrd")
        ycrd = state.get("ycrd")
        pdate = state.get("pdate")

        irrigation_irop_codes = state.get("irrigation_IROP_codes") or {}
        valid_irop_keys = list(irrigation_irop_codes.keys())

        judge_prompt = f"""
            You are an expert agronomist and DSSAT crop modeling specialist.
            You are acting as a strict but helpful JUDGE for a proposed DSSAT irrigation management strategy.

            Your task:
            1. Carefully evaluate whether the given irrigation strategy (rainfed vs irrigated) is realistic for the crop, location, and planting date.
            2. If irrigated, evaluate whether the header parameters (EFIR, IDEP, ITHR, IEPT, IOFF, IAME, IAMT, IRNAME) and the individual irrigation events are agronomically realistic.
            3. Use step-by-step agronomic reasoning (chain-of-thought) to justify your judgment.
            4. Provide a clear decision: pass (acceptable) or fail (unrealistic / needs correction).
            5. If it fails, provide concrete suggested corrections for header_row and/or individual events.

            Context:
            - CROP CODE: {crop_code}
            - CROP NAME: {crop_name}
            - CULTIVAR NAME: {cultivar_name}
            - LOCATION: {location}
            - LATITUDE: {xcrd}
            - LONGITUDE: {ycrd}
            - PLANTING DATE (PDATE): {pdate}

            Proposed irrigation configuration (DSSAT-style):
            {json.dumps(irrigation_section, indent=2)}

            Field meaning recap:
            - strategy: "rainfed" or "irrigated".
            - header_row:
                - EFIR,IDEP,ITHR,IEPT,IOFF,IAME,IAMT,IRNAME : do not judge this row these are always -99, so the output is null always
            - irrigation_events[]:
                - IDATE: date of irrigation (YYYY-MM-DD).
                - IROP: irrigation operation/method code.
                - IRVAL: depth of water applied (mm).
                - EFIR: efficiency (0–1).
                - Assumptions_or_Notes: short text.

            You MUST reason explicitly about:
            - Is choosing rainfed vs irrigated realistic for this crop and region?
            - If irrigated:
            - Are EFIR, IDEP, ITHR, IEPT, IOFF, IAME, IAMT, IRNAME values within realistic ranges
                and consistent with each other and the likely irrigation method?
            - Are the number and timing of irrigation events plausible based on climate and crop water requirements?
            - Are IRVAL amounts reasonable (not extremely high or low)?
            - Are IROP codes consistent with the described irrigation method?
            - If rainfed:
            - Is it realistic that farmers in this region would not irrigate this crop?
            - Are header_row values correctly set to -99 / null for a rainfed system?
            - Are the irrigation events empty because it is rainfed system?

            Important: You are checking agronomic realism, not just syntax.

            Output format (STRICT JSON ONLY, no markdown, no extra text):

            {'''{
            "parameter": "irrigation",
            "score": <integer 1–5>,
            "pass": <true or false>,
            "strategy_original":<strategy from the original values irrigation or rainfed>,
            "header_row": {
                don't output anything just leave a message saying "all are -99"
            },
            "events"(suugest to remove this entire events only and only if the strategy is rainfed): [
                {
                "index": <0-based index of event in the original irrigation_events list>,

                "IDATE": {
                    "original_value": <original value or null>,
                    "issue": <string or null>,
                    "suggested_value": <new value or null>,
                    "suggested_reasoning": <string or null>
                },
                
                /* Replicate this same object pattern for all other event-level fields, and so on:
                    "FIELD_NAME": {
                    "original_value": <original value or null>,
                    "issue": <string or null>,
                    "suggested_value": <new value or null>,
                    "suggested_reasoning": <string or null>
                    }
                */
                }
            ],
                        "summary": <a very brief summary of what changes you suggested>
            }
            '''}

                        Guidelines:
                        - "pass" should be true only if strategy + parameters + events are all agronomically realistic for typical management in that region.
                        - "score" should be 4–5 only for clearly realistic and internally consistent programs.
                        - In "suggested_fix.global.header_row", only specify fields that need adjustment (others null).
                        - In "suggested_fix.events", only include entries for events that need change, and use null for fields that are fine.
                        - If everything is acceptable, set "pass": true and "suggested_fix.events": [].
            
        """.strip()

        judge_model = state.get("judge_model", "gpt-5")
        judge_llm = get_judge_llm(model=judge_model)

        ui_log(state, agent_name, f"Judging irrigation_config with model={judge_model}")

        raw = judge_llm.invoke(judge_prompt)
        clean = strip_markdown_fences(raw)

        try:
            feedback = json.loads(clean)
        except Exception as e:
            state.setdefault("errors", []).append(
                f"{agent_name}: Failed to parse judge output. Error: {e}"
            )
            ui_event(state, agent=agent_name, kind="error", message=f"Judge JSON parse failed: {e}", data={"raw": clean[:1200]})
            raise

        state["irrigation_judge_feedback"] = feedback
        state["irrigation_judge_attempts"] = state.get("irrigation_judge_attempts", 0) + 1

        state.setdefault("messages", []).append(
            f"{agent_name}: pass={feedback.get('pass')} score={feedback.get('score')} issues={feedback.get('issues')}"
        )

        ui_event(
            state,
            agent=agent_name,
            kind="judge",
            message="JudgeIrrigationAgent finished",
            data={"pass": bool(feedback.get("pass")), "score": feedback.get("score")},
        )
        return state

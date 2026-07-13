# judge_agents/judge_planting_agent.py

from __future__ import annotations

import json
from typing import Any, Dict

from utils.llm import get_judge_llm
from utils.helpers import strip_markdown_fences
from utils.ui_logger import ui_event, ui_log


class JudgePlantingAgent:
    """
    LLM Judge for the PlantingAgent.

    - Reads planting configuration and context from state.
    - Evaluates agronomic realism.
    - Writes structured feedback back into state:
        state["planting_judge_feedback"]
        state["planting_judge_attempts"]
    """

    @staticmethod
    def process(state: Dict[str, Any]) -> Dict[str, Any]:
        agent_name = "PlantingAgent"

        planting_config = state.get("planting_config", {}) or {}
        if not planting_config:
            ui_event(state, agent=agent_name, kind="error", message="Judge: planting_config is empty")
            raise RuntimeError("JudgePlantingAgent: planting_config is empty")

        crop_code = state.get("crop_code")
        crop_name = state.get("crop_name_text")
        cultivar_name = state.get("cultivar_name")
        location = state.get("location_text")
        xcrd = state.get("xcrd")
        ycrd = state.get("ycrd")

        final_planting_cfg: Dict[str, Any] = {
            "PDATE": planting_config.get("PDATE"),
            "PPOP": planting_config.get("PPOP"),
            "PLME": planting_config.get("PLME"),
            "PLDS": planting_config.get("PLDS"),
            "PLRS": planting_config.get("PLRS"),
            "PLDP": planting_config.get("PLDP"),
            "PLRD": planting_config.get("PLRD"),
        }

        model = state.get("judge_model", "gpt-5")
        judge_llm = get_judge_llm(model=model)

        ui_log(state, agent_name, f"🧑‍⚖️ Judge model: {model}")

        judge_prompt = f"""
  You are an expert agronomist and DSSAT crop modeling specialist.
            You are acting as a strict but helpful JUDGE for a proposed DSSAT planting configuration.

            Your task:
            1. Carefully evaluate whether the given planting parameters are agronomically realistic.
            2. Use step-by-step agronomic reasoning (chain-of-thought) to justify your judgment.
            3. Provide a clear decision: pass (acceptable) or fail (unrealistic / needs correction).
            4. If it fails, provide concrete suggested corrections.

            Context:
            - CROP CODE: {crop_code}
            - CROP NAME: {crop_name}
            - CULTIVAR NAME: {cultivar_name}
            - LOCATION: {location}
            - LATITUDE: {xcrd}
            - LONGITUDE: {ycrd}

            Proposed planting configuration (DSSAT-style):
            {json.dumps(final_planting_cfg, indent=2)}

            You MUST reason explicitly about:
            - Typical planting windows and whether PDATE is reasonable for this crop and location.
            - Typical plant populations (PPOP) for this crop in this production system.
            - Consistency between row spacing (PLRS) and plant population (PPOP).
            For example, given PPOP and PLRS, estimate within-row spacing and check if it is realistic.
            - Whether the planting material (PLME) and distribution (PLDS) codes are appropriate for this crop.
            - Whether planting depth (PLDP) is realistic for the seed size and soil context.
            - Whether row direction (PLRD) is acceptable; otherwise recommend a typical value or -99 if unknown.

            Output format (STRICT JSON ONLY, no markdown, no extra text):

            {'''{
        "parameter": "planting",
        "score": <integer 1–5>,
        "pass": <true or false>,
        "planting": {
            "PDATE": {
            "original_value": <original value or null>,
            "issue": <string or null>,
            "suggested_value": <new value or null>,
            "suggested_reasoning": <string or null>
            },
            /* Replicate this same structure for any additional planting-related fields:
            "FIELD_NAME": {
                "original_value": <original value or null>,
                "issue": <string or null>,
                "suggested_value": <new value or null>,
                "suggested_reasoning": <string or null>
            }
            */
        }
        }
'''}

            Guidelines:
            - If a parameter is acceptable, set it to null inside suggested_fix.
            - If a parameter is clearly unrealistic, propose a specific corrected value.
            - "pass" should be true only if all parameters are within realistic agronomic ranges.
            - Use the reasoning array to show your chain-of-thought in human-readable steps.
""".strip()

        raw = judge_llm.invoke(judge_prompt)
        clean = strip_markdown_fences(raw)

        try:
            feedback = json.loads(clean)
        except Exception as e:
            state.setdefault("errors", []).append(
                f"JudgePlantingAgent: Failed to parse judge output. Error: {e}, raw: {raw}"
            )
            ui_event(state, agent=agent_name, kind="error", message=f"Judge JSON parse failed: {e}")
            raise

        state["planting_judge_feedback"] = feedback
        state["planting_judge_attempts"] = state.get("planting_judge_attempts", 0) + 1

        ui_event(
            state,
            agent=agent_name,
            kind="judge",
            message=f"Judge evaluated pass={feedback.get('pass')} score={feedback.get('score')}",
            data={"issues": feedback.get("issues", []), "summary": feedback.get("summary")},
        )

        return state

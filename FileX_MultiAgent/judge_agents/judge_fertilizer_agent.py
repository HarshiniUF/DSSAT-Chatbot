from __future__ import annotations

import json
from typing import Any, Dict, List

from utils.llm import get_judge_llm
from utils.helpers import strip_markdown_fences
from utils.ui_logger import ui_event, ui_log


class JudgeFertilizerAgent:
    """
    LLM Judge for the FertilizerAgent.

    Reads fertilizer_config from state.
    Returns a minimal PATCH in suggested_fix.events.
    """

    @staticmethod
    def process(state: Dict[str, Any]) -> Dict[str, Any]:
        agent_name = "JudgeFertilizerAgent"
        ui_event(state, agent=agent_name, kind="judge", message="JudgeFertilizerAgent started")

        fert_config: List[Dict[str, Any]] = state.get("fertilizer_config", []) or []
        if not fert_config:
            ui_event(state, agent=agent_name, kind="error", message="fertilizer_config is empty")
            raise RuntimeError("fertilizer_config is empty")

        crop_code = state.get("crop_code")
        crop_name = state.get("crop_name_text")
        cultivar_name = state.get("cultivar_name")
        location = state.get("location_text")
        xcrd = state.get("xcrd")
        ycrd = state.get("ycrd")
        pdate = state.get("pdate")

        judge_prompt = f"""
You are an expert agronomist and DSSAT crop modeling specialist.
You are acting as a strict but helpful JUDGE for a proposed DSSAT inorganic fertilizer program.

Your task:
1. Carefully evaluate whether the given fertilizer applications are agronomically realistic for the crop, location, and planting date.
2. Use step-by-step agronomic reasoning (chain-of-thought) to justify your judgment.
3. Provide a clear decision: pass (acceptable) or fail (unrealistic / needs correction).
4. If it fails, provide concrete suggested corrections at the event level.

Context:
- CROP CODE: {crop_code}
- CROP NAME: {crop_name}
- CULTIVAR NAME: {cultivar_name}
- LOCATION: {location}
- LATITUDE: {xcrd}
- LONGITUDE: {ycrd}
- PLANTING DATE (PDATE): {pdate}

Proposed fertilizer configuration (DSSAT-style events array):
{json.dumps(fert_config, indent=2)}

Each event has (derived from DSSAT FertilizerEvent fields):
- FDATE: calendar date (YYYY-MM-DD)
- FMCD: fertilizer material code (e.g., FE005, FE027, FE900)
- FACD: application method code (e.g., AP001, AP004)
- FDEP: depth (cm)
- FAMN: kg N/ha
- FAMP: kg P/ha (or P2O5 equivalent)
- FAMK: kg K/ha (or K2O equivalent)

You MUST reason explicitly about:
- Is the total seasonal N, P, K supplied by fertilizer reasonable for this crop and region?
- Are timing and splitting (at planting vs. topdressing) realistic for this crop and expected yield levels?
- Are individual event rates plausible (no extreme overdoses or unrealistically low values)?
- Are FMCD and FACD codes appropriate for the supposed fertilizer type and method?
- Are FDEP values consistent with method (e.g., broadcast at 0 cm, banded/incorporated 5–10 cm)?
- Are dates (FDATE) consistent with planting date, crop growth stages, and local climate?

Important: you are checking agronomic realism, not model syntax.

Output format (STRICT JSON ONLY, no markdown, no extra text):

{'''{
  "parameter": "fertilizer",
  "score": <integer 1–5>,
  "pass": <true or false>,
  "events": [
    {
      "index": <0-based index of the event in the original list>,

      "FDATE": {
        "original_value": <original value or null>,
        "issue": <string or null>,
        "suggested_value": <new value or null>,
        "suggested_reasoning": <string or null>
      },

      "FMCD": {
        "original_value": <original value or null>,
        "issue": <string or null>,
        "suggested_value": <new value or null>,
        "suggested_reasoning": <string or null>
      },

      "FACD": {
        "original_value": <original value or null>,
        "issue": <string or null>,
        "suggested_value": <new value or null>,
        "suggested_reasoning": <string or null>
      },

      "FDEP": {
        "original_value": <original value or null>,
        "issue": <string or null>,
        "suggested_value": <new value or null>,
        "suggested_reasoning": <string or null>
      },

      "FAMN": {
        "original_value": <original value or null>,
        "issue": <string or null>,
        "suggested_value": <new value or null>,
        "suggested_reasoning": <string or null>
      },

      "FAMP": {
        "original_value": <original value or null>,
        "issue": <string or null>,
        "suggested_value": <new value or null>,
        "suggested_reasoning": <string or null>
      },

      "FAMK": {
        "original_value": <original value or null>,
        "issue": <string or null>,
        "suggested_value": <new value or null>,
        "suggested_reasoning": <string or null>
      }
         {
           "COLUMN_NAME": {
             "original_value": <original value or null>,
             "issue": <string or null>,
             "suggested_value": <new value or null>,
             "suggested_reasoning": <string or null>
           }
         }
      
    }
  ]
}'''}

Guidelines:
- "pass" should be true only if all parameters are within realistic agronomic ranges for typical management in that region.
- "score" should be 4–5 only for clearly realistic and internally consistent programs.
- In "suggested_fix.events", only specify events that need adjustment. Use null for fields that are acceptable.
- If everything is acceptable, set "pass": true, and "suggested_fix.events": [].
""".strip()

        judge_model = state.get("judge_model", "gpt-5")
        judge_llm = get_judge_llm(model=judge_model)

        ui_log(state, agent_name, f"Judging fertilizer_config with model={judge_model}")

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

        state["fertilizer_judge_feedback"] = feedback
        state["fertilizer_judge_attempts"] = state.get("fertilizer_judge_attempts", 0) + 1

        state.setdefault("messages", []).append(
            f"{agent_name}: pass={feedback.get('pass')} score={feedback.get('score')} issues={feedback.get('issues')}"
        )

        ui_event(
            state,
            agent=agent_name,
            kind="judge",
            message="JudgeFertilizerAgent finished",
            data={"pass": bool(feedback.get("pass")), "score": feedback.get("score")},
        )
        return state

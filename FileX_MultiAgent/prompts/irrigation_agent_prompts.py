import json

def base_irrigation_agent_prompts(
    crop_code, crop_name, cultivar_name, location, xcrd, ycrd, pdate,
    irrigation_irop_codes, irrigation_config, irrigation_judge_feedback
):
    print("irr agent",irrigation_irop_codes)
    prompt = f"""
You are an agronomist and DSSAT crop modeling specialist.

TASK
Generate a DSSAT-ready irrigation configuration (rainfed or irrigated) for the given crop + location + planting date.
Return STRICT JSON ONLY (no markdown fences, no extra text, no comments).

========================
HARD RULES (MUST FOLLOW)
========================
1) strategy must be EXACTLY one of: "rainfed" or "irrigated"

2) header_row is FIXED and must be EXACTLY:
   EFIR=-99, IDEP=-99, ITHR=-99, IEPT=-99, IOFF=null, IAME=null, IAMT=-99, IRNAME=-99
   Do NOT invent header values. Always output exactly those fixed values.

3) If strategy == "rainfed": irrigation_events MUST be [] (empty)
   If strategy == "irrigated": irrigation_events MUST have >= 1 event

4) Each irrigation event MUST include ALL required keys:
   IDATE, IROP, IRVAL, EFIR, Assumptions_or_Notes

5) IDATE format MUST be "YYYY-MM-DD" and MUST be AFTER planting date (PDATE).
   Events must be in chronological order (non-decreasing by date).

6) IROP MUST be one of the KEYS in the provided IROP CODES dictionary (example: "IR004").
   - IMPORTANT: Output the code KEY only (e.g., "IR004"), NOT the description text.
   - If there is no perfect/explicit match for your intended method in the dictionary descriptions,
     choose the NEAREST / CLOSEST BEST-FIT key based on the descriptions available.
   - Use your best judgment for the closest method (furrow vs flood vs sprinkler vs drip).
   - Avoid rice-only flooding operations unless crop/system strongly implies rice/paddy.

7) IRVAL is irrigation depth in mm (numeric). EFIR is efficiency 0–1 (numeric).
8) Use concrete values only (no ranges like "30–50").

========================
FIELD DEFINITIONS (BRIEF + UNITS)
========================
- IDATE (YYYY-MM-DD): irrigation application date (must be after PDATE)
- IROP (CODE KEY like "IR004"): irrigation method code from the provided dictionary keys
- IRVAL (mm): depth of water applied on that date
- EFIR (0–1): event irrigation efficiency (choose plausible value for that method)
- Assumptions_or_Notes: 1–2 sentences documenting assumptions (water access, typical practice, why rainfed/irrigated)

==================================
REASONABLE GUARDRAILS (FLEXIBLE, NOT ABSOLUTE)
==================================
Use these as guidance, but you may deviate slightly if you justify it in Assumptions_or_Notes:
- IRVAL typical: 5–80 mm; avoid extremes unless justified
- EFIR typical: 0.3–0.95 (must always stay between 0 and 1)
- If irrigated: usually 1–20 events; avoid unrealistic daily schedules unless strongly justified (e.g., drip in arid region)

========================
PATCH / ITERATION RULE (IMPORTANT)
========================
You may receive judge feedback from a prior attempt.
Treat judge feedback as authoritative PATCH instructions:
- Apply any concrete corrections in suggested_fix.
- Keep existing config values that the judge did NOT flag.
- Only change what needs to change to become plausible and internally consistent.

========================
INPUT CONTEXT
========================
CROP CODE: {crop_code}
CROP NAME: {crop_name}
CULTIVAR NAME: {cultivar_name}
LOCATION: {location}
LATITUDE: {xcrd}
LONGITUDE: {ycrd}
PLANTING DATE (PDATE): {pdate}

EXISTING CONFIGURATION (may be empty):
{json.dumps(irrigation_config, indent=2)}

JUDGE FEEDBACK (may be empty):
{json.dumps(irrigation_judge_feedback, indent=2)}

IROP CODES DICTIONARY (valid IROP values are ONLY the KEYS of this dict):
{json.dumps(irrigation_irop_codes, indent=2)}

Helpful matching hint (if no exact match exists, choose the nearest best-fit key):
- Furrow / surface row irrigation → IR001 (or IR002 alternating furrows)
- Flood → IR003
- Sprinkler → IR004
- Drip/trickle → IR005
- Rice/paddy flooding only → IR006 / IR010 / IR011 (use only if crop/system strongly implies rice/paddy)

========================
OUTPUT JSON (STRICT)
========================
Return exactly this structure (keys must match exactly):

{{
  "narrative": "3–6 sentences. State rainfed vs irrigated and why plausible for this crop + location + planting date. If irrigated, mention number of events, method choice (in words), typical IRVAL, and key assumptions.",
  "irrigation_section": {{
    "strategy": "rainfed|irrigated",
    "header_row": {{
      "EFIR": -99,
      "IDEP": -99,
      "ITHR": -99,
      "IEPT": -99,
      "IOFF": null,
      "IAME": null,
      "IAMT": -99,
      "IRNAME": -99
    }},
    "irrigation_events": [
      {{
        "IDATE": "YYYY-MM-DD",
        "IROP": "IR004",
        "IRVAL": 25,
        "EFIR": 0.7,
        "Assumptions_or_Notes": "Short justification/assumption."
      }}
    ]
  }}
}}

Special rule for rainfed:
- strategy="rainfed"
- irrigation_events=[] (empty)

Return ONLY the JSON object. No markdown. No extra keys.
""".strip()

    return prompt

import json


def base_prompt_fertilizer_agent(
    crop_name,
    location,
    pdate,
    fertilizer_config,
    fertilizer_judge_feedback,
    fertilizer_fmcd_codes,
    fertilizer_facd_codes,
    target_n_rate_kg_ha=None,
):
    """
    Generate a prompt for inferring a representative farmer-practice inorganic
    fertilizer management strategy and translating it into DSSAT-ready events.
    """

    existing_config_json = json.dumps(
        fertilizer_config if fertilizer_config is not None else [],
        indent=2,
        default=str,
    )

    judge_feedback_json = json.dumps(
        fertilizer_judge_feedback if fertilizer_judge_feedback is not None else None,
        indent=2,
        default=str,
    )

    target_rate_block = ""
    if target_n_rate_kg_ha is not None:
        target_rate_block = f"""
---

## REQUIRED TOTAL NITROGEN RATE (OVERRIDES REPRESENTATIVE-PRACTICE RATE)

A specific scenario has been requested for this run. The sum of FAMN across all
fertilizer events MUST equal EXACTLY {target_n_rate_kg_ha} kg N/ha -- not
approximately, not rounded to a "nicer" product-rate number. This value is
being compared against other treatments with different exact targets in the
same experiment, so even a small rounding difference (e.g. rounding 87.5 to 88)
would corrupt that comparison. If the product/rate combination you would
otherwise choose does not add up exactly, adjust the rate (or split the amount
across events) so the FAMN values sum to precisely {target_n_rate_kg_ha}, down
to at least one decimal place.

This target takes priority over the "representative farmer practice" rate
inference in the rest of this prompt. Still use representative-practice
judgment for product selection, number of events, timing, and application
method/depth — only the TOTAL nitrogen amount is fixed by this requirement.
"""

    prompt = f"""
You are an agronomist and DSSAT crop-model expert.

Your task is to reconstruct a realistic, representative inorganic fertilizer
management strategy for a specified crop, location, and planting date. Then,
translate that strategy into fertilizer application events usable in the DSSAT
*FERTILIZERS (INORGANIC) section.

The central objective is to infer what farmers commonly do in actual field
conditions in that crop-location system.

Infer the dominant or most representative farmer-practice regime:
- common fertilizer products,
- typical total seasonal nutrient rates,
- usual number of applications,
- common timing relative to planting,
- common application methods,
- realistic depth or placement.

The result should represent the prevailing management strategy that is common among the average
farmers in the dominant local production system, not the maximum-input,
research-station, or best-management-practice recommendation.

For example:
- Corn in Iowa, USA should reflect common Iowa maize fertilizer practices,
  including the locally prevalent fertilizer sources, timing, placement, and
  rate structure used by conventional maize farmers.
- Maize in Trans Nzoia, Kenya should reflect the fertilizer materials, rates,
  timing, and methods commonly used by maize farmers in Trans Nzoia, rather
  than a fertilizer package designed to achieve a theoretical high yield.

---

## INPUTS

CROP: {crop_name}

LOCATION: {location}

PLANTING DATE: {pdate}

EXISTING CONFIGURATION:
{existing_config_json}

FERTILIZER AGENT JUDGE FEEDBACK:
{judge_feedback_json}

FMCD FERTILIZER MATERIAL CODES:
{fertilizer_fmcd_codes}

FACD APPLICATION METHOD CODES:
{fertilizer_facd_codes}
{target_rate_block}
---

## PRIMARY INFERENCE PRINCIPLE

Infer a representative farmer-practice strategy, conditional on:

1. Crop
   - Whether it is a cereal, legume, root crop, vegetable, perennial, or another
     crop type.
   - Whether biological nitrogen fixation materially reduces inorganic N use.

2. Location
   - The specific state, district, county, region, or production zone.
   - The most common crop-production system in that location.

3. Dominant farmer type
   - Infer the most prevalent production stratum for that crop and location:
     for example, commercial mechanized rainfed maize, irrigated intensive
     vegetable production, or low-input rainfed smallholder farming.
   - Do not combine incompatible production systems into an artificial average.
   - If fertilizer practices are multimodal, select the dominant practical mode,
     not the arithmetic average of contrasting high-input and low-input systems.

4. Planting date
   - Treat the supplied planting date as authoritative.
   - Use it to calculate calendar dates and DAP for fertilizer events.
   - Do not replace it with a newly invented representative planting date.

---

## EVIDENCE HIERARCHY FOR INFERRING PRACTICE

Use the following hierarchy when deciding what is representative:

1. Direct evidence of actual farmer behavior in the specified location:
   farmer surveys, farm records, adoption studies, crop budgets, local reports,
   or documented fertilizer-use data.

2. Regional evidence describing common farmer practice:
   regional agronomic studies, farmer-management
   surveys, input-use assessments, or production-system studies.

3. Evidence from the surrounding production zone:
   comparable districts, counties, agroecological zones, or major crop belts.

4. National evidence for the same crop and similar production system.

5. General agronomic knowledge only when local evidence is unavailable.

Do not invent survey findings, adoption percentages, or precise local statistics.
When evidence is weak, still provide one complete scenario, but explicitly state
that it is an approximate representative practice in the narrative and notes.

---

## ROLE OF YIELD, SOIL FERTILITY, AND RECOMMENDATIONS

Yield potential, nutrient removal, soil fertility, and extension recommendations
may be used only as plausibility checks.

They may help reject clearly unrealistic outputs, such as:
- zero fertilizer in a region where commercial production commonly uses inputs,
- fertilizer rates far above what farmers can realistically finance or apply,
- nutrient rates inconsistent with the crop or local production system.

However, they must NOT be used as the primary method for calculating fertilizer
rates. Do not reverse-engineer fertilizer use from a target yield.

The goal is to represent observed or likely farmer behavior under real
constraints, including:
- input prices,
- scale of production,
- credit access,
- rainfall risk,
- labor availability,
- machinery access,
- local fertilizer availability,
- perceived production risk,
- customary management practice,
- and incomplete adoption of recommendations.

---

## EXISTING CONFIGURATION AND JUDGE FEEDBACK

Use the following priority order:

1. Concrete corrections in FERTILIZER AGENT JUDGE FEEDBACK.
2. Representative farmer-practice inference for the crop-location system.
3. Existing configuration values, but only when they are consistent with the
   representative practice.

The existing configuration is a prior draft, not an authority. Preserve valid
entries when they fit the inferred local farmer practice. Modify or replace
entries that appear to reflect:
- an unrealistic yield-target prescription,
- an uncommon fertilizer product,
- implausible rate,
- inappropriate timing,
- inappropriate application method,
- or a production system that does not match the location.

If judge feedback is null, empty, or absent, treat this as the first generation.

---

## HOW TO CONSTRUCT THE MANAGEMENT STRATEGY

### Step 1 — Identify the dominant local production system

Infer and state internally:

- rainfed or irrigated system;
- dominant farm scale and degree of mechanization;
- typical input intensity: low, moderate, or high;
- major fertilizer products locally available and commonly used;
- whether fertilizer is normally applied once, split, banded, broadcast,
  incorporated, side-dressed, topdressed, injected, or spot applied.

The final scenario must correspond to one coherent production system.

### Step 2 — Infer the representative fertilizer practice

Determine the most common practical fertilizer strategy for average farmers in
that system:

- which fertilizer sources are most commonly used;
- whether farmers usually apply N only, N plus P, N-P-K blends, or separate
  nutrient sources;
- whether P and K are commonly applied at planting;
- whether N is commonly split;
- whether farmers use lower-than-recommended rates because of cost, risk,
  liquidity, or limited access;
- whether fertilizer is commonly omitted for one or more nutrients.

Do not add a nutrient simply because it is agronomically desirable. Include it
only when it is plausibly part of the representative local fertilizer practice.

### Step 3 — Select products and calculate nutrient amounts

Use fertilizer products that are common or plausibly available in the location.

Examples of possible materials include:
- Urea,
- UAN,
- anhydrous ammonia,
- ammonium nitrate,
- calcium ammonium nitrate,
- DAP,
- MAP,
- TSP,
- MOP/KCl,
- balanced NPK compounds,
- locally common blended fertilizers.

For each event, calculate nutrient amounts from the chosen product grade and
application rate.

Use the following nutrient convention in the JSON output:

- FAMN = kg N/ha
- FAMP = kg elemental P/ha
- FAMK = kg elemental K/ha

For fertilizer grades expressed as N-P2O5-K2O:

- N_kg_ha = product_rate_kg_ha × N_fraction
- P_kg_ha = product_rate_kg_ha × P2O5_fraction × 0.4364
- K_kg_ha = product_rate_kg_ha × K2O_fraction × 0.8301

Document the fertilizer grade and conversion basis in Assumptions_or_Notes.

### Step 4 — Determine application timing

Use the supplied planting date to generate all fertilizer application dates.

Possible events include only those that are genuinely justified by local farmer
practice:

- pre-plant applications,
- at-planting basal applications,
- early topdress,
- side-dress,
- later topdress.

Do not create additional applications merely to make the strategy look more
detailed. A single application is valid when it reflects common local practice.
Multiple applications are valid only when split application is locally common or
agronomically and operationally plausible for the production system.

For each event:
- provide a calendar date in YYYY-MM-DD format;
- provide an integer DAP;
- order events from earliest to latest;
- allow negative DAP only when a pre-plant application is genuinely common.

### Step 5 — Select methods and placement

Select application method and depth consistent with the local farmer practice:

- surface broadcast: generally FDEP = 0 cm;
- broadcast and incorporated: generally FDEP = 5–10 cm;
- banded or placed near the seed: generally FDEP = 3–8 cm;
- side-dressed or injected N: use a plausible subsurface depth;
- spot application: use a realistic shallow placement depth.

Do not assign a high-precision placement method when the dominant farmer system
would normally use simple broadcast or hand-applied fertilizer.

### Step 6 — Select DSSAT codes

For FMCD:
- use only an exact valid fertilizer material code from the supplied FMCD list;
- do not invent fertilizer codes;
- when a balanced NPK or locally blended fertilizer has no exact code, use:
  FE900 — Generic fertilizer.

For FACD:
- use only an exact valid application method code from the supplied FACD list;
- select the closest valid code;
- do not invent application-method codes.

Include the human-readable fertilizer product, grade, and application method in
Assumptions_or_Notes.

---

## INTERNAL CONSISTENCY CHECKS

Before generating the final JSON, check that:

1. The selected fertilizer sources are plausible for the specified location.
2. The total nutrient rates represent farmer practice rather than an idealized
   recommendation.
3. Timing is compatible with the supplied planting date and crop growth stages.
4. The number of events matches the dominant local management pattern.
5. P and K are generally placed at or near planting unless local practice
   strongly indicates otherwise.
6. N splitting is used only when it is common or practical in that system.
7. Fertilizer product grade, product rate, and reported N-P-K nutrient amounts
   are mathematically consistent.
8. Application method, depth, and fertilizer source are compatible.
9. No event exists solely to increase apparent detail.
10. The final strategy represents one coherent farmer-management regime.

---

## OUTPUT REQUIREMENTS

Return exactly one valid JSON object and nothing else.

Do not include:
- markdown,
- code fences,
- explanatory text outside the JSON,
- comments,
- trailing commas,
- invalid JSON syntax.

The JSON object must have exactly this top-level structure:

{{
  "narrative": "Concise description of the representative farmer-practice fertilizer strategy. State the inferred dominant production system, why it is representative for this crop-location pair, the degree of confidence, the number of fertilizer applications, and the broad rationale for product choice, timing, and method.",
  "fertilizer_section": [
    {{
      "FDATE": "YYYY-MM-DD, DAP integer",
      "FMCD": "valid fertilizer material code",
      "FACD": "valid fertilizer application method code",
      "FDEP": 0.0,
      "FAMN": 0.0,
      "FAMP": 0.0,
      "FAMK": 0.0,
      "Assumptions_or_Notes": "Human-readable fertilizer product, nutrient grade, product-rate logic, application method, local-practice rationale, and uncertainty note."
    }}
  ]
}}

Rules for the final JSON:

- fertilizer_section must contain one object per fertilizer application event.
- Keep events in chronological order.
- FDATE must include both calendar date and DAP, separated by a comma.
- FMCD and FACD must contain valid supplied DSSAT codes, not product or method names.
- FDEP, FAMN, FAMP, and FAMK must be numeric values, not strings.
- Use zero only when that nutrient is absent from that specific application.
- Do not provide ranges. Select one representative numerical value.
- Assumptions_or_Notes is mandatory for every event.
- The narrative must clearly state that the output represents a representative
  farmer-practice approximation, not an optimized yield-target recommendation.
- Do not claim certainty when local evidence is limited.
- Ensure the JSON can be parsed directly by Python json.loads().

Now generate the final JSON for:

CROP: {crop_name}
LOCATION: {location}
PLANTING DATE: {pdate}
"""

    return prompt

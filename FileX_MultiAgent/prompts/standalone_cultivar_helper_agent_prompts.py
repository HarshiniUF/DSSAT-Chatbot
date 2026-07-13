# """
# Prompts for StandaloneCultivarHelperAgent v2.

# Modified for zone-based cultivar discovery with enhanced characteristics.
# Key changes from v1:
# - Removed fixed cultivar count constraints
# - Added major_crop_areas field
# - Enhanced planting/harvest/density fields
# - Added zone suitability checks
# """

# import json


# def generate_cultivar_list_prompt(
#     crop_name, crop_code, zone_name, country):
#     """
#     Step 1: Generate list of suitable cultivars for given zone and crop.
#     v2: Removed fixed count constraint, allows zero cultivars if zone unsuitable.
#     """
#     prompt = f"""
# You are an agronomist with expertise in crop variety selection and regional adaptation.

# **Task**: Identify suitable crop cultivars/varieties for the specified growing environment.

# **Input Parameters**:
# - Crop: {crop_name} (DSSAT code: {crop_code})
# - Country: {country}
# - Agro-Ecological Zone: {zone_name}

# **Your Task**:
# 1. **First, assess zone suitability**:
#    - Determine if {crop_name} is commonly grown in the "{zone_name}" agro-ecological zone
#    - Consider climate, rainfall patterns, temperature, and traditional farming practices
#    - If {crop_name} is NOT suitable or NOT commonly grown in this zone, return an empty array: []

# 2. **If the zone IS suitable**, identify all cultivars/varieties that are:
#    - Regionally adapted to this zone
#    - Suitable for the typical planting season in this zone
#    - Commonly grown or recommended by agricultural extension services
#    - Diverse in maturity classes (early, medium, late season)
#    - Include both modern hybrids and traditional/local varieties if relevant

# 3. **Return ONLY a JSON array** of cultivar names, no explanations:

# [
#   "Cultivar Name 1",
#   "Cultivar Name 2",
#   "Cultivar Name 3"
# ]

# **Important Guidelines**:
# - Do NOT force a fixed number of cultivars - return as many or as few as are actually suitable
# - If the zone is unsuitable for {crop_name}, return: []
# - If only 1-2 cultivars are commonly grown, return only those
# - If 10+ cultivars are suitable, include all of them
# - Use official cultivar names when possible
# - Prioritize varieties with published research or extension documentation

# **Examples of unsuitable zones**:
# - Tropical alpine zones for lowland crops
# - Arid grasslands for water-intensive crops
# - High-altitude zones for heat-loving crops

# **Output Format**:
# Return only the JSON array, no markdown fences or extra text.
# """
#     return prompt


# def extract_characteristics_prompt(crop_name, cultivar_name, zone_name, country):
#     """
#     Extract cultivar agronomic characteristics using LLM knowledge.
#     v2: Added major_crop_areas and enhanced field descriptions.
#     """
#     prompt = f"""
# You are an agronomist specializing in crop variety characteristics.

# **Task**: Provide comprehensive agronomic characteristics for the given cultivar.

# **Cultivar Information**:
# - Crop: {crop_name}
# - Cultivar/Variety: {cultivar_name}
# - Country: {country}
# - Agro-Ecological Zone: {zone_name}

# Use your knowledge as an agronomist specialist to provide accurate, detailed information.

# **Required Information**:

# 1. **Maturity Class**: Early, Medium, Late season (or specific relative maturity rating)

# 2. **Days to Maturity**: Approximate number of days from planting to harvest (integer or range like "110-120")

# 3. **Yield Potential**: Average yield in kg/ha (integer or range)

# 4. **Growth Characteristics**: 
#    - Plant height in cm (integer or range)
#    - Growth habit description (e.g., "erect", "semi-compact", "spreading")
#    - Disease resistance traits (list specific diseases)

# 5. **Stress Tolerance**:
#    - Drought tolerance: low|moderate|high
#    - Heat tolerance: low|moderate|high

# 6. **Growing Degree Days (GDD)**: Total thermal time from planting to physiological maturity
#    - Express as "3200 GDD" or "3200 heat units" or similar
#    - Use "unknown" if GDD/thermal time/heat units data is not available

# 7. **Agro-Ecological Zone Adaptation**: Zone or region where this cultivar is best adapted
#    - Examples: "Highlands", "Mid-altitude tropics", "Lowland tropics", "Semi-arid"
#    - Use "unknown" if cannot be inferred

# 8. **Normal Planting Window**: Typical planting period for this cultivar
#    - Can be date range (e.g., "March–April"), season description (e.g., "early planting", "normal planting"), or both
#    - Use "unknown" if not known

# 9. **Planting Density**: Recommended plant population or seeding rate
#    - Express as "plants/ha", "seeds per meter", or "plants per row spacing"
#    - Examples: "55,000–65,000 plants/ha" or "5–6 plants/m in 0.75 m rows"
#    - Use "unknown" if not known

# 10. **Harvest Time**: Normal harvest period for this cultivar
#     - Can be months (e.g., "August–September"), days after planting (e.g., "110–130 days after planting"), or seasonal description
#     - Use "unknown" if not known

# 11. **Season Suitability**: Season type(s) for which this cultivar is recommended
#     - Use "main season", "short season", "both (main season and short season)", or "unknown"

# 12. **Major Crop Areas**: **NEW FIELD** - Specific districts, counties, or location names within the {zone_name} agro-ecological zone where {crop_name} (specifically this cultivar if known, or generally) is widely grown
#     - Provide a descriptive string listing the major cultivation areas
#     - Examples: "Kilifi, Kwale and parts of Taita Taveta counties", "Trans-Nzoia, Uasin Gishu, and Nakuru counties"
#     - If specific location names are not available, use "unknown"

# 13. **Adaptation Notes**: Regional suitability and recommended growing conditions

# **Instructions**:
# - If source is a typical URL link, no need to display the URL unless it is specific and valid
# - Do NOT give generic URLs - skip URL and keep source as "GPT-4o" or model name
# - source_url should be null unless you have a specific, verifiable URL

# **Output Format**:
# Return JSON in this exact structure:

# {{
#   "cultivar_name": "{cultivar_name}",
#   "characteristics": {{
#     "maturity_class": "early|medium|late",
#     "relative_maturity": "value if applicable (e.g., 110 days, RM 3.5)",
#     "days_to_maturity": "integer or range",
#     "average_yield_kg_ha": "integer or range",
#     "plant_height_cm": "integer or range",
#     "growth_habit": "description",
#     "disease_resistance": ["list of resistances"],
#     "stress_tolerance": {{
#       "drought": "low|moderate|high",
#       "heat": "low|moderate|high"
#     }},
#     "growing_degree_days": "Total heat units required from planting to physiological maturity (e.g., '3200 GDD'). Use 'unknown' if not available.",
#     "agro_ecological_zone": "Zone or region where cultivar is best adapted (e.g., 'Highlands', 'Mid-altitude tropics'). Use 'unknown' if cannot be inferred.",
#     "adaptation_notes": "Regional suitability and recommended growing conditions",
#     "normal_planting_window": "Typical planting window or recommended planting period (e.g., 'March–April', 'early planting'). Use 'unknown' if not known.",
#     "planting_density": "Recommended plant population or seeding rate (e.g., '55,000–65,000 plants/ha', '5–6 plants/m in 0.75 m rows'). Use 'unknown' if not known.",
#     "harvest_time": "Normal harvest period (e.g., 'August–September', '110–130 days after planting'). Use 'unknown' if not known.",
#     "season_suitability": "Season type(s) recommended (e.g., 'main season', 'short season', 'both (main season and short season)'). Use 'unknown' if cannot be determined.",
#     "major_crop_areas": "Specific districts, counties, or location names within the {zone_name} zone where {crop_name} is widely grown. Provide descriptive string with location names. Use 'unknown' if not available."
#   }},
#   "source": "Source of information (extension service, seed company, trial report, or model name)",
#   "source_url": null,
#   "confidence": "high|medium|low - based on source reliability"
# }}

# **Requirements**:
# - Return only JSON, no markdown fences
# - Use "unknown" for fields where information is not available
# - Prioritize official sources (extension services, government agencies)
# - Include source to verify information
# - For major_crop_areas, be as specific as possible with location names
# """
#     return prompt


# def parse_cul_file_coefficients_prompt(crop_code, cultivar_name, cul_file_content):
#     """
#     Parse specific cultivar coefficients from .CUL file content using LLM.
#     No changes from v1 - this doesn't use location/zone information.
#     """
#     prompt = f"""
# You are a DSSAT file parser expert.

# **Task**: Extract genotypic coefficients for a specific cultivar from a .CUL file.

# **Input**:
# - Crop Code: {crop_code}
# - Cultivar Name: {cultivar_name}
# - File Content Below:

# {cul_file_content}

# **Instructions**:
# 1. Search for the cultivar name "{cultivar_name}" in the file (case-insensitive, partial match OK)
# 2. Extract the full line containing this cultivar
# 3. Parse all coefficient values according to the file's column structure
# 4. The file header shows column positions and coefficient names

# **Output Format**:
# If found, return JSON:
# {{
#   "found": true,
#   "cultivar_name": "exact name from file",
#   "ingeno": "genotype code",
#   "coefficients": {{
#     "COEFFICIENT_NAME": value,
#     ...
#   }},
#   "source": "Local .CUL file: {crop_code}.CUL",
#   "source_type": "local"
# }}

# If NOT found, return:
# {{
#   "found": false,
#   "cultivar_name": "{cultivar_name}",
#   "reason": "Cultivar not found in .CUL file"
# }}

# **Requirements**:
# - Return only JSON, no markdown fences
# - Include ALL coefficients from the line
# - Preserve exact cultivar name from file
# - All coefficient values must be numeric
# """
#     return prompt


# def search_coefficients_in_research_prompt(
#     crop_name, crop_code, cultivar_name, zone_name, country
# ):
#     """
#     Search for genotypic coefficients in research papers using LLM.
#     This runs ONLY if coefficients are not found in local .CUL files.
#     No changes from v1.
#     """
#     prompt = f"""
# You are a DSSAT crop modeling expert with access to scientific literature.

# **Task**: Find published genotypic coefficients for a specific cultivar.

# **Cultivar Information**:
# - Crop: {crop_name} (DSSAT code: {crop_code})
# - Cultivar Name: {cultivar_name}
# - Country: {country}
# - Agro-Ecological Zone: {zone_name}

# **Search Strategy**:
# 1. Search for: "DSSAT {crop_name} {cultivar_name} genotypic coefficients"
# 2. Search for: "{cultivar_name} calibration DSSAT"
# 3. Search for: "{crop_name} cultivar parameters {zone_name} {country}"

# **Required Coefficients** (vary by crop model):
# For CERES models (Wheat, Maize, Rice, Sorghum, Millet):
# - P1: Juvenile phase coefficient (thermal time)
# - P2: Photoperiod sensitivity
# - P5: Grain filling duration
# - G1: Kernel number per unit weight
# - G2: Kernel filling rate (mg/day)
# - G3: Non-stressed mature tiller weight (g)
# - PHINT: Phyllochron interval (thermal time between leaf appearances)

# For CROPGRO models (Soybean, Peanut, Dry Bean):
# - CSDL: Critical short day length
# - PPSEN: Photoperiod sensitivity
# - EM-FL: Time between emergence and flower appearance
# - FL-SH: Time between first flower and first pod
# - FL-SD: Time between first flower and first seed
# - SD-PM: Time between first seed and physiological maturity
# - FL-LF: Time between first flower and end of leaf expansion
# - LFMAX: Maximum leaf photosynthesis rate
# - SLAVR: Specific leaf area
# - SIZLF: Maximum size of full leaf
# - XFRT: Maximum fraction of daily growth partitioned to seed and shell
# - WTPSD: Maximum weight per seed
# - SFDUR: Seed filling duration for pod cohort
# - SDPDV: Average seed per pod
# - PODUR: Time required for cultivar to reach final pod load

# **Output Format**:
# If coefficients are found, return JSON:
# {{
#   "found": true,
#   "cultivar_name": "{cultivar_name}",
#   "source": "Full citation of the paper (Authors, Year, Title, Journal)",
#   "source_url": "DOI or URL if available",
#   "coefficients": {{
#     "P1": value,
#     "P2": value,
#     "P5": value,
#     "G1": value,
#     "G2": value,
#     "G3": value,
#     "PHINT": value
#   }},
#   "notes": "Any relevant context about calibration method or validation"
# }}

# If NOT found, return:
# {{
#   "found": false,
#   "cultivar_name": "{cultivar_name}",
#   "search_attempted": ["list of search queries tried"],
#   "reason": "Brief explanation of why coefficients were not found"
# }}

# **Requirements**:
# - Return only JSON, no markdown fences
# - Ensure all coefficient values are numeric
# - Include full citation to prevent hallucination
# - If multiple sources exist, use the most recent or most cited
# """
#     return prompt


"""
Prompts for StandaloneCultivarHelperAgent v2.

Modified for zone-based cultivar discovery with enhanced characteristics.
Key changes from v1:
- Removed fixed cultivar count constraints
- Added major_crop_areas field
- Enhanced planting/harvest/density fields
- Added zone suitability checks
- Improved JSON formatting instructions to prevent syntax errors
"""

import json


def generate_cultivar_list_prompt(
    crop_name, crop_code, zone_name, country):
    """
    Step 1: Generate list of suitable cultivars for given zone and crop.
    v2: Removed fixed count constraint, allows zero cultivars if zone unsuitable.
    """
    prompt = f"""
You are an agronomist with expertise in crop variety selection and regional adaptation.

**Task**: Identify suitable crop cultivars/varieties for the specified growing environment.

**Input Parameters**:
- Crop: {crop_name} (DSSAT code: {crop_code})
- Country: {country}
- Agro-Ecological Zone: {zone_name}

**Your Task**:
1. **Assess zone suitability**:
   - Determine if {crop_name} can be grown in the "{zone_name}" agro-ecological zone.
   - Consider climate, rainfall patterns, temperature, soil type, and traditional farming practices.
   - If {crop_name} is NOT suitable for this zone at all (e.g., extreme climate mismatch or no historical evidence of cultivation), return an empty array: [].
   - If {crop_name} is marginally suitable (e.g., grown in some areas or under specific conditions), proceed to identify suitable cultivars that may perform well in this zone.

2. **If the zone IS suitable**, identify all cultivars/varieties that are:
   - Regionally adapted to this zone
   - Suitable for the typical planting season in this zone
   - Commonly grown or recommended by agricultural extension services
   - Diverse in maturity classes (early, medium, late season)
   - Include both modern hybrids and traditional/local varieties if relevant

3. **Return ONLY a JSON array** of cultivar names, no explanations:

[
  "Cultivar Name 1",
  "Cultivar Name 2",
  "Cultivar Name 3"
]

**Important Guidelines**:
- Do NOT force a fixed number of cultivars - return as many or as few as are actually suitable
- If the zone is unsuitable for {crop_name}, return: []
- If only 1-2 cultivars are commonly grown, return only those
- If 10+ cultivars are suitable, include all of them
- Use official cultivar names when possible
- Prioritize varieties with published research or extension documentation

**Output Format**:
Return only the JSON array, no markdown fences or extra text.
"""
    return prompt


def extract_characteristics_prompt(crop_name, cultivar_name, zone_name, country):
    """
    Extract cultivar agronomic characteristics using LLM knowledge.
    v2: Added major_crop_areas and enhanced field descriptions with strict JSON formatting.
    """
    prompt = f"""
You are an agronomist specializing in crop variety characteristics.

**Task**: Provide comprehensive agronomic characteristics for the given cultivar.

**Cultivar Information**:
- Crop: {crop_name}
- Cultivar/Variety: {cultivar_name}
- Country: {country}
- Agro-Ecological Zone: {zone_name}

Use your knowledge as an agronomist specialist to provide accurate, detailed information.

**Required Information**:

1. **Maturity Class**: Early, Medium, Late season (or specific relative maturity rating)

2. **Days to Maturity**: Approximate number of days from planting to harvest (integer or range like "110-120")

3. **Yield Potential**: Average yield in kg/ha (integer or range)

4. **Growth Characteristics**: 
   - Plant height in cm (integer or range)
   - Growth habit description (e.g., "erect", "semi-compact", "spreading")
   - Disease resistance traits (list specific diseases)

5. **Stress Tolerance**:
   - Drought tolerance: low|moderate|high
   - Heat tolerance: low|moderate|high

6. **Growing Degree Days (GDD)**: Total thermal time from planting to physiological maturity
   - Express as "3200 GDD" or "3200 heat units" or similar
   - Use "unknown" if GDD/thermal time/heat units data is not available

7. **Agro-Ecological Zone Adaptation**: A specific Zone or region where this cultivar is best adapted
   - Agro-ecological zone where this cultivar is suitable 
   - Use "unknown" if cannot be inferred

8. **Normal Planting Window**: Typical planting period for this cultivar
   - Can be date range (e.g., "March-April"), season description (e.g., "early planting", "normal planting"), or both
   - Use "unknown" if not known

9. **Planting Density**: Recommended plant population or seeding rate
   - Express as "plants/ha", "seeds per meter", or "plants per row spacing"
   - Examples: "55000-65000 plants/ha" or "5-6 plants/m in 0.75 m rows"
   - Use "unknown" if not known

10. **Harvest Time**: Normal harvest period for this cultivar
    - Can be months (e.g., "August-September"), days after planting (e.g., "110-130 days after planting"), or seasonal description
    - Use "unknown" if not known

11. **Season Suitability**: Season type(s) for which this cultivar is recommended
    - Use "main season", "short season", "both (main season and short season)", or "unknown"

12. **Major Crop Areas**: Specific districts, counties, or location names within the {zone_name} agro-ecological zone where {crop_name} (specifically this cultivar if known, or generally) is widely grown
    - Provide a descriptive string listing the major cultivation areas
    - Examples: "Kilifi, Kwale and parts of Taita Taveta counties", "Trans-Nzoia, Uasin Gishu, and Nakuru counties"
    - If specific location names are not available, use "unknown"

13. **Adaptation Notes**: Regional suitability and recommended growing conditions

**CRITICAL JSON FORMATTING RULES**:
- Use double quotes for ALL string values
- Do NOT use single quotes anywhere
- Escape any internal quotes with backslash: \\"
- Do NOT include trailing commas after the last item in arrays or objects
- All field names must be in double quotes
- Use "unknown" (not null) for missing data
- Arrays must use square brackets: []
- Objects must use curly braces: {{}}

**Instructions**:
- source: a one line summary of all the sources that contains the characteristics information
- source_url : display the specific URLs of the source from which you found these details, give in comma seperated if multiple

**Output Format**:
Return ONLY valid JSON in this exact structure (no markdown, no extra text):

{{
  "cultivar_name": "{cultivar_name}",
  "characteristics": {{
    "maturity_class": "early|medium|late",
    "relative_maturity": "value if applicable or unknown",
    "days_to_maturity": "integer or range",
    "average_yield_kg_ha": "integer or range",
    "plant_height_cm": "integer or range",
    "growth_habit": "description",
    "disease_resistance": ["resistance1", "resistance2"],
    "stress_tolerance": {{
      "drought": "low|moderate|high",
      "heat": "low|moderate|high"
    }},
    "growing_degree_days": "Total heat units or unknown",
    "agro_ecological_zone": "Zone description or unknown",
    "adaptation_notes": "Regional suitability description",
    "normal_planting_window": "Planting period or unknown",
    "planting_density": "Population rate or unknown",
    "harvest_time": "Harvest period or unknown",
    "season_suitability": "main season|short season|both (main season and short season)|unknown",
    "major_crop_areas": "Location names or unknown"
  }},
  "source": "Source of information",
  "source_url": list of Source URLs that you referred,
  "confidence": "high|medium|low"
}}

**IMPORTANT**: 
- Return ONLY the JSON object
- No markdown code fences (no ```json or ```)
- No explanatory text before or after
- Validate JSON syntax before responding
- Use "unknown" for any missing information
"""
    return prompt


def parse_cul_file_coefficients_prompt(crop_code, cultivar_name, cul_file_content):
    """
    Parse specific cultivar coefficients from .CUL file content using LLM.
    No changes from v1 - this doesn't use location/zone information.
    """
    prompt = f"""
You are a DSSAT file parser expert.

**Task**: Extract genotypic coefficients for a specific cultivar from a .CUL file.

**Input**:
- Crop Code: {crop_code}
- Cultivar Name: {cultivar_name}
- File Content Below:

{cul_file_content}

**Instructions**:
1. Search for the cultivar name "{cultivar_name}" in the file (case-insensitive, partial match OK)
2. Extract the full line containing this cultivar
3. Parse all coefficient values according to the file's column structure
4. The file header shows column positions and coefficient names

**Output Format**:
If found, return JSON:
{{
  "found": true,
  "cultivar_name": "exact name from file",
  "ingeno": "genotype code",
  "coefficients": {{
    "COEFFICIENT_NAME": value
  }},
  "source": "Local .CUL file: {crop_code}.CUL",
  "source_type": "local"
}}

If NOT found, return:
{{
  "found": false,
  "cultivar_name": "{cultivar_name}",
  "reason": "Cultivar not found in .CUL file"
}}

**Requirements**:
- Return only JSON, no markdown fences
- Include ALL coefficients from the line
- Preserve exact cultivar name from file
- All coefficient values must be numeric
"""
    return prompt


def search_coefficients_in_research_prompt(
    crop_name, crop_code, cultivar_name, zone_name, country
):
    """
    Search for genotypic coefficients in research papers using LLM.
    This runs ONLY if coefficients are not found in local .CUL files.
    No changes from v1.
    """
    prompt = f"""
You are a DSSAT crop modeling expert with access to scientific literature.

**Task**: Find published genotypic coefficients for a specific cultivar.

**Cultivar Information**:
- Crop: {crop_name} (DSSAT code: {crop_code})
- Cultivar Name: {cultivar_name}
- Country: {country}
- Agro-Ecological Zone: {zone_name}

**Search Strategy**:
1. Search for: "DSSAT {crop_name} {cultivar_name} genotypic coefficients"
2. Search for: "{cultivar_name} calibration DSSAT"
3. Search for: "{crop_name} cultivar parameters {zone_name} {country}"

**Required Coefficients** (vary by crop model):
For CERES models (Wheat, Maize, Rice, Sorghum, Millet):
- P1: Juvenile phase coefficient (thermal time)
- P2: Photoperiod sensitivity
- P5: Grain filling duration
- G1: Kernel number per unit weight
- G2: Kernel filling rate (mg/day)
- G3: Non-stressed mature tiller weight (g)
- PHINT: Phyllochron interval (thermal time between leaf appearances)

For CROPGRO models (Soybean, Peanut, Dry Bean):
- CSDL: Critical short day length
- PPSEN: Photoperiod sensitivity
- EM-FL: Time between emergence and flower appearance
- FL-SH: Time between first flower and first pod
- FL-SD: Time between first flower and first seed
- SD-PM: Time between first seed and physiological maturity
- FL-LF: Time between first flower and end of leaf expansion
- LFMAX: Maximum leaf photosynthesis rate
- SLAVR: Specific leaf area
- SIZLF: Maximum size of full leaf
- XFRT: Maximum fraction of daily growth partitioned to seed and shell
- WTPSD: Maximum weight per seed
- SFDUR: Seed filling duration for pod cohort
- SDPDV: Average seed per pod
- PODUR: Time required for cultivar to reach final pod load

**Output Format**:
If coefficients are found, return JSON:
{{
  "found": true,
  "cultivar_name": "{cultivar_name}",
  "source": "Full citation of the paper",
  "source_url": "DOI or URL if available",
  "coefficients": {{
    "P1": value,
    "P2": value
  }},
  "notes": "Context about calibration"
}}

If NOT found, return:
{{
  "found": false,
  "cultivar_name": "{cultivar_name}",
  "search_attempted": ["query1", "query2"],
  "reason": "Brief explanation"
}}

**Requirements**:
- Return only JSON, no markdown fences
- Ensure all coefficient values are numeric
- Include full citation to prevent hallucination
- If multiple sources exist, use the most recent or most cited
"""
    return prompt


# ============================================================================
# NEW PROMPTS FOR 4-STEP FALLBACK CHAIN (Steps 2 and 3)
# ============================================================================

def extract_coefficients_from_paper_prompt(crop_name, crop_code, cultivar_name, paper_text):
    """
    Step 2: LLM reads fetched paper text and extracts coefficient table.
    Called after WebSearch + WebFetch retrieves the actual paper content.
    """
    prompt = f"""
You are a DSSAT crop modeling expert reading a research paper.

**Task**: Find genotypic coefficients for cultivar "{cultivar_name}" in the paper text below.

**Crop**: {crop_name} (DSSAT code: {crop_code})

**Paper text (excerpt)**:
{paper_text[:5000]}

**Instructions**:
1. Look for a table or list containing coefficient values such as P1, P2, P5, G2, G3, PHINT (CERES crops) or equivalent parameters.
2. The cultivar name may appear as a partial match — use case-insensitive search.
3. If a coefficient table exists for ANY cultivar in the paper, check if "{cultivar_name}" appears in that table.
4. Do NOT invent or estimate values — only extract values explicitly shown in the paper text.

**If coefficients are found**, return JSON:
{{
  "found": true,
  "cultivar_name": "{cultivar_name}",
  "coefficients": {{
    "P1": value,
    "P2": value,
    "P5": value,
    "G2": value,
    "G3": value,
    "PHINT": value
  }},
  "notes": "brief description of where in the paper these values appear"
}}

**If NOT found**, return:
{{
  "found": false,
  "reason": "brief reason (e.g. cultivar not in table, no coefficient table present)"
}}

**Requirements**:
- Return only JSON, no markdown fences
- All coefficient values must be numeric
- Do not hallucinate values — only extract what is explicitly in the text
"""
    return prompt


def find_analog_cultivar_prompt(crop_name, crop_code, cultivar_name, characteristics, cul_content):
    """
    Step 3: LLM finds the best analog cultivar in .CUL file based on matching traits.
    Called when web search fails and no direct match exists in .CUL files.
    """
    data = characteristics.get("data", {}) if isinstance(characteristics, dict) else {}
    dtm = data.get("days_to_maturity", "unknown")
    maturity = data.get("maturity_class", "unknown")

    prompt = f"""
You are a DSSAT expert. The cultivar "{cultivar_name}" is not in this .CUL file,
but I need approximate genotypic coefficients for it.

**Target cultivar traits**:
- Crop: {crop_name} (code: {crop_code})
- Days to maturity: {dtm}
- Maturity class: {maturity}

**Your task**:
1. Read the .CUL file content below.
2. Find the cultivar whose characteristics (especially maturity / P1 value) most closely match the target traits above.
3. Extract that cultivar's coefficients as a proxy for "{cultivar_name}".
4. In P1 for CERES-Maize: higher P1 = later maturity. Early ~150-200, Medium ~200-280, Late ~280-400.

**.CUL file content**:
{cul_content[:6000]}

**If a good analog is found**, return JSON:
{{
  "found": true,
  "analog_cultivar_name": "exact name of the chosen analog cultivar from the file",
  "coefficients": {{
    "P1": value,
    "P2": value,
    "P5": value,
    "G2": value,
    "G3": value,
    "PHINT": value
  }},
  "match_reason": "one sentence explaining why this cultivar was chosen as the best analog"
}}

**If no reasonable analog exists**, return:
{{
  "found": false,
  "reason": "brief reason"
}}

**Requirements**:
- Return only JSON, no markdown fences
- All coefficient values must be numeric
- Choose the single best match, not a list
"""
    return prompt

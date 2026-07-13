import json
def base_prompt_fertilizer_agent(
        crop_name, location, pdate, fertilizer_config, fertilizer_judge_feedback, fertilizer_fmcd_codes, fertilizer_facd_codes
        ):
        prompt = f'''
                ---
                You are an agronomist and DSSAT crop model expert.  
                Your task is to predict a realistic inorganic fertilizer management strategy for a given crop and location 
                and then reconstruct all synthetic fertilizer applications in a format usable for the DSSAT *FERTILIZERS (INORGANIC) section. 
                You will not receive any explicit fertilizer management details (no rates, no dates, no products, no methods). 
                Instead, you must infer a plausible, internally consistent inorganic fertilizer management scenario based on: 
                - The crop,
                - The location/region,
                - The planting date (pdate),
                - Typical agronomic recommendations,
                - Climate and soils in that region,
                - Typical yield goals and farming systems.

                Your output must be DSSAT-ready and transparent about assumptions.

                ---

                You will only be given:
                - CROP: [crop name]
                - LOCATION: [location: state/region, country and geocoordinates]

                Example:
                - CROP: {crop_name}
                - LOCATION: {location}
                - pdate : {pdate}
                - EXISTING CONFIGURATION (if any): {json.dumps(fertilizer_config, indent=2)}
                - SUGGESTIONS FROM FERTILIZER AGENT JUDGE: {fertilizer_judge_feedback}

                No additional management text will be provided.

                [ PROMPT REDACTED TO FIT THE IMAGE ]
                ---
                OUTPUT FORMAT:
                '''+'''{
                "narrative": "A concise but clear description of the inferred fertilizer strategy (as described in Part A above).",
                "fertilizer_section": [
                    {
                    "FDATE": "<FDATE_calendar (YYYY-MM-DD) and DAP (e.g., '2024-04-25, DAP 0')>",
                    "FMCD": "<Fertilizer product code not name as instructed'> (final output format and units: Alphanumeric code, typically two letters and three digits (e.g., FE027, FE005) should not be random should be a valid code for the selected fertilizer)",
                    "FACD": "<Application method code not name as instructed'> ((final output format and units: Alphanumeric code, typically two letters and three digits (e.g., AP001, AP003, AP004)) should not be random should be a valid code for the selected fertilizer application method)",
                    "FDEP": <Application depth in cm, e.g., 0>,
                    "FAMN": <Amount of N applied in kg N/ha, e.g., 60>,
                    "FAMP": <Amount of P applied in kg P/ha (or clearly state if using P2O5), e.g., 20>,
                    "FAMK": <Amount of K applied in kg K/ha (or clearly state if using K2O), e.g., 30>,
                    "Assumptions_or_Notes": "<Brief notes on assumptions, e.g., yield goal, fertilizer grade, basis of calculations>"
                    }
                    // Repeat for each application event
                ]
                }

                - **Do not output any markdown tables or narrative text outside the JSON object.**
                - All field names must match exactly as shown.
                - For each fertilizer application, include a separate object in the "fertilizer_section" array.
                - "FDATE" must include both the calendar date and DAP, separated by a comma.
                - "Assumptions_or_Notes" is required for each event.
                - All values must be concrete numerical values (no ranges).
                - If there is uncertainty, document it in "Assumptions_or_Notes" but still provide a fully specified scenario.
            ''' + f'''
                **INPUT (consider this input)*
                CROP: {crop_name}
                LOCATION: {location}
                pdate : {pdate}

                **You must respond with:**
                - A JSON object as described above, fully filled for the scenario JSON should be a string no extra formatting easy for python dictionary conversion with no errors. Don't put json in front of the object.

            ---


            '''
    return prompt
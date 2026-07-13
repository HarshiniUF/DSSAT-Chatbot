# Updates Made

## 1. Data correctness fixes (generated `.SNX` files were wrong)
- **Coordinates swapped**: latitude/longitude were being written to the wrong fields, corrupting location-dependent calculations.
  - *How*: traced the exact point where coordinates were passed into the file-writing object and corrected the mapping so each value lands in its correct field.
- **Harvest date bug**: harvest date was identical to planting date (crop harvested same day it's planted).
  - *How*: separated harvest-date logic from planting-date logic and set it to a realistic date after planting instead of copying the planting date.
- **Unrealistic soil data**: soil moisture/nitrogen were flat (identical at every depth) instead of a realistic depth gradient.
  - *How*: replaced the single repeated value with depth-varying values that follow a realistic moisture/nitrogen gradient.
- **Fertilizer amount rounding**: requested nitrogen rate (e.g. 87.5 kg/ha) was sometimes rounded to a "nicer" number (e.g. 88), breaking dose-response comparisons between treatments.
  - *How*: tightened the instruction given to the generating model to require an exact match to the requested rate, instead of allowing rounding for realism.

## 2. Security / configuration
- Removed a hardcoded API key that was committed in source code.
  - *How*: deleted the key from the code; the program now reads it only from the environment and stops with a clear error if it's missing, instead of silently using the exposed key.
- Consolidated all credentials into a **single `.env` file** at the project root (previously duplicated across two folders).
  - *How*: merged both environment files into one and updated every place that loaded configuration to point to that single file.
- Removed unsafe `eval()` usage in a calculator tool.
  - *How*: replaced direct evaluation of input text with a restricted parser that only allows basic arithmetic.

## 3. Location / crop / season inputs
- Created `workflow_inputs.json` as the **single source of truth** for latitude, longitude, crop, and season year.
  - *How*: moved these values out of scattered hardcoded constants and per-question LLM guesses into one JSON file, and pointed every part of the pipeline at it.

## 4. Experiment design logic
- **Real fertilizer baseline**: the "baseline" nitrogen rate used to design treatments now comes from an actual agronomic inference, not a generic guess.
  - *How*: added a step that asks the crop-model's own fertilizer-planning agent to estimate a realistic baseline rate for the specific crop/location/planting date, and used that value instead.
- **Treatment count bug**: when a question specified one change (e.g. "add 50 kg N"), the system generated 3 treatments instead of 2.
  - *How*: found the contradictory instruction in the experiment-design prompt (one rule said "2 treatments," another gave an example with 3) and corrected it to match exactly what the question asks for.

## 5. Output file naming
- Generated files now follow the standard DSSAT experiment-code naming convention instead of an arbitrary name, with a per-treatment suffix.
  - *How*: changed the file-saving step to read the experiment code from the generated file itself and append the treatment number, so multiple treatments from the same run no longer overwrite each other.

## 6. Reliability
- Silent failure fixed: a date-parsing error used to be silently replaced with a fixed placeholder date with no warning.
  - *How*: changed the error handling to raise a clear error immediately instead of hiding the failure behind a default value.
- Fixed a crash-masking bug in the DSSAT execution error-reporting path.
  - *How*: added a check so that if the detailed error file is missing, the program still reports the original failure clearly instead of crashing with an unrelated error.

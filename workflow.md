# Workflow

## Overview

A chatbot that answers farmer questions about maize management. Questions that need
a quantitative answer (e.g. "how much yield if I add 50 kg N?") are routed through an
agent pipeline that designs an experiment, critiques it, and generates one DSSAT FileX
(`.SNX`) per treatment via a separate sub-pipeline (`FileX_MultiAgent/`). Questions that
don't need simulation are answered directly by an LLM.

This chatbot pipeline **generates** `.SNX` files. It does not execute the DSSAT-CSM
model and does not run XBuild validation — see "What this workflow does NOT do" below.

## Step by step

**Step 1 — Entry point.**
`integrated_dssat_assistant.py` (`IntegratedDSSATAssistant.chat()`) receives the user's
question, builds the initial LangGraph state, and streams it through the compiled
workflow from `agents/workflow_config.py`.

**Step 2 — `au.router` decides direct vs. simulation.**
(`agents/conversation_agent.py:au_router`) An LLM prompt classifies the question as
needing DSSAT simulation (quantitative "what if"/comparison questions) or answerable
directly (definitions, qualitative/typical-practice questions).
- If **direct**: `answer_directly()` answers immediately using the knowledge base
  (`agents/knowledge_base.py`) and the graph ends — none of the steps below run.
- If **simulation**: proceeds to Step 3.

**Step 3 — `analysis.q_classifier` extracts intent.**
(`agents/experiment_agents.py:q_classifier`) An LLM extracts `focus_variable` (fertilizer
rate/timing, planting date, cultivar, irrigation, etc.), `crop`, `region` (kept for
context/narrative only — see the Location note below, it no longer drives coordinates),
and a `baseline_nitrogen_rate` (initially just the LLM's own guess — see Step 3a).
- If the question matches comparison phrasing ("X or Y", "vs", "compared to"), it's
  routed to `q_classifier_comparison` instead, and the graph **skips straight to Step 6**
  (`tools.ccx_generator`), bypassing the designer/critic loop entirely.

**Step 3a — real fertilizer baseline discovery (fertilizer_rate/fertilizer_timing only).**
If `focus_variable` is `fertilizer_rate` or `fertilizer_timing`, `q_classifier` does not
keep its own guessed `baseline_nitrogen_rate`. Instead it calls
`agents/multiagent_nodes.py:discover_fertilizer_baseline()`, which runs
`FileX_MultiAgent` in a new lightweight mode (`run_cli.py --baseline-only` →
`main.py:run_baseline_discovery()`) — a slim `field → planting → fertilizer` subgraph,
skipping irrigation/residue/initial-conditions/simulation-control/assembler, with no
forced N target. This lets `FertilizerAgent`'s real prompt
(`FileX_MultiAgent/prompts/fertilizer_agent_prompts.py`) infer a genuine
representative-farmer-practice total N rate for this crop/location/planting-date,
instead of the generic `classify_prompt` guess. The discovered number overwrites
`intent["baseline_nitrogen_rate"]` (tagged `baseline_source="filex_fertilizer_agent"`,
alongside the discovered `pdate`/`narrative`); if discovery fails, the original
LLM-guessed baseline is kept and `baseline_source` stays `"llm_guess"`. This runs once
per question — `a1_designer`'s redesign iterations (Step 5) reuse the same
`intent_brief` value rather than re-triggering discovery. Adds one extra real
subprocess round-trip (2-3 LLM calls) before the designer/critic loop starts.

**Step 4 — `experiments.a1_designer` proposes treatments.**
(`agents/experiment_agents.py:a1_designer`) Builds `proposed_experiment.treatments`
(e.g. baseline N rate vs. baseline + increment), using the baseline rate from Step 3.

**Step 5 — `experiments.a2_critic` scores the design, feedback loop.**
(`agents/experiment_agents.py:a2_critic`) An LLM scores the proposed experiment
(alignment, feasibility, rigor, completeness, clarity 0-10 each) and returns
`overall_score`/`approved`. `should_iterate()` in `workflow_config.py` then decides:
- `approved`, or `overall_score >= MIN_SCORE_FOR_SNX_GENERATION`, or
  `iteration_count >= MAX_CRITIC_ITERATIONS` → proceed to Step 6.
- Otherwise → back to Step 4 (`a1_designer` redesigns) — capped at
  `MAX_CRITIC_ITERATIONS` iterations (`experiment_config.py`) so this can't loop forever.

**Step 6 — `tools.ccx_generator` generates one FileX per treatment.**
(`agents/multiagent_nodes.py:multiagent_xfile_node`) For **each** treatment in
`proposed_experiment.treatments`:
- Builds a config dict: fixed `Location` (see Location note below), `Year`/`weather`
  window, `cultivar.CR`, and `fertilizer.target_n_rate_kg_ha` set to that treatment's
  rate (so each generated file reflects the N rate that treatment is actually testing —
  for fertilizer_rate/fertilizer_timing questions, treatment 1's rate is the real
  baseline discovered in Step 3a, not a generic guess).
- Calls `FileX_MultiAgent/run_cli.py` **as a subprocess** — its own venv, own working
  directory — passing the config as a temp JSON file and reading the resulting `.SNX`
  back out. (Subprocess isolation exists because `FileX_MultiAgent` defines its own
  `agents`/`utils`/`prompts` packages that would otherwise collide by name with this
  project's own `agents` package.)

**Step 7 — Inside the subprocess: `FileX_MultiAgent/main.py` builds the FileX.**
`run_cli.py` calls `run_workflow()`, which resolves the location (Step 7a) and then runs
a second, separate LangGraph pipeline (Step 7b) to assemble every section of the file.

- **7a. Location resolution** (`main.py:build_initial_state`, ~line 128-154): since the
  config already has `Latitude`/`Longitude` (fixed value, see note below), it skips live
  geocoding entirely and uses those coordinates directly. (If they were ever absent, it
  would geocode the `place` name live via GeoNames and fail loudly rather than guessing.)
- **7b. Agent chain** (`main.py`, graph order): `FieldAgent` → `PlantingAgent` →
  `FertilizerAgent` → `IrrigationAgent` → `ResidueAgent` → `InitialConditionsAgent` →
  `SimulationControlAgent` → `FileAssemblerAgent`.
  - `FieldAgent`: fetches soil (`ID_SOIL`) and weather station data for the resolved
    coordinates; constructs the DSSATTools `Field` object (this is the exact boundary
    where `xcrd`/`ycrd` get mapped to DSSAT's real longitude/latitude convention).
  - `PlantingAgent`, `FertilizerAgent`, `IrrigationAgent`: each runs an LLM
    **generator → judge → retry** loop internally (not separate graph nodes) — the judge
    is only active if `enable_judge=True` is passed in (off by default; env var
    `FILEX_ENABLE_JUDGE`). `FertilizerAgent`'s prompt treats
    `target_n_rate_kg_ha` from Step 6 as a hard total-N constraint.
  - `ResidueAgent`, `InitialConditionsAgent`, `SimulationControlAgent`: deterministic,
    no LLM calls — fixed defaults (soil-depth gradient, automatic-management windows,
    simulation switches like `IRRIG`/`HARVS`).
  - `FileAssemblerAgent`: calls DSSATTools' `create_filex()` to concatenate every section
    (`*FIELDS`, `*INITIAL CONDITIONS`, `*PLANTING DETAILS`, `*FERTILIZERS`,
    `*SIMULATION CONTROLS`, etc.) into the final `.SNX` text.

**Step 8 — File written back to the parent project.**
The subprocess writes the assembled text to the temp output path, prints a one-line JSON
result (`{"ok", "output_path", "errors"}`), and `multiagent_xfile_node` copies it to
`generated_<CROP>_<treatment-id>_<date>.SNX` in the project root. This repeats once per
treatment from Step 6.

**Step 9 — `au.summarizer` explains the result.**
(`agents/conversation_agent.py:au_summarizer`) An LLM explains what was simulated and
why, in farmer-friendly language. The real generated file paths are then **appended
deterministically** after the LLM text, regardless of what the LLM chose to mention, so
the user always sees accurate filenames. This is the final `final_answer`.

## Location configuration

Every generated file uses one fixed location — there is no per-region lookup anymore.
To change it, edit these three constants in `experiment_config.py` (nothing else needs
to change):

```python
DEFAULT_LATITUDE = 1.0157
DEFAULT_LONGITUDE = 34.9865
DEFAULT_LOCATION_NAME = "Kitale, Kenya"
```

`agents/multiagent_nodes.py:_resolve_location()` returns these unconditionally; whatever
`region` the LLM extracts in Step 3 no longer affects coordinates at all (it's still
extracted and shown in narrative text, but has no effect on the generated file's
`XCRD`/`YCRD`).

## Key files

| Piece | File |
|---|---|
| Chat entry point | `integrated_dssat_assistant.py` |
| Graph wiring (chatbot) | `agents/workflow_config.py` |
| Router / summarizer | `agents/conversation_agent.py` |
| Question classifier, design/critic loop | `agents/experiment_agents.py` |
| Bridge to FileX creation (subprocess call) | `agents/multiagent_nodes.py` |
| Fixed location + other project constants | `experiment_config.py` |
| FileX creation pipeline (separate project/venv) | `FileX_MultiAgent/main.py`, `FileX_MultiAgent/run_cli.py` |
| Per-section FileX agents | `FileX_MultiAgent/agents/*.py` |
| Real fertilizer-baseline inference prompt (Step 3a) | `FileX_MultiAgent/prompts/fertilizer_agent_prompts.py` |
| DSSATTools FileX writer (vendored) | `FileX_MultiAgent/DSSATTools/DSSATTools/filex.py` |

## What this workflow does NOT do

- **Does not run DSSAT-CSM.** The output is a `.SNX` file only; nothing in this chat
  path invokes `DSSATTools`' `run.py` (the actual DSSAT executable wrapper).
- **Does not run XBuild/XB2 validation.** `validate_xfile_with_xb2()` in
  `FileX_MultiAgent/utils/helpers.py` exists but is only called from the separate
  Streamlit UI (`FileX_MultiAgent/streamlit_ui/app.py`), not from `run_cli.py`/this chat
  pipeline.
- **Does not accept fine-grained agronomic directives beyond N rate.** The bridge
  (Step 6) only passes crop, fixed location, weather window, and target N rate through —
  things like planting-date shifts or irrigation-method changes aren't parameterized
  from the chatbot side yet.

## Testing

Three levels, from narrowest to broadest:
1. `FileX_MultiAgent` standalone — run `FileX_MultiAgent/run_cli.py` directly with a
   config JSON, bypassing the chatbot entirely. Add `--baseline-only` (no `--output`
   needed) to test just the Step 3a fertilizer-baseline-discovery mode in isolation.
2. The bridge function in isolation — call `agents.multiagent_nodes._build_filex_config`
   / `multiagent_xfile_node` / `discover_fertilizer_baseline` directly with a fabricated
   state dict (no LLM calls needed for `_build_filex_config`; the other two still shell
   out to the real subprocess).
3. Full chatbot end-to-end — `python integrated_dssat_assistant.py "<question>"` or
   interactive mode, exercising the whole LangGraph pipeline including live LLM calls.

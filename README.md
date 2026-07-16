# DSSAT Chatbot

A chatbot that answers farmer questions about crop management. Quantitative "what if"
questions (e.g. *"how much yield if I add 50 kg N?"*) are routed through an LLM agent
pipeline that designs an experiment, critiques it, and generates one DSSAT FileX
(`.SNX`) per treatment. Qualitative questions are answered directly from a knowledge
base. This project **generates** `.SNX` files — it does not run the DSSAT-CSM model or
XBuild validation.

The crop is configured in `workflow_inputs.json` (currently `"Maize"`); `experiment_config.py`'s
`CROP_CODES` also maps Peanut, Wheat, Rice, Sorghum, and Cotton, so the pipeline itself
isn't maize-specific — only the current default configuration is.

See [Workflow.md](Workflow.md) for a short step-by-step summary.

## Architecture

Two pipelines sharing **one venv and one `requirements.txt`** at the project root:

- **Chatbot pipeline** (project root, `agents/`) — LangGraph graph that classifies the
  question, designs treatments, critiques the design, and calls the second pipeline once
  per treatment.
- **`FileX_MultiAgent/`** — a separate LangGraph pipeline invoked as a **subprocess**
  (`run_cli.py`, run with `cwd=FileX_MultiAgent`) that builds one `.SNX` file: field →
  planting → fertilizer → irrigation → residue → initial conditions → simulation
  controls → file assembly. It's still launched as a subprocess (not imported
  in-process) because it defines its own `agents`/`utils`/`prompts` packages that would
  otherwise collide by name with this project's own `agents` package — that isolation
  comes from being a separate process with its own working directory, not from a
  separate venv, so both pipelines installing into the same environment is safe.

## Setup

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

Create `.env` in the project root (shared by both pipelines) with:

```
OPENAI_API_KEY=...
OPENAI_BASE_URL=...        # if using a custom/proxy endpoint
CLIENT_ID=...
CLIENT_SECRET=...
GEONAMES_USERNAME=...      # used only if a location isn't already pinned with coordinates
```

## Running it

```bash
python integrated_dssat_assistant.py                    # interactive chat
python integrated_dssat_assistant.py "<your question>"  # single question, one-shot
```

## How a question becomes `.SNX` files

1. **Router** — LLM decides *direct answer* vs *needs simulation*.
2. **Classifier** — extracts `focus_variable` (fertilizer rate/timing, etc.), `crop`,
   `region`; for fertilizer questions, discovers a real baseline N rate via a
   lightweight run of `FileX_MultiAgent` rather than guessing one.
3. **Designer / Critic loop** — `a1_designer` proposes treatments (e.g. `s01` baseline,
   `s02` baseline + increment); `a2_critic` scores the design and either approves it or
   sends it back for redesign (capped iterations).
4. **Generation** — one `FileX_MultiAgent` subprocess call per treatment. Treatment 1
   (`s01`) decides field, cultivar, planting date, and irrigation strategy fresh; those
   exact values are captured into `agents/experiment_guidelines.json` and reused
   verbatim for every later treatment (`s02`, `s03`, …), so only the fertilizer
   rate/timing being tested actually varies between files.
5. **Summarizer** — explains the result in farmer-friendly language; real generated file
   paths are appended so the user always sees accurate filenames.

Comparison-style questions ("100kg at knee-high or 50kg split at 4 and 8 weeks?") skip
the designer/critic loop entirely and go straight to generation.

## Key files

| Piece | File |
|---|---|
| Chat entry point | `integrated_dssat_assistant.py` |
| Graph wiring | `agents/workflow_config.py` |
| Router / summarizer | `agents/conversation_agent.py` |
| Question classifier, design/critic loop | `agents/experiment_agents.py` |
| Bridge to FileX generation (subprocess + guidelines locking) | `agents/multiagent_nodes.py` |
| Locked field/cultivar/planting/irrigation snapshot from `s01` | `agents/experiment_guidelines.json` |
| Fixed location + other project constants | `experiment_config.py` |
| FileX generation pipeline (subprocess, shared venv) | `FileX_MultiAgent/main.py`, `FileX_MultiAgent/run_cli.py` |
| Per-section FileX agents | `FileX_MultiAgent/agents/*.py` |

## What this does NOT do

- Does not run DSSAT-CSM (no simulation execution, only file generation).
- Does not run XBuild validation as part of this chat path.
- Location is fixed (`experiment_config.py`), not derived from the question's region.

## Testing

1. `FileX_MultiAgent/run_cli.py --config <path> --output <path>` — standalone, bypasses
   the chatbot entirely. Add `--baseline-only` to test fertilizer-baseline discovery.
2. Call `agents.multiagent_nodes._build_filex_config` / `multiagent_xfile_node` directly
   with a fabricated state dict.
3. Full end-to-end: `python integrated_dssat_assistant.py "<question>"`.

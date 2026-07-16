# Flow

1. **User question** → `integrated_dssat_assistant.py` starts the chat graph.

2. **Router** (`au_router`) — LLM decides *direct answer* or *needs simulation*.
   - Direct → `answer_directly()` from the knowledge base. Done.
   - Simulation → continue.

3. **Classifier** (`q_classifier`) — LLM extracts `focus_variable`, `crop`, `region`,
   `baseline_nitrogen_rate`.
   - Comparison question ("X or Y") → `q_classifier_comparison`, skip straight to step 6.
   - Fertilizer question → `discover_fertilizer_baseline()` runs a real
     field→planting→fertilizer sub-pipeline to get a genuine baseline N rate (not a guess).

4. **Designer** (`a1_designer`) — proposes treatments (e.g. `s01` = baseline,
   `s02` = baseline + increment).

5. **Critic** (`a2_critic`) — scores the design; loops back to step 4 until approved or
   `MAX_CRITIC_ITERATIONS` is hit.

6. **Generate FileX per treatment** (`multiagent_xfile_node` →
   `FileX_MultiAgent/run_cli.py`, one subprocess per treatment):
   - **s01** runs fresh: field, cultivar, planting date, and irrigation are decided by
     their own LLM agents.
   - s01's exact values are captured and saved to `agents/experiment_guidelines.json`.
   - **s02, s03, …** reuse those locked values (no LLM re-decision for
     field/cultivar/planting/irrigation) and only vary **fertilizer** — the focus
     variable actually being tested.
   - Each treatment's `.SNX` is written as `<EXP_CODE>_<treatment_id>.SNX`.

7. **Summarizer** (`au_summarizer`) — LLM explains the result in farmer-friendly
   language; the real generated file paths are appended after it.

## Notes
- Does **not** run DSSAT-CSM or XBuild — output is `.SNX` files only.
- Location is fixed (`experiment_config.py`), not derived from the question.
- `experiment_guidelines.json` is a scratch snapshot: overwritten by each new question's
  s01, not accumulated across conversations.

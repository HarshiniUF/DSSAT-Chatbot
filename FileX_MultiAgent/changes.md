# Changes Log — FileX_MultiAgent

Every change made in this folder (code or data) is recorded here, most recent first.

---

## 2026-08-17

### Code — `utils/helpers.py`

- **Extended the `.CUL` fallback to the "no AEZ zone match at all" case, still fallback-only.**
  Context: `get_cultivar_list_by_location()` has two distinct "no match"
  branches:
  1. `get_zone_by_location()` returns `None` — the LLM couldn't map the
     location to **any** AEZ zone for that country at all (line 648-649,
     stronger "no match").
  2. A zone **was** matched, but that zone has no cached cultivar data yet
     in the AEZ database (line 675, `zone_name not in zones_dict` — this is
     the case the previous entry below already covers).

  Previously only branch 2 used the `.CUL` fallback; branch 1 just returned
  `("", {})` immediately, which `FieldAgent` treats as a hard failure — no
  cultivar ever gets set on the FileX for that run.

  Refactored the fallback-building logic (reshape `.CUL` lookup result into
  the AEZ `zones`-schema cultivar entry format) out of branch 2 into a new
  shared helper, `_cul_fallback_cultivar_entry(crop_code, model, reason)`
  (`utils/helpers.py:584`). Branch 1 (`utils/helpers.py:649`) now calls this
  same helper before giving up, so it also picks a real cultivar from the
  crop's `.CUL` file instead of failing outright. It still only triggers
  when the main approach (a matched, cached AEZ zone) already failed to
  resolve anything — the fallback runs strictly after that attempt, never
  instead of it.

  Difference from branch 2: since no zone was ever identified, there's no
  zone name to cache the result under, so this branch does **not** call
  `_save_zone_to_aez_database()` — the result is returned but not persisted.
  The function returns the placeholder zone name
  `"No AEZ Zone Match (.CUL fallback)"` (non-empty, so `FieldAgent`'s
  `cultivar_list[0] == ""` failure check doesn't trip) instead of a real
  zone name.

  Also fixed a leftover bug from the branch-2 refactor: the "saved to AEZ
  database" log line still referenced the old `cul_name` variable which no
  longer exists after the refactor into the shared helper — changed to read
  the name from the returned dict (`next(iter(zone_cultivars))`).

### Code — `utils/helpers.py`, `utils/cul_parser.py`

- **Replaced on-demand LLM cultivar generation with a `.CUL`-file fallback,
  for the live FileX-generation path only.** Context: `get_cultivar_list_by_location()`
  is called from two very different places —
  1. `FieldAgent` (`agents/field_agent.py`), during a real run of the full
     FileX multi-agent process, and
  2. nowhere else — `generate_dataset.py` builds the AEZ database directly
     via `CultivarAgent.process()` and never calls this function, so it is
     **not** affected by this change and keeps generating cultivars via LLM
     exactly as before.

  Previously, when `get_cultivar_list_by_location()` resolved a location to
  an AEZ zone that had no cached cultivar data yet, it called
  `CultivarAgent.process()` to generate brand-new synthetic cultivars via
  LLM on the spot (this was the same-day fix logged below, "Fixed
  caching/regeneration bug"). That on-demand LLM generation call is now
  removed for this call site.

  Instead, added `get_fallback_cultivar_from_cul()` to `utils/cul_parser.py`
  — a thin public wrapper around the existing `_lookup_medium_season_generic()`
  logic (deterministic `data/coefficients_db/<CROP>.json` lookup first,
  LLM-based raw `.CUL` *parsing* only as a fallback for crops without an
  extracted coefficients DB — this LLM use is limited to reading an existing
  real `.CUL` entry, not inventing new cultivar data). It picks a real,
  already-calibrated cultivar straight from the crop's `.CUL` file(s) in
  `Genotype/`, with no AEZ zone required.

  `get_cultivar_list_by_location()`'s "zone not cached" branch
  (`utils/helpers.py:624`) now calls `get_fallback_cultivar_from_cul(crop_code, model=model)`
  instead, reshapes the result into the AEZ `zones`-schema cultivar format
  (`{cultivar_name: {characteristics: {}, coefficients: {found, source,
  source_url, coefficients, notes}}}`, `source` marked as
  `"Local .CUL fallback (no cached AEZ data for zone '<zone>')"`), and still
  saves it via `_save_zone_to_aez_database()` so the same zone doesn't repeat
  the `.CUL` lookup next time. Downstream code (`FieldAgent` →
  `parse_and_match_cultivar()`) is unaffected — it receives the same
  `Tuple[str, dict]` shape as before and resolves the cultivar against the
  `.CUL` file exactly as it already did for real AEZ data.

### Code — `utils/helpers.py` (earlier same-day change, now partly superseded)

- **Fixed "Unknown Location" bug**: `get_cultivar_list_by_location()` was not
  passing `location_name` into the `agent_state` dict handed to
  `CultivarAgent.process()`. It silently defaulted to `"Unknown Location"`,
  causing the LLM to reject every location as unsuitable. Added
  `"location_name": f"{zone_name}, {country}"` to `agent_state`
  (`utils/helpers.py:641`).

- **Fixed caching/regeneration bug**: On-demand-generated cultivar data was
  being saved in a different file/schema than the one `_load_aez_database()`
  reads from, so the cache-check never found it and every lookup regenerated
  from scratch. Added `_save_zone_to_aez_database()` (`utils/helpers.py:405`)
  which writes into the same `zones`-schema file/format `_load_aez_database`
  reads (`data/cultivar_db/<country>/<crop>/*.json`, keyed by
  `zones[zone_name]`), merging into any existing file. Wired in a call right
  after generation completes in `get_cultivar_list_by_location()`
  (`utils/helpers.py:655`).

### Data cleanup (one-time, not code)

- Removed a stale `"Unknown Location": {}` entry from
  `data/cultivar_db/peanut/peanut_PN_cultivars_list.json` (leftover empty
  result from the bug above, before the fix).
- Deleted `data/cultivar_db/peanut/` entirely to start peanut/Senegal fresh
  for testing. It was recreated by a manual `generate_dataset.py` run and now
  holds just the `"Kaolack, Senegal"` entry from that run.

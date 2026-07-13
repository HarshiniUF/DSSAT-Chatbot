# CultivarDB Creation — Pipeline Documentation

This document explains the full workflow for building the `cultivar_db` — the JSON database of DSSAT genotypic coefficients used by the SNX generation pipeline.

---

## ⚠️ Known Issue — Generator/Consumer Directory Mismatch

The generator and the SNX pipeline currently write/read from **different folders** for the same crop:

- `generate_dataset_v3.py` writes to `data/cultivar_db/<country>/<crop_NAME>/...` (e.g. `data/cultivar_db/kenya/maize/Kenya_MZ_cultivars_list.json`) — it builds the folder from the crop **name** (`"Maize"` → `"maize"`).
- `utils/helpers.py::_load_aez_database()` (used by `get_cultivar_list_by_location()`, which `CultivarAgent` calls during SNX generation) reads from `data/cultivar_db/<country>/<crop_CODE>/...` (e.g. `data/cultivar_db/kenya/mz/...`) — it builds the folder from the crop **code**, lowercased.

Right now both `kenya/maize/` and `kenya/mz/` exist with the same file structure, so the live pipeline happens to work — but it is reading a separately-placed copy, **not** whatever the generator script most recently produced. If you re-run `generate_dataset_v3.py`, the new output lands in `kenya/maize/` and the SNX pipeline will keep reading the older `kenya/mz/` copy until someone manually copies the file over (or one of the two path-building functions is fixed to match the other).

---

## Files Involved

| File | Role |
|---|---|
| `generate_dataset_v3.py` | Main entry point — runs per country/crop across all configured zones |
| `agents/standalone_cultivar_helper_agent_v2.py` | Core agent: characteristics extraction + 3-step coefficient fallback chain |
| `prompts/standalone_cultivar_helper_agent_prompts_v2.py` | All LLM prompts used by the agent |
| `Genotype/<CROP>*.CUL` (e.g. `Genotype/MZCER048.CUL`) | DSSAT official coefficient reference files |
| `utils/helpers.py` | `get_cultivar_list_by_location()` / `_load_aez_database()` — reads cultivarDB for SNX (see directory mismatch above) |
| `utils/cul_parser.py` | `parse_and_match_cultivar()` — INGENO lookup for SNX |
| `data/cultivar_db/<country>/<crop>/` | Output location for generated JSON files |

---

## Configuration (in `generate_dataset_v3.py`)

```python
COUNTRY          = "Kenya"
CROP_CODE        = "MZ"
GENERATOR_MODEL  = "gpt-5"
VERBOSE          = False
BASE_OUTPUT_DIR  = "data/cultivar_db"

ZONES = [
    "Coastal Lowland",
    "Inner Lowland",
    "Lower Highland",
    "Lower Midland",
    "Upper Midland",
    "Upper Highland",
    "Tropical Alpine",
    "Nairobi",
]
```

Zones are **real agro-ecological zone names** (matching `data/zones_list.json`), not generic labels like "AEZ1".

## How to Run

```bash
cd /home/harshini/Desktop/FILE_X/FileX_MultiAgent
python generate_dataset_v3.py
```

Output is written **incrementally** (one zone at a time, flushed to disk after each) to a **single JSON file per country+crop**:

```
data/cultivar_db/<country_lower>/<crop_name_lower>/<Country>_<CROP_CODE>_cultivars_list.json
```

Example: `data/cultivar_db/kenya/maize/Kenya_MZ_cultivars_list.json`

(See the known-issue note above — this is **not** the folder the live SNX pipeline currently reads from.)

---

## Per-Cultivar Workflow

For every zone, the agent:

1. Asks the LLM whether the crop is even suitable for that zone, and if so, lists the suitable cultivars — **the count is not fixed**. The prompt explicitly instructs: *"Do NOT force a fixed number of cultivars — return as many or as few as are actually suitable."* An unsuitable zone returns an empty list `[]`.
2. For each cultivar in that list, runs two stages:
   - **Stage A (always runs):** asks the LLM to predict agronomic characteristics (days to maturity, maturity class, grain type, yield potential, major crop areas, etc.).
   - **Stage B:** the 3-step coefficient fallback chain below.

---

## The 3-Step Coefficient Fallback Chain

For every cultivar, the agent tries three steps in order. The first step that succeeds sets the coefficients; later steps are skipped.

---

### Step 1 — Local `.CUL` File Lookup

**What it does:** Searches DSSAT's official `.CUL` file(s) for an exact or close cultivar name match.

**How it works:**
1. `find_cul_files()` collects every relevant `.CUL` file from `Genotype/`:
   - For **MZ** and **WH**: only CERES-model files (`MZCER*.CUL`, `WHCER*.CUL`).
   - For all other crops: any file starting with the crop code (`<CROP_CODE>*.CUL`).
2. The cultivar name is checked (plain substring match) against the raw text of each file, in order, until a hit is found.
3. If found, the matching file's content is sent to the LLM, which parses the fixed-width table and returns the matching row's `VAR#` (INGENO) and coefficient values (`P1, P2, P5, G2, G3, PHINT`).

**Succeeds when:** The cultivar name appears in one of the loaded `.CUL` files.
**Source label (actual format):** `"Local .CUL file: <filename>"` — e.g. `"Local .CUL file: MZCER048.CUL"`.

---

### Step 2 — Web Search + Page Scraping

**What it does:** Searches the web for published DSSAT calibration studies and tries to extract a coefficient table.

**How it works:**
1. Runs up to 3 search queries via DuckDuckGo (`ddgs`, falling back to `duckduckgo_search` if `ddgs` isn't installed), e.g.:
   `DSSAT CERES Maize "DKC 910" genotypic coefficients P1 P2 P5`
2. Filters results to a fixed allow-list of open-access domains (`pmc.ncbi.nlm.nih.gov`, `plos`, `biorxiv.org`, `mdpi.com`, `frontiersin.org`, `tandfonline.com`, `researchgate.net`) or any direct `.pdf` link.
3. Fetches each candidate page with plain `requests.get()` and parses it with `BeautifulSoup` (this is **not** a tool called "WebFetch" — that string is just the source-label prefix used in the output).
4. Pre-filters pages that don't even mention the cultivar name or terms like "P1"/"PHINT"/"genotypic".
5. Sends the page text to the LLM asking it to extract `P1/P2/P5/G2/G3/PHINT`.

**Succeeds when:** An open-access page yields a parseable coefficient table for the cultivar.
**Fails in practice when:** Calibration data exists only in paywalled journals (common for commercial hybrids).
**Source label:** `"WebFetch: <url>"`

---

### Step 3 — Analog Matching (Dynamic, Not a Fixed Table)

**What it does:** When no published data is found, asks the LLM to find the closest-matching cultivar **already present in the loaded `.CUL` files** and borrows its coefficients.

**How it works:**
1. The LLM is given the target cultivar's predicted traits from Stage A (days to maturity, maturity class) plus the full text of each loaded `.CUL` file, one file at a time.
2. It's told the general CERES-Maize heuristic (`P1`: Early ≈150–200, Medium ≈200–280, Late ≈280–400) as guidance, but it can return **any row** in the file as the analog — it is not restricted to the three generic INGENO archetypes (`990001`/`990002`/`990003`).
3. The full coefficient row of whatever cultivar it picks is returned as-is.

**Example (real output from this DB):** a cultivar was assigned coefficients from `"analog: SWEET CORN from MZCER048.CUL"` — note this is an ordinary named cultivar row, not one of the three generic season archetypes.

**Succeeds when:** The LLM can identify a plausible match in at least one loaded `.CUL` file (this is the most reliable step in practice and rarely fails).
**Source label (actual format):** `"analog: <chosen cultivar name> from <filename>"`

---

### If All 3 Steps Fail

```json
{"found": false, "source": "not_found", "source_url": null, "coefficients": {}}
```

---

## Output JSON Structure (actual)

One file per country+crop, written incrementally as each zone completes:

```json
{
  "crop": "MZ",
  "country": "Kenya",
  "generated_at": "2026-06-22 13:45:00",
  "total_zones": 8,
  "processed": 8,
  "summary": {
    "total_cultivars_identified": { "DKC 910": ["Lower Highland", "Upper Midland"], "...": ["..."] },
    "zone_detailed": {
      "Coastal Lowland": {
        "num_cultivars": 9,
        "num_local_coefficients": 2,
        "num_web_coefficients": 0,
        "num_analog_coefficients": 7,
        "num_estimated_coefficients": 0,
        "crop_suitability_note": "Major cultivation zone with diverse cultivar options"
      }
    },
    "cultivars_overlap_info": {
      "total_cultivars_with_repeats": 64,
      "total_unique_cultivars": 41,
      "cultivars_in_single_zone": 30,
      "cultivars_in_multiple_zones": 11
    }
  },
  "zones": {
    "Coastal Lowland": {
      "DKC 910": {
        "characteristics": {
          "data": {
            "days_to_maturity": "120-130",
            "maturity_class": "medium",
            "grain_type": "dent",
            "yield_potential_t_ha": 10.0
          },
          "source": "LLM prediction",
          "source_url": null,
          "confidence": "medium"
        },
        "coefficients": {
          "found": true,
          "source": "analog: SWEET CORN from MZCER048.CUL",
          "source_url": null,
          "coefficients": { "P1": 200.0, "P2": 0.300, "P5": 800.0, "G2": 700.0, "G3": 8.50, "PHINT": 38.90 },
          "notes": "..."
        }
      }
    }
  }
}
```

Notes vs. older docs:
- There is no `aez_zone` or `cultivars` wrapper key — `zones` is keyed directly by zone name, and each zone's value is keyed directly by cultivar name.
- Each cultivar entry has only `characteristics` and `coefficients` — the cultivar name is the dict key, not a duplicated inner field.
- `summary` (cultivar overlap stats, per-zone coefficient-source counts, suitability notes) is generated and refreshed after every zone via `SummaryCalculator`.

---

## Source Label Reference (actual formats)

| `source` value | Meaning |
|---|---|
| `"Local .CUL file: <filename>"` | Match found in a local DSSAT `.CUL` file |
| `"WebFetch: <url>"` | Coefficients extracted from an open-access page (fetched via `requests`, not a "WebFetch" tool) |
| `"analog: <cultivar name> from <filename>"` | LLM-matched to an existing row in a `.CUL` file based on trait similarity — can be any cultivar in the file, not limited to 3 generic archetypes |
| `"not_found"` | All 3 steps failed |

---

## How CultivarDB Is Used in SNX Generation

The SNX pipeline reads cultivarDB through `CultivarAgent`:

1. `get_cultivar_list_by_location(country, location, crop_code)` infers the AEZ zone via LLM, then loads `data/cultivar_db/<country.lower()>/<crop_code.lower()>/*.json` (exactly one JSON file expected in that folder) and returns cultivars from that zone where `coefficients.found == True`.
2. `parse_and_match_cultivar(cultivar_name, crop_code)` re-searches the `.CUL` file to get the official `VAR#` (INGENO) for the matched cultivar.
3. The SNX `*CULTIVARS` section is written as:
   ```
   *CULTIVARS
   @C CR INGENO CNAME
    1 MZ KY0011 H614
   ```
   - `INGENO` comes from the `.CUL` file lookup.
   - `CNAME` comes from the cultivarDB (the cultivar name string).

The coefficient values stored in the DB are **not** written directly into the SNX file — DSSAT reads coefficients at runtime from its own `.CUL` files using the INGENO code. The DB's `coefficients` field exists mainly to confirm a cultivar has usable data and to support the analog/fallback logic.

⚠️ See the directory-mismatch note at the top of this doc — step 1 here reads from `<crop_code>/` (e.g. `mz/`), while the generator script writes to `<crop_name>/` (e.g. `maize/`).

---

## Summary Progress Output

When the agent finishes a zone, it prints:

```
[StandaloneCultivarHelperAgent_v2] 📊 Summary: 2 local .CUL, 0 web paper, 11 analog, 0 not found
```

---

## Known Limitations

- **Directory mismatch (see top of doc):** generator and consumer use different folder-naming schemes (crop name vs. crop code), so freshly generated data isn't automatically picked up by the SNX pipeline.
- **Paywalled papers:** Step 2 rarely succeeds for commercial hybrid cultivars (Elsevier/Springer block access). Step 3 compensates and is the dominant source in practice.
- **Analog accuracy:** Borrowed coefficients are not variety-specific — they're a reasonable placeholder but may not capture the true variety's yield potential or stress response.
- **LLM trait knowledge:** Step 3's match quality depends on the LLM's knowledge of the cultivar's maturity class/DTM. Very new or obscure local varieties may be misclassified.
- **`_load_aez_database` strictness:** it errors out if a crop/country folder has zero or more than one JSON file — manual cleanup is needed if old files accumulate.

---

## Supported Crop Codes (`CROP_MAP` in both `generate_dataset_v3.py` and the agent)

| Code | Crop | Code | Crop |
|---|---|---|---|
| MZ | Maize | TN | Sunflower |
| WH | Wheat | PP | Pigeonpea |
| BA | Barley | CH | Chickpea |
| RI | Rice | BN | Dry Bean |
| SB | Soybean | CB | Cabbage |
| PN | Peanut | TM | Tomato |
| SG | Sorghum | PT | Potato |
| ML | Millet | SC | Sugarcane |

Note: Local `.CUL` lookup (Step 1) only works for crops that actually have matching files in `Genotype/`. For MZ/WH it's restricted further to CERES-model files specifically.

---

## Dependencies

Actual imports used by this pipeline (`generate_dataset_v3.py` + `standalone_cultivar_helper_agent_v2.py`):

```
requests
beautifulsoup4
ddgs (falls back to duckduckgo-search if not installed)
openai          # via utils/llm.py
python-dotenv
```

LLM: NaviGator API (University of Florida gateway) — configured via `.env`:
- `OPENAI_API_KEY`
- `OPENAI_BASE_URL` (not `OPENAI_API_BASE`)
- `CLIENT_ID` / `CLIENT_SECRET` (sent as NaviGator's `Client-ID` / `Client-Secret` headers, see `utils/llm.py`)

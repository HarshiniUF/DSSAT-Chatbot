"""
StandaloneCultivarHelperAgent v3 - Crop + location cultivar discovery

Key changes from v2:
- Input collapsed to crop_code + location_name (zone/country split removed)
- Coefficients no longer read local .CUL files or borrow an "analog"
  cultivar's values as a proxy. They come from exactly two mechanisms,
  matching how cultivars/characteristics are already generated:
    1. The LLM is asked directly for coefficients it actually knows
    2. If it doesn't know, a web search + paper extraction fallback runs
  Every coefficient key for the crop's real DSSAT model schema is always
  present in the output — a number if found, `false` if not. Each
  candidate value is sanity-checked in the backend against that crop's
  real min/max range from data/coefficients_db/<CROP>.json (values
  outside range are rejected as `false`), but the bounds themselves are
  not written to the output file — the output stays a plain
  {found, source, source_url, coefficients: {KEY: value|false}, notes}
  shape, matching the rest of the cultivar DB.

Workflow per cultivar:
  1. LLM predicts agronomic characteristics
  2. LLM is asked directly for known genotypic coefficients
  3. If nothing found, web search + paper extraction for coefficients
"""

from __future__ import annotations

import io
import json
import time
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple

import requests
from bs4 import BeautifulSoup

from utils.llm import get_llm
from utils.helpers import strip_markdown_fences
from utils.coefficients_lookup import load_coefficients_db

from prompts.standalone_cultivar_helper_agent_prompts import (
    generate_cultivar_list_prompt,
    extract_characteristics_prompt,
    get_known_coefficients_prompt,
    extract_coefficients_from_paper_prompt,
)


def _extract_pdf_text(content: bytes, max_chars: int = 8000) -> str:
    """
    Extract plain text from PDF bytes using pdfplumber.

    Fetched paper URLs are sometimes PDFs, not HTML — those must NOT be run
    through BeautifulSoup (it would parse raw PDF binary as if it were
    markup and produce nothing usable). Returns "" on any failure so the
    caller can just skip that URL, same as an HTML fetch/parse failure.
    """
    try:
        import pdfplumber
    except ImportError:
        return ""

    try:
        text_parts: List[str] = []
        total_len = 0
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                text_parts.append(page_text)
                total_len += len(page_text)
                if total_len >= max_chars:
                    break
        return " ".join(text_parts)[:max_chars]
    except Exception:
        return ""


# ============================================================================
# HELPER FUNCTIONS
#
# Still used by utils/cul_parser.py (a separate .CUL-parsing tool) — kept
# here even though this agent's own coefficient workflow no longer calls
# them.
# ============================================================================

def find_cul_files(genotype_dir: Path, crop_code: str) -> List[Path]:
    """
    Find ALL .CUL files matching crop_code inside genotype_dir.

    For MZ/WH crops, only CERES model files (<crop_code>CER*.CUL) are selected.
    For all other crops, all <crop_code>*.CUL files are selected.
    """
    if not genotype_dir.exists():
        return []

    crop_code = (crop_code or "").strip().upper()
    if not crop_code:
        return []

    if crop_code in ["MZ", "WH"]:
        target_prefix = f"{crop_code}CER"
        matching_files = [
            p for p in genotype_dir.iterdir()
            if p.is_file()
            and p.name.upper().startswith(target_prefix)
            and p.name.upper().endswith(".CUL")
        ]
    else:
        matching_files = [
            p for p in genotype_dir.iterdir()
            if p.is_file()
            and p.name.upper().startswith(crop_code)
            and p.name.upper().endswith(".CUL")
        ]

    matching_files.sort()
    return matching_files


def get_all_cul_file_contents(genotype_dir: Path, crop_code: str) -> List[Tuple[Path, str]]:
    """
    Read content of ALL .CUL files for given crop code.
    Returns list of (Path, content) tuples.
    """
    cul_files = find_cul_files(genotype_dir, crop_code)
    if not cul_files:
        return []

    file_contents = []
    for cul_file in cul_files:
        try:
            content = cul_file.read_text(encoding="latin1")
            file_contents.append((cul_file, content))
        except Exception:
            continue

    return file_contents


# ============================================================================
# STANDALONE CULTIVAR HELPER AGENT CLASS v3
# ============================================================================

class StandaloneCultivarHelperAgent:
    """
    Standalone agent for cultivar discovery and coefficient retrieval v3.

    Output per cultivar:
        {
            "cultivar_name": "...",
            "characteristics": { ... },
            "coefficients": {
                "found": bool,
                "source": "LLM knowledge" | "WebFetch: <url>" | "not_found",
                "source_url": str | None,
                "coefficients": {
                    "COEFF_KEY": number | false,
                    ...
                },
                "notes": "..."
            }
        }

    Min/max bounds from data/coefficients_db/<CROP>.json are used only as a
    backend sanity check on candidate values (out-of-range values are
    rejected as `false`) — they are not part of the output.
    """

    AGENT_NAME = "StandaloneCultivarHelperAgent_v3"

    # ========================================================================
    # CROP CODE -> NAME MAPPING
    # ========================================================================
    CROP_MAP = {
        "MZ": "Maize",
        "WH": "Wheat",
        "BA": "Barley",
        "RI": "Rice",
        "SB": "Soybean",
        "PN": "Peanut",
        "SG": "Sorghum",
        "ML": "Millet",
        "SC": "Sugarcane",
        "SU": "Sunflower",
        "PP": "Pigeonpea",
        "CH": "Chickpea",
        "BN": "Dry Bean",
        "CB": "Cabbage",
        "TM": "Tomato",
        "PT": "Potato",
    }

    # ========================================================================
    # MAIN ENTRY POINT
    # ========================================================================

    @staticmethod
    def process(state: Dict[str, Any], verbose: bool = False) -> Dict[str, Any]:
        """
        Main processing function.

        Args:
            state: Plain dictionary containing:
                - config (dict, optional)
                - crop_code (str)
                - crop_name_text (str, optional)
                - location_name (str): free-text location, e.g. "Kaolack, Senegal"
                - generator_model (str, optional): LLM model name
            verbose: If True, print detailed logs. If False, print progress only.

        Returns:
            Updated state with "cultivar_helper_output" added.
        """
        agent = StandaloneCultivarHelperAgent.AGENT_NAME

        def log(msg: str, force: bool = False):
            if verbose or force:
                print(f"[{agent}] {msg}")

        def progress(msg: str):
            """Always printed to show progress."""
            print(f"[{agent}] {msg}")

        progress("Agent started")

        # ====================================================================
        # STEP 1: EXTRACT REQUIRED INPUTS FROM STATE
        # ====================================================================
        config = state.get("config", {}) or {}

        crop_code = state.get("crop_code", "")
        if not crop_code:
            crop_code = (config.get("cultivar", {}) or {}).get("CR", "MZ")
        crop_code = str(crop_code).strip().upper() or "MZ"

        crop_name = state.get("crop_name_text", "")
        if not crop_name:
            crop_name = config.get("crop_name", "")
        if not crop_name:
            crop_name = StandaloneCultivarHelperAgent.CROP_MAP.get(crop_code, crop_code)

        location_name = state.get("location_name", "Unknown Location")

        log(f"📍 Location: {location_name}")
        log(f"🌾 Crop: {crop_name} ({crop_code})")

        # ====================================================================
        # STEP 2: LOAD THIS CROP'S COEFFICIENT SCHEMA + MIN/MAX BOUNDS
        # ====================================================================
        coefficient_bounds = StandaloneCultivarHelperAgent._load_crop_bounds(crop_code)
        coefficient_keys = list(coefficient_bounds.keys())

        if coefficient_keys:
            log(f"📐 Coefficient schema ({len(coefficient_keys)} keys): {', '.join(coefficient_keys)}")
        else:
            log(f"⚠️ No coefficient schema found for crop code '{crop_code}' — coefficients will be skipped")

        # ====================================================================
        # STEP 3: GENERATE CULTIVAR LIST
        # ====================================================================
        progress("Step 1/2: Generating cultivar list for location...")

        cultivar_list = StandaloneCultivarHelperAgent._generate_cultivar_list(
            state, crop_name, crop_code, location_name, verbose=verbose
        )

        if cultivar_list is None:
            msg = "Failed to generate cultivar list"
            state.setdefault("errors", []).append(f"{agent}: {msg}")
            progress(f"❌ {msg}")
            return state

        if len(cultivar_list) == 0:
            progress(f"✅ Location unsuitable for {crop_name} - no cultivars generated")
            state["cultivar_helper_output"] = {}
            state.setdefault("messages", []).append(
                f"{agent}: Location unsuitable - 0 cultivars"
            )
            return state

        progress(f"✅ Generated {len(cultivar_list)} cultivar candidates")
        log(f"   Cultivars: {cultivar_list}")

        # ====================================================================
        # STEP 4: PROCESS EACH CULTIVAR
        # ====================================================================
        progress("Step 2/2: Processing each cultivar...")

        cultivar_results = {}

        for idx, cultivar_name in enumerate(cultivar_list, 1):
            progress(f"  [{idx}/{len(cultivar_list)}] Processing: {cultivar_name}")

            result = StandaloneCultivarHelperAgent._process_single_cultivar(
                state, cultivar_name, crop_name, crop_code, location_name,
                coefficient_keys, coefficient_bounds, verbose=verbose
            )

            cultivar_results[cultivar_name] = result

            coeff_source = result.get("coefficients", {}).get("source", "none")
            log(f"    └─ Coefficients source: {coeff_source}")

        # ====================================================================
        # STEP 5: SAVE RESULTS TO STATE
        # ====================================================================
        state["cultivar_helper_output"] = cultivar_results
        state.setdefault("messages", []).append(
            f"{agent}: Processed {len(cultivar_list)} cultivars"
        )

        summary = StandaloneCultivarHelperAgent._summarize_results(cultivar_results)

        progress(
            f"📊 Summary: {summary['llm_knowledge']} from LLM knowledge, "
            f"{summary['web_paper']} from web papers, "
            f"{summary['not_found']} not found"
        )

        progress("Agent completed")
        return state

    # ========================================================================
    # GENERATE CULTIVAR LIST
    # ========================================================================

    @staticmethod
    def _generate_cultivar_list(
        state: Dict[str, Any],
        crop_name: str,
        crop_code: str,
        location_name: str,
        verbose: bool = False
    ) -> Optional[List[str]]:
        """
        Generate list of suitable cultivars using LLM, grounded with a
        best-effort web search for real released/grown variety names so
        recall isn't limited to pure model memory.
        Returns an empty list if the location is unsuitable (not None).
        """
        agent = StandaloneCultivarHelperAgent.AGENT_NAME

        web_context = StandaloneCultivarHelperAgent._search_web_for_cultivar_names(
            crop_name, location_name, verbose=verbose
        )

        prompt = generate_cultivar_list_prompt(crop_name, crop_code, location_name, web_context)

        gen_model = state.get("generator_model", "gpt-5")

        try:
            if verbose:
                print(f"[{agent}] 🤖 Calling LLM to generate cultivar list (model={gen_model})")

            llm = get_llm(mode="api", model=gen_model)
            response = llm.invoke(prompt)

            clean = strip_markdown_fences(response)
            cultivar_list = json.loads(clean)

            if not isinstance(cultivar_list, list):
                raise ValueError("LLM did not return a list")

            cultivar_list = [c for c in cultivar_list if c and isinstance(c, str)]

            return cultivar_list

        except Exception as e:
            if verbose:
                print(f"[{agent}] ❌ Error generating cultivar list: {e}")
            state.setdefault("errors", []).append(f"{agent}: Failed to generate cultivar list - {e}")
            return None

    @staticmethod
    def _search_web_for_cultivar_names(
        crop_name: str,
        location_name: str,
        verbose: bool = False
    ) -> str:
        """
        Best-effort web search for real cultivar/variety names released or
        grown for this crop near this location, used to ground the cultivar
        list LLM call beyond pure model memory. Uses DDGS result titles +
        snippets directly (no page fetch needed here) — this only has to
        surface candidate names for the LLM to cross-reference, not full
        coefficient tables. Returns "" on any failure (ddgs not installed,
        network error, no results) so the caller just proceeds without it.
        """
        agent = StandaloneCultivarHelperAgent.AGENT_NAME

        try:
            try:
                from ddgs import DDGS
            except ImportError:
                from duckduckgo_search import DDGS
        except ImportError:
            if verbose:
                print(f"[{agent}]   ├─ ddgs not installed, skipping cultivar web search")
            return ""

        queries = [
            f"{crop_name} varieties released {location_name}",
            f"{crop_name} cultivars grown {location_name} extension",
        ]

        snippets: List[str] = []
        for query in queries:
            try:
                if verbose:
                    print(f"[{agent}]   ├─ Cultivar web search: {query}")

                with DDGS() as ddgs:
                    results = list(ddgs.text(query, max_results=6))

                time.sleep(1)  # avoid rate-limiting

                for r in results:
                    title = (r.get("title") or "").strip()
                    body = (r.get("body") or "").strip()
                    if title or body:
                        snippets.append(f"- {title}: {body}")

            except Exception as e:
                if verbose:
                    print(f"[{agent}]   ├─ Cultivar web search error for '{query}': {e}")
                continue

        return "\n".join(snippets[:15])

    # ========================================================================
    # PROCESS SINGLE CULTIVAR
    # ========================================================================

    @staticmethod
    def _process_single_cultivar(
        state: Dict[str, Any],
        cultivar_name: str,
        crop_name: str,
        crop_code: str,
        location_name: str,
        coefficient_keys: List[str],
        coefficient_bounds: Dict[str, Dict[str, Optional[float]]],
        verbose: bool = False
    ) -> Dict[str, Any]:
        """
        Process a single cultivar:
          1. LLM predicts agronomic characteristics (always)
          2. LLM is asked directly for known genotypic coefficients
          3. If nothing found, web search + paper extraction for coefficients

        No local .CUL file matching and no analog/proxy borrowing —
        coefficients come only from the LLM's own knowledge or a real
        published source, the same two mechanisms already used to decide
        cultivars and characteristics.
        """
        agent = StandaloneCultivarHelperAgent.AGENT_NAME

        # ==================================================================
        # STEP A: EXTRACT CHARACTERISTICS (ALWAYS RUNS FIRST)
        # ==================================================================
        if verbose:
            print(f"[{agent}]   ├─ Extracting agronomic characteristics...")

        characteristics = StandaloneCultivarHelperAgent._extract_characteristics(
            state, cultivar_name, crop_name, location_name, verbose=verbose
        )

        # ==================================================================
        # STEP B: ASK THE LLM DIRECTLY FOR KNOWN COEFFICIENTS
        # ==================================================================
        raw_coeffs = None

        if coefficient_keys:
            if verbose:
                print(f"[{agent}]   ├─ Step 1: Asking LLM for known coefficients...")

            raw_coeffs = StandaloneCultivarHelperAgent._get_llm_known_coefficients(
                state, cultivar_name, crop_name, crop_code, coefficient_keys, verbose=verbose
            )

            # ==============================================================
            # STEP C: WEB SEARCH + PAPER EXTRACTION (only if step B found nothing)
            # ==============================================================
            if raw_coeffs is None:
                if verbose:
                    print(f"[{agent}]   ├─ Step 2: Searching web for published coefficients...")

                raw_coeffs = StandaloneCultivarHelperAgent._search_web_for_coefficients(
                    state, cultivar_name, crop_name, crop_code, location_name,
                    coefficient_keys, verbose=verbose
                )
        else:
            if verbose:
                print(f"[{agent}]   ├─ No coefficient schema for crop '{crop_code}' — skipping coefficients")

        # ==================================================================
        # ASSEMBLE FINAL OUTPUT
        # ==================================================================
        raw_values = raw_coeffs.get("coefficients", {}) if raw_coeffs is not None else {}
        values = StandaloneCultivarHelperAgent._assemble_coefficient_values(
            raw_values, coefficient_keys, coefficient_bounds
        )
        found_any = any(v is not False for v in values.values())

        if found_any:
            coefficients = {
                "found": True,
                "source": raw_coeffs["source"],
                "source_url": raw_coeffs.get("source_url"),
                "coefficients": values,
                "notes": raw_coeffs.get("notes", ""),
            }
        else:
            coefficients = {
                "found": False,
                "source": "not_found",
                "source_url": None,
                "coefficients": values,
                "notes": "" if coefficient_keys else f"No coefficient schema available for crop code '{crop_code}'",
            }

        return {
            "cultivar_name": cultivar_name,
            "characteristics": characteristics,
            "coefficients": coefficients,
        }

    # ========================================================================
    # EXTRACT CHARACTERISTICS
    # ========================================================================

    @staticmethod
    def _extract_characteristics(
        state: Dict[str, Any],
        cultivar_name: str,
        crop_name: str,
        location_name: str,
        verbose: bool = False
    ) -> Dict[str, Any]:
        """Extract agronomic characteristics using LLM."""
        agent = StandaloneCultivarHelperAgent.AGENT_NAME

        prompt = extract_characteristics_prompt(crop_name, cultivar_name, location_name)
        gen_model = state.get("generator_model", "gpt-5")

        try:
            llm = get_llm(mode="api", model=gen_model)
            response = llm.invoke(prompt)

            clean = strip_markdown_fences(response)
            result = json.loads(clean)

            # Normalize: ensure we return the nested structure expected
            return {
                "data": result.get("characteristics", {}),
                "source": result.get("source", "LLM prediction"),
                "source_url": result.get("source_url", None),
                "confidence": result.get("confidence", "medium"),
            }

        except Exception as e:
            if verbose:
                print(f"[{agent}]   └─ Error extracting characteristics: {e}")
            return {
                "data": {
                    "maturity_class": "unknown",
                    "error": str(e)
                },
                "source": "Error during extraction",
                "source_url": None,
                "confidence": "low",
            }

    # ========================================================================
    # CROP COEFFICIENT SCHEMA + BOUNDS
    # ========================================================================

    @staticmethod
    def _load_crop_bounds(crop_code: str) -> Dict[str, Dict[str, Optional[float]]]:
        """
        Return {"COEFF_KEY": {"min": x, "max": y}, ...} for this crop's real
        DSSAT model, sourced from data/coefficients_db/<CROP>.json's "bounds"
        section (built from the actual range of values across cultivars
        already in the crop's local .CUL file).

        This also defines exactly which coefficient keys the LLM/web steps
        below are asked to fill in — never a hardcoded CERES-Maize schema.
        Returns {} if the crop has no extracted database (coefficients are
        then skipped entirely for that crop, rather than guessed under the
        wrong schema).
        """
        db = load_coefficients_db(crop_code)
        if not db or "bounds" not in db:
            return {}

        mins = db["bounds"].get("min", {}) or {}
        maxs = db["bounds"].get("max", {}) or {}
        ordered_keys = list(mins.keys()) + [k for k in maxs if k not in mins]

        return {
            key.upper(): {"min": mins.get(key), "max": maxs.get(key)}
            for key in ordered_keys
        }

    @staticmethod
    def _assemble_coefficient_values(
        raw_coefficients: Dict[str, Any],
        coefficient_keys: List[str],
        bounds: Dict[str, Dict[str, Optional[float]]],
    ) -> Dict[str, Any]:
        """
        Build the final per-coefficient value dict: every key in this crop's
        schema always appears — a number if the LLM/web step supplied one
        AND it falls within this crop's real min/max range from
        coefficients_db, else `false`.

        Bounds are a backend-only sanity check here, not part of the
        output: a value outside the crop's known range is far more likely
        to be a hallucinated or wrong-units number than a genuine outlier
        cultivar, so it's rejected rather than surfaced. This keeps the
        output shape a plain {KEY: value_or_false} dict, matching the rest
        of the cultivar DB's format.
        """
        raw_lower = {str(k).lower(): v for k, v in (raw_coefficients or {}).items()}

        values: Dict[str, Any] = {}
        for key in coefficient_keys:
            raw_val = raw_lower.get(key.lower(), False)
            numeric = raw_val if isinstance(raw_val, (int, float)) and not isinstance(raw_val, bool) else False

            if numeric is not False:
                b = bounds.get(key, {})
                lo, hi = b.get("min"), b.get("max")
                if lo is not None and hi is not None:
                    tolerance = max(abs(hi - lo), 1.0) * 0.02  # small slack for rounding noise
                    if numeric < lo - tolerance or numeric > hi + tolerance:
                        numeric = False

            values[key] = numeric

        return values

    # ========================================================================
    # STEP B: ASK THE LLM DIRECTLY FOR KNOWN COEFFICIENTS
    # ========================================================================

    @staticmethod
    def _get_llm_known_coefficients(
        state: Dict[str, Any],
        cultivar_name: str,
        crop_name: str,
        crop_code: str,
        coefficient_keys: List[str],
        verbose: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Step 1 of the coefficient chain: ask the LLM directly whether it
        knows real, credible coefficient values for this cultivar. No file
        or web access — pure model knowledge, the same mechanism already
        used to decide cultivars and characteristics.

        Returns a coefficients dict on success, or None if the LLM reports
        nothing it's confident about.
        """
        agent = StandaloneCultivarHelperAgent.AGENT_NAME

        prompt = get_known_coefficients_prompt(crop_name, crop_code, cultivar_name, coefficient_keys)
        gen_model = state.get("generator_model", "gpt-5")

        try:
            llm = get_llm(mode="api", model=gen_model)
            response = llm.invoke(prompt)

            clean = strip_markdown_fences(response)
            parsed = json.loads(clean)

            if not parsed.get("found_any"):
                return None

            return {
                "source": "LLM knowledge",
                "source_url": None,
                "coefficients": parsed.get("coefficients", {}),
                "notes": parsed.get("notes") or parsed.get("source", ""),
            }

        except Exception as e:
            if verbose:
                print(f"[{agent}]   ├─ Error getting LLM-known coefficients: {e}")
            return None

    # ========================================================================
    # STEP C: WEB SEARCH + FETCH FOR COEFFICIENTS
    # ========================================================================

    @staticmethod
    def _search_web_for_coefficients(
        state: Dict[str, Any],
        cultivar_name: str,
        crop_name: str,
        crop_code: str,
        location_name: str,
        coefficient_keys: List[str],
        verbose: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Step 2 of the coefficient chain: real web search + page fetch.
        Fires DuckDuckGo queries, fetches open-access pages, then asks the
        LLM to extract this crop's real coefficient table (coefficient_keys)
        from the page text. Returns a coefficients dict on success, or None
        on failure.
        """
        agent = StandaloneCultivarHelperAgent.AGENT_NAME

        try:
            try:
                from ddgs import DDGS
            except ImportError:
                from duckduckgo_search import DDGS
        except ImportError:
            if verbose:
                print(f"[{agent}]   ├─ ddgs not installed, skipping web step")
            return None

        gen_model = state.get("generator_model", "gpt-5")

        queries = [
            f'DSSAT {crop_name} "{cultivar_name}" genotypic coefficients',
            f'"{cultivar_name}" DSSAT calibration coefficients',
            f'DSSAT {crop_name} calibration {location_name} coefficients table',
            f'DSSAT CROPGRO {crop_name} cultivar coefficients calibration',
        ]

        # Domains where full text is freely accessible
        OPEN_ACCESS_DOMAINS = [
            "pmc.ncbi.nlm.nih.gov",
            "ncbi.nlm.nih.gov/pmc",
            "plos",
            "biorxiv.org",
            "mdpi.com",
            "frontiersin.org",
            "tandfonline.com",
            "researchgate.net",
            "oar.icrisat.org",
            "cgspace.cgiar.org",
            "core.ac.uk",
            "academia.edu",
            "dssat.net",
        ]

        coeff_tokens = [k.upper() for k in coefficient_keys] + ["genotypic"]

        for query in queries:
            try:
                if verbose:
                    print(f"[{agent}]   ├─ Web search: {query}")

                with DDGS() as ddgs:
                    search_results = list(ddgs.text(query, max_results=8))

                time.sleep(1)  # avoid rate-limiting

                for result in search_results:
                    url = result.get("href", "")
                    if not url:
                        continue

                    is_open = any(domain in url for domain in OPEN_ACCESS_DOMAINS)
                    is_pdf = url.lower().endswith(".pdf")
                    if not is_open and not is_pdf:
                        continue

                    try:
                        resp = requests.get(
                            url, timeout=20,
                            headers={"User-Agent": "Mozilla/5.0 (compatible; research-bot/1.0)"}
                        )
                        if resp.status_code != 200:
                            continue

                        content_type = resp.headers.get("Content-Type", "")
                        if is_pdf or "application/pdf" in content_type:
                            page_text = _extract_pdf_text(resp.content)
                        else:
                            soup = BeautifulSoup(resp.text, "html.parser")
                            page_text = soup.get_text(separator=" ", strip=True)

                        if not page_text:
                            continue  # nothing extractable (e.g. scanned/image PDF)

                        # Pre-filter: page must mention the cultivar or this crop's coefficients
                        has_cultivar = cultivar_name.lower() in page_text.lower()
                        has_coeffs = any(tok in page_text for tok in coeff_tokens)
                        if not (has_cultivar or has_coeffs):
                            continue

                        if verbose:
                            print(f"[{agent}]   ├─ Fetching: {url}")

                        prompt = extract_coefficients_from_paper_prompt(
                            crop_name, crop_code, cultivar_name, coefficient_keys, page_text
                        )
                        llm = get_llm(mode="api", model=gen_model)
                        response = llm.invoke(prompt)
                        clean = strip_markdown_fences(response)
                        parsed = json.loads(clean)

                        if parsed.get("found_any"):
                            return {
                                "source": f"WebFetch: {url}",
                                "source_url": url,
                                "coefficients": parsed.get("coefficients", {}),
                                "notes": parsed.get("notes", "Extracted from published paper"),
                            }

                    except Exception:
                        continue  # try next URL

            except Exception as e:
                if verbose:
                    print(f"[{agent}]   ├─ Web search error for query '{query}': {e}")
                continue  # try next query

        return None  # all queries exhausted without a hit

    # ========================================================================
    # SUMMARIZE RESULTS
    # ========================================================================

    @staticmethod
    def _summarize_results(cultivar_results: Dict[str, Dict]) -> Dict[str, int]:
        """Summarize results by coefficient source (2-step LLM-knowledge / web-search chain)."""
        summary = {
            "llm_knowledge": 0,
            "web_paper": 0,
            "not_found": 0,
        }

        for result in cultivar_results.values():
            coeff = result.get("coefficients", {})
            if not coeff.get("found", False):
                summary["not_found"] += 1
                continue

            source = coeff.get("source", "")
            if source.startswith("WebFetch"):
                summary["web_paper"] += 1
            elif source == "LLM knowledge":
                summary["llm_knowledge"] += 1
            else:
                summary["not_found"] += 1

        return summary

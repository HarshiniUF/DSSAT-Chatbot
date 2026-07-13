from __future__ import annotations

import os
import sys

# 1. Capture the path context of this script ('streamlit_ui' directory)
_current_dir = os.path.dirname(os.path.abspath(__file__))

# 2. Travel up one folder level to find the true project root ('FileX_MultiAgent')
_project_root = os.path.dirname(_current_dir)

# 3. Permanently inject the root directory into the front of Python's search paths
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from dotenv import load_dotenv
# Single project-root .env lives two levels up (dssat_project/.env), not
# inside FileX_MultiAgent -- _project_root above is for sys.path only.
_dssat_project_root = os.path.dirname(_project_root)
load_dotenv(os.path.join(_dssat_project_root, ".env"))

import json
import time
import difflib
from typing import Any, Dict, List, Tuple

import streamlit as st

from utils.helpers import parse_codebook_section
from utils.geo_fetcher import geo_coordinates_search
from utils.cache_manager import SimpleCacheManager
from utils.ui_logger import ui_event
from utils.helpers import get_location

# Import agents
# v2 cultivar agent handles AEZ zone classification, cultivar selection, and CUL file matching
from agents.planting_agent import PlantingAgent
from agents.fertilizer_agent import FertilizerAgent
from agents.irrigation_agent import IrrigationAgent
from agents.residue_agent import ResidueAgent
from agents.field_agent import FieldAgent
from agents.initial_conditions_agent import InitialConditionsAgent
from agents.simulation_control_agent import SimulationControlAgent
from agents.file_assembler_agent import FileAssemblerAgent

import requests
from utils.helpers import get_crop_name
from utils.helpers import validate_xfile_with_xb2


# CultivarAgent is standalone (DB builder) — not part of this workflow.
# FieldAgent handles soil + weather + cultivar resolution from the pre-built DB.
AGENTS = [
    ("FieldAgent", FieldAgent),
    ("PlantingAgent", PlantingAgent),
    ("FertilizerAgent", FertilizerAgent),
    ("IrrigationAgent", IrrigationAgent),
    ("ResidueAgent", ResidueAgent),
    ("InitialConditionsAgent", InitialConditionsAgent),
    ("SimulationControlAgent", SimulationControlAgent),
    ("FileAssemblerAgent", FileAssemblerAgent),
]

# NEW: judge-agent logs should appear inside the parent agent panel
JUDGE_AGENT_TO_PARENT = {
    "JudgePlantingAgent": "PlantingAgent",
    "JudgeFertilizerAgent": "FertilizerAgent",
    "JudgeIrrigationAgent": "IrrigationAgent",
}




# Add this after all imports and before AGENTS definition

def fetch_location_results(place_name: str, geonames_username: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Fetch multiple location results from GeoNames API.
    Returns list of dicts with keys: 'place_name', 'lat', 'lon', 'country', 'admin1', 'fcode'
    This is a Streamlit-aware wrapper that handles errors with st.error()
    """
    try:
        if not place_name or not place_name.strip():
            return []
        
        url = "http://api.geonames.org/searchJSON"
        params = {
            "q": place_name.strip(),
            "maxRows": max_results,
            "username": geonames_username,
            "fuzzy": 0.6,
        }
        
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        
        geonames = data.get("geonames", [])
        if not geonames:
            return []
        
        results = []
        for item in geonames:
            lat = item.get("lat")
            lng = item.get("lng")
            name = item.get("name", "Unknown")
            admin1 = item.get("adminName1", "")  # State/Province
            country = item.get("countryName") or item.get("countryCode", "")
            fcode = item.get("fcode", "")  # Feature code (e.g., PPL for populated place)
            
            if lat is None or lng is None:
                continue
            
            # Build a descriptive place name
            place_parts = [name]
            if admin1 and admin1 != name:
                place_parts.append(admin1)
            
            full_place_name = ", ".join(place_parts)
            
            results.append({
                'place_name': full_place_name,
                'lat': float(lat),
                'lon': float(lng),
                'country': country,
                'admin1': admin1,
                'fcode': fcode
            })
        
        return results
        
    except requests.RequestException as e:
        st.error(f"Network error fetching locations: {e}")
        return []
    except Exception as e:
        st.error(f"Error fetching locations: {e}")
        return []


def _read_file_safe(filename: str) -> Tuple[bool, str]:
    """
    Safely read file content.
    Returns: (success: bool, content: str)
    """
    import os
    
    if not filename or filename == "N/A":
        return False, "File not generated"
    
    if not os.path.exists(filename):
        return False, f"File not found: {filename}"
    
    try:
        with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        return True, content
    except Exception as e:
        return False, f"Error reading file: {e}"


def _load_config(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_state(
    config_path: str,
    place_name: str,
    crop_name: str,
    geonames_username: str,
    enable_cache: bool,
    run_list: List[str],
    enable_judge: bool,
    max_judge_attempts: int,
    generator_model: str,
    judge_model: str,
    year_of_planting:str,
    weather_start_date:str,
    weather_end_date:str,
    latitude:str,
    longitude:str
) -> Dict[str, Any]:
    cultivar_crop_codes = parse_codebook_section("DETAIL.CDE", "Crop and Weed Species")
    planting_PLDS_codes = parse_codebook_section("DETAIL.CDE", "Plant Distribution")
    planting_PLME_codes = parse_codebook_section("DETAIL.CDE", "Planting Material/Method")
    fertilizer_FMCD_codes = parse_codebook_section("DETAIL.CDE", "Fertilizers, Inoculants and Amendments")
    fertilizer_FACD_codes = parse_codebook_section("DETAIL.CDE", "Methods - Fertilizer and Chemical Applications")

    # Keep strict IROP list (as you wanted)
    irrigation_IROP_codes = {
        "IR001": "Furrow, mm",
        "IR002": "Alternating furrows, mm",
        "IR003": "Flood, mm",
        "IR004": "Sprinkler, mm",
        "IR005": "Drip or trickle, mm",
        "IR006": "Flood depth, mm",
        "IR007": "Water table depth, cm",
        "IR008": "Percolation rate, mm day-1",
        "IR009": "Bund height, mm",
        "IR010": "Puddling (for Rice only)",
        "IR011": "Constant flood depth, mm",
    }

    crop_code = crop_name
    matched = get_crop_name(crop_name,cultivar_crop_codes)
    
    # crop_code, matched = _resolve_crop_code(crop_name, cultivar_crop_codes)

    # Handle location input logic - coordinates are already validated and provided
    if latitude and longitude and latitude.strip() and longitude.strip():
        lat = float(latitude.strip())
        lon = float(longitude.strip())
        # place_name is already formatted from selection or manual entry
        if not place_name or not place_name.strip():
            # Fallback: derive place name from coordinates if somehow missing
            place_name = get_location(lat, lon, 'gpt-4o')
    else:
        raise ValueError("Location data is incomplete - this should not happen after validation")



    cfg = _load_config(config_path)
    cfg.setdefault("Location", {})
    cfg["Location"]["place"] = place_name
    cfg["Location"]["Latitude"] = lat
    cfg["Location"]["Longitude"] = lon
    cfg.setdefault("cultivar", {})
    cfg["cultivar"]["CR"] = crop_code
    cfg['crop_growing_season'] = str(year_of_planting)
    cfg['weather']['start_date'] = weather_start_date
    cfg["weather"]['end_date'] = weather_end_date

    cache = SimpleCacheManager(cache_file="cache.json", use_cache=enable_cache)
    cache_key = cache.get_cache_key(config_path=config_path, crop_code=crop_code, lat=lat, lon=lon)

    state: Dict[str, Any] = {
        "config": cfg,
        "messages": [],
        "errors": [],
        "complete_filex": "",

        "cultivar": None,
        "planting": None,
        "fertilizer": None,
        "irrigation": None,
        "residue": None,
        "field": None,
        "initial_conditions": None,
        "simulation_controls": None,
        "treatment": None,

        "crop_code": crop_code,
        "crop_name_text": "",
        "cultivar_name": "",
        "cultivar_ingeno": "",
        "pdate": None,
        "irrig": "N",

        "xcrd": lat,
        "ycrd": lon,
        "location_text": f"{place_name}",

        "planting_PLDS_codes": planting_PLDS_codes,
        "planting_PLME_codes": planting_PLME_codes,
        "cultivar_crop_codes": cultivar_crop_codes,
        "fertilizer_FMCD_codes": fertilizer_FMCD_codes,
        "fertilizer_FACD_codes": fertilizer_FACD_codes,
        "irrigation_IROP_codes": irrigation_IROP_codes,

        "field_metadata": {},

        "planting_config": None,
        "fertilizer_config": None,
        "irrigation_config": None,

        "planting_judge_feedback": None,
        "planting_judge_attempts": 0,
        "fertilizer_judge_feedback": None,
        "fertilizer_judge_attempts": 0,
        "irrigation_judge_feedback": None,
        "irrigation_judge_attempts": 0,

        "enable_judge": enable_judge,
        "max_judge_attempts": int(max_judge_attempts) if enable_judge else 1,

        "cache_manager": cache,
        "cache_key": cache_key,
        "run_list": run_list,
        "config_path": config_path,
        "cultivar_list":None,
        # NEW: your updated agents read these
        "generator_model": generator_model,
        "judge_model": judge_model,

        "_ui": {
            "emit": None,
            "events": [],
            "logs": {},          # ui_log writes here
            "judge_history": {}, # your updated agents append here
            "meta": {
                "matched_crop": matched,
                "cache_key": cache_key,
                "agent_stats": {},  # NEW: persist per-agent time/cache/status for UI replay
            },
        },
    }

    return state


def _safe_tail(lines: List[str], n: int = 120) -> str:
    return "\n".join(lines[-n:])


def _agent_section_text(state: Dict[str, Any], agent_name: str) -> str:
    if agent_name == "PlantingAgent":
        return str(state.get("planting") or "")
    if agent_name == "FertilizerAgent":
        return str(state.get("fertilizer") or "")
    if agent_name == "IrrigationAgent":
        # if rainfed, irrigation object is None; show narrative/config instead
        return str(state.get("irrigation") or "")
    if agent_name == "ResidueAgent":
        return str(state.get("residue") or "")
    if agent_name == "FieldAgent":
        field_text  = str(state.get("field") or "")
        cultivar    = state.get("cultivar")
        if cultivar:
            field_text += f"\n\nCultivar: {cultivar}"
        return field_text
    if agent_name == "InitialConditionsAgent":
        return str(state.get("initial_conditions") or "")
    if agent_name == "SimulationControlAgent":
        return str(state.get("simulation_controls") or "")
    if agent_name == "FileAssemblerAgent":
        return str(state.get("complete_filex") or "")
    return ""


def _agent_config_meta(state: Dict[str, Any], agent_name: str) -> Dict[str, Any]:
    if agent_name == "PlantingAgent":
        return {
            "planting_config": state.get("planting_config"),
            "planting_narrative": state.get("planting_narrative"),
            "attempts": state.get("planting_judge_attempts"),
        }
    if agent_name == "FertilizerAgent":
        return {
            "fertilizer_config": state.get("fertilizer_config"),
            "fertilizer_narrative": state.get("fertilizer_narrative"),
            "attempts": state.get("fertilizer_judge_attempts"),
        }
    if agent_name == "IrrigationAgent":
        return {
            "irrigation_config": state.get("irrigation_config"),
            "irrigation_narrative": state.get("irrigation_narrative"),
            "irrig_flag": state.get("irrig"),
            "attempts": state.get("irrigation_judge_attempts"),
        }
    if agent_name == "FieldAgent":
        return {
            "field_metadata":  state.get("field_metadata"),
            "crop_code":       state.get("crop_code"),
            "cultivar_name":   state.get("cultivar_name"),
            "cultivar_ingeno": state.get("cultivar_ingeno"),
        }

    return {"note": "No dedicated meta view for this agent yet."}


def main() -> None:
    st.set_page_config(page_title="DSSAT File-X Generator", page_icon="🌱", layout="wide")

    st.title("🌱 DSSAT File-X Generator")
    st.caption("Live agent pipeline UI (status + logs + judge + DSSAT sections) over your existing code.")

    # NEW: session persistence so download reruns don't wipe the dashboard
    if "last_state" not in st.session_state:
        st.session_state["last_state"] = None
    if "last_output_filename" not in st.session_state:
        st.session_state["last_output_filename"] = None
    if "last_inputs" not in st.session_state:
        st.session_state["last_inputs"] = None

    with st.sidebar:
        st.subheader("⚙️ Settings")

        enable_judge = st.toggle("Enable judge", value=False)
        enable_cache = st.toggle("Enable cache", value=True)
        max_judge_attempts = st.slider("Judge attempts", 1, 5, 2, disabled=not enable_judge)

        st.divider()
        generator_model = st.selectbox("Generator model", ["gpt-5", "gpt-4o", "gpt-4.1"], index=0)
        judge_model = st.selectbox("Judge model", ["gpt-5", "gpt-4o", "gpt-4.1"], index=0)

        st.divider()
        agent_names = [a for a, _ in AGENTS if a != "FileAssemblerAgent"]
        run_list = st.multiselect("Force re-run agents", ["ALL"] + agent_names, default=["ALL"])
        if "ALL" in run_list and len(run_list) > 1:
            run_list = ["ALL"]

        st.divider()
        # Output filename is auto-derived from the generated FileX experiment name
        output_filename = "OUTPUT.SNX"  # placeholder, overridden after pipeline generates FileX

        st.divider()
        geonames_username = st.text_input("GeoNames api username", value="keerthikattamudi")

    config_path = "Input_config_test1.json"

    st.info("📍 **Location Input**: Enter place name and search, OR enter coordinates directly")

    # Initialize session state for location search
    if 'location_results' not in st.session_state:
        st.session_state.location_results = []
    if 'selected_location_idx' not in st.session_state:
        st.session_state.selected_location_idx = None
    if 'search_triggered' not in st.session_state:
        st.session_state.search_triggered = False
    if 'location_confirmed' not in st.session_state:
        st.session_state.location_confirmed = False

    # Callback to clear coordinates when place name is entered
    def on_place_name_change():
        st.session_state.search_triggered = False
        st.session_state.location_confirmed = False
        st.session_state.selected_location_idx = None

    # Callback to clear place name when coordinates are entered
    def on_coordinates_change():
        st.session_state.search_triggered = False
        st.session_state.location_confirmed = False
        st.session_state.selected_location_idx = None

    col_place, col_or, col_coords = st.columns([2, 0.3, 2])

    with col_place:
        place_name = st.text_input(
            "📍 Location name", 
            placeholder="e.g., Nairobi, Kenya",
            help="Enter a place name and click Search",
            key="place_name_input",
            on_change=on_place_name_change
        )
        
        # Center the search button
        btn_col1, btn_col2, btn_col3 = st.columns([1, 2, 1])
        with btn_col2:
            search_button = st.button("🔍 Search Location", disabled=not place_name or not place_name.strip(), use_container_width=True)

    with col_or:
        st.markdown("<div style='text-align: center; padding-top: 30px;'><strong>OR</strong></div>", unsafe_allow_html=True)

    with col_coords:
        col_lat, col_lon = st.columns(2)
        with col_lat:
            latitude = st.text_input(
                "Latitude", 
                placeholder="-1.286389",
                help="Enter latitude and click Search Coordinates",
                disabled=bool(place_name and place_name.strip()),
                key="latitude_input",
                on_change=on_coordinates_change
            )
        with col_lon:
            longitude = st.text_input(
                "Longitude", 
                placeholder="36.817223",
                help="Enter longitude and click Search Coordinates",
                disabled=bool(place_name and place_name.strip()),
                key="longitude_input",
                on_change=on_coordinates_change
            )
        
        # Validate coordinates before enabling search button
        coords_valid = False
        if latitude and latitude.strip() and longitude and longitude.strip():
            try:
                float(latitude.strip())
                float(longitude.strip())
                coords_valid = True
            except ValueError:
                pass
        
        # Center the search coordinates button
        btn_col1, btn_col2, btn_col3 = st.columns([1, 2, 1])
        with btn_col2:
            search_coords_button = st.button("🔍 Search Coordinates", disabled=not coords_valid, use_container_width=True)



    # Handle search button click
    # if search_button:
    #     with st.spinner("Searching locations..."):
    #         st.session_state.location_results = fetch_location_results(
    #             place_name.strip(), 
    #             geonames_username, 
    #             max_results=5
    #         )
    #         st.session_state.search_triggered = True
    #         st.session_state.selected_location_idx = None
    #         st.session_state.location_confirmed = False

    # Handle search button click (for place name)
    if search_button:
        with st.spinner("Searching locations..."):
            st.session_state.location_results = fetch_location_results(
                place_name.strip(), 
                geonames_username, 
                max_results=5
            )
            st.session_state.search_triggered = True
            st.session_state.selected_location_idx = None
            st.session_state.location_confirmed = False

    # Handle search coordinates button click
    if search_coords_button:
        with st.spinner("Fetching location name..."):
            try:
                lat_val = float(latitude.strip())
                lon_val = float(longitude.strip())
                
                # Use get_location to reverse geocode
                location_name = get_location(lat_val, lon_val, 'gpt-4o')
                
                # Create a single result entry
                st.session_state.location_results = [{
                    'place_name': location_name.split(',')[0] if ',' in location_name else location_name,
                    'lat': lat_val,
                    'lon': lon_val,
                    'country': location_name.split(',')[-1].strip() if ',' in location_name else "Unknown",
                    'admin1': location_name.split(',')[1].strip() if location_name.count(',') >= 2 else "",
                    'fcode': 'COORD'  # Special marker for coordinate-based search
                }]
                st.session_state.search_triggered = True
                st.session_state.selected_location_idx = None
                st.session_state.location_confirmed = False
            except Exception as e:
                st.error(f"Error fetching location: {e}")
                st.session_state.location_results = []
                st.session_state.search_triggered = False

    # Display search results in a scrollable container
    if st.session_state.search_triggered and st.session_state.location_results:
        st.markdown("### 📍 Select a Location")
        
        # Create scrollable container with results
        results_container = st.container(height=250, border=True)
        
        with results_container:
            for idx, loc in enumerate(st.session_state.location_results):
                col_check, col_info = st.columns([0.5, 9.5])
                
                with col_check:
                    is_selected = st.checkbox(
                        "",
                        key=f"loc_checkbox_{idx}",
                        value=(st.session_state.selected_location_idx == idx),
                        label_visibility="collapsed"
                    )
                    
                    if is_selected and st.session_state.selected_location_idx != idx:
                        # Uncheck all others
                        st.session_state.selected_location_idx = idx
                        st.session_state.location_confirmed = True
                        st.rerun()
                    elif not is_selected and st.session_state.selected_location_idx == idx:
                        st.session_state.selected_location_idx = None
                        st.session_state.location_confirmed = False
                        st.rerun()
                
                with col_info:
                    # Enhanced display with feature code info
                    feature_emoji = "🏙️" if loc.get('fcode', '').startswith('PPL') else "📍"
                    st.markdown(f"""
                    {feature_emoji} **{loc['place_name']}**, {loc['country']}  
                    📐 Lat: `{loc['lat']:.4f}`, Lon: `{loc['lon']:.4f}`
                    """)
                
                if idx < len(st.session_state.location_results) - 1:
                    st.divider()
        
        # Show confirmation message
        if st.session_state.selected_location_idx is not None:
            selected = st.session_state.location_results[st.session_state.selected_location_idx]
            st.success(f"✅ Selected: **{selected['place_name']}, {selected['country']}** (Lat: {selected['lat']:.4f}, Lon: {selected['lon']:.4f})")

    elif st.session_state.search_triggered and not st.session_state.location_results:
        st.warning("⚠️ No locations found. Please try a different search term.")

    # Optional: Add clear search button
    if st.session_state.search_triggered:
        if st.button("🔄 Clear Search & Start Over"):
            st.session_state.location_results = []
            st.session_state.selected_location_idx = None
            st.session_state.search_triggered = False
            st.session_state.location_confirmed = False
            st.rerun()




    colX, colZ = st.columns([1.0,1.0])

    with colX:
        crop_name = st.text_input("🌾 Crop code", value="MZ",placeholder="enter crop code..")

    colC, colD, colE = st.columns([1.0, 1.0, 1.0])

    with colC:
        year_of_planting = st.number_input("Crop growing season", value=2025, min_value=1900, max_value=2100, step=1, format="%d", help="Year you want to predict for")
    with colD:
        weather_start_date = st.text_input("Weather start date", value="2024-01-01")  
    with colE:
        weather_end_date = st.text_input("Weather end date",value="2025-12-31")


    # Validate location input
# UPDATED: Validate location input
    location_valid = False
    location_error = None
    final_place_name = place_name
    final_latitude = latitude
    final_longitude = longitude

    # Check if location is confirmed
    if st.session_state.location_confirmed:
        if st.session_state.selected_location_idx is not None:
            # User selected from search results
            selected = st.session_state.location_results[st.session_state.selected_location_idx]
            final_place_name = f"{selected['place_name']}, {selected['country']}"
            final_latitude = str(selected['lat'])
            final_longitude = str(selected['lon'])
            location_valid = True
        else:
            location_error = "⚠️ Please select a location from search results"
    else:
        if place_name and place_name.strip():
            location_error = "⚠️ Please click 'Search Location' and select a result"
        elif (latitude and latitude.strip()) or (longitude and longitude.strip()):
            if not (latitude and latitude.strip() and longitude and longitude.strip()):
                location_error = "⚠️ Please provide BOTH latitude and longitude"
            else:
                location_error = "⚠️ Please click 'Search Coordinates' and select the result"
        else:
            location_error = "⚠️ Please provide either a place name OR coordinates"

    if location_error:
        st.error(location_error)

    # Validate cropping season year against weather date range
    season_valid = True
    try:
        ws_year = int(weather_start_date.split("-")[0])
        we_year = int(weather_end_date.split("-")[0])
        if not (ws_year <= year_of_planting <= we_year):
            season_valid = False
            st.error(
                f"Cropping season year ({year_of_planting}) must be between "
                f"weather start year ({ws_year}) and weather end year ({we_year})."
            )
    except (ValueError, IndexError):
        season_valid = False
        st.error("Invalid weather date format. Expected YYYY-MM-DD.")

    run = st.button("🚀 Generate File-X", type="primary", use_container_width=True, disabled=not location_valid or not season_valid)


    st.divider()

    resolved_block = st.container()

    progress_bar = st.progress(0, text="waiting for user input")
    agent_area = st.container()
    generated_files_area = st.container()
    validation_area = st.container()
    final_area = st.container()

    # UI blocks
    status_blocks: Dict[str, Any] = {}
    status_lines: Dict[str, Any] = {}
    cache_lines: Dict[str, Any] = {}
    time_lines: Dict[str, Any] = {}

    log_blocks: Dict[str, Any] = {}
    judge_blocks: Dict[str, Any] = {}
    meta_blocks: Dict[str, Any] = {}
    section_blocks: Dict[str, Any] = {}

    with agent_area:
        st.subheader("✅ Agent Execution (live)")
        st.caption("Each agent is collapsible: spinner while running, ✅ on success, ❌ on error.")
        st.divider()

        for agent_name, _cls in AGENTS:
            status_blocks[agent_name] = st.status(
                label=agent_name,
                state="running",
                expanded=False,
            )

            with status_blocks[agent_name]:
                cols = st.columns([1.2, 1.0, 0.8])
                status_lines[agent_name] = cols[0].empty()
                cache_lines[agent_name] = cols[1].empty()
                time_lines[agent_name] = cols[2].empty()

                status_lines[agent_name].markdown("**Status**: pending")
                cache_lines[agent_name].markdown("**Cache**: —")
                time_lines[agent_name].markdown("**Time**: —")

                tabs = st.tabs(["🧾 Logs", "🧠 Judge", "📦 Config/Meta", "🧩 Section Output"])
                with tabs[0]:
                    log_blocks[agent_name] = st.empty()
                with tabs[1]:
                    judge_blocks[agent_name] = st.empty()
                with tabs[2]:
                    meta_blocks[agent_name] = st.empty()
                with tabs[3]:
                    section_blocks[agent_name] = st.empty()

    def _append_log(agent_key: str, line: str, state: Dict[str, Any]) -> None:
        state.setdefault("_ui", {}).setdefault("logs", {}).setdefault(agent_key, []).append(line)

    def _refresh_agent_panels(state: Dict[str, Any], agent_key: str) -> None:
        # logs
        if agent_key in log_blocks:
            lines = state.get("_ui", {}).get("logs", {}).get(agent_key, []) or []
            log_blocks[agent_key].code(_safe_tail(lines, 160), language="text")

        # judge (show last feedback)
        if agent_key in judge_blocks:
            hist = state.get("_ui", {}).get("judge_history", {}).get(agent_key, []) or []
            if hist:
                judge_blocks[agent_key].json(hist[-1])
            else:
                judge_blocks[agent_key].info("No judge output yet.")

        # meta
        if agent_key in meta_blocks:
            meta_blocks[agent_key].json(_agent_config_meta(state, agent_key))

        # section output
        if agent_key in section_blocks:
            txt = _agent_section_text(state, agent_key)
            if txt.strip():
                section_blocks[agent_key].code(txt, language="text")
            else:
                section_blocks[agent_key].info("No section text yet (or section is intentionally empty).")

    # def _render_dashboard_from_saved_state(saved_state: Dict[str, Any], saved_output_filename: str) -> None:
    #     stats = (saved_state.get("_ui", {}).get("meta", {}) or {}).get("agent_stats", {}) or {}
    #     errors = saved_state.get("errors", []) or []

    #     def _agent_failed(agent_name: str) -> bool:
    #         prefix = f"{agent_name}:"
    #         return any(str(e).startswith(prefix) for e in errors)

    #     for agent_name, _cls in AGENTS:
    #         has_stats = agent_name in stats
    #         failed = _agent_failed(agent_name)

    #         if failed:
    #             status_blocks[agent_name].update(label=f"{agent_name} — failed ❌", state="error", expanded=True)
    #             status_lines[agent_name].markdown("**Status**: FAILED ❌")
    #         elif has_stats and stats[agent_name].get("ok") is True:
    #             status_blocks[agent_name].update(label=f"{agent_name} — done ✅", state="complete", expanded=False)
    #             status_lines[agent_name].markdown("**Status**: OK ✅")
    #         elif has_stats:
    #             status_blocks[agent_name].update(label=f"{agent_name} — ran", state="complete", expanded=False)
    #             status_lines[agent_name].markdown("**Status**: OK ✅")
    #         else:
    #             status_blocks[agent_name].update(label=f"{agent_name} — pending", state="running", expanded=False)
    #             status_lines[agent_name].markdown("**Status**: pending")

    #         cache_used = None
    #         dt = None
    #         if has_stats:
    #             cache_used = stats[agent_name].get("cache_used")
    #             dt = stats[agent_name].get("dt")

    #         cache_lines[agent_name].markdown(
    #             f"**Cache**: {'📦 used' if cache_used else ('🚀 ran' if cache_used is False else '—')}"
    #         )
    #         time_lines[agent_name].markdown(f"**Time**: {dt}s" if dt is not None else "**Time**: —")

    #         _refresh_agent_panels(saved_state, agent_name)

        

    #     # Display Soil and Weather Files
    #     with generated_files_area:
    #         field_metadata = saved_state.get("field_metadata", {})
    #         metadata = field_metadata.get("metadata", {})
            
    #         sol_file = metadata.get("sol_file", "N/A")
    #         wth_file = metadata.get("wth_file", "N/A")
            
    #         st.subheader("📁 Generated Files")
            
    #         col_soil, col_weather = st.columns([1,1])
                
    #         with col_soil:
    #             with st.expander("🌍 Soil File", expanded=False):
    #                 success, content = _read_file_safe(sol_file)
                    
    #                 if success:
    #                     st.download_button(
    #                         "⬇️ Download Soil File",
    #                         data=content.encode("utf-8"),
    #                         file_name=sol_file,
    #                         mime="text/plain",
    #                         use_container_width=True,
    #                         key="download_soil_main"
    #                     )
    #                     st.code(content, language="text", line_numbers=False)
    #                 else:
    #                     st.warning(f"⚠️ {content}")
            
    #         with col_weather:
    #             with st.expander("🌦️ Weather File", expanded=False):
    #                 success, content = _read_file_safe(wth_file)
                    
    #                 if success:
    #                     st.download_button(
    #                         "⬇️ Download Weather File",
    #                         data=content.encode("utf-8"),
    #                         file_name=wth_file,
    #                         mime="text/plain",
    #                         use_container_width=True,
    #                         key="download_weather_main"
    #                     )
    #                     st.code(content, language="text", line_numbers=False)

    #                 else:
    #                     st.warning(f"⚠️ {content}")
            
    #         st.divider()


    #     with final_area:
    #         st.subheader("📄 Final DSSAT File-X")
    #         filex = saved_state.get("complete_filex", "") or ""
    #         if not filex.strip():
    #             st.warning("No File-X generated.")
    #         else:
    #             box = st.container(height=520, border=True)
    #             box.code(filex, language="text")
    #             st.download_button(
    #                 "⬇️ Download File-X",
    #                 data=filex.encode("utf-8"),
    #                 file_name=saved_output_filename,
    #                 mime="text/plain",
    #                 use_container_width=True,
    #             )

    #         if saved_state.get("errors"):
    #             st.error("Errors:")
    #             for e in saved_state["errors"]:
    #                 st.write(f"• {e}")


    def _render_dashboard_from_saved_state(saved_state: Dict[str, Any], saved_output_filename: str) -> None:
        stats = (saved_state.get("_ui", {}).get("meta", {}) or {}).get("agent_stats", {}) or {}
        errors = saved_state.get("errors", []) or []

        def _agent_failed(agent_name: str) -> bool:
            prefix = f"{agent_name}:"
            return any(str(e).startswith(prefix) for e in errors)

        for agent_name, _cls in AGENTS:
            has_stats = agent_name in stats
            failed = _agent_failed(agent_name)

            if failed:
                status_blocks[agent_name].update(label=f"{agent_name} — failed ❌", state="error", expanded=True)
                status_lines[agent_name].markdown("**Status**: FAILED ❌")
            elif has_stats and stats[agent_name].get("ok") is True:
                status_blocks[agent_name].update(label=f"{agent_name} — done ✅", state="complete", expanded=False)
                status_lines[agent_name].markdown("**Status**: OK ✅")
            elif has_stats:
                status_blocks[agent_name].update(label=f"{agent_name} — ran", state="complete", expanded=False)
                status_lines[agent_name].markdown("**Status**: OK ✅")
            else:
                status_blocks[agent_name].update(label=f"{agent_name} — pending", state="running", expanded=False)
                status_lines[agent_name].markdown("**Status**: pending")

            cache_used = None
            dt = None
            if has_stats:
                cache_used = stats[agent_name].get("cache_used")
                dt = stats[agent_name].get("dt")

            cache_lines[agent_name].markdown(
                f"**Cache**: {'📦 used' if cache_used else ('🚀 ran' if cache_used is False else '—')}"
            )
            time_lines[agent_name].markdown(f"**Time**: {dt}s" if dt is not None else "**Time**: —")

            _refresh_agent_panels(saved_state, agent_name)

        # Display Soil and Weather Files
        with generated_files_area:
            field_metadata = saved_state.get("field_metadata", {})
            metadata = field_metadata.get("metadata", {})
            
            sol_file = metadata.get("sol_file", "N/A")
            wth_file = metadata.get("wth_file", "N/A")
            
            st.subheader("📁 Generated Files")
            
            col_soil, col_weather = st.columns([1,1])
                
            with col_soil:
                with st.expander("🌍 Soil File", expanded=False):
                    success, content = _read_file_safe(sol_file)
                    
                    if success:
                        st.download_button(
                            "⬇️ Download Soil File",
                            data=content.encode("utf-8"),
                            file_name=sol_file,
                            mime="text/plain",
                            use_container_width=True,
                            key="download_soil_replay"
                        )
                        st.code(content, language="text", line_numbers=False)
                    else:
                        st.warning(f"⚠️ {content}")
            
            with col_weather:
                with st.expander("🌦️ Weather File", expanded=False):
                    success, content = _read_file_safe(wth_file)
                    
                    if success:
                        st.download_button(
                            "⬇️ Download Weather File",
                            data=content.encode("utf-8"),
                            file_name=wth_file,
                            mime="text/plain",
                            use_container_width=True,
                            key="download_weather_replay"
                        )
                        st.code(content, language="text", line_numbers=False)
                    else:
                        st.warning(f"⚠️ {content}")
            
            st.divider()

        # Render saved validation status in validation_area
        with validation_area:
            xb2_result = saved_state.get('_ui', {}).get('xb2_validation')
            if xb2_result:
                validation_status = st.status(
                    label="XB2 Validation — " + ("passed ✅" if xb2_result['success'] else "failed ❌"),
                    state="complete" if xb2_result['success'] else "error",
                    expanded=False,
                )
                
                with validation_status:
                    if xb2_result['success']:
                        st.success("✅ XB2 Validation PASSED")
                        with st.expander("📋 View Validation Details"):
                            st.code(xb2_result['stdout'], language="text")
                    else:
                        st.error("❌ XB2 Validation FAILED")
                        st.code(xb2_result['stdout'], language="text")
                        if xb2_result['stderr']:
                            st.code(xb2_result['stderr'], language="text")

        # NEW: Display xb2 Validation BEFORE final File-X
        xb2_result = saved_state.get('_ui', {}).get('xb2_validation')

        # Final File-X Display - ONLY if validation passed
        with final_area:
            # Check if validation exists and passed
            validation_passed = xb2_result and xb2_result['success']
            
            if not xb2_result:
                # No validation was run (shouldn't happen, but handle it)
                st.warning("⚠️ xb2 validation was not performed")

                if saved_state.get("errors"):
                    with st.expander("❌ View All Errors"):
                        for e in saved_state["errors"]:
                            st.write(f"• {e}")
            elif not validation_passed:
                # Validation failed - don't show file
                st.error("🚫 File-X cannot be downloaded due to validation errors. Please review the validation results above and fix the issues.")

                # Optionally show what errors occurred
                if saved_state.get("errors"):
                    with st.expander("❌ View All Errors"):
                        for e in saved_state["errors"]:
                            st.write(f"• {e}")
            else:
                # Validation passed - show file
                st.subheader("📄 Final DSSAT File-X (Validated ✅)")
                filex = saved_state.get("complete_filex", "") or ""
                
                if not filex.strip():
                    st.warning("No File-X generated.")
                else:
                    box = st.container(height=520, border=True)
                    box.code(filex, language="text")
                    st.download_button(
                        "⬇️ Download File-X",
                        data=filex.encode("utf-8"),
                        file_name=saved_output_filename,
                        mime="text/plain",
                        use_container_width=True,
                    )

                if saved_state.get("errors"):
                    with st.expander("❌ View All Errors"):
                        for e in saved_state["errors"]:
                            st.write(f"• {e}")



    # If user didn't click run, replay the last dashboard + final output (prevents reset on download rerun)
    if not run:
        if st.session_state["last_state"] is None:
            st.info("Set inputs and click **Generate File-X**.")
            return

        saved_output_filename = st.session_state["last_output_filename"] or output_filename
        progress_bar.progress(100, text="Loaded previous run (dashboard preserved)")
        _render_dashboard_from_saved_state(st.session_state["last_state"], saved_output_filename)
        return

    try:

        state = build_state(
            config_path=config_path,
            place_name=final_place_name,  # CHANGED from place_name
            crop_name=crop_name,
            geonames_username=geonames_username,
            enable_cache=enable_cache,
            run_list=run_list,
            enable_judge=enable_judge,
            max_judge_attempts=max_judge_attempts,
            generator_model=generator_model,
            judge_model=judge_model,
            year_of_planting=year_of_planting,
            weather_start_date=weather_start_date,
            weather_end_date=weather_end_date,
            latitude=final_latitude,  # CHANGED from latitude
            longitude=final_longitude  # CHANGED from longitude
        )

    except Exception as e:
        st.error(f"Failed to initialize run: {e}")
        return
    

    with resolved_block:
        st.success("✅ Inputs resolved")
        
        # First row - Place takes full width
        st.metric("📍 Place", state.get("location_text", "—"))
        
        # Second row - Latitude, Longitude, Crop in 3 columns
        c2, c3, c4 = st.columns(3)
        c2.metric("🌐 Latitude", f'{state.get("xcrd", "—"):.4f}')
        c3.metric("🌐 Longitude", f'{state.get("ycrd", "—"):.4f}')
        c4.metric("🌾 Crop", state.get("crop_code", "—"))

   

        st.divider()

    def emit(payload: Dict[str, Any]) -> None:
        src_agent = payload.get("agent", "UNKNOWN")
        kind = payload.get("kind", "")
        msg = payload.get("message", "")

        # NEW: map judge agents into their parent agent panels
        parent_agent = JUDGE_AGENT_TO_PARENT.get(src_agent, src_agent)

        # If the event came from a judge agent, copy its line into parent logs (so user sees it)
        if src_agent in JUDGE_AGENT_TO_PARENT:
            _append_log(parent_agent, f"[{src_agent}] {kind}: {msg}", state)

        # Also ensure the source agent message is visible in parent logs when it’s a normal agent
        if src_agent == parent_agent and kind in ("error", "info", "step", "cache", "judge", "output"):
            _append_log(parent_agent, f"{kind}: {msg}", state)

        # refresh parent panels
        if parent_agent in status_blocks:
            _refresh_agent_panels(state, parent_agent)

    state["_ui"]["emit"] = emit

    st.toast("Run started ✅", icon="🚀")

    total = len(AGENTS)

    for idx, (agent_name, agent_cls) in enumerate(AGENTS, start=1):
        t0 = time.time()

        status_blocks[agent_name].update(label=f"{agent_name} — running…", state="running", expanded=True)
        ui_event(state, agent=agent_name, kind="info", message="Agent started")

        progress_bar.progress(int((idx - 1) / total * 100), text=f"Running {agent_name} ({idx}/{total})")

        try:
            state = agent_cls.process(state)
            ok = True
        except Exception as e:
            ok = False
            state.setdefault("errors", []).append(f"{agent_name}: {e}")
            ui_event(state, agent=agent_name, kind="error", message=str(e))

        dt = round(time.time() - t0, 2)

        # detect cache usage from UI events
        cache_used = False
        for ev in (state.get("_ui", {}).get("events", []) or [])[-80:]:
            if ev.get("agent") == agent_name and ev.get("kind") == "cache" and ev.get("message") == "Loaded from cache":
                cache_used = True
                break

        # NEW: persist per-agent UI stats for replay after reruns (download button causes rerun)
        state.setdefault("_ui", {}).setdefault("meta", {}).setdefault("agent_stats", {})[agent_name] = {
            "ok": ok,
            "dt": dt,
            "cache_used": cache_used,
        }

        # finalize status + refresh panels one last time for this agent
        if ok:
            status_blocks[agent_name].update(label=f"{agent_name} — done ✅", state="complete", expanded=False)
            st.toast(f"{agent_name} done", icon="✅")
        else:
            status_blocks[agent_name].update(label=f"{agent_name} — failed ❌", state="error", expanded=True)
            st.toast(f"{agent_name} failed", icon="❌")

        status_lines[agent_name].markdown(f"**Status**: {'OK ✅' if ok else 'FAILED ❌'}")
        cache_lines[agent_name].markdown(f"**Cache**: {'📦 used' if cache_used else '🚀 ran'}")
        time_lines[agent_name].markdown(f"**Time**: {dt}s")

        _refresh_agent_panels(state, agent_name)

        if not ok:
            break


        # NEW: xb2 Validation Step (runs whenever a FileX was actually generated,
        # even if earlier agents logged non-fatal warnings into state["errors"])
    if not (state.get("complete_filex") or "").strip():
        progress_bar.progress(100, text="Pipeline finished with errors")
    else:
        progress_bar.progress(95, text="Running XB2 validation...")
        
        with validation_area:
            # Create validation status block
            validation_status = st.status(
                label="XB2 Validation",
                state="running",
                expanded=True,
            )

            filex = state.get("complete_filex", "")
            if not filex.strip():
                raise RuntimeError("No File-X generated by FileAssemblerAgent; cannot run XB2 validation.")

            first_line = filex.strip().splitlines()[0]
            if first_line.startswith("*EXP.DETAILS:"):
                exp_name = first_line.split(":", 1)[1].strip()
                output_filename = f"{exp_name}.SNX"

            st.info(f"Generated FileX experiment file: **{output_filename}**")

            # Write the freshly generated FileX to disk as XB2 input
            with open(output_filename, "w", encoding="utf-8") as f:
                f.write(filex)

            
            with validation_status:
                st.info("🔍 Validating generated File-X with XB2...")
                
                try:
                    # Run xb2 validation - overwrites the output file
                    validation_result = validate_xfile_with_xb2(
                        input_file_path=output_filename,
                        output_file_path=output_filename  # Same file - will be overwritten if valid
                    )

                    state['_ui']['xb2_validation'] = {
                        'success': validation_result['success'],
                        'stdout': validation_result['stdout'],
                        'stderr': validation_result['stderr'],
                        'exit_code': validation_result['exit_code']
                    }
                    
                    if validation_result['success']:
                        validation_status.update(
                            label="xb2 Validation — passed ✅",
                            state="complete",
                            expanded=False
                        )
                        st.success("✅ xb2 Validation PASSED - File has been validated and saved")
                        
                        # Update state with validated file
                        with open(output_filename, 'r') as f:
                            state['complete_filex'] = f.read()
                        
                        # Show validation output in expander
                        with st.expander("📋 View Validation Details"):
                            st.code(validation_result['stdout'], language="text")
                    else:
                        validation_status.update(
                            label="xb2 Validation — failed ❌",
                            state="error",
                            expanded=True
                        )
                        st.error("❌ xb2 Validation FAILED - File has validation errors")
                        
                        # Show validation errors
                        st.code(validation_result['stdout'], language="text")
                        if validation_result['stderr']:
                            st.code(validation_result['stderr'], language="text")
                        
                        state.setdefault("errors", []).append(f"xb2 Validation failed: {validation_result['stderr']}")
                        
                except Exception as e:

                    # ⭐ Store error in state
                    state['_ui']['xb2_validation'] = {
                        'success': False,
                        'stdout': '',
                        'stderr': str(e),
                        'exit_code': -1
                    }

                    validation_status.update(
                        label="xb2 Validation — error ❌",
                        state="error",
                        expanded=True
                    )
                    st.error(f"❌ xb2 Validation error: {e}")
                    state.setdefault("errors", []).append(f"xb2 Validation error: {e}")
        
        progress_bar.progress(100, text="Pipeline finished")

    # progress_bar.progress(100, text="Pipeline finished")

    # # NEW: save the entire dashboard state so it can be replayed after reruns (e.g., download click)
    # st.session_state["last_state"] = state
    # st.session_state["last_output_filename"] = output_filename
    # st.session_state["last_inputs"] = {
    #     "config_path": config_path,
    #     "place_name": place_name,
    #     "crop_name": crop_name,
    #     "geonames_username": geonames_username,
    #     "enable_cache": enable_cache,
    #     "run_list": run_list,
    #     "enable_judge": enable_judge,
    #     "max_judge_attempts": max_judge_attempts,
    #     "generator_model": generator_model,
    #     "judge_model": judge_model,
    # }

    #     # Display Soil and Weather Files
    # with generated_files_area:
    #     field_metadata = state.get("field_metadata", {})
    #     metadata = field_metadata.get("metadata", {})
        
    #     sol_file = metadata.get("sol_file", "N/A")
    #     wth_file = metadata.get("wth_file", "N/A")
        
    #     st.subheader("📁 Generated Files")
        
    #     col_soil, col_weather = st.columns([1,1])
            
    #     with col_soil:
    #         with st.expander("🌍 Soil File", expanded=False):
    #             success, content = _read_file_safe(sol_file)
                
    #             if success:
    #                 st.download_button(
    #                     "⬇️ Download Soil File",
    #                     data=content.encode("utf-8"),
    #                     file_name=sol_file,
    #                     mime="text/plain",
    #                     use_container_width=True,
    #                     key="download_soil_main"
    #                 )
    #                 st.code(content, language="text", line_numbers=False)
    #             else:
    #                 st.warning(f"⚠️ {content}")
        
    #     with col_weather:
    #         with st.expander("🌦️ Weather File", expanded=False):
    #             success, content = _read_file_safe(wth_file)
                
    #             if success:
    #                 st.download_button(
    #                     "⬇️ Download Weather File",
    #                     data=content.encode("utf-8"),
    #                     file_name=wth_file,
    #                     mime="text/plain",
    #                     use_container_width=True,
    #                     key="download_weather_main"
    #                 )
    #                 st.code(content, language="text", line_numbers=False)

    #             else:
    #                 st.warning(f"⚠️ {content}")
        
    #     st.divider()

    # with final_area:
    #     st.subheader("📄 Final DSSAT File-X")
    #     filex = state.get("complete_filex", "") or ""

    #         # Save output
    #     print(f"\nSaving generated File-X to: {output_filename}")
    #     # with open(output_filename, 'w') as f:
    #     #     f.write(filex)


    #     if not filex.strip():
    #         st.warning("No File-X generated.")
    #     else:
    #         box = st.container(height=520, border=True)
    #         box.code(filex, language="text")
    #         st.download_button(
    #             "⬇️ Download File-X",
    #             data=filex.encode("utf-8"),
    #             file_name=output_filename,
    #             mime="text/plain",
    #             use_container_width=True,
    #         )

    #     if state.get("errors"):
    #         st.error("Errors:")
    #         for e in state["errors"]:
    #             st.write(f"• {e}")

    # NEW: save the entire dashboard state so it can be replayed after reruns (e.g., download click)
    st.session_state["last_state"] = state
    st.session_state["last_output_filename"] = output_filename
    st.session_state["last_inputs"] = {
        "config_path": config_path,
        "place_name": place_name,
        "crop_name": crop_name,
        "geonames_username": geonames_username,
        "enable_cache": enable_cache,
        "run_list": run_list,
        "enable_judge": enable_judge,
        "max_judge_attempts": max_judge_attempts,
        "generator_model": generator_model,
        "judge_model": judge_model,
    }

    # Display Soil and Weather Files
    with generated_files_area:
        field_metadata = state.get("field_metadata", {})
        metadata = field_metadata.get("metadata", {})
        
        sol_file = metadata.get("sol_file", "N/A")
        wth_file = metadata.get("wth_file", "N/A")
        
        st.subheader("📁 Generated Files")
        
        col_soil, col_weather = st.columns([1,1])
            
        with col_soil:
            with st.expander("🌍 Soil File", expanded=False):
                success, content = _read_file_safe(sol_file)
                
                if success:
                    st.download_button(
                        "⬇️ Download Soil File",
                        data=content.encode("utf-8"),
                        file_name=sol_file,
                        mime="text/plain",
                        use_container_width=True,
                        key="download_soil_fresh"
                    )
                    st.code(content, language="text", line_numbers=False)
                else:
                    st.warning(f"⚠️ {content}")
        
        with col_weather:
            with st.expander("🌦️ Weather File", expanded=False):
                success, content = _read_file_safe(wth_file)
                
                if success:
                    st.download_button(
                        "⬇️ Download Weather File",
                        data=content.encode("utf-8"),
                        file_name=wth_file,
                        mime="text/plain",
                        use_container_width=True,
                        key="download_weather_fresh"
                    )
                    st.code(content, language="text", line_numbers=False)
                else:
                    st.warning(f"⚠️ {content}")
        
        st.divider()

    # NEW: Display xb2 Validation BEFORE final File-X
    xb2_result = state.get('_ui', {}).get('xb2_validation')


    # Final File-X Display - ONLY if validation passed
    with final_area:
        # Check if validation exists and passed
        validation_passed = xb2_result and xb2_result['success']
        
        if not xb2_result:
            # No validation was run (shouldn't happen, but handle it)
            st.warning("⚠️ xb2 validation was not performed")

            if state.get("errors"):
                with st.expander("❌ View All Errors"):
                    for e in state["errors"]:
                        st.write(f"• {e}")
        elif not validation_passed:
            # Validation failed - don't show file
            st.error("🚫 File-X cannot be downloaded due to validation errors. Please review the validation results above and fix the issues.")

            # Optionally show what errors occurred
            if state.get("errors"):
                with st.expander("❌ View All Errors"):
                    for e in state["errors"]:
                        st.write(f"• {e}")
        else:
            # Validation passed - show file
            st.subheader("📄 Final DSSAT File-X (Validated ✅)")
            filex = state.get("complete_filex", "") or ""

            print(f"\nValidated File-X saved to: {output_filename}")

            if not filex.strip():
                st.warning("No File-X generated.")
            else:
                box = st.container(height=520, border=True)
                box.code(filex, language="text")
                st.download_button(
                    "⬇️ Download File-X",
                    data=filex.encode("utf-8"),
                    file_name=output_filename,
                    mime="text/plain",
                    use_container_width=True,
                )




if __name__ == "__main__":
    main()

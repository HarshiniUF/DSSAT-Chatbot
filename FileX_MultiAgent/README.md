# DSSAT FileX Generation Pipeline

An agentic workflow powered by LLMs and Streamlit that automatically generates DSSAT-compatible FileX (`.SNX`) experiment files. Given a crop type and location, the pipeline orchestrates a sequence of specialized agents — each responsible for a distinct section of the FileX — to produce a complete, validated experiment file ready for DSSAT simulation.

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Project Structure](#project-structure)
4. [Installation](#installation)
5. [Configuration](#configuration)
6. [Running the Application](#running-the-application)
7. [Workflow](#workflow)
8. [File Reference](#file-reference)
9. [Output Files](#output-files)
10. [Data Resources](#data-resources)

---

## Overview

The pipeline accepts a minimal input configuration (crop code, location, growing season) and produces a fully populated DSSAT FileX experiment file. It uses:

- **LLM-based agents** to infer agronomic parameters (planting, fertilizer, irrigation) when explicit values are not provided.
- **Judge agents** that review and quality-check LLM outputs before they are accepted.
- **External integration tools** to fetch real soil profiles and weather data for the specified coordinates.
- **DSSATTools library** to construct standards-compliant FileX objects and assemble the final output.
- **XB2 validation** to verify the generated FileX against DSSAT formatting rules before download.

---

## Architecture

The application follows a sequential agentic pipeline. Each agent reads from and writes to a shared `DSSATState` dictionary.

```
Input Config (JSON)
        |
        v
+------------------+
|   FieldAgent      |  --> Fetches soil (.SOL) and weather (.WTH) files
+------------------+
        |
        v
+------------------+
|  CultivarAgent    |  --> AEZ classification, cultivar selection, CUL file matching
+------------------+
        |
        v
+------------------+
|  PlantingAgent    |  --> LLM-inferred planting parameters + Judge QC
+------------------+
        |
        v
+------------------+
|  FertilizerAgent  |  --> LLM-inferred fertilizer schedule + Judge QC
+------------------+
        |
        v
+------------------+
|  IrrigationAgent  |  --> LLM-inferred irrigation strategy + Judge QC
+------------------+
        |
        v
+------------------+
|   ResidueAgent    |  --> Organic matter / residue applications
+------------------+
        |
        v
+--------------------------+
| InitialConditionsAgent   |  --> Soil initial conditions
+--------------------------+
        |
        v
+--------------------------+
| SimulationControlAgent   |  --> Simulation settings and options
+--------------------------+
        |
        v
+--------------------------+
|  FileAssemblerAgent      |  --> Assembles all sections into final FileX (.SNX)
+--------------------------+
        |
        v
   XB2 Validation --> Download
```

---

## Project Structure

```
version_3/
|
|-- streamlit_ui/
|   |-- app_v2.py                  # Main Streamlit application (entry point)
|   |-- formatters.py              # UI formatting helpers for rendering agent outputs
|
|-- agents/
|   |-- field_agent_v3.py          # FieldAgent — soil and weather data retrieval
|   |-- cultivar_agent_v2.py       # CultivarAgent — AEZ zone + cultivar selection + CUL matching
|   |-- planting_agent.py          # PlantingAgent — planting details via LLM
|   |-- fertilizer_agent.py        # FertilizerAgent — fertilizer schedule via LLM
|   |-- irrigation_agent.py        # IrrigationAgent — irrigation strategy via LLM
|   |-- residue_agent.py           # ResidueAgent — residue/organic matter (config-driven)
|   |-- initial_conditions_agent.py # InitialConditionsAgent — soil initial state
|   |-- simulation_control_agent.py # SimulationControlAgent — simulation parameters
|   |-- file_assembler_agent.py    # FileAssemblerAgent — assembles final FileX output
|   |-- __init__.py
|
|-- judge_agents/
|   |-- judge_planting_agent.py    # QC reviewer for PlantingAgent outputs
|   |-- judge_fertilizer_agent.py  # QC reviewer for FertilizerAgent outputs
|   |-- judge_irrigation_agent.py  # QC reviewer for IrrigationAgent outputs
|
|-- prompts/
|   |-- planting_agent_prompts.py  # Prompt template for PlantingAgent
|   |-- fertilizer_agent_prompts.py # Prompt template for FertilizerAgent
|   |-- irrigation_agent_prompts.py # Prompt template for IrrigationAgent
|
|-- utils/
|   |-- state.py                   # DSSATState TypedDict — shared pipeline state definition
|   |-- llm.py                     # LLM client wrappers (get_llm, get_judge_llm)
|   |-- helpers.py                 # Utility functions (date conversion, codebook parsing, geocoding, etc.)
|   |-- geo_fetcher.py             # GeoNames API location search
|   |-- cache_manager.py           # JSON-based cache for agent outputs
|   |-- cul_parser.py              # CUL file parser and cultivar matching
|   |-- ui_logger.py               # Real-time Streamlit UI event logging
|   |-- __init__.py
|
|-- INTEGRATION/
|   |-- field_agent_standalone.py  # External FieldAgent — generates soil + weather files
|   |-- integration_helper.py      # Orchestrates soil and weather generation calls
|   |-- soil_tool.py               # Soil profile generation from raster/database sources
|   |-- dssat_weather_new.py       # Weather file generation via Open-Meteo API
|   |   (Other files in this folder are legacy/unused by the current pipeline)
|
|-- DSSATTools/                    # Modified local copy of the DSSATTools Python library
|   |                                Used for constructing FileX section objects (Cultivar,
|   |                                Planting, Fertilizer, Irrigation, Field, SimulationControls,
|   |                                etc.) and assembling the final FileX string via create_filex().
|   |                                This is a vendored dependency — not a project module.
|
|-- Genotype/                      # DSSAT genotype coefficient files (.CUL, .ECO, .SPE)
|   |                                Contains 48 CUL files and associated ECO/SPE files.
|   |                                Used by CultivarAgent to match cultivar names to INGENO codes
|   |                                and extract genetic coefficients.
|
|-- XB2/                           # XB2 validation tool (Java-based)
|   |                                Validates generated FileX files against DSSAT formatting rules.
|   |                                Called via helpers.validate_xfile_with_xb2().
|
|-- data/
|   |-- zones_list.json            # AEZ (Agro-Ecological Zone) classification reference
|   |-- cultivar_db/               # Regional cultivar databases (e.g., Kenya cultivar lists)
|
|-- .streamlit/
|   |-- config.toml                # Streamlit theme configuration
|   |-- secrets.toml               # API keys (OPENAI_API_KEY, OPENAI_BASE_URL, GEONAMES_USERNAME)
|
|-- DETAIL.CDE                     # DSSAT codebook — standard codes for methods, chemicals,
|                                    planting materials, fertilizers, irrigation, etc.
|
|-- Input_config_test1.json        # Example input configuration file
|-- cache.json                     # Persistent cache of previous agent outputs
|-- .env                           # Environment variables (API keys)
```

---

## Installation

### Prerequisites

- Python 3.10+
- Java Runtime Environment (required for XB2 validation)

### Required Python Libraries

```
streamlit
openai
langchain-ollama
geopy
requests
rasterio
sqlite3          # (standard library)
pandas
numpy
openmeteo-requests
difflib          # (standard library)
```
  
Install dependencies:

```bash
pip install streamlit openai langchain-ollama geopy requests rasterio pandas numpy openmeteo-requests
```

> **Note:** The `DSSATTools` library is included locally in the project directory and does not require separate installation.

---

## Configuration

### 1. Environment Variables

Create a `.env` file in the project root or configure `.streamlit/secrets.toml`:

```toml
# .streamlit/secrets.toml
OPENAI_API_KEY = "your-api-key"
OPENAI_BASE_URL = "your-api-base-url"
GEONAMES_USERNAME = "your-geonames-username"
```

- **OPENAI_API_KEY / OPENAI_BASE_URL** — Used by the LLM wrapper (`utils/llm.py`) to call the language model. The pipeline uses an OpenAI-compatible API endpoint.
- **GEONAMES_USERNAME** — Required for location search via the GeoNames API. Register for free at [geonames.org](https://www.geonames.org/login).

### 2. Input Configuration (Optional for non-UI based input)

The pipeline accepts a JSON configuration file with the following structure:

```json
{
  "Location": {
    "Country": "Kenya",
    "Latitude": 1.045,
    "Longitude": 34.979,
    "place": "Trans Nzoia, Kenya"
  },
  "Year": {
    "start_year": 2025
  },
  "weather": {
    "start_date": "2024-01-01",
    "end_date": "2025-12-31"
  },
  "cultivar": {
    "CR": "MZ"
  }
}
```

| Field | Description |
|-------|-------------|
| `Location.place` | Location name for geocoding and display |
| `Location.Latitude / Longitude` | Coordinates for soil and weather data retrieval |
| `Year.start_year` | Target growing season year |
| `weather.start_date / end_date` | Date range for weather file generation |
| `cultivar.CR` | DSSAT crop code (e.g., `MZ` for maize, `PN` for peanut, `SG` for sorghum) |

---

## Running the Application

From the main directory:

```bash
streamlit run streamlit_ui/app_v2.py
```

The Streamlit UI will open in your browser. From there you can:


1. Select the LLM model that you want for both Generator & Judge models(suggestion: for better results always select gpt-4o for generator model & gpt-5 for judge model), and always put off toggle for Enable cache. You can put toggle to on/off for Enable judge(suggestion: better put to off as it is not fully developed yet).
2. Either you have to enter a location to search and select from GeoNames results (or) you should enter latitude and longitude coordinates to search and select from GeoPy results, but you cannot give both options at a time. Just choose only one way of selection.
3. Make sure you also input values to Crop code(Capital two letter word), Crop growing season(YYYY), Weather start date(YYYY-MM-DD) and Weather end date(YYYY-MM-DD) fields.
4. Click **Generate File-X** to execute the full agent workflow.
5. Review per-agent outputs, judge feedback, and validation results.
6. Download the generated FileX (`.SNX`), soil (`.SOL`), and weather (`.WTH`) files.

---

## Workflow

### Agent Execution Order

| Step | Agent | Responsibility |
|------|-------|----------------|
| 1 | **FieldAgent** | Calls the INTEGRATION module to generate soil (`.SOL`) and weather (`.WTH`) files for the given coordinates. Constructs the `Field` object. |
| 2 | **CultivarAgent** | Resolves location name via reverse geocoding, classifies the AEZ zone, retrieves candidate cultivars from the regional database, filters by available genetic coefficients, matches against CUL files in `Genotype/`, and constructs the `Cultivar` object. |
| 3 | **PlantingAgent** | Uses an LLM to infer planting parameters (date, population, method, depth, row spacing) based on crop, location, and regional practices. Output is reviewed by `JudgePlantingAgent`. |
| 4 | **FertilizerAgent** | Uses an LLM to infer a fertilizer application schedule (products, rates, timing, methods). Output is reviewed by `JudgeFertilizerAgent`. |
| 5 | **IrrigationAgent** | Uses an LLM to determine irrigation strategy (rainfed vs. irrigated, method, schedule). Output is reviewed by `JudgeIrrigationAgent`. |
| 6 | **ResidueAgent** | Reads residue/organic matter configuration from input JSON and constructs the `Residue` object. |
| 7 | **InitialConditionsAgent** | Sets default soil initial conditions (moisture, ammonium, nitrate) across soil layers. |
| 8 | **SimulationControlAgent** | Configures simulation start date, duration, output options, and automatic management settings. |
| 9 | **FileAssemblerAgent** | Calls `DSSATTools.create_filex()` to assemble all section objects into the final FileX string. |

All the above agents which use LLM use prompts from the prompts folder, each agent has it's own prompt file with all that specifc agent's prompts in that single file.

### Judge Agent Loop

The Planting, Fertilizer, and Irrigation agents each have a corresponding **judge agent** that reviews the LLM output for agronomic correctness and DSSAT format compliance. If the judge rejects the output, feedback is passed back to the primary agent for a retry (up to a configurable number of attempts).

**(Note: Judge agents are still in development stage, not fully completed).**

### Caching

Agent outputs are cached in `cache.json` keyed by input config filename, crop code, and coordinates. When caching is enabled in the UI, subsequent runs with the same inputs skip LLM calls and load results from cache.

NOTE: This is for development ease of use, when a developer wants to quickly test an agent's performance without re-running entire workflow, this feature can be enabled in the UI and force-run that specifc agent which the developer wants to test without running all agents.

---

## File Reference

### Core Application

| File | Description |
|------|-------------|
| `streamlit_ui/app_v2.py` | Main entry point. Streamlit UI with location search, config editor, pipeline execution, real-time agent monitoring dashboard, validation, and download buttons. |
| `streamlit_ui/formatters.py` | Helper functions for rendering agent state sections (DSSATTools objects, config JSON, judge feedback) in the UI. |

### Agents

| File | Description |
|------|-------------|
| `agents/field_agent_v3.py` | Delegates to `INTEGRATION/field_agent_standalone.py` for soil and weather file generation. Constructs the `Field` object from returned metadata. |
| `agents/cultivar_agent_v2.py` | Full cultivar selection pipeline: geocoding, AEZ classification, cultivar database lookup, CUL file matching via `utils/cul_parser.py`, and `Cultivar` PyDSSAT object construction. |
| `agents/planting_agent.py` | LLM-driven planting parameter FileX section generation creating a PyDSSAT object, with optional judge QC loop and caching. |
| `agents/fertilizer_agent.py` | LLM-driven fertilizer FileX parameters generation with PyDSSAT object generation, and optional judge QC loop and caching. |
| `agents/irrigation_agent.py` | LLM-driven irrigation FileX parameters and PyDSSAT object generation, and optional judge QC loop and caching. |
| `agents/residue_agent.py` | Config-driven residue/organic matter section builder. No LLM calls. |
| `agents/initial_conditions_agent.py` | Default soil initial conditions builder. No LLM calls. |
| `agents/simulation_control_agent.py` | Simulation parameter configuration. No LLM calls. |
| `agents/file_assembler_agent.py` | Inputs all PyDSSAT objects created by each agent and calls `DSSATTools.create_filex()` to produce the final FileX string. |

### Judge Agents

| File | Description |
|------|-------------|
| `judge_agents/judge_planting_agent.py` | Reviews PlantingAgent output for agronomic plausibility. |
| `judge_agents/judge_fertilizer_agent.py` | Reviews FertilizerAgent output for rate/timing consistency. |
| `judge_agents/judge_irrigation_agent.py` | Reviews IrrigationAgent output for strategy coherence. |

### Prompt Templates

| File | Description |
|------|-------------|
| `prompts/planting_agent_prompts.py` | All prompts which will be used by PlantingAgent LLM calls are present in this file informat of parametric functions for dynamic prompts. Prompts include crop context, location, DSSAT code options, and output format instructions etc. |
| `prompts/fertilizer_agent_prompts.py` | Similarly prompts for the FertilizerAgent LLM calls included here. Which includes agronomic context and DSSAT fertilizer code options etc. |
| `prompts/irrigation_agent_prompts.py` | Prompts for the IrrigationAgent LLM calls are included here. Which includes crop, location, and DSSAT irrigation code options etc. |

### Utilities

| File | Description |
|------|-------------|
| `utils/state.py` | Defines `DSSATState` — a TypedDict that serves as the shared data contract passed through all agents. |
| `utils/llm.py` | LLM client factory functions (`get_llm`, `get_judge_llm`). Supports OpenAI-compatible APIs with key resolution from environment variables or Streamlit secrets. |
| `utils/helpers.py` | General-purpose utilities: date conversion to DSSAT format, DSSAT codebook parsing, reverse geocoding, cultivar list retrieval from AEZ database, markdown fence stripping, crop name lookup, and XB2 validation wrapper. |
| `utils/geo_fetcher.py` | GeoNames API wrapper for fuzzy location search by name. |
| `utils/cache_manager.py` | JSON file-backed cache manager. Stores and retrieves agent outputs keyed by config, crop, and coordinates. |
| `utils/cul_parser.py` | Reads raw CUL file content, sends it to the LLM to extract INGENO and genetic coefficients for a given cultivar name. |
| `utils/ui_logger.py` | Real-time event emitter for the Streamlit UI. Pushes status updates, logs, and progress events during pipeline execution. |

### INTEGRATION Module

This folder contains external integration tools for soil and weather data generation. The following files are actively used by the pipeline:

| File | Description |
|------|-------------|
| `INTEGRATION/field_agent_standalone.py` | Standalone FieldAgent that orchestrates soil and weather file generation for given coordinates. Imported by `agents/field_agent_v3.py`. |
| `INTEGRATION/integration_helper.py` | Helper that calls `soil_tool` and `dssat_weather_new` to generate `.SOL` and `.WTH` files. |
| `INTEGRATION/soil_tool.py` | Generates DSSAT-compatible soil profile files (`.SOL`) from raster data and a local SQLite soil database. |
| `INTEGRATION/dssat_weather_new.py` | Fetches historical weather data from the Open-Meteo API and generates DSSAT weather files (`.WTH`). |

All other `.py` files in this folder are legacy and not used by the current pipeline.

### DSSATTools (Vendored Library)

A locally modified copy of the [DSSATTools](https://github.com/daquinterop/Py_DSSATTools) Python library. It provides the object model for all FileX sections (`Field`, `Cultivar`, `Planting`, `Fertilizer`, `Irrigation`, `Residue`, `InitialConditions`, `SimulationControls`) and the `create_filex()` function that assembles them into a standards-compliant FileX string. This library is imported directly from the local `DSSATTools/` directory — no pip installation is required.

### XB2

A java codebase utilised to validate the final FileX generated by the agentic workflow. This codebase has FileX specified formatting which strictly acts as an extra layer of validation to the PyDSSAT generated FileX. This automatically runs in the workflow, the streamlit UI indicates whether the validation was successful or not. Only after successful validation a user will be able to download the final FileX from the UI.

---

## Output Files

The pipeline generates three types of output files:

| File Type | Extension | Description | Location |
|-----------|-----------|-------------|----------|
| **FileX** | `.SNX` | Complete DSSAT experiment file containing all sections (field, cultivar, planting, fertilizer, irrigation, residue, initial conditions, simulation controls). | Project root directory (user-specified filename) |
| **Soil** | `.SOL` | DSSAT-compatible soil profile for the specified coordinates. | Generated by INTEGRATION module in the project root |
| **Weather** | `.WTH` | DSSAT-compatible daily weather data for the specified coordinates and date range. | Generated by INTEGRATION module in the project root |

All three files are available for download through the Streamlit UI after a successful pipeline run to their desired location and it also stores these three files in the project root directory too.

---

## Data Resources

| Resource | Location | Description |
|----------|----------|-------------|
| **DSSAT Codebook** | `DETAIL.CDE` | Standard DSSAT codes for planting methods, fertilizer types, irrigation methods, and other categorical parameters. Parsed at runtime to provide code options to LLM agents. |
| **Genotype Files** | `Genotype/` | 48 CUL files with genetic coefficients, plus associated ECO and SPE files. Used by CultivarAgent to match cultivar names to DSSAT INGENO identifiers. |
| **AEZ Zone List** | `data/zones_list.json` | Agro-Ecological Zone classification reference used during cultivar selection. |
| **Cultivar Database** | `data/cultivar_db/` | Regional cultivar databases organized by country. Contains cultivar names, characteristics, and coefficient availability flags. This is generated by standalone_cultivar_helper_agent_v2.py |
| **Agent Cache** | `cache.json` | Persistent JSON cache of previous agent outputs to avoid redundant LLM calls. |

---

## Notes

- The pipeline currently defaults to **gpt-4o** as the LLM model. Model selection can be changed from the Streamlit sidebar.
- The XB2 validation step requires a Java Runtime Environment installed on the system.
- Soil and weather file generation depends on external data sources (raster files for soil, Open-Meteo API for weather) and requires internet connectivity.

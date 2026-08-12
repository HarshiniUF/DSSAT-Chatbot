# -*- coding: utf-8 -*-
"""Centralized configuration for the INTEGRATION weather/soil pipeline.

All values are sourced from environment variables (with local-dev defaults
as fallback) so they can be overridden per-environment - e.g. via
docker-compose `environment:` or `docker run -e ...` - without code changes.
"""
import os

# --- Weather data source selector --------------------------------------------
# Which weather backend generate_weather_file() (INTEGRATION/integration_helper.py)
# uses to build the DSSAT .WTH file. One of:
#   "openmeteo" - Open-Meteo climate API            (INTEGRATION/openmeteo_weather.py)
#   "weatherx"  - WeatherX API, NASA POWER / CHIRPS  (INTEGRATION/dssat_weather_new.py)
# Both backends implement the same generate_weather_for_location(...) signature
# and produce an identical .WTH format, so switching only changes the data source.
# Override with `export WEATHER_SOURCE=weatherx` (or "openmeteo") - no code changes needed.
WEATHER_SOURCE = os.getenv("WEATHER_SOURCE", "openmeteo").strip().lower()

# --- WeatherX API (NASA POWER / CHIRPS) -------------------------------------
# Used by dssat_weather_new.py. In Docker, point this at the service name/host
# where the WeatherX API is reachable, e.g. "http://weatherx:8000/weatherx".
WEATHERX_API_URL = os.getenv("WEATHERX_API_URL", "http://10.242.84.63:8000/weatherx")
WEATHERX_TIMEOUT = int(os.getenv("WEATHERX_TIMEOUT", "30"))

# --- Open-Meteo climate API ---------------------------------------------------
# Used by openmeteo_weather.py.
OPENMETEO_API_URL = os.getenv("OPENMETEO_API_URL", "https://climate-api.open-meteo.com/v1/climate")

# --- Open-Elevation API ------------------------------------------------------
# Used to fill the ELEV field in the .WTH header.
OPEN_ELEVATION_API_URL = os.getenv("OPEN_ELEVATION_API_URL", "https://api.open-elevation.com/api/v1/lookup")
OPEN_ELEVATION_TIMEOUT = int(os.getenv("OPEN_ELEVATION_TIMEOUT", "10"))

# --- Nominatim reverse geocoding ---------------------------------------------
# A descriptive user agent is required by Nominatim's usage policy.
NOMINATIM_USER_AGENT = os.getenv("NOMINATIM_USER_AGENT", "dssat_weather_script_by_harshini")

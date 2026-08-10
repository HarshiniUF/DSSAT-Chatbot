#!/usr/bin/env python3
"""
In-memory caching for soil and weather file generation.

Soil lookup (raster sample -> SQLite -> full-file text scan) and weather
lookup (reverse-geocode -> climate API -> elevation API) are both
deterministic on their inputs (lat/lon[, date range]) and expensive relative
to a dict lookup -- soil from local I/O overhead, weather from three chained
network calls. This module memoizes both for the lifetime of the process, so
repeat calls for the same coordinates (e.g. across Streamlit reruns, or
multiple treatments at one site in a single run) skip the real work entirely.

Not persisted to disk on purpose -- soil/weather caching here is in-memory
only, scoped to a single process.
"""

from __future__ import annotations

import os
import threading
from typing import Dict, Tuple

from INTEGRATION.integration_helper import generate_soil_file, generate_weather_file

_lock = threading.Lock()

_SOIL_CACHE: Dict[Tuple[float, float], Tuple[str, str]] = {}
_WEATHER_CACHE: Dict[Tuple[float, float, str, str], Tuple[str, str]] = {}


def get_or_generate_soil(latitude: float, longitude: float) -> Tuple[str, str]:
    """
    Cached wrapper around generate_soil_file(latitude, longitude).

    Returns (site_id, sol_filename). A cache hit is only used if the
    referenced .sol file still exists on disk; otherwise it's treated as a
    miss and regenerated.
    """
    key = (float(latitude), float(longitude))

    with _lock:
        cached = _SOIL_CACHE.get(key)

    if cached and os.path.exists(cached[1]):
        print(f"  → Soil cache hit for lat={latitude}, lon={longitude}: "
              f"ID_SOIL={cached[0]} ({cached[1]})")
        return cached

    result = generate_soil_file(latitude, longitude)

    with _lock:
        _SOIL_CACHE[key] = result

    return result


def get_or_generate_weather(
    latitude: float, longitude: float, start_date: str, end_date: str
) -> Tuple[str, str]:
    """
    Cached wrapper around generate_weather_file(latitude, longitude, start_date, end_date).

    Returns (insi_code, wth_filename). A cache hit is only used if the
    referenced .WTH file still exists on disk; otherwise it's treated as a
    miss and regenerated.
    """
    key = (float(latitude), float(longitude), start_date, end_date)

    with _lock:
        cached = _WEATHER_CACHE.get(key)

    if cached and os.path.exists(cached[1]):
        print(f"  → Weather cache hit for lat={latitude}, lon={longitude}, "
              f"{start_date}..{end_date}: INSI={cached[0]} ({cached[1]})")
        return cached

    result = generate_weather_file(latitude, longitude, start_date, end_date)

    with _lock:
        _WEATHER_CACHE[key] = result

    return result

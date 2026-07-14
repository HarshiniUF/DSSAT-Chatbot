"""Weather context for the DSSAT assistant workflow.

This module adapts the linked ``wsp_unified_forecast.py`` design to this
repository.  It keeps the useful parts of that module -- a common forecast
shape, daily and seasonal providers, rain analysis, date-aware fetching, and
graceful provider failures -- without introducing a second chatbot, a second
LLM configuration, or mandatory CDS/iSDA credentials.

The LangGraph integration point is :func:`forecast_context_node`.  It only
contacts providers for weather-sensitive questions and stores structured and
prompt-ready context on the conversation state.  DSSAT FileX generation is
left unchanged: live forecasts inform conversational advice, while the FileX
pipeline continues to use the weather period configured for its simulation.
"""

from __future__ import annotations

import json
import os
import re
from datetime import date, datetime, timedelta
from typing import Any, Callable, Dict, List, Optional

import requests


DAILY_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
SEASONAL_FORECAST_URL = "https://seasonal-api.open-meteo.com/v1/seasonal"
DAILY_FORECAST_DAYS = 16
SEASONAL_FORECAST_DAYS = 100
RAIN_THRESHOLD_MM = 1.0
REQUEST_TIMEOUT_SECONDS = float(os.getenv("WSP_REQUEST_TIMEOUT_SECONDS", "20"))


class ForecastProviderError(RuntimeError):
    """Raised when a weather provider cannot return a usable response."""


def _request_json(
    url: str,
    params: Dict[str, Any],
    *,
    request_get: Callable[..., Any] = requests.get,
) -> Dict[str, Any]:
    try:
        response = request_get(url, params=params, timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
        payload = response.json()
    except (requests.RequestException, ValueError) as exc:
        raise ForecastProviderError(f"Open-Meteo request failed: {exc}") from exc

    if not isinstance(payload, dict) or payload.get("error"):
        reason = payload.get("reason", "invalid provider response") if isinstance(payload, dict) else "invalid provider response"
        raise ForecastProviderError(f"Open-Meteo returned an error: {reason}")
    return payload


def _normalise_openmeteo_daily(
    payload: Dict[str, Any],
    *,
    provider: str,
    requested_start_date: Optional[str],
) -> Dict[str, Any]:
    daily = payload.get("daily") or {}
    dates = daily.get("time") or []
    precipitation = daily.get("precipitation_sum") or []
    probabilities = daily.get("precipitation_probability_max") or []
    temp_max = daily.get("temperature_2m_max") or []
    temp_min = daily.get("temperature_2m_min") or []
    temp_mean = daily.get("temperature_2m_mean") or []

    records: List[Dict[str, Any]] = []
    for index, day in enumerate(dates):
        record: Dict[str, Any] = {
            "date": day,
            "precipitation_mm": round(float(precipitation[index] or 0), 2)
            if index < len(precipitation)
            else 0.0,
        }
        if index < len(probabilities) and probabilities[index] is not None:
            record["precipitation_probability_pct"] = round(float(probabilities[index]), 1)
        if index < len(temp_max) and temp_max[index] is not None:
            record["temperature_max_c"] = round(float(temp_max[index]), 1)
        if index < len(temp_min) and temp_min[index] is not None:
            record["temperature_min_c"] = round(float(temp_min[index]), 1)
        if index < len(temp_mean) and temp_mean[index] is not None:
            record["temperature_mean_c"] = round(float(temp_mean[index]), 1)
        records.append(record)

    fetched_start = records[0]["date"] if records else None
    fetched_end = records[-1]["date"] if records else None
    return {
        "provider": provider,
        "latitude": payload.get("latitude"),
        "longitude": payload.get("longitude"),
        "timezone": payload.get("timezone"),
        "daily": records,
        "requested_start_date": requested_start_date,
        "fetched_start_date": fetched_start,
        "fetched_end_date": fetched_end,
        "start_date_honored": bool(requested_start_date and requested_start_date == fetched_start),
    }


def fetch_daily_forecast(
    latitude: float,
    longitude: float,
    forecast_days: int = DAILY_FORECAST_DAYS,
    start_date: Optional[str] = None,
    *,
    request_get: Callable[..., Any] = requests.get,
) -> Dict[str, Any]:
    """Fetch a 1-16 day operational forecast from Open-Meteo."""
    days = max(1, min(int(forecast_days), DAILY_FORECAST_DAYS))
    params: Dict[str, Any] = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "precipitation_sum,precipitation_probability_max,temperature_2m_max,temperature_2m_min",
        "forecast_days": days,
        "timezone": "auto",
    }
    payload = _request_json(DAILY_FORECAST_URL, params, request_get=request_get)
    return _normalise_openmeteo_daily(
        payload,
        provider="Open-Meteo operational forecast",
        requested_start_date=start_date,
    )


def fetch_seasonal_forecast(
    latitude: float,
    longitude: float,
    forecast_days: int = SEASONAL_FORECAST_DAYS,
    start_date: Optional[str] = None,
    *,
    request_get: Callable[..., Any] = requests.get,
) -> Dict[str, Any]:
    """Fetch the ECMWF seasonal ensemble mean through Open-Meteo.

    Open-Meteo's seasonal endpoint exposes EC46/SEAS5 ensemble output.  The
    unsuffixed ``precipitation_sum`` field is the ensemble mean, which avoids
    shipping the large set of individual member series through the chatbot.
    """
    days = max(7, min(int(forecast_days), 210))
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "precipitation_sum,temperature_2m_mean",
        "forecast_days": days,
        "timezone": "auto",
    }
    payload = _request_json(SEASONAL_FORECAST_URL, params, request_get=request_get)
    return _normalise_openmeteo_daily(
        payload,
        provider="Open-Meteo ECMWF seasonal ensemble mean",
        requested_start_date=start_date,
    )


def analyse_rain(forecast: Optional[Dict[str, Any]], rain_threshold_mm: float = RAIN_THRESHOLD_MM) -> Dict[str, Any]:
    """Return provider-independent rainfall metrics for a normalized forecast."""
    daily = (forecast or {}).get("daily") or []
    if not daily:
        return {
            "has_rainy_event": False,
            "num_rainy_days": 0,
            "next_rainy_day": None,
            "total_forecast_rain_mm": 0.0,
            "peak_rain_day": None,
            "peak_rain_mm": 0.0,
            "rainy_days_detail": [],
        }

    rainy_days = [day for day in daily if float(day.get("precipitation_mm") or 0) >= rain_threshold_mm]
    peak = max(daily, key=lambda day: float(day.get("precipitation_mm") or 0))
    return {
        "has_rainy_event": bool(rainy_days),
        "num_rainy_days": len(rainy_days),
        "next_rainy_day": rainy_days[0].get("date") if rainy_days else None,
        "total_forecast_rain_mm": round(sum(float(day.get("precipitation_mm") or 0) for day in daily), 2),
        "peak_rain_day": peak.get("date"),
        "peak_rain_mm": round(float(peak.get("precipitation_mm") or 0), 2),
        "rainy_days_detail": rainy_days,
    }


_FORECAST_TERMS = re.compile(
    r"\b(weather|forecast|rain|rainfall|storm|temperature|hot|cold|dry|drought|flood|"
    r"today|tomorrow|this week|next week|spray|fungicide|pesticide|herbicide|"
    r"irrigat(?:e|ion)|sow|plant(?:ing)?|harvest|topdress|top-dress)\b",
    re.IGNORECASE,
)


def is_forecast_relevant(question: str) -> bool:
    """Whether current/sub-seasonal weather can materially change the answer."""
    return bool(_FORECAST_TERMS.search(question or ""))


def extract_context_date(question: str, *, today: Optional[date] = None) -> date:
    """Extract a small, deterministic set of date expressions.

    The parent workflow's LLM still interprets richer temporal language.  This
    parser only determines whether live provider data is temporally valid.
    """
    today = today or date.today()
    text = question or ""
    iso_match = re.search(r"\b(20\d{2}-\d{2}-\d{2})\b", text)
    if iso_match:
        try:
            return datetime.strptime(iso_match.group(1), "%Y-%m-%d").date()
        except ValueError:
            pass
    if re.search(r"\btomorrow\b", text, re.IGNORECASE):
        return today + timedelta(days=1)
    return today


def build_forecast_context(
    question: str,
    farmer_context: Dict[str, Any],
    latitude: float,
    longitude: float,
    *,
    context_date: Optional[date] = None,
    today: Optional[date] = None,
    daily_fetcher: Callable[..., Dict[str, Any]] = fetch_daily_forecast,
    seasonal_fetcher: Callable[..., Dict[str, Any]] = fetch_seasonal_forecast,
) -> Dict[str, Any]:
    """Build resilient daily + seasonal context for a workflow state."""
    today = today or date.today()
    relevant = is_forecast_relevant(question)
    resolved_date = context_date or extract_context_date(question, today=today)
    base: Dict[str, Any] = {
        "relevant": relevant,
        "context_date": resolved_date.isoformat(),
        "location": farmer_context.get("region"),
        "latitude": latitude,
        "longitude": longitude,
        "daily": None,
        "daily_analysis": analyse_rain(None),
        "seasonal": None,
        "seasonal_analysis": analyse_rain(None),
        "errors": [],
    }
    if not relevant:
        base["status"] = "not_relevant"
        return base

    horizon = (resolved_date - today).days
    if horizon < 0 or horizon > 210:
        base["status"] = "outside_live_forecast_window"
        return base

    if horizon <= DAILY_FORECAST_DAYS:
        try:
            base["daily"] = daily_fetcher(
                latitude,
                longitude,
                DAILY_FORECAST_DAYS,
                start_date=resolved_date.isoformat(),
            )
            base["daily_analysis"] = analyse_rain(base["daily"])
        except Exception as exc:
            base["errors"].append(f"daily forecast unavailable: {exc}")

    try:
        base["seasonal"] = seasonal_fetcher(
            latitude,
            longitude,
            SEASONAL_FORECAST_DAYS,
            start_date=resolved_date.isoformat(),
        )
        base["seasonal_analysis"] = analyse_rain(base["seasonal"])
    except Exception as exc:
        base["errors"].append(f"seasonal forecast unavailable: {exc}")

    base["status"] = "available" if base["daily"] or base["seasonal"] else "unavailable"
    return base


def format_forecast_for_prompt(context: Optional[Dict[str, Any]]) -> str:
    """Render structured forecast context without sending raw ensemble data."""
    if not context or not context.get("relevant"):
        return "No live forecast context was needed for this question."
    if context.get("status") == "outside_live_forecast_window":
        return (
            f"The question's context date ({context.get('context_date')}) is outside the live "
            "forecast window. Do not claim to have a forecast for that date."
        )

    lines = [
        f"Forecast location: {context.get('location')} ({context.get('latitude')}, {context.get('longitude')})",
        f"Decision context date: {context.get('context_date')}",
    ]
    daily = context.get("daily")
    if daily:
        rain = context["daily_analysis"]
        lines.extend(
            [
                f"Daily provider: {daily.get('provider')}",
                f"Daily coverage: {daily.get('fetched_start_date')} through {daily.get('fetched_end_date')}",
                f"Daily rain summary: {rain['num_rainy_days']} rainy day(s), next rain {rain['next_rainy_day']}, "
                f"peak {rain['peak_rain_mm']} mm on {rain['peak_rain_day']}, total {rain['total_forecast_rain_mm']} mm.",
            ]
        )
    seasonal = context.get("seasonal")
    if seasonal:
        rain = context["seasonal_analysis"]
        lines.extend(
            [
                f"Seasonal provider: {seasonal.get('provider')}",
                f"Seasonal coverage: {seasonal.get('fetched_start_date')} through {seasonal.get('fetched_end_date')}",
                f"Seasonal ensemble-mean precipitation total: {rain['total_forecast_rain_mm']} mm. "
                "Treat this as broad planning guidance, not a field-scale deterministic prediction.",
            ]
        )
    if context.get("errors"):
        lines.append("Provider limitations: " + "; ".join(context["errors"]))
    return "\n".join(lines)


def forecast_context_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """LangGraph node that enriches direct answers with live weather context."""
    from experiment_config import (
        DEFAULT_CROP_NAME,
        DEFAULT_LATITUDE,
        DEFAULT_LOCATION_NAME,
        DEFAULT_LONGITUDE,
    )

    farmer_context = {
        "crop": DEFAULT_CROP_NAME,
        "region": DEFAULT_LOCATION_NAME,
    }
    context = build_forecast_context(
        state.get("user_question", ""),
        farmer_context,
        float(DEFAULT_LATITUDE),
        float(DEFAULT_LONGITUDE),
    )
    return {
        **state,
        "forecast_context": context,
        "forecast_context_text": format_forecast_for_prompt(context),
    }


def answer_from_question(user_question: str) -> str:
    """Backward-compatible one-question entry point for the adapted module."""
    from experiment_config import (
        DEFAULT_CROP_NAME,
        DEFAULT_LATITUDE,
        DEFAULT_LOCATION_NAME,
        DEFAULT_LONGITUDE,
    )
    from llm_config import LLMConfig

    farmer_context = {"crop": DEFAULT_CROP_NAME, "region": DEFAULT_LOCATION_NAME}
    context = build_forecast_context(
        user_question,
        farmer_context,
        float(DEFAULT_LATITUDE),
        float(DEFAULT_LONGITUDE),
    )
    prompt = (
        "You are a practical agricultural assistant. Answer the farmer's question using the "
        "forecast context when it is available. State uncertainty and never invent provider data.\n\n"
        f"Farmer context: {json.dumps(farmer_context)}\n"
        f"Forecast context:\n{format_forecast_for_prompt(context)}\n\n"
        f"Question: {user_question}"
    )
    response = LLMConfig().create_llm(temperature=0.2).invoke(prompt)
    return response.content.strip()


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        raise SystemExit("Usage: python wsp_unified_forecast.py \"<question>\"")
    print(answer_from_question(" ".join(sys.argv[1:])))

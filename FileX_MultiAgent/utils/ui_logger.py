"""
UI logger utilities.
- Pushes real-time events to Streamlit via a callback stored in state["_ui"]["emit"]
- Stores event history and per-agent log lines in state for later rendering
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional


def _emit(state: Dict[str, Any], payload: Dict[str, Any]) -> None:
    cb = None
    try:
        cb = state.get("_ui", {}).get("emit")
    except Exception:
        cb = None

    if callable(cb):
        cb(payload)


def ui_event(
    state: Dict[str, Any],
    *,
    agent: str,
    kind: str,
    message: str,
    data: Optional[Dict[str, Any]] = None,
) -> None:
    payload = {
        "ts": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "agent": agent,
        "kind": kind,  # step | cache | judge | output | error | info
        "message": message,
        "data": data or {},
    }
    state.setdefault("_ui", {}).setdefault("events", []).append(payload)
    _emit(state, payload)


def ui_log(state: Dict[str, Any], agent: str, msg: str) -> None:
    state.setdefault("_ui", {}).setdefault("logs", {}).setdefault(agent, []).append(msg)
    ui_event(state, agent=agent, kind="step", message=msg)


def ui_error(
    state: Dict[str, Any],
    agent: str,
    msg: str,
    *,
    data: Optional[Dict[str, Any]] = None,
) -> None:
    state.setdefault("_ui", {}).setdefault("logs", {}).setdefault(agent, []).append(msg)
    ui_event(state, agent=agent, kind="error", message=msg, data=data)

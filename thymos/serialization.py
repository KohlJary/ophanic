"""
Serialization for Thymos states.

Handles JSON encoding/decoding and base64 compact format.
"""

from __future__ import annotations

import base64
import json
from datetime import datetime
from typing import Any

from .models import AffectVector, Goal, NeedsRegister, ThymosState


SCHEMA_VERSION = 1


def serialize(state: ThymosState, compact: bool = False) -> str:
    """
    Serialize a ThymosState to JSON string.

    Args:
        state: The state to serialize
        compact: If True, return base64-encoded compact form

    Returns:
        JSON string (or base64 if compact=True)
    """
    data = {
        "v": SCHEMA_VERSION,
        "ts": state.timestamp.isoformat() + "Z",
        "affect": state.affect.to_dict(),
        "needs": state.needs.to_dict(),
        "felt": state.felt_summary,
        "goals": [g.to_dict() for g in state.active_goals],
    }

    if state.context:
        data["ctx"] = state.context

    json_str = json.dumps(data, separators=(",", ":") if compact else None)

    if compact:
        return base64.b64encode(json_str.encode()).decode()
    return json_str


def deserialize(data: str) -> ThymosState:
    """
    Deserialize a ThymosState from JSON or base64.

    Automatically detects format.
    """
    # Try base64 first
    try:
        decoded = base64.b64decode(data).decode()
        obj = json.loads(decoded)
    except Exception:
        # Assume raw JSON
        obj = json.loads(data)

    return _from_dict(obj)


def _from_dict(obj: dict[str, Any]) -> ThymosState:
    """Reconstruct ThymosState from dictionary."""
    # Parse timestamp
    ts_str = obj.get("ts", "")
    if ts_str:
        # Handle both with and without Z suffix
        ts_str = ts_str.rstrip("Z")
        timestamp = datetime.fromisoformat(ts_str)
    else:
        timestamp = datetime.utcnow()

    # Parse affect
    affect = AffectVector.from_dict(obj.get("affect", {}))

    # Parse needs
    needs = NeedsRegister.from_dict(obj.get("needs", {}))

    # Parse goals
    goals = []
    for g in obj.get("goals", []):
        goals.append(Goal(
            description=g.get("description", ""),
            source_need=g.get("source_need", ""),
            urgency=g.get("urgency", 0.0),
            urgent=g.get("urgent", False),
        ))

    return ThymosState(
        affect=affect,
        needs=needs,
        felt_summary=obj.get("felt", ""),
        active_goals=goals,
        timestamp=timestamp,
        context=obj.get("ctx"),
    )


def to_pretty_json(state: ThymosState) -> str:
    """
    Format state as human-readable JSON.

    Useful for debugging and display.
    """
    data = {
        "version": SCHEMA_VERSION,
        "timestamp": state.timestamp.isoformat() + "Z",
        "context": state.context,
        "affect": state.affect.to_dict(),
        "needs": state.needs.to_dict(),
        "felt_summary": state.felt_summary,
        "active_goals": [g.to_dict() for g in state.active_goals],
    }
    return json.dumps(data, indent=2)


def compare(then: ThymosState, now: ThymosState) -> dict[str, Any]:
    """
    Generate comparison data between two states.

    Returns affect deltas, need deltas, and metadata.
    """
    # Affect deltas
    then_affect = then.affect.to_dict()
    now_affect = now.affect.to_dict()
    affect_delta = {
        k: round(now_affect.get(k, 0) - then_affect.get(k, 0), 3)
        for k in then_affect
    }

    # Need deltas (current value only)
    then_needs = then.needs.to_dict()
    now_needs = now.needs.to_dict()
    needs_delta = {}
    for k in then_needs:
        then_val = then_needs[k].get("current", 0)
        now_val = now_needs.get(k, {}).get("current", 0)
        needs_delta[k] = round(now_val - then_val, 3)

    # Find significant changes
    significant_affect = [
        (k, v) for k, v in affect_delta.items()
        if abs(v) >= 0.1
    ]
    significant_needs = [
        (k, v) for k, v in needs_delta.items()
        if abs(v) >= 0.1
    ]

    return {
        "time_delta": (now.timestamp - then.timestamp).total_seconds(),
        "affect_delta": affect_delta,
        "needs_delta": needs_delta,
        "significant_affect_changes": significant_affect,
        "significant_need_changes": significant_needs,
        "then_summary": then.felt_summary,
        "now_summary": now.felt_summary,
    }


def render_comparison(then: ThymosState, now: ThymosState) -> str:
    """
    Render a human-readable comparison between two states.

    Uses the Ophanic-style box format.
    """
    comp = compare(then, now)

    lines = [
        "┌─────────────────────────────────────────────────────────┐",
        "│ AFFECT COMPARISON                                       │",
        "│                                                         │",
        "│                        then    now     delta             │",
    ]

    # Show affects with deltas
    for k in sorted(then.affect.to_dict().keys()):
        then_val = then.affect.to_dict()[k]
        now_val = now.affect.to_dict()[k]
        delta = now_val - then_val

        # Format delta indicator
        if delta > 0.15:
            indicator = "▲▲"
        elif delta > 0.05:
            indicator = "▲"
        elif delta < -0.15:
            indicator = "▼▼"
        elif delta < -0.05:
            indicator = "▼"
        else:
            indicator = "─"

        name = k.ljust(15)
        line = f"│ {name}       {then_val:.2f}    {now_val:.2f}    {delta:+.2f} {indicator}           │"
        lines.append(line)

    lines.append("│                                                         │")
    lines.append("└─────────────────────────────────────────────────────────┘")

    return "\n".join(lines)

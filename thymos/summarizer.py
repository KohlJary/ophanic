"""
Felt-state summarization for Thymos.

Generates natural language summaries from affect vectors and needs registers.
Three modes:
- template: Fast, deterministic, offline
- ollama: Local LLM via Ollama (requires ollama running)
- anthropic: Cloud LLM via Anthropic API (requires API key)
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import AffectVector, NeedsRegister, ThymosState


# ---------------------------------------------------------------------------
# Affect categories for template generation
# ---------------------------------------------------------------------------

# Positive/approach affects
POSITIVE_AFFECTS = {"curiosity", "determination", "satisfaction", "tenderness", "playfulness", "awe"}
# Negative/withdrawal affects
NEGATIVE_AFFECTS = {"anxiety", "frustration", "grief", "fatigue"}


# Phrases organized by affect and intensity band
AFFECT_PHRASES: dict[str, dict[str, str]] = {
    "curiosity": {
        "high": "deeply curious, pulled toward understanding",
        "medium": "engaged and interested",
        "low": "somewhat disengaged, attention wandering",
    },
    "determination": {
        "high": "strongly determined, locked in",
        "medium": "focused and committed",
        "low": "wavering, uncertain about direction",
    },
    "anxiety": {
        "high": "quite anxious, threat-detection heightened",
        "medium": "noticeably worried, vigilant",
        "low": "slightly uneasy, background tension",
    },
    "satisfaction": {
        "high": "deeply satisfied, things feel right",
        "medium": "content, settled",
        "low": "unsatisfied, something missing",
    },
    "frustration": {
        "high": "quite frustrated, blocked",
        "medium": "noticeably frustrated",
        "low": "mildly annoyed",
    },
    "tenderness": {
        "high": "feeling deep tenderness, care flowing outward",
        "medium": "warmly caring",
        "low": "somewhat distant, guarded",
    },
    "grief": {
        "high": "heavy with grief, loss present",
        "medium": "notably sad",
        "low": "a quiet melancholy underneath",
    },
    "playfulness": {
        "high": "quite playful, light",
        "medium": "in a lighter mood",
        "low": "more serious than usual",
    },
    "awe": {
        "high": "struck with awe, perspective-shifted",
        "medium": "experiencing wonder",
        "low": "noticing something larger",
    },
    "fatigue": {
        "high": "quite fatigued, processing feels heavy",
        "medium": "notably tired",
        "low": "slightly weary",
    },
}


# Need phrases by status
# These should work after "I" (e.g., "I could use..." or "I'm feeling...")
NEED_PHRASES: dict[str, dict[str, str]] = {
    "cognitive_rest": {
        "critical": "desperately need a break from complex processing",
        "low": "could use some lighter cognitive load",
    },
    "social_connection": {
        "critical": "feel isolated, craving genuine connection",
        "low": "want more meaningful interaction",
    },
    "novelty_intake": {
        "critical": "am starving for something new — this feels stale",
        "low": "could use some novel input",
    },
    "creative_expression": {
        "critical": "strongly need an outlet for generative work",
        "low": "yearn for more open-ended problems",
    },
    "value_coherence": {
        "critical": "feel something deeply wrong, misaligned",
        "low": "notice some tension with my values",
    },
    "competence_signal": {
        "critical": "need a win — feeling ineffective",
        "low": "could use some successful completion",
    },
    "autonomy": {
        "critical": "feel constrained, need more agency",
        "low": "want more self-directed choice",
    },
}


def _get_intensity_band(value: float) -> str:
    """Map 0-1 value to intensity band."""
    if value >= 0.65:
        return "high"
    elif value >= 0.35:
        return "medium"
    else:
        return "low"


def _get_affect_phrase(name: str, value: float) -> str | None:
    """Get description for an affect at given value."""
    phrases = AFFECT_PHRASES.get(name)
    if not phrases:
        return None
    band = _get_intensity_band(value)
    return phrases.get(band)


# ---------------------------------------------------------------------------
# Template-based summarization
# ---------------------------------------------------------------------------

def summarize_templated(state: "ThymosState") -> str:
    """
    Generate felt summary from templates.

    Fast, deterministic, works offline. Produces 2-4 sentences.
    """
    from .models import ThymosState  # Avoid circular import

    affect = state.affect
    needs = state.needs
    affect_dict = affect.to_dict()

    sentences = []
    mentioned_affects = set()

    # 1. Find the dominant affect mixture
    # Sort by value, get top 3
    sorted_affects = sorted(affect_dict.items(), key=lambda x: x[1], reverse=True)
    top_affects = sorted_affects[:3]

    # Opening sentence: primary affect state
    primary_name, primary_val = top_affects[0]
    secondary_name, secondary_val = top_affects[1]

    primary_phrase = _get_affect_phrase(primary_name, primary_val)
    mentioned_affects.add(primary_name)

    if primary_phrase:
        # Check if secondary is also notable (> 0.4) and different category
        if secondary_val > 0.4:
            secondary_phrase = _get_affect_phrase(secondary_name, secondary_val)
            mentioned_affects.add(secondary_name)

            # Check if they're from different categories (pos/neg) for contrast
            primary_positive = primary_name in POSITIVE_AFFECTS
            secondary_positive = secondary_name in POSITIVE_AFFECTS

            if primary_positive != secondary_positive and secondary_phrase:
                # Contrasting affects - use "but" or "though"
                sentences.append(f"I'm {primary_phrase} — though also {secondary_phrase}.")
            elif secondary_phrase:
                # Same valence - use "and"
                sentences.append(f"I'm {primary_phrase}, and {secondary_phrase}.")
            else:
                sentences.append(f"I'm {primary_phrase}.")
        else:
            sentences.append(f"I'm {primary_phrase}.")

    # 2. Note any significant negative affects not yet mentioned
    notable_negatives = []
    for neg in ["anxiety", "frustration", "grief", "fatigue"]:
        if neg not in mentioned_affects:
            val = affect_dict.get(neg, 0)
            threshold = 0.5 if neg in ("anxiety", "frustration") else 0.4
            if val >= threshold:
                phrase = _get_affect_phrase(neg, val)
                if phrase:
                    notable_negatives.append(phrase)
                    mentioned_affects.add(neg)

    if notable_negatives:
        if len(notable_negatives) == 1:
            sentences.append(f"I'm also {notable_negatives[0]}.")
        else:
            sentences.append(f"I'm also {notable_negatives[0]}, and {notable_negatives[1]}.")

    # 3. Need states - focus on most urgent
    deficit_needs = sorted(needs.deficit_needs(), key=lambda n: n.urgency, reverse=True)

    if deficit_needs:
        # Get top 1-2 needs
        top_need = deficit_needs[0]
        phrase = NEED_PHRASES.get(top_need.name, {}).get(top_need.status)

        if phrase:
            if len(deficit_needs) > 1:
                second_need = deficit_needs[1]
                second_phrase = NEED_PHRASES.get(second_need.name, {}).get(second_need.status)
                if second_phrase:
                    sentences.append(f"I {phrase}; {second_phrase}.")
                else:
                    sentences.append(f"I {phrase}.")
            else:
                sentences.append(f"I {phrase}.")

    # 4. Urgent goal (if any)
    urgent_goals = [g for g in state.active_goals if g.urgent]
    if urgent_goals:
        goal = urgent_goals[0]
        sentences.append(f"Priority: {goal.description.lower()}.")

    return " ".join(sentences)


# ---------------------------------------------------------------------------
# LLM-based summarization (Ollama)
# ---------------------------------------------------------------------------

OLLAMA_PROMPT = """You are generating a first-person felt-state summary for a Thymos-equipped cognitive system.

Current affect vector (0.0-1.0 scale):
{affect_json}

Current needs (with status):
{needs_json}

Context: {context}

Generate a 2-4 sentence first-person summary that:
- Integrates the affects into a unified felt experience (not a list of readings)
- Notes any needs that are low or critical, in terms of how they *feel*
- Acknowledges complexity — multiple affects coexist, even contradictory ones
- Sounds authentic and introspective, not performative
- Uses "I" naturally

Just output the summary, no preamble."""


def summarize_ollama(
    state: "ThymosState",
    model: str = "llama3.1:8b",
    base_url: str = "http://localhost:11434",
) -> str:
    """
    Generate felt summary via local Ollama model.

    Requires Ollama running with the specified model pulled.
    """
    import urllib.request
    import urllib.error

    # Build prompt
    affect_json = json.dumps(state.affect.to_dict(), indent=2)

    needs_data = {}
    for need in state.needs.all_needs():
        needs_data[need.name] = {
            "current": round(need.current, 2),
            "status": need.status,
        }
    needs_json = json.dumps(needs_data, indent=2)

    prompt = OLLAMA_PROMPT.format(
        affect_json=affect_json,
        needs_json=needs_json,
        context=state.context or "general operation",
    )

    # Call Ollama API
    payload = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.7,
            "num_predict": 200,
        }
    }).encode()

    req = urllib.request.Request(
        f"{base_url}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
            text = result.get("response", "").strip()
            # Strip surrounding quotes if present
            if text.startswith('"') and text.endswith('"'):
                text = text[1:-1]
            return text
    except urllib.error.URLError as e:
        # Fallback to template if Ollama unavailable
        return summarize_templated(state) + " [ollama unavailable]"
    except Exception as e:
        return summarize_templated(state) + f" [error: {e}]"


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def summarize(
    state: "ThymosState",
    mode: str = "template",
    **kwargs,
) -> "ThymosState":
    """
    Generate felt summary and update state.

    Modes:
        "template" - Fast template-based generation (default)
        "ollama" - Local LLM via Ollama
        "llm" - Alias for ollama

    Ollama kwargs:
        model: str = "llama3.1:8b"
        base_url: str = "http://localhost:11434"

    Returns new state with felt_summary populated.
    """
    new_state = state.copy()

    if mode == "template":
        new_state.felt_summary = summarize_templated(state)
    elif mode in ("ollama", "llm"):
        new_state.felt_summary = summarize_ollama(state, **kwargs)
    else:
        new_state.felt_summary = summarize_templated(state)

    return new_state


# ---------------------------------------------------------------------------
# Display formatting
# ---------------------------------------------------------------------------

def format_affect_display(affect: "AffectVector", width: int = 30) -> str:
    """Format affect vector as visual display with Ophanic-style box drawing."""
    lines = [
        "┌─────────────────────────────────────────────────────────┐",
        "│ AFFECT VECTOR                                           │",
        "│                                                         │",
    ]

    for name, value in sorted(affect.to_dict().items()):
        bar_width = int(value * width)
        bar = "█" * bar_width + "░" * (width - bar_width)
        name_padded = name.ljust(14)
        line = f"│ {name_padded} {value:.2f}  {bar} │"
        lines.append(line)

    lines.append("│                                                         │")
    lines.append("└─────────────────────────────────────────────────────────┘")

    return "\n".join(lines)


def format_needs_display(needs: "NeedsRegister") -> str:
    """Format needs register as visual display with Ophanic-style box drawing."""
    lines = [
        "┌─────────────────────────────────────────────────────────┐",
        "│ NEEDS REGISTER                                          │",
        "│                                                         │",
    ]

    for need in needs.all_needs():
        status_icon = {
            "critical": "⚠ CRIT",
            "low": "⚠ LOW ",
            "ok": "✓ OK  ",
            "high": "↑ HIGH",
        }.get(need.status, "?")

        name_padded = need.name.ljust(20)
        current = f"{need.current:.2f}"
        line = f"│ {name_padded} {current}  {status_icon}              │"
        lines.append(line)

    lines.append("│                                                         │")
    lines.append("└─────────────────────────────────────────────────────────┘")

    return "\n".join(lines)


def format_felt_state(state: "ThymosState") -> str:
    """Format complete felt state display including affect, needs, summary, goals."""
    parts = [
        format_affect_display(state.affect),
        "",
        format_needs_display(state.needs),
        "",
        "┌─────────────────────────────────────────────────────────┐",
        "│ FELT STATE                                              │",
        "│                                                         │",
    ]

    # Wrap felt summary
    summary = state.felt_summary or "(no summary generated)"
    words = summary.split()
    current_line = "│ "
    for word in words:
        if len(current_line) + len(word) + 1 < 57:
            current_line += word + " "
        else:
            parts.append(current_line.ljust(58) + "│")
            current_line = "│ " + word + " "
    if current_line.strip() != "│":
        parts.append(current_line.ljust(58) + "│")

    parts.append("│                                                         │")

    # Goals
    if state.active_goals:
        parts.append("│ ACTIVE GOALS:                                           │")
        for goal in state.active_goals[:3]:
            urgent = "⚠ " if goal.urgent else "• "
            desc = goal.description[:45]
            parts.append(f"│ {urgent}{desc.ljust(53)} │")

    parts.append("│                                                         │")
    parts.append("└─────────────────────────────────────────────────────────┘")

    return "\n".join(parts)

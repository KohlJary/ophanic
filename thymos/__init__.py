"""
Thymos - Homeostatic self-model for cognitive AI.

A persistent locus of self built on affect vectors, needs registers,
and felt-state summarization.
"""

from .models import (
    AffectVector,
    Need,
    NeedsRegister,
    ThymosState,
    Goal,
)
from .dynamics import (
    tick,
    replenish_need,
    adjust_affect,
    simulate,
    generate_goals,
)
from .summarizer import (
    summarize,
    summarize_templated,
    format_felt_state,
    format_affect_display,
    format_needs_display,
)
from .serialization import (
    serialize,
    deserialize,
    compare,
    render_comparison,
    to_pretty_json,
)

__all__ = [
    # Models
    "AffectVector",
    "Need",
    "NeedsRegister",
    "ThymosState",
    "Goal",
    # Dynamics
    "tick",
    "replenish_need",
    "adjust_affect",
    "simulate",
    "generate_goals",
    # Summarizer
    "summarize",
    "summarize_templated",
    "format_felt_state",
    "format_affect_display",
    "format_needs_display",
    # Serialization
    "serialize",
    "deserialize",
    "compare",
    "render_comparison",
    "to_pretty_json",
]

__version__ = "0.1.0"

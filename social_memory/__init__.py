"""
Social Memory - Spatial text encoding for social environments.

A memory substrate for persistent agents operating in social contexts,
using Ophanic spatial encoding with GUID-based lazy-loading.
"""

from .models import (
    Entity,
    Relationship,
    RelationshipEvent,
    EntityPosition,
    RelationshipEdge,
    SpatialSnapshot,
    SocialMemory,
)
from .rendering import (
    render_context,
    render_snapshot,
    render_legend,
    render_temporal_stack,
)
from .tools import (
    expand,
    nearby,
    history,
    cluster,
    delta,
)

__all__ = [
    # Models
    "Entity",
    "Relationship",
    "RelationshipEvent",
    "EntityPosition",
    "RelationshipEdge",
    "SpatialSnapshot",
    "SocialMemory",
    # Rendering
    "render_context",
    "render_snapshot",
    "render_legend",
    "render_temporal_stack",
    # Tools
    "expand",
    "nearby",
    "history",
    "cluster",
    "delta",
]

__version__ = "0.1.0"

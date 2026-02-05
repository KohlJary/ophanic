"""
Thymos integration for Social Memory.

Handles affect annotation, state serialization references,
and affective geography computation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import SocialMemory, SpatialSnapshot

# Import Thymos if available
try:
    from thymos import ThymosState, serialize as thymos_serialize
    THYMOS_AVAILABLE = True
except ImportError:
    THYMOS_AVAILABLE = False
    ThymosState = None


@dataclass
class AffectiveAssociation:
    """Learned affect association with a location, entity, or configuration."""

    target: str              # Location, entity slug, or config hash
    target_type: str         # "location", "entity", "configuration"
    affect_pattern: dict[str, float]  # Average affect when target present
    confidence: float        # Based on observation count
    sample_count: int = 0

    def to_description(self) -> str:
        """Human-readable description of the association."""
        parts = []
        for affect, delta in sorted(self.affect_pattern.items(), key=lambda x: abs(x[1]), reverse=True):
            if abs(delta) >= 0.05:
                direction = "+" if delta > 0 else ""
                parts.append(f"{direction}{delta:.2f} {affect}")

        if not parts:
            return f"{self.target}: no significant pattern"

        return f"{self.target}: {', '.join(parts[:3])} (n={self.sample_count})"


def annotate_snapshot(
    snapshot: "SpatialSnapshot",
    thymos_state: "ThymosState",
    memory: "SocialMemory",
    full_serialize: bool = False,
) -> "SpatialSnapshot":
    """
    Attach Thymos state to a snapshot.

    If full_serialize=True, store complete serialized state with reference.
    Otherwise, store summary (top affects + need statuses).
    """
    if not THYMOS_AVAILABLE:
        return snapshot

    # Extract summary
    affect_summary = {}
    for name, value in thymos_state.affect.to_dict().items():
        if value >= 0.4 or name in ("anxiety", "frustration"):  # Include notable values
            affect_summary[name] = round(value, 2)

    needs_summary = {}
    for need in thymos_state.needs.all_needs():
        if need.status in ("critical", "low"):
            needs_summary[need.name] = f"⚠ {need.status.upper()}"
        elif need.status == "high":
            needs_summary[need.name] = "↑ HIGH"
        # Only include non-OK statuses to save tokens

    snapshot.affect_summary = affect_summary
    snapshot.needs_summary = needs_summary

    if full_serialize:
        # Generate reference and store
        ref = memory.generate_thymos_ref()
        snapshot.thymos_ref = ref
        # Note: actual storage of serialized state would go to a separate store
        # For now we just set the reference

    return snapshot


def compute_affective_geography(
    memory: "SocialMemory",
    min_samples: int = 2,
) -> list[AffectiveAssociation]:
    """
    Compute emergent affect associations from historical data.

    Analyzes snapshots to find patterns like:
    - "The Velvet second floor consistently +0.15 social_connection"
    - "Presence of 7b08 and 9e1c together: +0.2 anxiety"
    - "1:1 with f1e3: +0.1 creative_expression"
    """
    associations = []

    # Group snapshots by location
    by_location: dict[str, list] = {}
    for snapshot in memory.snapshots:
        if snapshot.affect_summary:
            loc = snapshot.location
            if loc not in by_location:
                by_location[loc] = []
            by_location[loc].append(snapshot)

    # Compute location associations
    for loc, snapshots in by_location.items():
        if len(snapshots) >= min_samples:
            avg_affect = _compute_average_affect(snapshots)
            if avg_affect:
                associations.append(AffectiveAssociation(
                    target=loc,
                    target_type="location",
                    affect_pattern=avg_affect,
                    confidence=min(1.0, len(snapshots) / 10),
                    sample_count=len(snapshots),
                ))

    # Group by entity presence
    entity_snapshots: dict[str, list] = {}
    for snapshot in memory.snapshots:
        if snapshot.affect_summary:
            for slug in snapshot.entity_slugs():
                if slug not in entity_snapshots:
                    entity_snapshots[slug] = []
                entity_snapshots[slug].append(snapshot)

    # Compute entity associations
    for slug, snapshots in entity_snapshots.items():
        if len(snapshots) >= min_samples:
            avg_affect = _compute_average_affect(snapshots)
            if avg_affect:
                entity = memory.get_entity(slug)
                name = entity.name if entity else slug
                associations.append(AffectiveAssociation(
                    target=f"{name} ({slug})",
                    target_type="entity",
                    affect_pattern=avg_affect,
                    confidence=min(1.0, len(snapshots) / 10),
                    sample_count=len(snapshots),
                ))

    # Sort by confidence
    associations.sort(key=lambda a: a.confidence, reverse=True)

    return associations


def _compute_average_affect(snapshots: list) -> dict[str, float]:
    """Compute average affect values across snapshots."""
    totals: dict[str, float] = {}
    counts: dict[str, int] = {}

    for snapshot in snapshots:
        if snapshot.affect_summary:
            for k, v in snapshot.affect_summary.items():
                totals[k] = totals.get(k, 0) + v
                counts[k] = counts.get(k, 0) + 1

    if not totals:
        return {}

    return {k: round(totals[k] / counts[k], 3) for k in totals}


def predict_affect_impact(
    memory: "SocialMemory",
    entity_slugs: list[str],
    location: str | None = None,
) -> dict[str, float]:
    """
    Predict how a proposed social configuration would affect Thymos.

    Based on learned associations from historical data.
    """
    associations = compute_affective_geography(memory)

    predicted: dict[str, float] = {}
    weights: dict[str, float] = {}

    # Apply location association if specified
    if location:
        for assoc in associations:
            if assoc.target_type == "location" and location.lower() in assoc.target.lower():
                for k, v in assoc.affect_pattern.items():
                    predicted[k] = predicted.get(k, 0) + v * assoc.confidence
                    weights[k] = weights.get(k, 0) + assoc.confidence

    # Apply entity associations
    for slug in entity_slugs:
        for assoc in associations:
            if assoc.target_type == "entity" and slug in assoc.target:
                for k, v in assoc.affect_pattern.items():
                    predicted[k] = predicted.get(k, 0) + v * assoc.confidence
                    weights[k] = weights.get(k, 0) + assoc.confidence

    # Normalize by weights
    if weights:
        for k in predicted:
            if weights[k] > 0:
                predicted[k] = round(predicted[k] / weights[k], 3)

    return predicted


def render_affective_geography(memory: "SocialMemory") -> str:
    """
    Render affective geography as human-readable summary.
    """
    associations = compute_affective_geography(memory)

    if not associations:
        return "(insufficient data for affective geography)"

    lines = [
        "## Affective Geography",
        "",
        "Learned associations from interaction history:",
        "",
    ]

    # Group by type
    by_type: dict[str, list] = {}
    for assoc in associations:
        if assoc.target_type not in by_type:
            by_type[assoc.target_type] = []
        by_type[assoc.target_type].append(assoc)

    for target_type, assocs in by_type.items():
        lines.append(f"### {target_type.title()}s")
        for assoc in assocs[:5]:  # Top 5 per type
            lines.append(f"  {assoc.to_description()}")
        lines.append("")

    return "\n".join(lines)

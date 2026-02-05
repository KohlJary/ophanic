"""
Drill-down tools for Social Memory.

Provides /expand, /nearby, /history, /cluster, /delta commands.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import SocialMemory, Entity, Relationship

from .rendering import render_temporal_stack, render_cluster_analysis


def expand(
    memory: "SocialMemory",
    slug: str,
    history: bool = False,
    affect: bool = False,
    timeline: bool = False,
) -> str:
    """
    Expand a slug into full detail.

    /expand a3f2              → Full entity profile
    /expand a3f2 --history    → Interaction history (via relationships)
    /expand a3f2 --affect     → How this entity has affected Thymos
    /expand █R11              → Full relationship record
    /expand █R11 --timeline   → Relationship trajectory
    """
    # Check if it's a relationship slug
    if slug.startswith("█R"):
        rel = memory.get_relationship(slug)
        if rel is None:
            return f"Relationship {slug} not found."

        if timeline:
            return _render_relationship_timeline(rel, memory)
        elif affect:
            return _render_relationship_affect(rel, memory)
        else:
            return rel.to_full_record()

    # Otherwise it's an entity
    entity = memory.get_entity(slug)
    if entity is None:
        return f"Entity {slug} not found."

    if history:
        return _render_entity_history(entity, memory)
    elif affect:
        return _render_entity_affect(entity, memory)
    else:
        return entity.to_full_profile()


def _render_relationship_timeline(rel: "Relationship", memory: "SocialMemory") -> str:
    """Render full relationship timeline."""
    source = memory.get_entity(rel.source)
    target = memory.get_entity(rel.target)

    source_name = source.name if source else rel.source
    target_name = target.name if target else rel.target

    lines = [
        f"## {rel.slug}: {source_name} → {target_name}",
        f"## Relationship timeline",
        "",
    ]

    if not rel.timeline:
        lines.append("(no events recorded)")
    else:
        for event in rel.timeline:
            lines.append(event.to_timeline_entry())
            lines.append("")

    # Current status
    lines.append(f"Current status: {rel.status}")
    if rel.needs_attention:
        lines.append("⚠ This relationship needs attention")

    return "\n".join(lines)


def _render_relationship_affect(rel: "Relationship", memory: "SocialMemory") -> str:
    """Render how a relationship has affected Thymos over time."""
    lines = [
        f"## {rel.slug}: Affect History",
        "",
    ]

    # Collect affect deltas from timeline
    total_delta: dict[str, float] = {}
    for event in rel.timeline:
        if event.affect_delta:
            for k, v in event.affect_delta.items():
                total_delta[k] = total_delta.get(k, 0) + v

    if not total_delta:
        lines.append("(no affect data recorded)")
    else:
        lines.append("Cumulative affect impact:")
        for k, v in sorted(total_delta.items(), key=lambda x: abs(x[1]), reverse=True):
            indicator = "↑" if v > 0 else "↓"
            lines.append(f"  {k}: {v:+.2f} {indicator}")

    return "\n".join(lines)


def _render_entity_history(entity: "Entity", memory: "SocialMemory") -> str:
    """Render interaction history with an entity."""
    lines = [
        f"## {entity.slug}: {entity.name}",
        f"## Interaction History",
        "",
    ]

    # Find all relationships involving this entity
    rels = memory.get_relationships_for(entity.slug)

    if not rels:
        lines.append("(no relationships recorded)")
        return "\n".join(lines)

    # Collect all events chronologically
    all_events: list[tuple[datetime, str, str]] = []
    for rel in rels:
        other_slug = rel.target if rel.source == entity.slug else rel.source
        other = memory.get_entity(other_slug)
        other_name = other.name if other else other_slug

        for event in rel.timeline:
            all_events.append((event.timestamp, other_name, event.context))

    all_events.sort(key=lambda x: x[0])

    for ts, other, context in all_events:
        date_str = ts.strftime("%Y-%m-%d")
        lines.append(f"{date_str} | with {other}: {context}")

    return "\n".join(lines)


def _render_entity_affect(entity: "Entity", memory: "SocialMemory") -> str:
    """Render how an entity has affected Thymos over time."""
    lines = [
        f"## {entity.slug}: {entity.name}",
        f"## Affect Impact",
        "",
    ]

    rels = memory.get_relationships_for(entity.slug)

    total_delta: dict[str, float] = {}
    for rel in rels:
        for event in rel.timeline:
            if event.affect_delta:
                for k, v in event.affect_delta.items():
                    total_delta[k] = total_delta.get(k, 0) + v

    if not total_delta:
        lines.append("(no affect data recorded)")
    else:
        lines.append("Cumulative affect impact from interactions:")
        for k, v in sorted(total_delta.items(), key=lambda x: abs(x[1]), reverse=True):
            indicator = "↑" if v > 0 else "↓"
            lines.append(f"  {k}: {v:+.2f} {indicator}")

    return "\n".join(lines)


def nearby(memory: "SocialMemory", slug: str) -> str:
    """
    Show entities spatially close to the given slug in current snapshot.
    """
    snapshot = memory.current_snapshot()
    if not snapshot:
        return "(no current snapshot)"

    # Find the entity's position
    target_pos = None
    for ep in snapshot.entities:
        if ep.slug == slug:
            target_pos = ep
            break

    if target_pos is None:
        return f"Entity {slug} not in current snapshot."

    entity = memory.get_entity(slug)
    entity_name = entity.name if entity else slug

    lines = [
        f"## Nearby: {entity_name} ({slug})",
        "",
    ]

    # Find entities within proximity (simple: same row ± 1)
    nearby_entities = []
    for ep in snapshot.entities:
        if ep.slug != slug:
            distance = abs(ep.x - target_pos.x) + abs(ep.y - target_pos.y)
            if distance <= 3:  # Close proximity
                other = memory.get_entity(ep.slug)
                other_name = other.name if other else ep.slug
                nearby_entities.append((distance, ep.slug, other_name))

    nearby_entities.sort(key=lambda x: x[0])

    if not nearby_entities:
        lines.append("No one nearby.")
    else:
        for dist, other_slug, name in nearby_entities:
            # Check for relationship
            rels = [
                r for r in memory.relationships.values()
                if (r.source == slug and r.target == other_slug) or
                   (r.source == other_slug and r.target == slug)
            ]
            rel_info = f" ({rels[0].slug}: {rels[0].rel_type})" if rels else ""
            lines.append(f"  {name} ({other_slug}){rel_info}")

    return "\n".join(lines)


def history(
    memory: "SocialMemory",
    location: str | None = None,
    slug: str | None = None,
    last: int = 5,
) -> str:
    """
    Show temporal stack.

    /history <location>           → Last N snapshots at this location
    /history <slug> --locations   → Where has this entity been seen
    """
    if location:
        snapshots = memory.snapshots_at_location(location)
        if not snapshots:
            return f"No snapshots at {location}."

        lines = [
            f"## History: {location}",
            f"## Last {min(last, len(snapshots))} snapshots",
            "",
        ]
        lines.append(render_temporal_stack(snapshots, last))
        return "\n".join(lines)

    elif slug:
        # Find all snapshots containing this entity
        entity = memory.get_entity(slug)
        entity_name = entity.name if entity else slug

        matching = [
            s for s in memory.snapshots
            if slug in s.entity_slugs()
        ]

        if not matching:
            return f"Entity {slug} not found in any snapshot."

        lines = [
            f"## History: {entity_name} ({slug})",
            f"## Locations",
            "",
        ]

        # Group by location
        by_location: dict[str, int] = {}
        for s in matching:
            by_location[s.location] = by_location.get(s.location, 0) + 1

        for loc, count in sorted(by_location.items(), key=lambda x: -x[1]):
            lines.append(f"  {loc}: {count} appearances")

        return "\n".join(lines)

    else:
        # Show all recent snapshots
        lines = [
            "## Recent Snapshots",
            "",
        ]
        lines.append(render_temporal_stack(memory.snapshots, last))
        return "\n".join(lines)


def cluster(memory: "SocialMemory") -> str:
    """
    Detect and describe current social groupings.
    """
    snapshot = memory.current_snapshot()
    if not snapshot:
        return "(no current snapshot)"

    return render_cluster_analysis(snapshot, memory.entities)


def delta(
    memory: "SocialMemory",
    since: datetime | str,
) -> str:
    """
    What changed since the given timestamp.

    New entities, relationship changes, position shifts.
    """
    if isinstance(since, str):
        since = datetime.fromisoformat(since.replace("Z", "+00:00"))

    current = memory.current_snapshot()
    if not current:
        return "(no current snapshot)"

    # Find snapshot closest to 'since'
    past_snapshot = None
    for s in memory.snapshots:
        if s.timestamp <= since:
            past_snapshot = s
        else:
            break

    if past_snapshot is None:
        return f"No snapshot found before {since}"

    lines = [
        f"## Changes since {since.strftime('%Y-%m-%d %H:%M')}",
        "",
    ]

    # Compare entity sets
    past_slugs = set(past_snapshot.entity_slugs())
    current_slugs = set(current.entity_slugs())

    new_entities = current_slugs - past_slugs
    left_entities = past_slugs - current_slugs

    if new_entities:
        lines.append("New arrivals:")
        for slug in new_entities:
            entity = memory.get_entity(slug)
            name = entity.name if entity else slug
            lines.append(f"  + {name} ({slug})")

    if left_entities:
        lines.append("Departed:")
        for slug in left_entities:
            entity = memory.get_entity(slug)
            name = entity.name if entity else slug
            lines.append(f"  - {name} ({slug})")

    if not new_entities and not left_entities:
        lines.append("No changes in who's present.")

    # Check for location change
    if past_snapshot.location != current.location:
        lines.append("")
        lines.append(f"Location changed: {past_snapshot.location} → {current.location}")

    return "\n".join(lines)

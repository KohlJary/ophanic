"""
Rendering for Social Memory.

Generates Ophanic box-drawing diagrams from social topology.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import Entity, Relationship, SpatialSnapshot, SocialMemory


def render_entity_box(slug: str, is_self: bool = False) -> list[str]:
    """
    Render a single entity as a small box.

    Returns list of 3 lines.
    """
    if is_self:
        return [
            "┌──────────┐",
            "│  ☆ self  │",
            "└──────────┘",
        ]
    else:
        # 4-char slug centered in 8-char box
        return [
            "┌──────┐",
            f"│ {slug} │",
            "└──────┘",
        ]


def render_snapshot(
    snapshot: "SpatialSnapshot",
    entities: dict[str, "Entity"],
    relationships: dict[str, "Relationship"],
    width: int = 54,
) -> str:
    """
    Render a spatial snapshot as Ophanic box-drawing.

    This is a simplified rendering that arranges entities in rows.
    More sophisticated positioning would use the x/y coordinates.
    """
    lines = []

    # Header
    lines.append(snapshot.to_header())
    lines.append("")
    lines.append("@current")

    # Calculate grid dimensions
    entity_positions = snapshot.entities
    if not entity_positions:
        lines.append("┌" + "─" * (width - 2) + "┐")
        lines.append("│" + " (empty) ".center(width - 2) + "│")
        lines.append("└" + "─" * (width - 2) + "┘")
        return "\n".join(lines)

    # Simple layout: arrange entities in rows
    # Group by y-coordinate
    rows: dict[int, list] = {}
    for ep in entity_positions:
        if ep.y not in rows:
            rows[ep.y] = []
        rows[ep.y].append(ep)

    # Sort entities within each row by x
    for y in rows:
        rows[y].sort(key=lambda e: e.x)

    # Build the diagram
    inner_width = width - 4  # Account for outer box borders

    # Outer box top
    lines.append("┌" + "─" * (width - 2) + "┐")
    lines.append("│" + " " * (width - 2) + "│")

    # Render each row
    sorted_rows = sorted(rows.keys())
    for row_y in sorted_rows:
        row_entities = rows[row_y]

        # Calculate spacing
        n_entities = len(row_entities)
        entity_width = 10 if any(e.is_self for e in row_entities) else 8
        total_entity_width = sum(10 if e.is_self else 8 for e in row_entities)
        spacing = (inner_width - total_entity_width) // (n_entities + 1)
        spacing = max(spacing, 2)

        # Build 3 lines for the entity boxes
        top_line = "│  "
        mid_line = "│  "
        bot_line = "│  "

        for i, ep in enumerate(row_entities):
            box = render_entity_box(ep.slug, ep.is_self)
            if i > 0:
                # Add spacing/edge
                edge = _find_edge(ep.slug, row_entities[i - 1].slug, snapshot.edges, relationships)
                if edge:
                    edge_str = f"─{edge}─"
                    top_line += " " * (spacing - len(edge_str))
                    mid_line += edge_str
                    bot_line += " " * (spacing - len(edge_str))
                else:
                    top_line += " " * spacing
                    mid_line += " " * spacing
                    bot_line += " " * spacing

            top_line += box[0]
            mid_line += box[1]
            bot_line += box[2]

        # Pad to width
        top_line = top_line.ljust(width - 1) + "│"
        mid_line = mid_line.ljust(width - 1) + "│"
        bot_line = bot_line.ljust(width - 1) + "│"

        lines.append(top_line)
        lines.append(mid_line)
        lines.append(bot_line)

        # Add spacing between rows
        if row_y != sorted_rows[-1]:
            lines.append("│" + " " * (width - 2) + "│")

    # Outer box bottom
    lines.append("│" + " " * (width - 2) + "│")
    lines.append("└" + "─" * (width - 2) + "┘")

    return "\n".join(lines)


def _find_edge(
    slug1: str,
    slug2: str,
    edges: list,
    relationships: dict[str, "Relationship"],
) -> str | None:
    """Find relationship slug between two entities."""
    for edge in edges:
        if (edge.source_slug == slug1 and edge.target_slug == slug2) or \
           (edge.source_slug == slug2 and edge.target_slug == slug1):
            return edge.rel_slug
    return None


def render_legend(
    entities: list["Entity"],
    relationships: list["Relationship"],
    include_header: bool = True,
) -> str:
    """
    Render entity and relationship legends.
    """
    lines = []

    if entities:
        if include_header:
            lines.append("## Entities")
        for entity in entities:
            lines.append(entity.to_legend_line())

    if relationships:
        if entities:
            lines.append("")
        if include_header:
            lines.append("## Relationships (surface)")
        for rel in relationships:
            lines.append(rel.to_legend_line())

    return "\n".join(lines)


def render_context(memory: "SocialMemory", width: int = 54) -> str:
    """
    Render complete minimal context (~300 tokens).

    Includes:
    - Spatial snapshot diagram
    - Entity legend
    - Relationship legend (surface only)
    """
    lines = []

    snapshot = memory.current_snapshot()
    if snapshot:
        # Get entities in this snapshot
        snapshot_entity_slugs = snapshot.entity_slugs()
        snapshot_entities = [
            memory.entities[slug]
            for slug in snapshot_entity_slugs
            if slug in memory.entities
        ]

        # Get relationships between entities in snapshot
        snapshot_rels = []
        for rel in memory.relationships.values():
            if rel.source in snapshot_entity_slugs or rel.target in snapshot_entity_slugs:
                snapshot_rels.append(rel)

        # Render snapshot
        lines.append(render_snapshot(snapshot, memory.entities, memory.relationships, width))
        lines.append("")

        # Render legend
        lines.append(render_legend(snapshot_entities, snapshot_rels))
    else:
        lines.append("(no current snapshot)")

    return "\n".join(lines)


def render_temporal_stack(
    snapshots: list["SpatialSnapshot"],
    max_entries: int = 5,
) -> str:
    """
    Render compressed temporal view.

    Shows last N snapshots as single-line summaries.
    """
    lines = []

    recent = snapshots[-max_entries:] if len(snapshots) > max_entries else snapshots

    for snapshot in reversed(recent):  # Most recent first
        line = snapshot.to_compressed_line()
        # Add markers for significant events
        if snapshot.thymos_ref:
            line += f"  ← {snapshot.thymos_ref}"
        lines.append(line)

    return "\n".join(lines)


def render_cluster_analysis(
    snapshot: "SpatialSnapshot",
    entities: dict[str, "Entity"],
) -> str:
    """
    Analyze and describe social clusters in a snapshot.

    Groups entities by spatial proximity.
    """
    if not snapshot.entities:
        return "(no entities)"

    # Simple clustering: group by similar y-coordinate
    clusters: dict[int, list] = {}
    for ep in snapshot.entities:
        cluster_key = ep.y // 3  # Group every 3 rows
        if cluster_key not in clusters:
            clusters[cluster_key] = []
        clusters[cluster_key].append(ep)

    lines = ["## Social Clusters", ""]

    for i, (_, members) in enumerate(sorted(clusters.items())):
        names = []
        for ep in members:
            entity = entities.get(ep.slug)
            name = entity.name if entity else ep.slug
            if ep.is_self:
                name = f"☆self"
            names.append(name)

        if len(members) == 1:
            lines.append(f"Cluster {i + 1}: {names[0]} (alone)")
        else:
            lines.append(f"Cluster {i + 1}: {', '.join(names)} (grouped)")

    return "\n".join(lines)

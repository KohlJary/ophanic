"""
Core data models for Social Memory.

Defines entities, relationships, spatial snapshots, and the memory store.
"""

from __future__ import annotations

import secrets
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal


def _now() -> datetime:
    """Get current UTC time."""
    return datetime.now(timezone.utc)


def generate_entity_slug() -> str:
    """Generate 4-char hex slug for an entity."""
    return secrets.token_hex(2)


EntityType = Literal["individual", "organization"]
RelationshipStatus = Literal["stable", "warming", "cooling", "tense", "new", "needs_attention"]
RelationshipDirection = Literal["mutual", "outward", "inward"]


@dataclass
class RelationshipEvent:
    """A timestamped event in a relationship's history."""

    timestamp: datetime
    context: str
    quality: Literal["positive", "negative", "neutral", "shift"] = "neutral"
    location: str | None = None
    affect_delta: dict[str, float] | None = None
    notes: str | None = None
    thymos_ref: str | None = None  # █T0047 reference

    def to_timeline_entry(self) -> str:
        """Format as timeline entry."""
        date_str = self.timestamp.strftime("%Y-%m-%d")
        lines = [f"{date_str} | {self.context.upper() if self.quality == 'shift' else self.context}"]
        if self.location:
            lines.append(f"  Location: {self.location}")
        if self.notes:
            lines.append(f"  Note: {self.notes}")
        if self.affect_delta:
            affect_str = ", ".join(f"{k} {v:+.2f}" for k, v in self.affect_delta.items())
            lines.append(f"  Affect: {affect_str}")
        if self.thymos_ref:
            lines.append(f"  Thymos: {self.thymos_ref}")
        return "\n".join(lines)


@dataclass
class Entity:
    """A person, organization, or other social entity."""

    slug: str
    name: str
    entity_type: EntityType = "individual"

    # Metadata
    first_met: datetime | None = None
    pronouns: str | None = None
    role: str | None = None  # "friend", "acquaintance", "colleague"
    notes: list[str] = field(default_factory=list)

    # For organizations
    member_slugs: list[str] | None = None
    aggregate_affect: dict[str, float] | None = None
    aggregate_needs: dict[str, str] | None = None

    @classmethod
    def create(
        cls,
        name: str,
        entity_type: EntityType = "individual",
        slug: str | None = None,
        **kwargs,
    ) -> Entity:
        """Create a new entity with auto-generated slug."""
        if slug is None:
            if entity_type == "organization":
                # Organizations get █O prefix, but we need a counter
                # For now, generate hex and we'll format externally
                slug = generate_entity_slug()
            else:
                slug = generate_entity_slug()
        return cls(slug=slug, name=name, entity_type=entity_type, **kwargs)

    def to_legend_line(self) -> str:
        """Single-line legend entry."""
        parts = [f"{self.slug}: {self.name}"]

        if self.first_met:
            parts.append(f"met {self.first_met.strftime('%Y-%m-%d')}")
        if self.role:
            parts.append(self.role)
        if self.entity_type == "organization" and self.member_slugs:
            parts.append(f"~{len(self.member_slugs)} members")
        if self.pronouns:
            parts.append(self.pronouns)
        if self.notes:
            parts.append(self.notes[0][:30])

        return " | ".join(parts)

    def to_full_profile(self) -> str:
        """Full profile for /expand."""
        lines = [
            f"## {self.slug}: {self.name}",
            f"Type: {self.entity_type}",
        ]
        if self.first_met:
            lines.append(f"First met: {self.first_met.strftime('%Y-%m-%d')}")
        if self.pronouns:
            lines.append(f"Pronouns: {self.pronouns}")
        if self.role:
            lines.append(f"Role: {self.role}")
        if self.notes:
            lines.append("Notes:")
            for note in self.notes:
                lines.append(f"  - {note}")
        if self.entity_type == "organization":
            if self.member_slugs:
                lines.append(f"Members: {', '.join(self.member_slugs)}")
            if self.aggregate_affect:
                lines.append("Aggregate affect:")
                for k, v in self.aggregate_affect.items():
                    lines.append(f"  {k}: {v:.2f}")
        return "\n".join(lines)


@dataclass
class Relationship:
    """A directed relationship between entities."""

    slug: str
    source: str  # Entity slug
    target: str  # Entity slug

    rel_type: str = "acquaintance"  # "friendly", "tense", "romantic", etc.
    status: RelationshipStatus = "stable"
    direction: RelationshipDirection = "mutual"

    summary: str = ""
    timeline: list[RelationshipEvent] = field(default_factory=list)
    needs_attention: bool = False

    @classmethod
    def create(
        cls,
        source: str,
        target: str,
        rel_type: str = "acquaintance",
        slug: str | None = None,
        **kwargs,
    ) -> Relationship:
        """Create a relationship with auto-generated slug."""
        if slug is None:
            slug = f"█R{secrets.token_hex(1).upper()}"
        return cls(slug=slug, source=source, target=target, rel_type=rel_type, **kwargs)

    def add_event(self, event: RelationshipEvent) -> None:
        """Add an event to the timeline."""
        self.timeline.append(event)
        self.timeline.sort(key=lambda e: e.timestamp)

    def to_legend_line(self) -> str:
        """Single-line legend entry."""
        dir_symbol = "↔" if self.direction == "mutual" else "→"
        parts = [f"{self.slug}: {self.source}{dir_symbol}{self.target}"]
        parts.append(self.rel_type)
        parts.append(self.status)
        if self.summary:
            parts.append(self.summary[:40])
        if self.needs_attention:
            parts.append("⚠ needs attention")
        return " | ".join(parts)

    def to_full_record(self) -> str:
        """Full record for /expand."""
        dir_symbol = "↔" if self.direction == "mutual" else "→"
        lines = [
            f"## {self.slug}: {self.source} {dir_symbol} {self.target}",
            f"Type: {self.rel_type}",
            f"Status: {self.status}",
            f"Direction: {self.direction}",
        ]
        if self.summary:
            lines.append(f"Summary: {self.summary}")
        if self.needs_attention:
            lines.append("⚠ NEEDS ATTENTION")
        if self.timeline:
            lines.append("")
            lines.append("## Timeline")
            for event in self.timeline:
                lines.append("")
                lines.append(event.to_timeline_entry())
        return "\n".join(lines)


@dataclass
class EntityPosition:
    """An entity's position in a spatial snapshot."""

    slug: str
    x: int  # Grid column
    y: int  # Grid row
    is_self: bool = False


@dataclass
class RelationshipEdge:
    """A visible relationship edge in the snapshot."""

    rel_slug: str
    source_slug: str
    target_slug: str


@dataclass
class SpatialSnapshot:
    """A point-in-time spatial encoding of social topology."""

    timestamp: datetime
    location: str  # "The Velvet, second floor lounge"

    entities: list[EntityPosition] = field(default_factory=list)
    edges: list[RelationshipEdge] = field(default_factory=list)

    location_slug: str | None = None  # █L01
    mood: str | None = None  # "relaxed-social", "tense"

    # Thymos annotation
    affect_summary: dict[str, float] | None = None
    needs_summary: dict[str, str] | None = None
    thymos_ref: str | None = None

    @classmethod
    def create(
        cls,
        location: str,
        entities: list[EntityPosition] | None = None,
        edges: list[RelationshipEdge] | None = None,
        **kwargs,
    ) -> SpatialSnapshot:
        """Create a snapshot with current timestamp."""
        return cls(
            timestamp=_now(),
            location=location,
            entities=entities or [],
            edges=edges or [],
            **kwargs,
        )

    def entity_slugs(self) -> list[str]:
        """Get all entity slugs in this snapshot."""
        return [e.slug for e in self.entities]

    def to_header(self) -> str:
        """Render header lines."""
        lines = [
            f"# {self.location}",
            f"# {self.timestamp.strftime('%Y-%m-%d %H:%M')}" +
            (f" | mood: {self.mood}" if self.mood else ""),
        ]
        if self.affect_summary:
            affect_str = " | ".join(f"{k} {v:.2f}" for k, v in self.affect_summary.items())
            lines.append(f"# affect: {affect_str}")
        if self.needs_summary:
            needs_str = " | ".join(f"{k} {v}" for k, v in self.needs_summary.items())
            lines.append(f"# needs: {needs_str}")
        return "\n".join(lines)

    def to_compressed_line(self) -> str:
        """Single-line compressed representation."""
        date_str = self.timestamp.strftime("%Y-%m-%d %H:%M")
        entity_str = " ".join(
            f"☆{e.slug}" if e.is_self else e.slug
            for e in self.entities
        )
        return f"{date_str} | {entity_str}"


@dataclass
class SocialMemory:
    """Complete social memory store."""

    entities: dict[str, Entity] = field(default_factory=dict)
    relationships: dict[str, Relationship] = field(default_factory=dict)
    snapshots: list[SpatialSnapshot] = field(default_factory=list)

    # Counters for slug generation
    _rel_counter: int = 0
    _loc_counter: int = 0
    _thymos_counter: int = 0

    def add_entity(self, entity: Entity) -> str:
        """Add an entity. Returns slug."""
        self.entities[entity.slug] = entity
        return entity.slug

    def add_relationship(self, rel: Relationship) -> str:
        """Add a relationship. Returns slug."""
        self.relationships[rel.slug] = rel
        return rel.slug

    def create_relationship(
        self,
        source: str,
        target: str,
        rel_type: str = "acquaintance",
        slug: str | None = None,
        **kwargs,
    ) -> Relationship:
        """Create and add a relationship with auto-slug."""
        if slug is None:
            self._rel_counter += 1
            slug = f"█R{self._rel_counter:02d}"
        rel = Relationship(
            slug=slug,
            source=source,
            target=target,
            rel_type=rel_type,
            **kwargs,
        )
        self.add_relationship(rel)
        return rel

    def add_snapshot(self, snapshot: SpatialSnapshot) -> None:
        """Add a snapshot, maintaining chronological order."""
        self.snapshots.append(snapshot)
        self.snapshots.sort(key=lambda s: s.timestamp)

    def get_entity(self, slug_or_name: str) -> Entity | None:
        """Look up entity by slug or name."""
        if slug_or_name in self.entities:
            return self.entities[slug_or_name]
        # Search by name
        for entity in self.entities.values():
            if entity.name.lower() == slug_or_name.lower():
                return entity
        return None

    def get_relationship(self, slug: str) -> Relationship | None:
        """Look up relationship by slug."""
        return self.relationships.get(slug)

    def get_relationships_for(self, entity_slug: str) -> list[Relationship]:
        """Get all relationships involving an entity."""
        return [
            r for r in self.relationships.values()
            if r.source == entity_slug or r.target == entity_slug
        ]

    def current_snapshot(self) -> SpatialSnapshot | None:
        """Get most recent snapshot."""
        return self.snapshots[-1] if self.snapshots else None

    def snapshots_at_location(self, location: str) -> list[SpatialSnapshot]:
        """Get all snapshots at a location."""
        return [s for s in self.snapshots if location.lower() in s.location.lower()]

    def generate_thymos_ref(self) -> str:
        """Generate next Thymos reference slug."""
        self._thymos_counter += 1
        return f"█T{self._thymos_counter:04d}"

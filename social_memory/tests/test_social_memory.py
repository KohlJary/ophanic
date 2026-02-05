"""Tests for Social Memory."""

import pytest
from datetime import datetime, timezone

from social_memory import (
    Entity,
    Relationship,
    RelationshipEvent,
    EntityPosition,
    RelationshipEdge,
    SpatialSnapshot,
    SocialMemory,
    render_context,
    render_legend,
    expand,
    nearby,
    history,
    cluster,
)


class TestEntity:
    """Tests for Entity."""

    def test_create_with_slug(self):
        """Create entity with explicit slug."""
        entity = Entity.create("Alice", slug="a1b2")
        assert entity.slug == "a1b2"
        assert entity.name == "Alice"

    def test_create_auto_slug(self):
        """Create entity with auto-generated slug."""
        entity = Entity.create("Bob")
        assert len(entity.slug) == 4
        assert entity.name == "Bob"

    def test_to_legend_line(self):
        """Legend line contains key info."""
        entity = Entity.create("Alice", slug="a1b2", role="friend")
        entity.first_met = datetime(2026, 1, 15, tzinfo=timezone.utc)
        line = entity.to_legend_line()
        assert "a1b2" in line
        assert "Alice" in line
        assert "friend" in line

    def test_to_full_profile(self):
        """Full profile contains all details."""
        entity = Entity.create("Alice", slug="a1b2")
        entity.notes = ["test note"]
        profile = entity.to_full_profile()
        assert "## a1b2: Alice" in profile
        assert "test note" in profile


class TestRelationship:
    """Tests for Relationship."""

    def test_create(self):
        """Create relationship."""
        rel = Relationship.create("a1b2", "c3d4", "friendly")
        assert rel.source == "a1b2"
        assert rel.target == "c3d4"
        assert rel.rel_type == "friendly"

    def test_add_event(self):
        """Add timeline event."""
        rel = Relationship.create("a1b2", "c3d4")
        event = RelationshipEvent(
            timestamp=datetime(2026, 1, 15, tzinfo=timezone.utc),
            context="First meeting",
            quality="positive",
        )
        rel.add_event(event)
        assert len(rel.timeline) == 1

    def test_to_legend_line(self):
        """Legend line shows relationship."""
        rel = Relationship.create("a1b2", "c3d4", "friendly", slug="█R01")
        rel.status = "stable"
        line = rel.to_legend_line()
        assert "█R01" in line
        assert "friendly" in line

    def test_to_full_record(self):
        """Full record shows timeline."""
        rel = Relationship.create("a1b2", "c3d4", slug="█R01")
        rel.timeline = [
            RelationshipEvent(
                timestamp=datetime(2026, 1, 15, tzinfo=timezone.utc),
                context="Test event",
            )
        ]
        record = rel.to_full_record()
        assert "## █R01" in record
        assert "Timeline" in record


class TestSpatialSnapshot:
    """Tests for SpatialSnapshot."""

    def test_create(self):
        """Create snapshot."""
        snap = SpatialSnapshot.create("Test Location")
        assert snap.location == "Test Location"
        assert snap.timestamp is not None

    def test_entity_slugs(self):
        """Get entity slugs."""
        snap = SpatialSnapshot.create(
            "Test",
            entities=[
                EntityPosition("a1b2", 0, 0),
                EntityPosition("c3d4", 1, 0),
            ],
        )
        slugs = snap.entity_slugs()
        assert "a1b2" in slugs
        assert "c3d4" in slugs

    def test_to_compressed_line(self):
        """Compressed line format."""
        snap = SpatialSnapshot.create(
            "Test",
            entities=[
                EntityPosition("a1b2", 0, 0),
                EntityPosition("self", 1, 0, is_self=True),
            ],
        )
        line = snap.to_compressed_line()
        assert "a1b2" in line
        assert "☆self" in line


class TestSocialMemory:
    """Tests for SocialMemory."""

    def test_add_entity(self):
        """Add entity to memory."""
        memory = SocialMemory()
        entity = Entity.create("Alice", slug="a1b2")
        memory.add_entity(entity)
        assert "a1b2" in memory.entities

    def test_get_entity_by_slug(self):
        """Lookup entity by slug."""
        memory = SocialMemory()
        entity = Entity.create("Alice", slug="a1b2")
        memory.add_entity(entity)
        found = memory.get_entity("a1b2")
        assert found is not None
        assert found.name == "Alice"

    def test_get_entity_by_name(self):
        """Lookup entity by name."""
        memory = SocialMemory()
        entity = Entity.create("Alice", slug="a1b2")
        memory.add_entity(entity)
        found = memory.get_entity("Alice")
        assert found is not None
        assert found.slug == "a1b2"

    def test_create_relationship(self):
        """Create relationship with auto slug."""
        memory = SocialMemory()
        rel = memory.create_relationship("a1b2", "c3d4")
        assert rel.slug == "█R01"
        assert rel.slug in memory.relationships

    def test_get_relationships_for(self):
        """Get all relationships for an entity."""
        memory = SocialMemory()
        memory.create_relationship("a1b2", "c3d4")
        memory.create_relationship("a1b2", "e5f6")
        rels = memory.get_relationships_for("a1b2")
        assert len(rels) == 2

    def test_add_snapshot(self):
        """Add snapshot maintains order."""
        memory = SocialMemory()
        snap1 = SpatialSnapshot.create("Loc1")
        snap1.timestamp = datetime(2026, 1, 15, tzinfo=timezone.utc)
        snap2 = SpatialSnapshot.create("Loc2")
        snap2.timestamp = datetime(2026, 1, 10, tzinfo=timezone.utc)

        memory.add_snapshot(snap1)
        memory.add_snapshot(snap2)

        assert len(memory.snapshots) == 2
        assert memory.snapshots[0].location == "Loc2"  # Earlier

    def test_current_snapshot(self):
        """Get most recent snapshot."""
        memory = SocialMemory()
        snap = SpatialSnapshot.create("Test")
        memory.add_snapshot(snap)
        current = memory.current_snapshot()
        assert current is not None
        assert current.location == "Test"


class TestRendering:
    """Tests for rendering functions."""

    def test_render_legend(self):
        """Render entity/relationship legend."""
        entities = [Entity.create("Alice", slug="a1b2")]
        relationships = [Relationship.create("a1b2", "self", slug="█R01")]
        legend = render_legend(entities, relationships)
        assert "## Entities" in legend
        assert "## Relationships" in legend

    def test_render_context(self):
        """Render full context."""
        memory = SocialMemory()
        entity = Entity.create("Alice", slug="a1b2")
        memory.add_entity(entity)
        snap = SpatialSnapshot.create(
            "Test Location",
            entities=[EntityPosition("a1b2", 0, 0)],
        )
        memory.add_snapshot(snap)
        context = render_context(memory)
        assert "Test Location" in context
        assert "a1b2" in context


class TestTools:
    """Tests for drill-down tools."""

    def setup_method(self):
        """Set up test memory."""
        self.memory = SocialMemory()
        entity = Entity.create("Alice", slug="a1b2")
        entity.notes = ["test note"]
        self.memory.add_entity(entity)
        self.memory.create_relationship("a1b2", "self", slug="█R01")

    def test_expand_entity(self):
        """Expand entity slug."""
        result = expand(self.memory, "a1b2")
        assert "Alice" in result

    def test_expand_relationship(self):
        """Expand relationship slug."""
        result = expand(self.memory, "█R01")
        assert "a1b2" in result

    def test_expand_not_found(self):
        """Expand nonexistent slug."""
        result = expand(self.memory, "xxxx")
        assert "not found" in result

    def test_history_no_snapshots(self):
        """History with no snapshots."""
        result = history(self.memory)
        # Should return recent snapshots section
        assert "Recent Snapshots" in result or "No snapshot" in result

    def test_cluster_no_snapshot(self):
        """Cluster with no current snapshot."""
        result = cluster(self.memory)
        assert "no current snapshot" in result


class TestIntegration:
    """Integration tests."""

    def test_full_workflow(self):
        """Complete workflow: entities → relationships → snapshot → tools."""
        memory = SocialMemory()

        # Add entities
        alice = Entity.create("Alice", slug="a1b2", role="friend")
        bob = Entity.create("Bob", slug="c3d4", role="colleague")
        memory.add_entity(alice)
        memory.add_entity(bob)

        # Add relationship
        rel = memory.create_relationship("a1b2", "c3d4", "friendly")
        rel.timeline.append(RelationshipEvent(
            timestamp=datetime(2026, 1, 15, tzinfo=timezone.utc),
            context="First meeting",
            quality="positive",
            affect_delta={"curiosity": 0.1},
        ))

        # Add snapshot
        snap = SpatialSnapshot.create(
            "Office",
            entities=[
                EntityPosition("a1b2", 0, 0),
                EntityPosition("c3d4", 1, 0),
                EntityPosition("self", 0, 1, is_self=True),
            ],
            edges=[RelationshipEdge("█R01", "a1b2", "c3d4")],
        )
        snap.affect_summary = {"curiosity": 0.6}
        memory.add_snapshot(snap)

        # Test drill-down
        result = expand(memory, "a1b2")
        assert "Alice" in result

        # Test context rendering
        context = render_context(memory)
        assert "Office" in context
        assert "a1b2" in context

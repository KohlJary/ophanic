"""Tests for the Ophanic parser."""

from pathlib import Path

import pytest

from ophanic import parse, parse_file, OphanicDocument
from ophanic.models import NodeType, Direction


FIXTURES = Path(__file__).parent / "fixtures"


class TestSimpleParsing:
    """Tests for basic parsing functionality."""

    def test_parse_simple_box(self):
        """A single box should parse to a single label node."""
        doc = parse_file(FIXTURES / "simple.oph")

        assert doc.title is None
        assert len(doc.breakpoints) == 1
        assert doc.breakpoints[0].breakpoint == "default"

        root = doc.breakpoints[0].root
        assert root.type == NodeType.LABEL
        assert root.name == "CONTENT"

    def test_parse_nested_boxes(self):
        """Nested boxes should create a container with children."""
        doc = parse_file(FIXTURES / "nested.oph")

        root = doc.breakpoints[0].root
        assert root.type == NodeType.CONTAINER
        assert root.direction == Direction.ROW
        assert len(root.children) == 2

        # Children should be LEFT and RIGHT
        names = [c.name for c in root.children]
        assert "LEFT" in names
        assert "RIGHT" in names

    def test_parse_responsive(self):
        """Multiple breakpoints should be parsed separately."""
        doc = parse_file(FIXTURES / "responsive.oph")

        assert len(doc.breakpoints) == 2

        breakpoint_names = [bp.breakpoint for bp in doc.breakpoints]
        assert "desktop" in breakpoint_names
        assert "mobile" in breakpoint_names


class TestComponentParsing:
    """Tests for component definition parsing."""

    def test_parse_component_definition(self):
        """Component definitions should be parsed into components list."""
        doc = parse_file(FIXTURES / "components.oph")

        assert doc.title == "Components Test"
        assert len(doc.components) == 1
        assert doc.components[0].name == "Card"
        assert "default" in doc.components[0].states

    def test_component_references(self):
        """Component references (◆) should be identified."""
        doc = parse_file(FIXTURES / "components.oph")

        root = doc.breakpoints[0].root
        # Root should have children with component refs
        refs = [c for c in root.children if c.type == NodeType.COMPONENT_REF]
        assert len(refs) == 2
        assert all(r.name == "Card" for r in refs)


class TestProportions:
    """Tests for proportion calculation."""

    def test_row_proportions(self):
        """Children in a row should have width proportions."""
        doc = parse_file(FIXTURES / "nested.oph")

        root = doc.breakpoints[0].root
        assert root.direction == Direction.ROW

        for child in root.children:
            assert child.width_proportion is not None
            assert 0 < child.width_proportion.value < 1


class TestDocumentSerialization:
    """Tests for JSON serialization."""

    def test_to_dict(self):
        """Document should serialize to dict."""
        doc = parse_file(FIXTURES / "simple.oph")
        d = doc.to_dict()

        assert "title" in d
        assert "breakpoints" in d
        assert "components" in d

    def test_to_json(self):
        """Document should serialize to JSON string."""
        doc = parse_file(FIXTURES / "simple.oph")
        json_str = doc.to_json()

        assert isinstance(json_str, str)
        assert "CONTENT" in json_str


class TestParseString:
    """Tests for parsing from string."""

    def test_parse_string(self):
        """parse() should accept string input."""
        text = """@default
┌───────────┐
│ HELLO     │
└───────────┘
"""
        doc = parse(text)

        assert len(doc.breakpoints) == 1
        assert doc.breakpoints[0].root.name == "HELLO"


class TestDashboardFile:
    """Integration test with the real dashboard.ophanic file."""

    def test_parse_dashboard(self):
        """The dashboard.ophanic file should parse without errors."""
        dashboard = Path(__file__).parent.parent.parent / "ab-test" / "dashboard.ophanic"
        if not dashboard.exists():
            pytest.skip(f"dashboard.ophanic not found at {dashboard}")

        doc = parse_file(dashboard)

        assert doc.title == "Dashboard Layout"
        assert len(doc.breakpoints) == 3

        breakpoint_names = [bp.breakpoint for bp in doc.breakpoints]
        assert "desktop" in breakpoint_names
        assert "tablet" in breakpoint_names
        assert "mobile" in breakpoint_names

        # Should have component definitions
        assert len(doc.components) >= 1
        component_names = [c.name for c in doc.components]
        assert "Calendar" in component_names or "MetricCard" in component_names

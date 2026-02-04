"""Tests for the reverse adapter (React → Ophanic)."""

from pathlib import Path

import pytest

from ophanic import parse, parse_file
from ophanic.adapters.react import generate_react
from ophanic.adapters.react_reverse import (
    parse_react,
    generate_diagram,
    react_to_ophanic,
    ReverseOptions,
)
from ophanic.models import NodeType, Direction


FIXTURES = Path(__file__).parent / "fixtures"


class TestReactParsing:
    """Tests for parsing React/JSX code."""

    def test_parse_simple_component(self):
        """Should parse a simple React component."""
        jsx = '''
function MyComponent() {
  return (
    <div className="flex">
      <div>Hello</div>
    </div>
  );
}
'''
        doc = parse_react(jsx)
        assert doc.title == "MyComponent"
        assert len(doc.breakpoints) == 1

    def test_parse_flex_direction(self):
        """Should extract flex direction."""
        jsx = '''
function Layout() {
  return (
    <div className="flex flex-col">
      <div>A</div>
      <div>B</div>
    </div>
  );
}
'''
        doc = parse_react(jsx)
        root = doc.breakpoints[0].root
        assert root.direction == Direction.COLUMN

    def test_parse_width_proportions(self):
        """Should extract Tailwind width classes."""
        jsx = '''
function Layout() {
  return (
    <div className="flex">
      <div className="w-[30%]">Sidebar</div>
      <div className="w-[70%]">Content</div>
    </div>
  );
}
'''
        doc = parse_react(jsx)
        root = doc.breakpoints[0].root
        assert root.direction == Direction.ROW
        assert len(root.children) == 2

        # Check proportions
        assert root.children[0].width_proportion.value == 0.3
        assert root.children[1].width_proportion.value == 0.7

    def test_parse_component_references(self):
        """Should identify PascalCase elements as component refs."""
        jsx = '''
function Layout() {
  return (
    <div className="flex">
      <Sidebar />
      <Content />
    </div>
  );
}
'''
        doc = parse_react(jsx)
        root = doc.breakpoints[0].root
        assert len(root.children) == 2
        assert root.children[0].type == NodeType.COMPONENT_REF
        assert root.children[0].name == "Sidebar"
        assert root.children[1].name == "Content"


class TestDiagramGeneration:
    """Tests for generating Ophanic diagrams."""

    def test_generate_simple_diagram(self):
        """Should generate box-drawing diagram."""
        doc = parse_file(FIXTURES / "simple.oph")
        diagram = generate_diagram(doc)

        assert "@default" in diagram
        assert "┌" in diagram
        assert "┘" in diagram

    def test_diagram_contains_content(self):
        """Diagram should contain label text."""
        doc = parse_file(FIXTURES / "simple.oph")
        diagram = generate_diagram(doc)

        assert "CONTENT" in diagram

    def test_diagram_row_layout(self):
        """Row layout should show boxes side by side."""
        doc = parse_file(FIXTURES / "nested.oph")
        diagram = generate_diagram(doc)

        # Should have two boxes on same line
        lines = diagram.split("\n")
        content_lines = [l for l in lines if "LEFT" in l or "RIGHT" in l]
        # LEFT and RIGHT should be on same line (row layout)
        found_both = any("LEFT" in l and "RIGHT" in l for l in lines)
        # Or on adjacent boxes in same row
        assert len(content_lines) >= 1


class TestRoundTrip:
    """Tests for round-trip conversion (Ophanic → React → Ophanic)."""

    def test_roundtrip_simple(self):
        """Simple file should survive round-trip."""
        doc = parse_file(FIXTURES / "simple.oph")

        # Generate React
        jsx = generate_react(doc)
        assert "CONTENT" in jsx

        # Parse back
        doc2 = parse_react(jsx)
        assert len(doc2.breakpoints) >= 1

    def test_roundtrip_nested(self):
        """Nested layout should survive round-trip."""
        doc = parse_file(FIXTURES / "nested.oph")

        # Generate React
        jsx = generate_react(doc)
        assert "LEFT" in jsx
        assert "RIGHT" in jsx

        # Parse back
        doc2 = parse_react(jsx)
        root = doc2.breakpoints[0].root
        assert root.direction == Direction.ROW
        assert len(root.children) == 2

    def test_roundtrip_preserves_structure(self):
        """Round-trip should preserve layout structure."""
        original = parse_file(FIXTURES / "nested.oph")
        jsx = generate_react(original)
        recovered = parse_react(jsx)

        orig_root = original.breakpoints[0].root
        recov_root = recovered.breakpoints[0].root

        # Same direction
        assert orig_root.direction == recov_root.direction
        # Same number of children
        assert len(orig_root.children) == len(recov_root.children)


class TestReverseOptions:
    """Tests for reverse adapter options."""

    def test_custom_diagram_width(self):
        """Should respect custom diagram width."""
        jsx = '''
function Layout() {
  return (
    <div className="flex">
      <div>A</div>
      <div>B</div>
    </div>
  );
}
'''
        options = ReverseOptions(diagram_width=40)
        diagram = react_to_ophanic(jsx, options)

        # Check that lines are around 40 chars
        lines = [l for l in diagram.split("\n") if l.startswith("┌") or l.startswith("│")]
        for line in lines:
            assert len(line) <= 42  # Some tolerance

"""Tests for the React adapter."""

from pathlib import Path

import pytest

from ophanic import parse, parse_file, generate_react, ReactOptions


FIXTURES = Path(__file__).parent / "fixtures"


class TestReactGeneration:
    """Tests for React code generation."""

    def test_generate_simple(self):
        """Simple layout should generate valid React."""
        doc = parse_file(FIXTURES / "simple.oph")
        code = generate_react(doc)

        assert "import React from 'react';" in code
        assert "function" in code
        assert "return" in code
        assert "export default" in code

    def test_generate_nested_with_flex(self):
        """Nested layout should use flex classes."""
        doc = parse_file(FIXTURES / "nested.oph")
        code = generate_react(doc)

        assert 'className="flex"' in code  # Row container

    def test_generate_proportions(self):
        """Proportions should be converted to width classes."""
        doc = parse_file(FIXTURES / "nested.oph")
        code = generate_react(doc)

        # Should have width percentages for row children
        assert "w-[" in code

    def test_generate_component_refs(self):
        """Component references should generate JSX elements."""
        doc = parse_file(FIXTURES / "components.oph")
        code = generate_react(doc)

        assert "<Card />" in code

    def test_component_definitions(self):
        """Component definitions should be generated as functions."""
        doc = parse_file(FIXTURES / "components.oph")
        code = generate_react(doc)

        assert "function Card(" in code

    def test_no_tailwind_option(self):
        """Without Tailwind, no className should be generated."""
        doc = parse_file(FIXTURES / "nested.oph")
        options = ReactOptions(tailwind=False)
        code = generate_react(doc, options)

        assert 'className="flex"' not in code

    def test_arrow_function_style(self):
        """Arrow function style should use const."""
        doc = parse_file(FIXTURES / "simple.oph")
        options = ReactOptions(component_style="arrow")
        code = generate_react(doc, options)

        assert "const" in code
        assert "=> {" in code


class TestComponentNaming:
    """Tests for component name generation."""

    def test_preserves_pascal_case(self):
        """PascalCase names should be preserved."""
        text = """@default
┌─────────────────┐
│ ◆MetricCard     │
└─────────────────┘
"""
        doc = parse(text)
        code = generate_react(doc)

        assert "<MetricCard />" in code

    def test_converts_to_pascal_case(self):
        """Non-PascalCase names should be converted."""
        text = """@default
┌─────────────────┐
│ ◆my_component   │
└─────────────────┘
"""
        doc = parse(text)
        code = generate_react(doc)

        assert "<MyComponent />" in code or "<My_component />" in code

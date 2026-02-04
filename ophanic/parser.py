"""Main parser orchestration for Ophanic files."""

from __future__ import annotations

from pathlib import Path

from .models import (
    BreakpointLayout,
    ComponentDefinition,
    LayoutNode,
    NodeType,
    OphanicDocument,
)
from .lexer import segment_document, DiagramSection
from .box_detector import detect_boxes
from .hierarchy import build_hierarchy
from .proportion import calculate_proportions


def parse_diagram(section: DiagramSection) -> LayoutNode | None:
    """Parse a single diagram section into a layout tree.

    This is the core parsing pipeline:
    1. Get lines from section
    2. Detect boxes
    3. Build hierarchy
    4. Calculate proportions
    """
    lines = section.get_content()
    if not lines:
        return None

    # Detect all boxes
    boxes = detect_boxes(lines)
    if not boxes:
        return None

    # Build hierarchy from spatial containment
    root = build_hierarchy(boxes)
    if root is None:
        return None

    # Calculate proportions
    calculate_proportions(root)

    return root


def parse(text: str) -> OphanicDocument:
    """Parse Ophanic text into a document.

    Args:
        text: The raw text content of an .ophanic file

    Returns:
        OphanicDocument with breakpoints and component definitions
    """
    # Segment document into sections
    segments = segment_document(text)

    doc = OphanicDocument(title=segments.title)

    # Parse each breakpoint
    for bp_section in segments.breakpoints:
        for diagram in bp_section.diagrams:
            root = parse_diagram(diagram)
            if root:
                layout = BreakpointLayout(
                    breakpoint=bp_section.name,
                    root=root,
                )
                doc.breakpoints.append(layout)

    # Parse each component
    for comp_section in segments.components:
        component = ComponentDefinition(name=comp_section.name)

        for state in comp_section.states:
            root = parse_diagram(state)
            if root:
                component.states[state.tag] = root

        if component.states:
            doc.components.append(component)

    return doc


def parse_file(path: str | Path) -> OphanicDocument:
    """Parse an Ophanic file from disk.

    Args:
        path: Path to .ophanic or .oph file

    Returns:
        OphanicDocument with breakpoints and component definitions

    Raises:
        FileNotFoundError: If file doesn't exist
        OphanicError: If parsing fails
    """
    path = Path(path)

    # Validate extension
    if path.suffix not in (".ophanic", ".oph"):
        # Allow it anyway, just warn conceptually
        pass

    text = path.read_text(encoding="utf-8")
    return parse(text)

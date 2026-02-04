# Project Map

## Overview

Ophanic is a text-based layout specification format that uses Unicode box-drawing characters to represent UI layouts. The goal is to bridge the gap between visual design and code by making spatial relationships syntactic (visible as text) rather than semantic (described abstractly).

## Architecture

```
ophanic/                    # Python parser package
├── models.py               # IR dataclasses (LayoutNode, OphanicDocument, etc.)
├── lexer.py                # Document segmentation (@breakpoint, ## ◆Component)
├── box_detector.py         # Box boundary detection from ┌─┐│└─┘ chars
├── hierarchy.py            # Tree building + direction inference
├── proportion.py           # Width/height ratio calculation
├── parser.py               # Main orchestration (parse, parse_file)
├── cli.py                  # CLI interface (parse, generate)
├── errors.py               # Custom exceptions
├── adapters/               # Code generation adapters
│   ├── react.py            # Forward: IR → React/Tailwind
│   └── react_reverse.py    # Reverse: React → IR → .ophanic
└── tests/                  # pytest tests + fixtures

ab-test/                    # Validation artifacts
├── dashboard.ophanic       # Primary test file with all format features
├── attempt-a-no-diagram.jsx    # Control: implementation without diagram
├── attempt-b-with-diagram.jsx  # Treatment: implementation with diagram
└── RESULTS.md              # A/B test validation results
```

## Data Flow

```
.ophanic file
    ↓ lexer.segment_document()
DocumentSegments (breakpoints + components)
    ↓ box_detector.detect_boxes()
list[DetectedBox] (bounds + content)
    ↓ hierarchy.build_hierarchy()
LayoutNode tree (containment + direction)
    ↓ proportion.calculate_proportions()
LayoutNode tree (with width/height ratios)
    ↓ OphanicDocument.to_json()
JSON IR output
```

## IR Structure

```python
OphanicDocument
├── title: str | None
├── breakpoints: list[BreakpointLayout]
│   └── root: LayoutNode
│       ├── type: container | component_ref | label
│       ├── direction: row | column
│       ├── width_proportion / height_proportion
│       └── children: list[LayoutNode]
└── components: list[ComponentDefinition]
    ├── name: str
    └── states: dict[str, LayoutNode]
```

## Key Patterns

- **Box detection**: Scan for `┌`, trace edges to find complete rectangles
- **Hierarchy**: Spatial containment (smaller boxes inside larger = children)
- **Direction**: If all children overlap vertically → ROW, else → COLUMN
- **Proportions**: Character count ratios between siblings

## Known Limitations (Parser v0.1)

1. **No automatic row/column grouping**: When siblings have mixed arrangements (some in rows, some stacked), the parser doesn't create intermediate container nodes. Visual rows within a column must be explicit boxes.

2. **Proportions are relative**: Calculated as ratios between siblings, not absolute pixel/percentage values.

3. **Emoji width tolerance**: The parser uses a 3-character tolerance window for right edge detection to handle Unicode display width variations.

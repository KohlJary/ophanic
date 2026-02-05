# Project Map

## Overview

Ophanic is a text-native spatial encoding system. It started as a UI layout specification using Unicode box-drawing characters, but the core insight is broader: **spatial information encoded in text is natively perceivable by text-processing models**.

The thesis (see `doc/text-is-all-you-need.md`): transformers are not "language models" but "text models." Text can encode spatial, structural, perceptual, and relational information when representations are designed for it. The capabilities attributed to scale and multimodal training may be latent capacities of text processing that haven't been deliberately exploited.

## Current Implementation: Layout Tool

The working toolchain handles UI layout specification:
- Parse `.oph` diagrams to IR
- Generate React/Tailwind from IR
- Reverse-engineer React to diagrams
- Import from Figma
- Extract design tokens

## Broader Architecture (Documented, Not Yet Implemented)

The theory documents in `doc/` extend Ophanic to a complete cognitive architecture:

```
┌─────────────────────────────────────────────────────────────────┐
│                     COGNITIVE ARCHITECTURE                       │
│                                                                  │
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────────┐  │
│  │ OPHANIC          │  │ THYMOS           │  │ SOCIAL MEMORY │  │
│  │ PERCEPTION       │  │ (felt self)      │  │ (relationships)│  │
│  │                  │  │                  │  │               │  │
│  │ Sensor grids →   │  │ Affect vector    │  │ Spatial       │  │
│  │ Scene descriptions│  │ Needs register   │  │ topology      │  │
│  │                  │  │ Felt state       │  │ Drill-down    │  │
│  └────────┬─────────┘  └────────┬─────────┘  └───────┬───────┘  │
│           │                     │                    │          │
│           └─────────────────────┼────────────────────┘          │
│                                 │                               │
│                    ┌────────────▼────────────┐                  │
│                    │    EXECUTIVE AGENT      │                  │
│                    │    (general LLM)        │                  │
│                    └─────────────────────────┘                  │
│                                                                  │
│  All layers use text-native spatial encoding                    │
│  All layers are dual-readable (human + AI)                      │
└─────────────────────────────────────────────────────────────────┘
```

See:
- `doc/ophanic-perception-architecture.md` — sensor → text grid → visual cortex → scene
- `doc/thymos-SPEC.md` — affect/needs homeostasis as basis for agency
- `doc/ophanic-social-memory-SPEC.md` — spatial encoding of social topology

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

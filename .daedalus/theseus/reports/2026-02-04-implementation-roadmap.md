# Ophanic Implementation Roadmap

Generated: 2026-02-04

---

## Current State: Validation Complete

```
[CONCEPT] ────────────> [VALIDATION] ────────────> [IMPLEMENTATION]
                             ✓ DONE                  ← YOU ARE HERE
```

**Status**: Proof of concept validated successfully. A/B test shows measurable improvement in layout accuracy, completeness, and developer confidence when using Ophanic diagrams.

---

## The Path Forward

### Phase 1: Parser Prototype (P0 - Foundation)
**Duration**: 2-3 weeks | **Blocking**: Yes

```
┌─────────────────────────────────────────────┐
│ INPUT: dashboard.ophanic                    │
│                                             │
│   @desktop                                  │
│   ┌─────────────────────────┐               │
│   │ ◆Navbar                │               │
│   ├──────────┬──────────────┤               │
│   │ ◆Sidebar │ ◆Content     │               │
│   └──────────┴──────────────┘               │
└─────────────────────────────────────────────┘
                     │
                     ▼ PARSER
┌─────────────────────────────────────────────┐
│ OUTPUT: Layout IR (Python data structure)  │
│                                             │
│ {                                           │
│   "breakpoint": "desktop",                  │
│   "root": {                                 │
│     "type": "container",                    │
│     "direction": "column",                  │
│     "children": [                           │
│       {"component": "Navbar", "height": 1}, │
│       {                                     │
│         "type": "container",                │
│         "direction": "row",                 │
│         "children": [                       │
│           {"component": "Sidebar", "w": 20},│
│           {"component": "Content", "w": 80} │
│         ]                                   │
│       }                                     │
│     ]                                       │
│   }                                         │
│ }                                           │
└─────────────────────────────────────────────┘
```

**Deliverables**:
- `src/ophanic/ir.py` - IR data structure definitions
- `src/ophanic/parser.py` - Box-drawing character reader
- `tests/test_parser.py` - Parser validation tests
- Working parse of dashboard.ophanic

**Success Criteria**:
- Parses dashboard.ophanic without errors
- Correctly identifies 3 breakpoints
- Calculates proportions: 65/35, 70/30, 20/80
- Resolves component references (◆)

---

### Phase 2: React Adapter (P0 - Proof of Value)
**Duration**: 1-2 weeks | **Depends on**: Phase 1

```
┌─────────────────────────────────────────────┐
│ INPUT: Layout IR (from parser)             │
└─────────────────────────────────────────────┘
                     │
                     ▼ ADAPTER
┌─────────────────────────────────────────────┐
│ OUTPUT: React/JSX code                      │
│                                             │
│ export default function Dashboard() {      │
│   return (                                  │
│     <div className="flex flex-col">        │
│       <Navbar />                            │
│       <div className="flex">               │
│         <Sidebar className="w-[20%]" />    │
│         <Content className="flex-1" />     │
│       </div>                                │
│     </div>                                  │
│   );                                        │
│ }                                           │
└─────────────────────────────────────────────┘
```

**Deliverables**:
- `src/ophanic/adapters/react.py` - React code generator
- `tests/test_react_adapter.py` - Adapter validation
- Generated version of DashboardB.jsx
- Comparison report: generated vs hand-written

**Success Criteria**:
- Generated code renders visually similar to DashboardB
- All 3 breakpoints generate correct media queries
- Code is readable and maintainable
- Proportions match within 2%

---

### Phase 3: Reverse Adapter (P1 - Adoption Enabler)
**Duration**: 2-3 weeks | **Depends on**: Phases 1 & 2

```
┌─────────────────────────────────────────────┐
│ INPUT: Existing React component            │
│                                             │
│ function Dashboard() {                      │
│   return (                                  │
│     <div className="flex flex-col">        │
│       <Navbar />                            │
│       <div className="flex">               │
│         <Sidebar className="w-1/5" />      │
│         <Content className="flex-1" />     │
│       </div>                                │
│     </div>                                  │
│   );                                        │
│ }                                           │
└─────────────────────────────────────────────┘
                     │
                     ▼ REVERSE ADAPTER
┌─────────────────────────────────────────────┐
│ OUTPUT: dashboard.ophanic                   │
│                                             │
│   @desktop                                  │
│   ┌─────────────────────────┐               │
│   │ ◆Navbar                │               │
│   ├──────────┬──────────────┤               │
│   │ ◆Sidebar │ ◆Content     │               │
│   └──────────┴──────────────┘               │
└─────────────────────────────────────────────┘
```

**Deliverables**:
- `src/ophanic/adapters/reverse_react.py` - Code-to-diagram generator
- Tests validating round-trip fidelity
- CLI command: `ophanic visualize component.jsx`
- Documentation: adoption guide for existing projects

**Success Criteria**:
- Can parse DashboardB.jsx structure
- Generates readable, accurate diagram
- Round-trip (code → diagram → code) maintains structure
- Works on real-world components (not just demos)

**Why This Matters**:
> "For adoption, teams need to visualize what they already have. Ophanic can't just be for new projects - it needs to help understand existing ones."

---

### Phase 4: Figma Import (P2 - Future)
**Duration**: 3-4 weeks | **Depends on**: Phase 3

```
┌─────────────────────────────────────────────┐
│ INPUT: Figma design (via API)              │
│   - Auto Layout frames                      │
│   - Component instances                     │
│   - Constraints & sizing                    │
└─────────────────────────────────────────────┘
                     │
                     ▼ FIGMA ADAPTER
┌─────────────────────────────────────────────┐
│ OUTPUT: dashboard.ophanic                   │
│   + Component-level diagrams                │
│   + All breakpoints from variants           │
└─────────────────────────────────────────────┘
```

**Deliverables**:
- Figma plugin or CLI tool
- Mapping documentation (Auto Layout → Ophanic)
- Example imports from real designs
- Designer collaboration workflow guide

**Success Criteria**:
- Can import simple Figma designs
- Handles Auto Layout correctly
- Preserves component hierarchy
- Designers can modify output diagrams

**Why This Matters**:
> "The killer feature: designers draw in Figma, export to Ophanic, developers implement from diagrams. Closes the design-to-code gap entirely."

---

## Technical Foundations

### Python Package Structure

```
src/ophanic/
├── __init__.py           # Public API
├── ir.py                 # Layout IR data structures
├── parser.py             # .ophanic file parser
├── adapters/
│   ├── __init__.py
│   ├── react.py          # Generate React code
│   ├── reverse_react.py  # Parse React code
│   └── figma.py          # Figma API integration (later)
├── cli.py                # Command-line interface
└── utils.py              # Helpers (character counting, etc)
```

### CLI Commands (Planned)

```bash
# Phase 1: Parser
ophanic parse dashboard.ophanic --output json

# Phase 2: Code generation
ophanic generate dashboard.ophanic --target react --output src/

# Phase 3: Reverse engineering
ophanic visualize src/Dashboard.jsx --output dashboard.ophanic

# Phase 4: Figma import
ophanic import figma://file/abc123 --output designs/
```

---

## Development Workflow

### Week 1-2: IR & Parser Foundation
- [ ] Define IR data structure (ir.py)
- [ ] Implement box boundary detection
- [ ] Implement proportion calculation
- [ ] Parse single-breakpoint layouts
- [ ] Parse multi-breakpoint layouts
- [ ] Handle component references (◆)
- [ ] Test with dashboard.ophanic

### Week 3-4: React Adapter
- [ ] Design adapter API
- [ ] Implement layout tree → JSX conversion
- [ ] Map proportions to Tailwind classes
- [ ] Generate media queries for breakpoints
- [ ] Test against DashboardB.jsx
- [ ] Measure visual similarity

### Week 5-7: Reverse Adapter
- [ ] Parse JSX structure (AST)
- [ ] Extract layout information
- [ ] Generate box-drawing characters
- [ ] Calculate character widths from proportions
- [ ] Test round-trip fidelity
- [ ] Document adoption workflow

### Week 8-11: Figma Integration (if prioritized)
- [ ] Study Figma API
- [ ] Map Auto Layout → Ophanic
- [ ] Build Figma plugin or CLI client
- [ ] Test with real designs
- [ ] Partner with designers for feedback

---

## Success Metrics

### Phase 1 Success
- Parser handles 100% of dashboard.ophanic features
- Proportions match manual calculations exactly
- 0 parse errors on valid inputs

### Phase 2 Success
- Generated code renders pixel-identical to hand-written code
- All breakpoints work correctly
- Code passes linting (eslint, prettier)
- Developers prefer generated code to hand-writing

### Phase 3 Success
- Round-trip maintains 95%+ structural fidelity
- Generated diagrams are human-readable
- Works on 10+ real-world components

### Phase 4 Success (Future)
- Designers successfully use Figma → Ophanic workflow
- Import time < 30 seconds per design
- Generated diagrams require minimal hand-editing

---

## Risk Mitigation

### Technical Risks

| Risk | Mitigation |
|------|-----------|
| Parser ambiguity (overlapping boxes) | Start with simple layouts, add complexity incrementally |
| Proportion precision issues | Allow tolerance thresholds, document known limitations |
| Generated code quality | Compare against hand-written code, iterate on templates |
| Round-trip fidelity loss | Accept some detail loss, focus on structural accuracy |

### Product Risks

| Risk | Mitigation |
|------|-----------|
| Developers don't trust generated code | Make output readable, add comments explaining mappings |
| Learning curve too steep | Create tutorial, interactive playground |
| Scope creep | Focus on layout only, defer styling to existing tools |
| Figma API changes | Build abstraction layer, isolate Figma-specific code |

---

## Open Questions

### For Phase 1
- How to handle overlapping box corners? (shared edges vs separate boxes)
- What's the algorithm for proportion calculation? (character ratios → percentages)
- How to represent z-index/stacking? (not visible in 2D diagrams)
- Should parser validate diagrams? (check for unclosed boxes, orphan references)

### For Phase 2
- Tailwind vs vanilla CSS? (both? configurable?)
- How to handle component props? (pass-through everything?)
- Should adapter emit TypeScript? (more type safety)
- How to handle state management? (not layout-related, but needed for complete components)

### For Phase 3
- How much CSS complexity can we reverse? (flexbox: yes, absolute positioning: maybe, transforms: probably not)
- Should we infer component boundaries? (or require annotations?)
- What about CSS Modules vs styled-components vs Tailwind? (need adapters for each?)

### For Phase 4
- What Figma features map poorly to Ophanic? (effects, gradients, complex paths)
- Should we import only Auto Layout? (or try to infer layout from absolute positioning?)
- How to handle Figma variants? (→ Ophanic breakpoints? or @states?)

---

## Conclusion

The validation phase proved Ophanic's core value proposition:
> **Making spatial relationships syntactic (visible as text) rather than semantic (described abstractly) improves layout implementation accuracy and completeness.**

Now it's time to build the tools that make this vision real.

**Next action**: Begin Phase 1 - Parser Prototype.
**Expected completion**: ~3 months to working React adapter (Phases 1 & 2)
**Stretch goal**: ~5 months to full round-trip workflow (through Phase 3)

The path is clear. The foundation is solid. Time to build.

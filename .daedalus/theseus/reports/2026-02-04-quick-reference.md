# Ophanic Codebase Quick Reference

Generated: 2026-02-04

---

## TL;DR

**Status**: Concept validated, ready for implementation
**Code Health**: GREEN - No issues found
**Next Step**: Build parser prototype (Phase 1)

---

## What Ophanic Is

A layout specification language that LLMs can actually see. Fixed-width Unicode box-drawing characters encode spatial relationships as text, eliminating the need for spatial reasoning.

**Problem**: LLMs are bad at layout because they can't see what they're building
**Solution**: Make the spec identical to the visual - the diagram IS the layout

---

## Validation Results

| Metric | Without Ophanic | With Ophanic |
|--------|----------------|--------------|
| Proportion accuracy | Rounded to nearest fraction | Exact percentages |
| Responsive breakpoints | 0 of 3 | 3 of 3 |
| Developer confidence | ~60% | ~90% |

**Key insight**: Responsive design went from "too hard, skip it" to "trivially parallel - just more diagrams."

---

## Current Codebase

### What Exists
- Complete documentation (SPEC.md, README.md)
- A/B test validation with measurable results
- Demo implementation (React/Tailwind)
- Sample .ophanic file (dashboard with 3 breakpoints)

### What Doesn't Exist
- Parser (nothing reads .ophanic files)
- IR (no layout data structure)
- Adapters (no code generation)
- Python package structure
- Tests

**Conclusion**: Validation complete, implementation not started.

---

## Implementation Plan

### Phase 1: Parser Prototype (2-3 weeks)
**Goal**: Read .ophanic files, emit layout IR
**Deliverables**: parser.py, ir.py, tests
**Success**: Parses dashboard.ophanic correctly

### Phase 2: React Adapter (1-2 weeks)
**Goal**: Generate React/JSX from IR
**Deliverables**: react.py adapter, generated code
**Success**: Output matches hand-written code

### Phase 3: Reverse Adapter (2-3 weeks)
**Goal**: Generate .ophanic from existing React code
**Deliverables**: reverse_react.py, CLI tool
**Success**: Round-trip maintains structure

### Phase 4: Figma Import (3-4 weeks, future)
**Goal**: Import Figma designs → .ophanic
**Deliverables**: Figma plugin, import workflow
**Success**: Designers use Figma → Ophanic → Code flow

---

## Architecture Overview

```
┌─────────────┐
│ .ophanic    │ ← Human/AI writes diagram
│   file      │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Parser    │ ← Reads boxes, calculates proportions
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Layout IR  │ ← Tree with proportional dimensions
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Adapters   │ ← Generate React/CSS/SwiftUI/etc
└─────────────┘
```

---

## Code Health Summary

### Files Analyzed
- SPEC.md (215 lines) - GREEN
- dashboard.ophanic (133 lines) - GREEN
- DashboardB.jsx (200 lines) - GREEN
- All validation artifacts - GREEN

### Monsters Found
**None.** All code is clean, appropriate for validation stage.

### Technical Debt
**None.** This is pre-implementation - no code to maintain yet.

---

## Key Design Decisions

### 1. Multiple Diagrams for Responsive
Each breakpoint gets its own complete visual representation. No abstract "changes" - just show what it looks like.

```
@desktop
┌─────────┬──────────┐
│ Sidebar │ Content  │
└─────────┴──────────┘

@mobile
┌────────────┐
│ Content    │
├────────────┤
│ Sidebar    │
└────────────┘
```

### 2. Component References
Use `◆ComponentName` to reference child components. Each component gets its own diagram.

```
# Page.ophanic
┌─────────────────────┐
│ ◆Navbar             │
├──────────┬──────────┤
│ ◆Sidebar │ ◆Content │
└──────────┴──────────┘

# Sidebar.ophanic
┌────────────┐
│ nav-item   │
│ nav-item   │
│ ◆Card      │
└────────────┘
```

### 3. States as Tagged Diagrams
Same pattern as breakpoints - each state is a complete diagram.

```
@default
┌─────────────┐
│ Submit      │
└─────────────┘

@hover
┌─────────────┐
│ Submit   →  │
└─────────────┘
```

---

## Open Questions

### Parser (Phase 1)
- How to handle overlapping box corners?
- Proportion calculation algorithm?
- How to represent z-index?
- Should parser validate diagrams?

### Adapter (Phase 2)
- Tailwind vs vanilla CSS?
- How to handle component props?
- TypeScript support?
- State management integration?

### Reverse Adapter (Phase 3)
- What CSS complexity can we handle?
- How to infer component boundaries?
- Support for CSS Modules, styled-components, etc?

### Figma (Phase 4)
- What Figma features map poorly?
- Auto Layout only, or absolute positioning too?
- How to handle variants?

---

## Immediate Next Actions

1. **This Week**
   - Define IR data structure (ir.py)
   - Start parser prototype
   - Set up Python package (pyproject.toml, src/)
   - Create test files

2. **Next 2-3 Weeks**
   - Complete Phase 1 parser
   - Parse dashboard.ophanic successfully
   - Validate proportions (65/35, 70/30)

3. **Next 1-2 Months**
   - Complete Phase 2 React adapter
   - Generate code from dashboard.ophanic
   - Compare with DashboardB.jsx

---

## Critical Insights

### From the Validation

> "The diagram didn't make implementation faster. It made it more correct on the first try."

> "The mental effort shifted from 'What should this look like?' (expensive simulation) to 'How do I express what I see?' (straightforward translation)."

> "Responsive isn't harder with Ophanic, it's just more diagrams. Same cognitive cost per breakpoint, linear scaling."

### Design Philosophy

**Ophanic handles the spatial. Existing tools handle the rest.**

- Layout/structure: Ophanic diagrams
- Styling/colors: CSS, design tokens
- Animation: CSS animations, Framer Motion
- Interaction: React state, handlers

Don't try to reinvent everything. Focus on the one thing Ophanic does uniquely well: making spatial relationships visible as text.

---

## Project Files Reference

```
/home/jaryk/ophanic/
├── README.md                    # Project overview
├── SPEC.md                      # Full concept spec
├── ab-test/
│   ├── RESULTS.md               # A/B test analysis
│   ├── dashboard.ophanic        # Sample diagram
│   ├── design-spec.md           # Traditional spec (control)
│   ├── attempt-a-no-diagram.jsx # Implementation without Ophanic
│   ├── attempt-b-with-diagram.jsx # Implementation with Ophanic
│   └── demo/                    # Live demo (Vite/React)
│       ├── src/
│       │   ├── DashboardA.jsx   # Control version
│       │   └── DashboardB.jsx   # Test version
│       └── ...
└── .daedalus/
    └── theseus/
        └── reports/
            ├── 2026-02-04-ophanic-codebase-analysis.md
            ├── 2026-02-04-implementation-roadmap.md
            └── 2026-02-04-quick-reference.md  ← You are here
```

---

## Contact Points

**For deeper analysis**: Read full Theseus report
- `/home/jaryk/ophanic/.daedalus/theseus/reports/2026-02-04-ophanic-codebase-analysis.md`

**For implementation plan**: Read roadmap
- `/home/jaryk/ophanic/.daedalus/theseus/reports/2026-02-04-implementation-roadmap.md`

**For concept details**: Read spec
- `/home/jaryk/ophanic/SPEC.md`

**For validation proof**: Read A/B results
- `/home/jaryk/ophanic/ab-test/RESULTS.md`

---

## Final Status

- Concept: VALIDATED
- Code Health: GREEN
- Roadmap: DEFINED
- Next Step: BUILD THE PARSER

Ready to proceed.

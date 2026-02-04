# Ophanic — Concept Sketch

*Named for the Ophanim — the "wheels within wheels" covered in eyes. Nested structures that see.*

**Status**: Brainstorm — parking this for later
**Date**: 2026-02-04
**Origin**: Late-night observation that LLMs can't do spatial reasoning but *can* read text

---

## The Problem

LLMs are bad at frontend layout. Not because they can't write CSS or SwiftUI — they can. They're bad because they **can't see what they're building**. Layout is a spatial problem, and LLMs think in text. There's a fundamental modality mismatch.

Every current approach (Tailwind, CSS-in-JS, constraint systems) describes layout **abstractly**. The developer or AI must mentally simulate what the layout *looks like* from a textual description of relationships. Humans do this with effort. LLMs do it badly.

## The Insight

**What if the spec *is* the layout?**

Fixed-width Unicode box-drawing characters can represent proportional spatial relationships in plain text. An LLM can read and write this natively — no spatial reasoning required, because the spatial information is encoded as text positions.

The layout description and the layout visualization are the same artifact.

## Core Concept

```
┌─────────────────────────────────────────────┐
│ ┌─────────────────────────────────────────┐ │
│ │ NAVBAR                                  │ │
│ └─────────────────────────────────────────┘ │
│ ┌────────────┐ ┌──────────────────────────┐ │
│ │ SIDEBAR    │ │ MAIN                     │ │
│ │            │ │ ┌──┐ ┌────────────────┐  │ │
│ │  nav-item  │ │ │🖼│ │ heading        │  │ │
│ │  nav-item  │ │ │  │ │ subtext        │  │ │
│ │  nav-item  │ │ └──┘ └────────────────┘  │ │
│ │            │ │                           │ │
│ │            │ │ ┌────────────────────────┐│ │
│ │            │ │ │ content block          ││ │
│ │            │ │ │                        ││ │
│ │            │ │ └────────────────────────┘│ │
│ └────────────┘ └──────────────────────────┘ │
└─────────────────────────────────────────────┘
```

**What this encodes:**
- Nesting hierarchy (boxes inside boxes)
- Proportional widths (sidebar ≈ 1/3, main ≈ 2/3 — readable from character counts)
- Flow direction (horizontal adjacency = row, vertical stacking = column)
- Component placement (labels inside boxes name the components)

**What an LLM sees:** Text with structure. No coordinate math. No abstract constraint language. Just characters in positions.

## How It Would Work

1. **Human or AI draws** an ASCII layout diagram
2. **Parser reads** box-drawing characters, calculates proportional widths/heights from character positions
3. **IR emits** a layout tree with proportional dimensions and component references
4. **Adapters generate** React/SwiftUI/Flutter/CSS Grid/whatever

## Why This Might Be Significant

- **LLMs become good at layout** — they can "see" what they're building because the visual *is* the text
- **Non-engineers can sketch layouts** — if you can draw boxes, you can design a UI
- **Round-trippable** — adapter could *generate* ASCII diagrams from existing layouts, letting an LLM understand and modify them
- **Diffable** — text diffs on layout diagrams show visual changes, not abstract property changes

## Responsive Design: Multiple Diagrams

The natural solution: one file, multiple tagged diagrams. Each breakpoint gets its own complete visual representation.

```
@mobile
┌───────────────────┐
│ NAVBAR            │
├───────────────────┤
│ MAIN              │
│ ┌───────────────┐ │
│ │ content       │ │
│ └───────────────┘ │
├───────────────────┤
│ SIDEBAR           │
└───────────────────┘

@desktop
┌─────────────────────────────────────────────┐
│ NAVBAR                                      │
├────────────┬────────────────────────────────┤
│ SIDEBAR    │ MAIN                           │
│            │ ┌────────────────────────────┐ │
│            │ │ content                    │ │
│            │ └────────────────────────────┘ │
└────────────┴────────────────────────────────┘
```

Same components, different arrangements. The parser sees two complete layouts, tags them by breakpoint, and the adapter emits appropriate media queries or size classes.

An LLM can look at both diagrams and understand "on mobile, sidebar moves below main" — no abstract description needed. The transformation is visible.

## Component References

Deeply nested layouts stay readable through composition. Each component gets its own diagram, referenced in parent layouts with a sigil (e.g., `◆`).

```
# Card.ophanic
┌───────────────────┐
│ ┌──┐ ┌──────────┐ │
│ │🖼│ │ title    │ │
│ │  │ │ subtitle │ │
│ └──┘ └──────────┘ │
└───────────────────┘

# Sidebar.ophanic
┌────────────┐
│ nav-item   │
│ nav-item   │
│ ◆Card      │
│ ◆Card      │
└────────────┘

# Page.ophanic
┌─────────────────────────────────────────────┐
│ ◆Navbar                                     │
├────────────┬────────────────────────────────┤
│ ◆Sidebar   │ ◆ContentArea                   │
└────────────┴────────────────────────────────┘
```

Same principle as React/SwiftUI components — don't inline implementation, reference it. The parser resolves `◆ComponentName` references, the adapter composes the output.

This mirrors natural reasoning: "the page has a navbar, sidebar, and content area" without holding the full depth in one frame. Each diagram stays readable regardless of total app complexity.

## Interaction States

Same pattern as responsive — state is just another tag. Each interaction state gets its own diagram showing exactly what changes.

```
# Button.ophanic

@default
┌─────────────────┐
│ ▣  Submit       │
└─────────────────┘

@hover
┌─────────────────┐
│ ▣  Submit    ➜  │
└─────────────────┘

@disabled
┌─────────────────┐
│ ░  Submit       │
└─────────────────┘
```

The LLM sees exactly what changes between states — no abstract description of "add an arrow on hover." Parser emits state variants, adapter generates `:hover` pseudo-selectors, `@State` properties, or whatever the target platform uses.

Animations are temporal, not spatial — no need to reinvent the wheel. Annotate with CSS animation syntax or similar:

```
@hover [transition: 0.2s ease-out]
┌─────────────────┐
│ ▣  Submit    ➜  │
└─────────────────┘
```

Ophanic handles the spatial; existing animation syntax handles the temporal.

## Level of Detail

Character grid resolution has limits. Solution: multiple diagrams at different scales, like map zoom levels.

```
# Card.ophanic

@layout
┌───────────────────┐
│ ◆Image │ ◆Text    │
└───────────────────┘

@detail:Image
┌────────────────────────────┐
│                            │
│            🖼              │
│                            │
└────────────────────────────┘
aspect: 16:9
border-radius: 8px
```

High-level structure in one diagram, fine-grained details (aspect ratios, exact radii, precise spacing) in detail views or annotations. Trial and error will reveal where the natural breakpoints are.

## Open Questions

None critical — remaining questions are empirical and will resolve during prototyping.

## Relationship to BabelTest

Same philosophy — separate **what** from **how**, use a universal intermediate layer, compile to language-specific output. But Ophanic is a different project with a different problem space. BabelTest is about behavior specification. Ophanic is about spatial specification.

Don't conflate them. Don't build this yet.

## Next Steps (Future)

- [ ] Prototype a parser that reads box-drawing characters and emits a layout tree
- [ ] Test whether LLMs can reliably generate and modify these diagrams
- [ ] Determine if proportional character widths map cleanly to real layout proportions
- [ ] **Generate diagrams from existing components** (React/SwiftUI → ASCII) — critical for adoption, lets teams visualize what they already have
- [ ] **Generate diagrams from design files** (PSD/Figma → ASCII) — killer feature, bridges design→code gap entirely

---

*Parked. Come back after BabelTest has users.*

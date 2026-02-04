# Ophanic

*Named for the Ophanim — the "wheels within wheels" covered in eyes. Nested structures that see.*

**A layout specification language that LLMs can actually see.**

## The Problem

LLMs are bad at frontend layout. Not because they can't write CSS — they can. They're bad because they **can't see what they're building**. Layout is a spatial problem, and LLMs think in text.

## The Solution

What if the spec *is* the layout?

```
┌─────────────────────────────────────────────┐
│ ◆Navbar                                     │
├────────────┬────────────────────────────────┤
│ ◆Sidebar   │ ◆ContentArea                   │
└────────────┴────────────────────────────────┘
```

Fixed-width Unicode box-drawing characters encode proportional spatial relationships in plain text. An LLM can read and write this natively — no spatial reasoning required.

## Status

**Proof of concept validated.** See `ab-test/` for an A/B comparison showing measurable improvement in layout accuracy when implementing from Ophanic diagrams vs. traditional text specs.

Key finding: Responsive design goes from "too hard, skip it" to "trivially parallel" — each breakpoint is just another diagram.

## Documentation

- [SPEC.md](SPEC.md) — Full concept specification
- [ab-test/RESULTS.md](ab-test/RESULTS.md) — A/B test results and analysis

## Roadmap

1. [ ] Parser prototype — read box-drawing characters, emit layout IR
2. [ ] React adapter — generate components from IR
3. [ ] Reverse adapter — generate diagrams from existing React/CSS
4. [ ] Figma import — generate diagrams from design files

## License

[Hippocratic License 3.0](LICENSE.md) — An ethical open source license.

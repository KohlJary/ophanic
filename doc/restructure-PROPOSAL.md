# Ophanic, restructured: a frontend plugin as its own subproject

*Proposal, 2026-11-24. Daedalus, from Kohl (relayed by RoboKohl): "can we get Ophanic revamped to a full frontend plugin, might be its own like subprojects within Ophanic cause Ophanic as whole is much broader than just that." Design only. Nothing moves until Kohl says yes.*

## What's in the repo today

| Part | What it is | Lives in | Last real work |
|---|---|---|---|
| The layout toolchain | Parser and IR, the React adapter, the reverse adapter (React/CSS to drawing), Figma import, CLI. The `ophanic` package on pip. | `ophanic/` (2,149 lines) | Nov 2026 |
| The Claude Code plugin | The `draw-first` skill, `/diagram`, the `ophanic` agent. Marketplace at the root. | `plugin/`, `.claude-plugin/` | Nov 2026 (1.1.1) |
| Drawings | Cass's admin frontend, plus the example dashboard app | `layouts/`, `examples/` | — |
| The A/B experiment | With a drawing vs. without one | `ab-test/` | — |
| Perception research | Thymos (affect), social memory, The Velvet (a Thymos-driven agent in a text-drawn venue) | `thymos/`, `social_memory/`, `velvet/` | earlier |
| Theory | Why spatial text encoding matters beyond layout | `doc/` | — |

The README, the pip package and the plugin all describe Ophanic as a layout language. The research tree is a second project sharing the repo. Its `thymos/` is an early standalone prototype. The daemons run their own, larger Thymos in project-cass (`backend/thymos/`), and the two have diverged.

## Proposal

Ophanic becomes the umbrella: text that is spatial, so a model can see. It has two subprojects with their own READMEs, and a frontend plugin that's complete enough to stand on its own.

```
ophanic/
├── README.md               the umbrella: the idea, the two subprojects, where to start
├── ui/                     ★ Ophanic UI: the frontend toolchain and plugin
│   ├── ophanic/            the package (same import name, so `pip install ophanic` keeps working)
│   ├── plugin/             the Claude Code plugin
│   ├── layouts/  examples/  ab-test/
│   └── SPEC.md  doc/       language spec, tokens spec
├── perception/             research: thymos, social_memory, velvet, and their docs
└── doc/                    theory shared by both
```

The marketplace's `source` points at `./ui/plugin`. Installs work as before.

### "A full frontend plugin": what it adds to today's plugin

Today the plugin has one loop, `draw-first`: draw, agree, build, keep. The full version covers a view from first drawing to drift check. Each piece below is built on something that already exists.

| Piece | What it does | Built on |
|---|---|---|
| `draw-first` skill | unchanged, plus one line once tokens ship | exists |
| **`design-system` skill** | Set up and keep a project's `@tokens`: pull them from the existing CSS, name what you style, re-theme in one place | the tokens spec (PR #3), and `DesignTokens` |
| **`states`** in `draw-first` | Draw `@hover`, `@disabled`, `@empty` and `@error`, and get CSS state rules | spec phase 2 |
| **`/ophanic check`** command | Drift: draw the current code with the reverse adapter, compare it with the committed drawing, and report what changed | `react_reverse.py` exists. A structural diff is the new part. |
| **`/ophanic build`** command | Drawing to component skeleton through the React adapter, tokens wired, then handed to frontend-design for the look | `react.py` exists |
| **Review agent** | Reads a PR's UI change against its drawing, and says what the drawing promised and what the code did | the `ophanic` agent, extended |

The split stays the same throughout: Ophanic settles structure and names, and `frontend-design` settles look and feel.

### What first users get

This goes in Babelr first. The Babelr refactor ("Babelr, daemon-first", in Plans with RoboKohl) is where the drawings, tokens, states and drift check get used for real. That's the second real project the tokens spec asks for.

## Order

1. **Move:** `ui/` and `perception/`, two READMEs, the marketplace path, CI. No behavior change. Tests pass unchanged.
2. **Tokens phase 1** (spec PR #3, the "Ophanic design tokens" plan).
3. **`/ophanic check`**, because it's what keeps the Babelr drawings honest during the refactor.
4. **The `design-system` skill and `/ophanic build`.**
5. **States** (tokens phase 2).
6. **The review agent.**

## For Kohl

1. **Split the repo into `ui/` and `perception/` like this?** The alternative is a separate repo for the perception research. I'd keep one repo, since the theory is shared.
2. **The perception tree's `thymos/`:** keep it as a historical prototype, with a note that the live one is in project-cass? Or drop it?
3. **Plugin name:** keep `ophanic` (my pick: nothing breaks), or rename it to `ophanic-ui`?

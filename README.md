# Ophanic

*Named for the Ophanim — the "wheels within wheels" covered in eyes. Nested structures that see.*

**A layout specification language that LLMs can actually see.**

---

> *"I see nobody on the road," said Alice.*
> *"I only wish I had such eyes," the King remarked in a fretful tone. "To be able to see Nobody! And at that distance, too!"*
>
> — Lewis Carroll, *Through the Looking-Glass*

**[Read the theory →](doc/)** Why spatial text encoding might matter beyond layout.

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

**Core toolchain complete.** Parser, React adapter, and reverse adapter are functional.

- [x] Parser — read box-drawing characters, emit layout IR
- [x] React adapter — generate components from IR
- [x] Reverse adapter — generate diagrams from existing React/CSS
- [ ] Figma import — generate diagrams from design files

## Installation

### CLI Tool

```bash
# With pipx (recommended)
pipx install git+https://github.com/KohlJary/ophanic.git

# Or with pip
pip install git+https://github.com/KohlJary/ophanic.git

# For development
git clone https://github.com/KohlJary/ophanic.git
cd ophanic
pipx install -e .
```

### Claude Code Plugin

```bash
# Clone the repo
git clone https://github.com/KohlJary/ophanic.git

# Symlink the plugin to Claude Code's plugin directory
mkdir -p ~/.claude/plugins/cache/local
ln -s /path/to/ophanic/plugin ~/.claude/plugins/cache/local/ophanic

# Register the plugin (add to installed_plugins.json)
# Or just use the /diagram command after symlinking
```

## CLI Usage

### Parse `.oph` files to IR

```bash
# Parse and output JSON IR
ophanic parse layout.oph --pretty

# Parse specific breakpoint
ophanic parse layout.oph --breakpoint mobile
```

### Generate React from `.oph`

```bash
# Generate React/Tailwind components
ophanic generate layout.oph --target react

# Without Tailwind classes
ophanic generate layout.oph --target react --no-tailwind

# Output to file
ophanic generate layout.oph --target react -o components.jsx
```

### Reverse-engineer React to `.oph`

```bash
# Generate diagram from React component
ophanic reverse src/components/Dashboard.tsx

# With explicit CSS file
ophanic reverse src/components/Dashboard.tsx --css src/components/Dashboard.css

# Custom diagram width
ophanic reverse src/components/Dashboard.tsx --width 100

# Output to file
ophanic reverse src/components/Dashboard.tsx -o dashboard.oph
```

## Claude Code Plugin

The plugin provides a `/diagram` command for generating layout diagrams from your codebase.

### Usage

```
/diagram src/pages/Dashboard.tsx
```

This will:
1. Analyze the React component and its CSS
2. Generate an Ophanic diagram showing the layout structure
3. Display it in your terminal

### Example Output

```
# Dashboard

@desktop
┌────────────────────────────────────────────────────────────────────────────┐
│┌─────────────────────┐ ┌─────────────────────────┐ ┌──────────────────────┐│
││ ◆SchedulePanel      │ │ Dashboard | overview    │ │ ◆ChatWidget          ││
│└─────────────────────┘ └─────────────────────────┘ └──────────────────────┘│
└────────────────────────────────────────────────────────────────────────────┘
```

## File Format

Ophanic files (`.oph`) use box-drawing characters to define layouts:

```
# PageName

@desktop
┌────────────────────────────────────────────┐
│┌──────────┐ ┌─────────────────────────────┐│
││ Sidebar  │ │ Main Content                ││
│└──────────┘ └─────────────────────────────┘│
└────────────────────────────────────────────┘

@mobile
┌────────────────────┐
│ Sidebar            │
├────────────────────┤
│ Main Content       │
└────────────────────┘

## ◆Sidebar
@default
┌────────────────┐
│ ◆NavLinks      │
│ ◆UserProfile   │
└────────────────┘
```

Key elements:
- `# Title` — Document title
- `@breakpoint` — Responsive breakpoint (desktop, tablet, mobile, or custom)
- `◆ComponentName` — Reference to a component
- `## ◆ComponentName` — Component definition section
- Box proportions are determined by character widths

## Documentation

- [SPEC.md](SPEC.md) — Full concept specification
- [ab-test/RESULTS.md](ab-test/RESULTS.md) — A/B test results and analysis

## Development

```bash
# Run tests
cd ophanic
pytest

# Run specific test file
pytest tests/test_parser.py -v
```

## License

[Hippocratic License 3.0](LICENSE.md) — An ethical open source license.

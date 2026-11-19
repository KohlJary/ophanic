# Ophanic Plugin for Claude Code

Draw UI layouts as Unicode box diagrams before building them, and keep the drawings as the project's map of its interface.

## Installation

```bash
claude plugin marketplace add /path/to/ophanic   # or KohlJary/ophanic
claude plugin install ophanic@ophanic
```

You also need the CLI on your PATH: `pipx install git+https://github.com/KohlJary/ophanic.git`.

## What's in it

- **`draw-first` skill**: draw a UI before building it, agree on the drawing, build from it, and keep it in `layouts/` as the map of the interface.
- **`/diagram` command** and **`ophanic` agent**: diagrams from existing React components. `reverse` isn't reliable on complex components yet; they say so and fall back to drawing by hand.

## Usage

### /diagram Command

```bash
# Generate diagram from a React component
/diagram src/pages/Dashboard.tsx

# Specify output file
/diagram src/pages/Chat.tsx -o layouts/chat.oph

# Custom width
/diagram src/components/Layout.tsx --width 100
```

### Ophanic Agent

The agent can be invoked for complex layout tasks:
- Batch diagram generation
- Responsive design planning
- Round-trip editing (diagram ↔ code)

## License

MIT

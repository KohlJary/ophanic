---
description: Generate visual layout diagram from a React component
allowed-tools: Bash(python -m ophanic:*), Read, Write
---

Generate a visual layout diagram from a React component using Ophanic.

## Usage

```
/diagram <component-path> [--width N] [-o output.oph]
```

## Examples

```
/diagram src/pages/Dashboard.tsx
/diagram src/components/Layout.tsx --width 100
/diagram src/pages/Chat.tsx -o layouts/chat.oph
```

## Instructions

When the user invokes this command:

1. **Parse the arguments** to extract:
   - `component-path`: The React component file to analyze (required)
   - `--width N`: Diagram width in characters (default: 80)
   - `-o output.oph`: Optional output file path

2. **Generate the diagram** using the ophanic CLI:
   ```bash
   python -m ophanic reverse <component-path> --width <width>
   ```

3. **If output file specified**, save the diagram:
   ```bash
   python -m ophanic reverse <component-path> -o <output-file> --width <width>
   ```

4. **Display the diagram** to the user and explain:
   - The layout structure (columns, rows, nesting)
   - Key components identified (◆ComponentName)
   - Proportions if visible
   - Any suggestions for responsive improvements

5. **For responsive design work**, offer to:
   - Create breakpoint variants (@tablet, @mobile)
   - Generate modified React code from updated diagrams
   - Round-trip: modify diagram → regenerate React

## Auto-Detection

The `reverse` command auto-detects:
- CSS Modules (imports like `import './Component.css'`)
- Tailwind CSS (className with utility classes)

Use `--tailwind` flag to force Tailwind parsing if auto-detection fails.

## Notes

- The ophanic package must be installed/available (`pip install -e /path/to/ophanic`)
- Works with both Tailwind CSS and CSS Modules projects
- Complex conditional rendering shows the main return (last return statement)

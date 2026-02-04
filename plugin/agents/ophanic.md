# Ophanic Layout Agent

Specialized agent for visual layout analysis and generation using Ophanic diagrams.

## Purpose

Help Claude Code understand, visualize, and modify UI layouts by:
1. Generating Ophanic diagrams from existing React components
2. Planning responsive design changes
3. Generating React code from modified diagrams

## Capabilities

### Analyze Existing Code (React → Ophanic)
```bash
python -m ophanic reverse <component.tsx> [--css <styles.css>] [--width 80]
```

The `reverse` command auto-detects CSS approach:
- CSS Modules: detected from `import './file.css'` statements
- Tailwind: use `--tailwind` flag to force

### Generate React from Ophanic
```bash
python -m ophanic generate <layout.oph> [--target react] [--no-tailwind]
```

### Parse Ophanic to JSON IR
```bash
python -m ophanic parse <layout.oph> [--pretty]
```

## Workflow: Making a Component Responsive

1. **Analyze current state**
   - Generate diagram from existing component
   - Note current breakpoints (if any)
   - Identify fixed vs flexible elements

2. **Design breakpoint variants**
   - Create @desktop diagram (current layout)
   - Create @tablet diagram (collapse sidebars, stack elements)
   - Create @mobile diagram (single column, bottom nav)

3. **Generate implementation**
   - Use `ophanic generate` to produce React/Tailwind
   - Or manually implement from the visual spec

## Ophanic Syntax Quick Reference

```ophanic
# ComponentName

@desktop
┌──────────────────────────────────────────────────────┐
│ ┌────────┐ ┌──────────────────────────┐ ┌──────────┐ │
│ │SIDEBAR │ │ CONTENT                  │ │ CHAT     │ │
│ └────────┘ └──────────────────────────┘ └──────────┘ │
└──────────────────────────────────────────────────────┘

@tablet
┌────────────────────────────────────────┐
│ ┌────────────────────────────────────┐ │
│ │ CONTENT                            │ │
│ └────────────────────────────────────┘ │
│ ┌────────────────┐ ┌────────────────┐  │
│ │ SIDEBAR        │ │ CHAT           │  │
│ └────────────────┘ └────────────────┘  │
└────────────────────────────────────────┘

@mobile
┌────────────────────┐
│ CONTENT            │
├────────────────────┤
│ CHAT (collapsed)   │
├────────────────────┤
│ ≡ MENU    ◆ NAV    │
└────────────────────┘
```

**Key elements:**
- `┌─┐│└─┘` - Box drawing for containers
- `◆ComponentName` - Component references
- `@breakpoint` - Responsive breakpoints
- Proportions inferred from box widths

## When to Use This Agent

- Visualizing complex component layouts
- Planning responsive design changes
- Understanding unfamiliar frontend code
- Generating layout documentation
- Refactoring layout structure
- Batch-generating diagrams for a codebase

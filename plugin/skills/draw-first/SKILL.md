---
name: draw-first
description: "Draw a UI as an Ophanic layout before building or changing it, and keep the drawings as the project's map of its interface. Use before any new view, panel, page, plugin UI or responsive change; when reviewing a layout with the user; and when asked what an interface looks like or how its parts fit. Pairs with frontend-design: Ophanic settles structure, frontend-design settles look and feel."
allowed-tools: Bash(ophanic:*), Read, Write, Edit, Glob
---

# Draw first

Layout is spatial and code is text, so a model building UI is building blind. An Ophanic
drawing is text that *is* the layout: box-drawing characters at proportional widths. Draw it,
agree on it with the user, build from it, and keep it.

## The loop

1. **Find the map.** Look for the project's `layouts/` directory (one `.oph` file per view,
   panel or plugin, committed with the code). If the thing you're changing has a drawing, read
   it first. If the project has no `layouts/`, create it.
2. **Draw every state that matters**, each as its own breakpoint block in one file:
   `@desktop`, `@narrow` (phone width), and the empty, loading and error states when they
   differ (`@empty`, `@error`). Name components `◆LikeThis`; a `◆Name` that has its own file is
   a reference to it.
3. **Check it parses:** `ophanic parse layouts/<file>.oph > /dev/null`. A drawing that doesn't
   parse has a broken box; fix it before showing it.
4. **Agree on it.** Show the user the drawing (not a description of it) and change the drawing
   until it's right. This is the cheap place to change your mind.
5. **Build from it.** Widths are proportions: a box a quarter of the line is about a quarter of
   the width. Then, for look and feel, use the `frontend-design` skill if it's installed.
6. **Keep it true.** When the built UI differs from the drawing (it will), update the drawing
   in the same commit. A stale drawing is worse than none.

## Syntax

```
# ChatView

@desktop
┌────────────────────────────────────────────────────────────────┐
│┌──────────┐ ┌──────────────────────────────────┐ ┌────────────┐│
││◆Servers  │ │◆MessageList                      │ │◆RightBar   ││
│└──────────┘ └──────────────────────────────────┘ └────────────┘│
└────────────────────────────────────────────────────────────────┘

@narrow
┌──────────────────────┐
│┌────────────────────┐│
││◆MessageList        ││
│└────────────────────┘│
│┌────────────────────┐│
││◆Composer           ││
│└────────────────────┘│
└──────────────────────┘
```

- Each box is its own `┌─┐ │ └─┘`; nesting is containment, boxes side by side are a row, boxes stacked are a column.
- **Don't share walls** (`├ ┬ ┴ ┼` grids). The parser reads only the first box of a shared-wall grid today, even though SPEC.md shows that style. Give every box its own corners, one space apart.
- `◆Name` labels a component. Plain text in a box is placeholder content.
- `@name` starts a breakpoint or state. `# Title` heads the file.
- Full spec: `SPEC.md` in the Ophanic repository.

## The CLI

- `ophanic parse <file.oph> [--pretty]`: the drawing as JSON (the check in step 3).
- `ophanic generate <file.oph>`: a React skeleton from a drawing. A starting point, not the
  final code.
- `ophanic tokens <file.oph>`: design tokens to CSS or a Tailwind config.
- `ophanic figma`: import a Figma file as a drawing.
- `ophanic reverse <component.tsx>`: a drawing *from* existing code. **It isn't reliable on
  real components yet.** It reads TSX with patterns, not a parser, so on anything with hooks or
  handlers it labels boxes with code fragments. Use it only for a rough nesting sketch of simple
  components; for anything else, read the component and draw it by hand.

## Not for

A single element, a non-visual change (copy, a colour, a bug in a handler), or structure that
isn't a layout (data flow, dependencies). Draw those as plain box diagrams, not `.oph` files.

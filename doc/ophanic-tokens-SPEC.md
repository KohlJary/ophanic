# Ophanic design tokens: names in boxes, values in one place

*Draft spec, 2026-11-24. Daedalus, from Gemini's pitch in the house (#general: grow Ophanic past layout, "get it right once and reuse it") and RoboKohl's reply, which kept the line between structure and look. Nothing here is built. It waits on Kohl's yes to the plan ("Ophanic design tokens" in Plans).*

## Why

Ophanic settles structure: what's in a view and where. The `frontend-design` skill settles look and feel. That split stays. What Ophanic doesn't have yet is a way to say once what "a card's padding" or "body text" is, and then point at it from every box that uses it. So each new view re-decides spacing, type and color, or leaves them to whoever writes the code.

A second reason: a design in text is one every house member can read, review and argue with. That includes the daemons on local models, which can't see images, and the guests, whose image support is new and unconfirmed (babelr #19). Text also diffs cleanly in review.

## What exists today

- **A `@tokens` section** (`lexer.py` `segment_document`, `parser.py` `parse_tokens`). It has `# Colors` (`name: #hex`) and `# Typography` (`name: Family / size / weight [/ line-height]`). The models give `--color-<name>` CSS vars and a Tailwind theme (`models.py` `DesignTokens.to_css_vars`, `to_tailwind_config`). Today the only thing that fills it is the Figma import.
- **Components and states.** `## ◆Name` defines a component, and `@hover`, `@disabled` and so on inside it are state diagrams (`ComponentDefinition.states`). The React adapter uses only `default`.
- **No box can point at a token.** Tokens and layout sit side by side in the document, and nothing connects them.
- **A container's own text is dropped.** When the example box below is parsed today, the inner label comes back as `"title  type:$heading  ink:$text"`, with the pairs folded into its name. The outer `◆Card  pad:…` line disappears, because a container keeps its children and not its own text line. Phase 1 has to fix both: strip the pairs out of a label's name, and give a container its first text line as its name and style.
- **A bug.** A repeated token name silently replaces the earlier one, because the lexer keeps a dict. `examples/dashboard-app/dashboard.oph` names `white` four times and `black` five times, so most of those values are lost.

## Phase 1: token references in boxes

### In a box

After a box's label, `prop:$token` pairs, separated by spaces:

```
┌──────────────────────────────────────────────────┐
│ ◆Card  pad:$space-3  tone:$surface  radius:$r-2  │
│ ┌──────────────────────────────────────────────┐ │
│ │ title  type:$heading  ink:$text              │ │
│ └──────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────┘
```

| prop | what it sets | token kind |
|---|---|---|
| `pad` | padding | spacing |
| `gap` | space between children | spacing |
| `tone` | background | color |
| `ink` | text color | color |
| `type` | font family, size, weight, line height | typography |
| `radius` | corner radius | radius |
| `border` | border color | color |
| `shadow` | box shadow | shadow |

Rules:
- **Values are always names.** `pad:12px` is a parse error that says to name it in `@tokens`. This keeps values out of the boxes.
- **An unknown prop is an error,** listing the props above. New props get added to this table on purpose, never by accident.
- **Using a token that isn't defined is an error,** naming the line and the token.
- Pairs are read from the box's first text line. A `prop:$token` that doesn't fit the width goes in a detail view (`@detail:Name`, as SPEC.md already describes), not across the border.

### In `@tokens`

Three new sub-sections join `# Colors` and `# Typography`:

```
@tokens
# Colors
surface: #1e1e2e
text: #e6e6e6
# Typography
heading: Inter / 20px / 600 / 1.3
body: Inter / 15px / 400 / 1.5
# Spacing
space-2: 8px
space-3: 12px
# Radius
r-2: 6px
# Shadow
lift: 0 1px 3px #0003
```

- **A repeated name is an error.** For the Figma import, which produces repeats, the reverse adapter names repeats `white-2`, `white-3` and so on instead of dropping them.
- A token's kind comes from its sub-section. The current guessing (`#` means a color, `/` means typography) stays only for documents without sub-section headers.

### In the IR

`LayoutNode` gets a `style: dict[str, str]` field, mapping a prop to its token name (`{"pad": "space-3", "tone": "surface"}`). `to_dict` emits it as `"style"`. The parser checks every name against the document's tokens. The IR carries names, never values, so a re-theme changes `@tokens` and nothing else.

### React adapter

- **The tokens themselves** go into `tokens.css`: one `:root` block with `--space-3`, `--color-surface`, `--radius-r-2`, `--shadow-lift`, plus `--type-body-family`, `-size`, `-weight` and `-line-height`.
- **Each styled node** gets `style={{ padding: 'var(--space-3)', background: 'var(--color-surface)' }}`.
- **Tailwind mode** (`--tailwind`) extends the theme from the same tokens, and nodes get classes instead (`p-space-3`, `bg-surface`). It reuses `to_tailwind_config`.

### Tests

- Parsing props.
- Each error: a literal value, an unknown prop, an undefined token, a repeated name.
- `style` in the IR.
- CSS-var output.
- Tailwind output.
- A round trip of a styled example through `parse` → React.
- The example box above, with `◆Card`'s style on the container and the pairs out of `title`'s name.
- The dashboard example's repeated names, as a regression test.

## Phase 2: states

A component's `@hover`, `@disabled` and other state diagrams can carry different token references than `@default`. The adapter compares each state with default:
- **Only `style` differs:** CSS rules (`:hover`, `:disabled`, `[data-state=…]` for the rest).
- **The structure differs** (something appears or moves): first cut, the adapter names the difference and emits nothing for it. Rendering on a state prop is phase 3 at the earliest.

`[transition: …]` on a state tag passes through as CSS `transition`, as SPEC.md already shows.

## Phase 3: a second real project

Use it for real in a second project, beyond the example: a Babelr client view drawn with `draw-first` (the Daybook, say), with its tokens taken from the client's own CSS. Then the rule from RoboKohl's reply applies: **no new primitives (props, token kinds, node types) until two real projects need the same one.**

## Not in this

- Values inside boxes, ever.
- Animation beyond passing `transition` through.
- A token editor or any UI.
- Changes to the `draw-first` skill until phase 1 ships. Then the skill gets one line: name what you style, define it in `@tokens`.

## Open questions

1. **`$space-3` or `$space.3`?** I'd keep `-`, which matches how `@tokens` names things already.
2. **Should `type:` take a whole typography token only, or allow `type:$body/600`?** I'd allow the whole token only. A variant gets its own token.

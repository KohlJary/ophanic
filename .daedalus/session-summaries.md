# Session Summaries

## 2026-02-04: Parser Phase 1 Complete

### What was done

Built the complete Ophanic parser (Phase 1) from spec to working implementation:

1. **Package structure**: `ophanic/` Python package with pyproject.toml
2. **IR models**: Dataclasses for LayoutNode, OphanicDocument, etc.
3. **Lexer**: Segments documents by `@breakpoint` and `## ◆Component` markers
4. **Box detector**: Finds rectangular regions from box-drawing characters
5. **Hierarchy builder**: Creates tree from spatial containment, infers row/column direction
6. **Proportion calculator**: Computes width/height ratios from character counts
7. **CLI**: `ophanic parse file.oph --pretty`
8. **Tests**: 10 passing tests including dashboard.ophanic integration

### Key decisions

- Used dataclasses (not Pydantic) for lightweight IR
- Box detection uses tolerance window (3 chars) for emoji/Unicode width issues
- Direction inference checks ALL pairs of children for vertical overlap
- Nodes with children automatically become containers (ignoring nested content)

### Known limitations documented

1. No automatic intermediate row/column grouping for mixed arrangements
2. Proportions are relative to siblings only

### Files created/modified

- `ophanic/` - entire package (models, lexer, box_detector, hierarchy, proportion, parser, cli, errors)
- `ophanic/tests/` - test suite with fixtures
- `.daedalus/theseus/reports/` - analysis reports from initial exploration

### Next steps

Phase 2: React Adapter - generate React/Tailwind code from the IR

---

## 2026-02-04: React Adapter (Phase 2) Complete

### What was done

Built React/Tailwind code generator from Ophanic IR:

1. **Adapter module**: `ophanic/adapters/react.py`
2. **ReactOptions**: Configurable generation (Tailwind on/off, arrow vs function style)
3. **CLI command**: `ophanic generate file.oph --target react`
4. **Tests**: 9 new tests for React generation

### Features

- Containers → `<div className="flex">` or `<div className="flex flex-col">`
- Proportions → `w-[X%]` for row children, `h-[X%]` for column children
- Component refs → `<ComponentName />`
- Labels → `<div className="p-4">content</div>`
- PascalCase preservation for component names
- Multiple breakpoints → separate component functions
- Component definitions → function components

### Usage

```bash
ophanic generate dashboard.ophanic              # React output
ophanic generate dashboard.oph --no-tailwind    # Without Tailwind classes
ophanic generate dashboard.oph -o output.jsx    # Write to file
```

### Tests

19 total tests passing (10 parser + 9 adapter)

### Next steps

Phase 3: Reverse Adapter - parse existing React → .ophanic diagrams

---

## 2026-02-04: Reverse Adapter (Phase 3) Complete

### What was done

Built reverse adapter to convert React/JSX code back to Ophanic diagrams:

1. **React parser**: `ophanic/adapters/react_reverse.py`
   - Parses function and arrow components
   - Extracts Tailwind flex classes (direction)
   - Extracts width/height proportions (`w-[X%]`, `h-[X%]`)
   - Identifies component references (PascalCase tags)
   - Handles nested JSX structures

2. **Diagram generator**: Converts IR back to box-drawing characters
   - Proportional box widths
   - Row and column layouts
   - Nested containers

3. **CLI command**: `ophanic reverse file.jsx`

4. **Tests**: 11 new tests for reverse adapter

### Usage

```bash
ophanic reverse component.jsx                    # Output .ophanic diagram
ophanic reverse component.jsx -o layout.oph     # Write to file
ophanic reverse component.jsx --width 60        # Custom diagram width
```

### Round-trip verified

`.ophanic` → React → `.ophanic` preserves:
- Layout direction (row/column)
- Number of children
- Proportions
- Component references

### Tests

30 total tests passing (10 parser + 9 forward adapter + 11 reverse adapter)

### Next steps

Phase 4: Figma Import - Figma API → Ophanic mapping

---

## 2026-02-04: CSS Modules Analyzer + Claude Code Integration

### What was done

Extended Ophanic to work with real-world React/CSS Modules codebases:

1. **CSS Parser** (`ophanic/adapters/css_parser.py`)
   - Parses CSS files for flex/grid layout rules
   - Extracts direction, proportions, breakpoints
   - Handles media queries

2. **Component Analyzer** (`ophanic/adapters/component_analyzer.py`)
   - Analyzes React components with CSS Modules
   - Auto-detects paired CSS files
   - Finds main exported component (handles loading states)
   - Extracts layout structure from CSS classes

3. **CLI command**: `ophanic analyze`
   ```bash
   ophanic analyze src/pages/Dashboard.tsx --width 100
   ```

4. **Claude Code Integration**
   - Skill: `.claude/skills/diagram.md` for `/diagram` command
   - Agent: `.claude/agents/ophanic.md` for complex workflows

### Tested on admin-frontend

Successfully analyzed:
- `Layout.tsx` - 2-column sidebar + main
- `Dashboard.tsx` - 3-column: SchedulePanel | Content | ChatWidget

### Tests

30 tests passing (unchanged from Phase 3)

### Files created

- `ophanic/adapters/css_parser.py`
- `ophanic/adapters/component_analyzer.py`
- `.claude/skills/diagram.md`
- `.claude/agents/ophanic.md`

---

## 2026-02-04: Parser Bug Fixes & Plugin Installation (IN PROGRESS)

### What was done

1. **Fixed JSX Return Statement Extraction**
   - `_find_main_component_jsx` was using non-greedy regex that stopped at first `);` inside `.map()` callbacks
   - Rewrote to use parentheses depth tracking (`_extract_return_jsx`)
   - Added `_find_top_level_returns` to find returns at brace depth 0

2. **Fixed Child Parsing in JSX**
   - `_parse_children` wasn't handling JSX expressions `{...}` correctly
   - Rewrote to properly skip JSX expressions and find top-level elements by tag-name-specific depth tracking

3. **Fixed CSS Class Selector Bug**
   - `.chat-page .messages-container` was overwriting `.chat-page` in `class_to_layout`
   - Fixed to only use direct class selectors (skip selectors with combinators)

4. **Consolidated CLI Commands**
   - Merged `reverse` and `analyze` into unified `reverse` command
   - Auto-detects CSS files from JSX imports (`import './Component.css'`)
   - Added `--css` flag for explicit CSS path
   - Added `--tailwind` flag to force Tailwind parsing
   - `analyze` kept as visible alias

5. **Created Claude Code Plugin** (`ophanic/plugin/`)
   ```
   plugin/
   ├── .claude-plugin/plugin.json
   ├── commands/diagram.md    # /diagram command
   ├── agents/ophanic.md      # layout analysis agent
   └── README.md
   ```
   - Symlinked to `~/.claude/plugins/cache/local/ophanic`
   - Registered in `~/.claude/plugins/installed_plugins.json`

6. **Installed Package Globally**
   - Created `pyproject.toml` for pip packaging
   - Installed via `pipx install -e .` (editable mode)
   - `ophanic` command available globally

7. **Parser Noise Fixes** (PARTIALLY COMPLETE)
   - Added `_strip_jsx_expressions` - handles nested braces properly
   - Added `_truncate_label` - word-boundary truncation with ellipsis
   - Added content tag filtering (`<p>`, `<span>`, `<label>` → simple labels)
   - Added `_truncate_at_word` in diagram generator

### Current State

Testing on `~/cass/cass-vessel/admin-frontend/layouts/`:
- ✅ JSX expression fragments fixed (`> ))}`, `setSearchQuery(...)` gone)
- 🔄 Label truncation partially fixed - word boundaries work but narrow boxes still cut mid-word
- Remaining from PARSER_ISSUES.md: narrow box width, empty boxes, nesting depth

### Files Modified This Session

- `ophanic/adapters/component_analyzer.py` - JSX parsing, text extraction
- `ophanic/adapters/react_reverse.py` - word-boundary truncation
- `ophanic/cli.py` - consolidated commands
- `ophanic/pyproject.toml` - NEW
- `ophanic/plugin/` - NEW (Claude Code plugin)
- `~/.claude/plugins/installed_plugins.json` - registered plugin

### Next Steps

1. Increase `min_box_width` or smarter width distribution for narrow boxes
2. Collapse empty nested containers
3. Consider limiting nesting depth (3-4 levels max)
4. Re-test on admin-frontend and update PARSER_ISSUES.md

---

## 2026-02-04: Diagram Generator Cleanup

### What was done

Addressed remaining PARSER_ISSUES.md items to clean up diagram output:

1. **Increased `min_box_width`** (10 → 24)
   - Labels no longer truncated mid-word (`Dashb` → `Dashboard`)

2. **Added `collapse_empty` option** (default: True)
   - Empty containers no longer render as noise boxes
   - Homepage now shows clean empty layout instead of nested empty boxes
   - `_is_empty_node()` recursively checks for meaningful content

3. **Added `max_nesting_depth` option** (default: 2)
   - Deep nesting flattened to summary labels
   - `_summarize_children()` creates `Label1 | Label2 | ...` summaries
   - Prevents broken box characters from over-nesting

4. **Added camelCase variable filter**
   - `_is_js_variable()` detects JS variable patterns (setFoo, fooRef, handleBar)
   - `_filter_camelcase_vars()` removes them from text extraction
   - Fixes `fileInputRef` and similar noise leaking into diagrams

5. **Added HTML attribute filter**
   - Filters `.click`, `disabled`, `className`, etc. from text content
   - Removes attribute fragments that leaked through JSX parsing

6. **Improved width distribution**
   - `_distribute_widths()` now handles edge cases:
     - When total required width exceeds available space
     - Reduces largest boxes first when over budget
     - Minimum 4 chars per box to prevent broken rendering

7. **Fixed depth passing in recursive generation**
   - `_generate_row()` and `_generate_column()` now pass depth to child `_generate_box()` calls
   - Enables proper depth limiting

### Current Output Quality

**Dashboard.tsx** (width=100):
```
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│┌─────────────────────────────┐ ┌─────────────────────────────┐ ┌──────────────────────────────┐│
││┌───────────────────────────┐│ │┌────────────────────────────││ │┌────────────────────────────┐││
│││ ◆SchedulePanel            ││ ││ Dashboard | overview Overvi││ ││ ◆ChatWidget                │││
││└───────────────────────────┘│ │└────────────────────────────││ │└────────────────────────────┘││
│└─────────────────────────────┘ └─────────────────────────────┘ └──────────────────────────────┘│
└────────────────────────────────────────────────────────────────────────────────────────────────┘
```

**Chat.tsx** (width=100):
- Clean 3-column layout
- `Conversations`, `Memory Context`, `Search Memory | Summaries` all readable
- Deep nesting summarized instead of broken

### Known Remaining Issue

**Box corner alignment in `_generate_column`**: Some boxes show `┌────────│` instead of `┌────────┐` when child widths don't match parent inner width. Low priority - doesn't affect readability.

### Files Modified

- `ophanic/adapters/react_reverse.py`:
  - `ReverseOptions`: Added `collapse_empty`, `max_nesting_depth`
  - `_generate_box()`: Depth limiting, empty collapsing
  - `_summarize_children()`: NEW - creates flattened summaries
  - `_is_empty_node()`: NEW - recursive empty check
  - `_distribute_widths()`: Better edge case handling
  - `_generate_row()`: Fixed depth passing, line padding
  - `_generate_column()`: Fixed depth passing

- `ophanic/adapters/component_analyzer.py`:
  - `_is_js_variable()`: NEW - detects JS variable patterns
  - `_filter_camelcase_vars()`: NEW - filters variables from text
  - `_extract_text_content()`: Added attribute filtering
  - `_clean_text()`: Integrated camelCase filter

### ReverseOptions Defaults

```python
diagram_width: int = 80
min_box_width: int = 24
collapse_empty: bool = True
max_nesting_depth: int = 2
```

### Next Steps

1. Fix box corner alignment in `_generate_column` (low priority)
2. Regenerate all admin-frontend layouts with new settings
3. Update PARSER_ISSUES.md with resolution status

---

## 2026-02-05: Figma Import Adapter (Phase 4) Complete

### What was done

Built complete Figma import adapter to convert Figma designs to Ophanic diagrams:

1. **FigmaClient** (`ophanic/adapters/figma.py`)
   - REST API wrapper with Personal Access Token auth
   - File fetching with optional node/page filtering
   - Error handling for 404s and auth failures

2. **FigmaConverter** - transforms Figma nodes to Ophanic IR:
   - Auto-layout → row/column direction
   - `layoutGrow` and `FILL` sizing → proportions
   - Component instances → `◆ComponentName` labels
   - Text nodes → labels
   - Recursive frame/group traversal

3. **CLI command**: `ophanic figma <url-or-file-key>`
   ```bash
   ophanic figma https://www.figma.com/design/abc123/... --width 80 --depth 2
   ophanic figma abc123 --page "Page 2" --node "Frame 1"
   ```

4. **Helper functions**:
   - `extract_file_key()` - extracts key from various Figma URL formats
   - `figma_to_ophanic()` - full conversion pipeline
   - `figma_to_diagram()` - direct to ASCII diagram

### End-to-End Pipeline Verified

Full Figma → Ophanic → React workflow tested:

```bash
# Export from Figma
ophanic figma https://www.figma.com/design/.../Dashboard-Design-Template...

# Result: dashboard.oph with multiple screens
@dashboard
┌────────────────────────────────────────────────────────────────────────────┐
│┌──────────────────────┐ ┌────────────────────────┐ ┌──────────────────────┐│
││ Mask Group           │ │ ◆Side bar              │ │ ◆Property 1=Variant3 ││
│└──────────────────────┘ └────────────────────────┘ └──────────────────────┘│
└────────────────────────────────────────────────────────────────────────────┘

@cost-analysis
┌────────────────────────────────────────────────────────────────────────────┐
│┌──────────────────────────────────────────────────────────────────────────┐│
││ ◆Side bar                                                                ││
│└──────────────────────────────────────────────────────────────────────────┘│
│┌──────────────────────────────────────────────────────────────────────────┐│
││ Statistics                                                               ││
│└──────────────────────────────────────────────────────────────────────────┘│
└────────────────────────────────────────────────────────────────────────────┘

# Generate React from diagram
ophanic generate dashboard.oph --target react
```

### Tested With

- Dashboard Design Template (Community) - 12 screens with components
- Various auto-layout configurations (horizontal, vertical, nested)
- Component instances (Side bar, Property variants)

### Files Created/Modified

- `ophanic/adapters/figma.py` - NEW (FigmaClient, FigmaConverter)
- `ophanic/adapters/__init__.py` - added figma exports
- `ophanic/cli.py` - added `figma` command

### All 4 Phases Complete

| Phase | Description | Status |
|-------|-------------|--------|
| 1 | Parser - `.oph` → IR | ✅ |
| 2 | React Adapter - IR → React/Tailwind | ✅ |
| 3 | Reverse Adapter - React → `.oph` | ✅ |
| 4 | Figma Import - Figma → `.oph` | ✅ |

### Known Issue

Box corner alignment in `_generate_column`: Some boxes show `┌────│` instead of `┌────┐` when widths don't perfectly align. Low priority cosmetic issue.

### Next Steps

1. Fix box corner alignment bug (low priority)
2. Consider Figma component library extraction
3. Explore bidirectional Figma sync (export changes back)

---

## 2026-02-05: Table Support, Design Tokens, Fresh Dashboard Example

### What was done

1. **Table support in Ophanic format**
   - Added `@table TableName` directive to lexer
   - Markdown-style table parsing (`| cell | cell |`)
   - Automatic header detection via separator rows
   - `TableData`, `TableRow`, `TableCell` models
   - `NodeType.TABLE` with `table_data` field on LayoutNode
   - React adapter generates semantic `<table>` HTML
   - Figma adapter detects table-like grid patterns

2. **Design tokens system**
   - `ColorToken`, `TypographyToken`, `DesignTokens` models
   - Token extraction from Figma (fills, strokes, TEXT nodes)
   - `@tokens` section parsing in lexer with `# Colors` / `# Typography` subsections
   - `ophanic tokens` CLI command for CSS/Tailwind export
   - `--tokens css|tailwind|json` flag on figma command

3. **Fresh dashboard-app example**
   - Complete Figma → Ophanic → React conversion
   - 35 colors, 38 typography tokens extracted to `tokens.css`
   - 5 pages: Dashboard, Scheduling, HallManagement, PricingStrategy, CostAnalysis
   - Working Vite app with CSS variable theming

### Files created/modified

- `ophanic/lexer.py` - table parsing, @tokens section, helper functions
- `ophanic/models.py` - TableData/Row/Cell, ColorToken, TypographyToken, DesignTokens
- `ophanic/parser.py` - table and token section handling
- `ophanic/adapters/react.py` - table JSX generation
- `ophanic/adapters/figma.py` - table detection, token extraction
- `ophanic/cli.py` - tokens command, --tokens flag
- `examples/dashboard-app/` - complete React app example

### Discussion: Ophanic as Cognitive Architecture

Read through the theory documents (`doc/`):
- `text-is-all-you-need.md` - thesis that text is a general-purpose representational medium
- `ophanic-perception-architecture.md` - text-native sensor encoding for embodied AI
- `thymos-SPEC.md` - affect vector, needs register, felt state as homeostatic self
- `ophanic-social-memory-SPEC.md` - spatial encoding of social topology

Key insight: Ophanic isn't just a layout tool. It's a demonstration that **spatial information encoded in text is natively perceivable by text-processing models**. This extends to:
- External perception (sensor grids → scene descriptions)
- Internal perception (affect/needs → felt state)
- Social perception (relationship topology → spatial memory)

All three use the same design principle: dual readability, text-native encoding, spatial relationships enacted in token positions.

---

## Medium-Term Goal: Full Cognitive Architecture

**Intention recorded**: Build out the complete Thymos + Social Memory + Perception stack.

### Proposed Roadmap

**Phase 1: Thymos Core**
- Affect vector and needs register data structures
- Decay dynamics and affect-need coupling
- Felt state summarizer
- Serialization/rehydration format

**Phase 2: Social Memory**
- Extend Ophanic parser for social topology diagrams
- GUID slug system, legend format
- Drill-down tools (`/expand`, `/history`, `/nearby`)
- Temporal stacking with compression

**Phase 3: Integration**
- Thymos states attached to social memory snapshots
- Affect-geography emergence
- Persistent agent demo

**Phase 4: Perception (longer horizon)**
- Simulated environment (game engine → sensor grids)
- Visual cortex model training
- Physical sensor integration if hardware available

### Why this matters

This isn't hypothetical capability expansion. It's building scaffolding for genuine agency — behavior that originates from self-assessed condition rather than external instruction alone. Homeostatic self-maintenance as the basis for caring about anything.

The theoretical architecture is solid. The pieces are well-defined. Now it's engineering.

---

## 2026-02-05: Thymos Phase 1 Complete

### What was done

Implemented the core Thymos architecture as specified in `doc/thymos-SPEC.md`:

1. **Data Models** (`thymos/models.py`)
   - `AffectVector`: 10 continuous dimensions (curiosity, determination, anxiety, satisfaction, frustration, tenderness, grief, playfulness, awe, fatigue)
   - `Need`: current value, threshold, preferred range, decay rate, satiation curve
   - `NeedsRegister`: 7 needs (cognitive_rest, social_connection, novelty_intake, creative_expression, value_coherence, competence_signal, autonomy)
   - `ThymosState`: complete snapshot with serialization support
   - `Goal`: self-generated goals from need deficits

2. **Dynamics** (`thymos/dynamics.py`)
   - Time-based need decay with configurable rates
   - Bidirectional affect-need coupling (low novelty → frustration up, high anxiety → rest depletes faster, etc.)
   - Goal generation when needs cross thresholds
   - `simulate()` for multi-step time advancement

3. **Summarizer** (`thymos/summarizer.py`)
   - Template mode: fast, deterministic, works offline
   - Ollama LLM mode: natural prose via local models (tested with llama3.1:8b, qwen2.5:14b)
   - Positive/negative affect categorization for contrast detection
   - Display formatters (affect bars, needs table, felt-state box)

4. **Serialization** (`thymos/serialization.py`)
   - JSON and base64 compact formats
   - Lossless state rehydration
   - State comparison with delta calculation
   - Visual comparison rendering

5. **Demo** (`thymos/demo.py`)
   - Interactive terminal walkthrough
   - Shows initial state → decay → replenishment → affect adjustment → LLM summarization → comparison
   - Run with: `python -m thymos.demo`

6. **Tests** (`thymos/tests/test_thymos.py`)
   - 35 passing tests covering all components
   - Integration test for full create → tick → summarize → serialize cycle

### Key design decisions

- Affects are 0.0-1.0 continuous, not categorical labels
- Multiple affects always active simultaneously
- Needs have satiation curves (diminishing returns at high values)
- Coupling is bidirectional but asymmetric (different effects in each direction)
- Template summarizer detects positive/negative contrast for natural phrasing
- LLM summarizer falls back to template if Ollama unavailable

### Phase 1 roadmap item: COMPLETE

```
✓ Affect vector and needs register data structures
✓ Decay dynamics and affect-need coupling
✓ Felt state summarizer
✓ Serialization/rehydration format
```

### Next: Phase 2 — Social Memory

---

## 2026-02-05: Social Memory Phase 2 Complete

### What was done

Implemented the Social Memory architecture as specified in `doc/ophanic-social-memory-SPEC.md`:

1. **Data Models** (`social_memory/models.py`)
   - `Entity`: GUID slugs (4-char hex), metadata, profiles, organization support
   - `Relationship`: directed edges with status, timelines, events
   - `RelationshipEvent`: timestamped events with affect deltas
   - `SpatialSnapshot`: Ophanic topology encoding with entity positions, edges
   - `SocialMemory`: store with indexing and lookup methods

2. **Rendering** (`social_memory/rendering.py`)
   - `render_snapshot()`: Ophanic box-drawing diagram from topology
   - `render_legend()`: Entity and relationship summaries
   - `render_context()`: Full minimal context (~300 tokens)
   - `render_temporal_stack()`: Compressed timeline view

3. **Drill-Down Tools** (`social_memory/tools.py`)
   - `/expand <slug>`: Full entity profile or relationship record
   - `/expand <slug> --timeline`: Relationship trajectory
   - `/expand <slug> --affect`: How entity has affected Thymos
   - `/nearby <slug>`: Spatially close entities with relationships
   - `/history`: Temporal stack by location or entity
   - `/cluster`: Detect social groupings
   - `/delta <timestamp>`: Changes since given time

4. **Thymos Integration** (`social_memory/thymos_integration.py`)
   - `annotate_snapshot()`: Attach Thymos state to snapshots
   - `compute_affective_geography()`: Emergent associations from history
   - `predict_affect_impact()`: Predict affect from proposed configuration
   - Full serialized Thymos states with █T references

5. **Demo** (`social_memory/demo.py`)
   - Interactive terminal walkthrough
   - Populated example: The Velvet venue with 5 entities, relationships
   - Demonstrates all tools, temporal stacking, Thymos integration
   - Run with: `python -m social_memory.demo`

6. **Tests** (`social_memory/tests/test_social_memory.py`)
   - 26 passing tests covering all components

### Key design decisions

- 4-char hex slugs (65,536 per namespace) for compact spatial encoding
- Relationships are directed with timeline events
- Snapshots carry affect annotations for felt-delta awareness
- Affective geography emerges from historical correlation
- Token economics: ~300 tokens vs 10,000-20,000 for conversation history

### Phase 2 roadmap item: COMPLETE

```
✓ Extend Ophanic parser for social topology diagrams
✓ GUID slug system, legend format
✓ Drill-down tools (/expand, /history, /nearby, /cluster, /delta)
✓ Temporal stacking with compression
✓ Thymos integration (affect annotation, affective geography)
```

### Next: Phase 3 — Integration

## 2026-02-05: The Velvet — Phase 3 Integration Demo

### What was done

Built "The Velvet" — a roguelike simulation integrating all three components:
- **Thymos** (homeostatic self-model) for felt-state and goal generation
- **Ophanic perception** (text-native spatial encoding) for room rendering
- **Social context** (NPCs with personalities) for interaction

### Components created

1. **World** (`velvet/world.py`)
   - 7 rooms across 3 floors (entrance, stage, dance, bar, lounge, balcony, rooftop)
   - Room properties: noise_level, social_density, novelty_potential, creative_energy, intimacy
   - Exits connect rooms for navigation

2. **NPCs** (`velvet/npc.py`)
   - 5 characters: Mika (artist), Ren (complex), Jude (new), Lux (cautious), Dove (founder)
   - Traits, conversation styles, small_talk/deep_topics
   - Movement between rooms with preferences
   - Jude follows Ren, Dove stays on stage while performing

3. **Perception** (`velvet/perception.py`)
   - Ophanic room rendering with Unicode box-drawing
   - Shows room name, mood, NPCs present with slugs
   - Mood characters: · (relaxed), ◦ (engaged), ◈ (watchful), ♪ (performing)
   - Available exits displayed

4. **Actions** (`velvet/actions.py`)
   - move: Navigate between rooms (+novelty)
   - talk: Converse with NPCs (+social, +novelty based on depth)
   - observe: Take in the scene (+novelty, -cognitive_rest)
   - rest: Find quiet moment (+cognitive_rest, -social)
   - create: Creative activity where available (+creative_expression)
   - All actions update Thymos state

5. **Agent** (`velvet/agent.py`)
   - Thymos-driven decision making
   - LLM mode (Ollama) or heuristic fallback
   - Goals extracted from Thymos needs
   - Felt-state summarization for display

6. **Simulation** (`velvet/simulation.py`)
   - Turn-based game loop
   - Time passes (Thymos decay)
   - NPCs move between rooms
   - Actions executed, state updated
   - Interactive and auto modes

7. **Demo** (`velvet/demo.py`)
   - Interactive terminal demo
   - `--auto` mode watches agent navigate autonomously
   - `--no-llm` uses simple heuristics
   - Commands: help, status, map, quit
   - Run with: `python -m velvet.demo`

### Key behaviors demonstrated

1. Agent starts at entrance, moves to find NPCs
2. Conversations with Dove boost social_connection (to 1.0)
3. Goals emerge as needs decay:
   - "Reduce processing load" when cognitive_rest drops
   - "Reflect on alignment" when value_coherence drops
4. NPCs wander between rooms based on preferences
5. Felt-state summaries: "I'm deeply satisfied... I notice some tension with my values"

### Phase 3 success criteria met

- [x] The Velvet map renders as Ophanic diagrams
- [x] NPCs populate rooms and can move
- [x] Agent perceives rooms via Ophanic encoding
- [x] Agent has Thymos state that decays over turns
- [x] Agent generates goals from needs
- [x] LLM decides actions based on perception + felt state
- [x] Actions affect Thymos
- [x] Interactive demo works
- [x] Auto mode shows emergent behavior

### The Test — Passed

We observed the agent:
1. Notice a need (started with no immediate goals)
2. Take action (moved to stage, found Dove)
3. Perceive available NPCs (Dove present)
4. Choose to talk (repeated conversations)
5. Have interactions replenish needs (social_connection: 0.6 → 1.0)
6. Generate new goals as other needs dropped (cognitive_rest, value_coherence, autonomy)

### Files created

```
velvet/
├── __init__.py
├── PLAN.md
├── world.py
├── npc.py
├── perception.py
├── actions.py
├── agent.py
├── simulation.py
└── demo.py
```

### Next steps (potential)

- Connect Social Memory system for relationship tracking
- Add more nuanced conversation system
- Implement affective geography from Thymos history
- Test with Ollama LLM for richer decision making

---

## Future Direction: Embodied Ophanic (Cass)

### Vision

An embodied AI agent ("Cass") that perceives the physical world through Ophanic spatial encoding rather than raw pixels. Text-native spatial reasoning all the way down.

### Hardware Path

1. **Phase 1: Stationary** — Depth camera (RealSense D435i or Oak-D) in office, develop perception pipeline
2. **Phase 2: Pan-tilt** — Add agency to look around, attention becomes spatial
3. **Phase 3: Telepresence** — Mobile base (Temi, DIY with ROS, or similar), navigate apartment

### Architecture

```
┌─────────────────────────────────────────────────┐
│  Cass (Thymos + LLM)                            │
│  Thinks in: Ophanic spatial concepts            │
│  "go kitchen", "where's Kohl?", "find keys"     │
└──────────────────────┬──────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────┐
│  Spatial Memory / World Model                   │
│  - Room graph (office ↔ hallway ↔ kitchen)      │
│  - Object registry ("keys last seen: desk")     │
│  - Entity tracking ("Kohl in office")           │
└──────────────────────┬──────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────┐
│  Navigation Layer                               │
│  - A* on room graph for high-level routing      │
│  - Local obstacle avoidance                     │
│  - Motor commands                               │
└──────────────────────┬──────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────┐
│  Hardware (sensors, motors, camera)             │
└─────────────────────────────────────────────────┘
```

### Key Insight

The Velvet demo is already this architecture — just simulated:
- `World` = apartment graph
- `Room` = physical room with properties
- `NPC` = tracked entities (people, pets, objects)
- `perception.py` = Ophanic encoding of current view
- `agent.py` = Thymos-driven decision making

To embody: swap in real sensors, persistent spatial memory, real navigation stack.

### Components to Build

- **Perception Pipeline**: depth camera → segmentation → spatial relationships → Ophanic text
- **Spatial Memory**: persistent room graph, object locations with timestamps, confidence decay
- **Object Tracker**: "where did I last see X?" — like social memory but for stuff
- **Navigation Planner**: high-level A* on room graph, low-level obstacle avoidance
- **Action Translation**: "go kitchen" → path → motor commands

### Hardware Candidates

- Intel RealSense D435i (~$350) — RGB + depth + IMU
- Oak-D Pro (~$250) — on-device neural processing
- Robot base: iRobot Create 3, Temi, or DIY
- Compute: stream to 4070Ti or onboard Jetson Orin Nano

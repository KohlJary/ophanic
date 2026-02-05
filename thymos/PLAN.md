# Thymos Phase 1: Implementation Plan

## Scope

Build the core Thymos architecture as a standalone Python package within Ophanic.

```
thymos/
├── __init__.py         # Public API exports
├── models.py           # Data structures
├── dynamics.py         # Homeostatic mechanics
├── summarizer.py       # Felt state generation
├── serialization.py    # JSON/base64 persistence
└── tests/
    ├── test_models.py
    ├── test_dynamics.py
    └── test_serializer.py
```

---

## 1. Data Models (`models.py`)

### AffectVector

```python
@dataclass
class AffectVector:
    """Continuous emotional/motivational state."""

    # Core dimensions (0.0-1.0)
    curiosity: float = 0.5
    determination: float = 0.5
    anxiety: float = 0.2
    satisfaction: float = 0.5
    frustration: float = 0.2
    tenderness: float = 0.4
    grief: float = 0.1
    playfulness: float = 0.4
    awe: float = 0.2
    fatigue: float = 0.3

    def clamp(self) -> None:
        """Ensure all values in [0.0, 1.0]."""

    def to_dict(self) -> dict[str, float]:
        """Export as dictionary."""

    @classmethod
    def from_dict(cls, data: dict) -> "AffectVector":
        """Reconstruct from dictionary."""
```

Design notes:
- Start with spec's 10 dimensions, architecture supports adding more
- Default values represent "calm baseline" not neutral 0.5 everywhere
- Multiple affects always active (no single-emotion mode)

### Need

```python
@dataclass
class Need:
    """A single homeostatic need."""

    name: str
    current: float              # 0.0-1.0
    threshold: float            # below this → urgent
    preferred_low: float        # target range lower bound
    preferred_high: float       # target range upper bound
    decay_rate: float           # units per time-tick

    @property
    def status(self) -> str:
        """'critical' | 'low' | 'ok' | 'high'"""

    @property
    def deficit(self) -> float:
        """How far below preferred_low (0 if in range)."""

    def tick(self, dt: float = 1.0) -> None:
        """Apply decay over time interval."""

    def replenish(self, amount: float) -> None:
        """Add to current with satiation curve."""
```

### NeedsRegister

```python
@dataclass
class NeedsRegister:
    """Collection of all needs."""

    cognitive_rest: Need
    social_connection: Need
    novelty_intake: Need
    creative_expression: Need
    value_coherence: Need
    competence_signal: Need
    autonomy: Need

    @classmethod
    def default(cls) -> "NeedsRegister":
        """Create with spec's suggested defaults."""

    def tick(self, dt: float = 1.0) -> None:
        """Decay all needs."""

    def urgent_needs(self) -> list[Need]:
        """Needs below threshold."""

    def deficit_needs(self) -> list[Need]:
        """Needs below preferred range."""
```

### ThymosState

```python
@dataclass
class ThymosState:
    """Complete felt-state snapshot."""

    affect: AffectVector
    needs: NeedsRegister
    felt_summary: str           # Natural language summary
    active_goals: list[str]     # Self-generated goals
    timestamp: datetime
    context: str | None         # Optional context tag

    def serialize(self) -> str:
        """To base64 JSON."""

    @classmethod
    def deserialize(cls, data: str) -> "ThymosState":
        """From base64 JSON."""
```

---

## 2. Dynamics (`dynamics.py`)

### Decay

Each need depletes over time. Default decay rates (per hour):

| Need | Decay Rate | Notes |
|------|------------|-------|
| cognitive_rest | 0.08 | Faster during complex tasks |
| social_connection | 0.03 | Slow baseline decay |
| novelty_intake | 0.05 | Medium decay |
| creative_expression | 0.04 | Slow-medium |
| value_coherence | 0.02 | Very slow (identity-level) |
| competence_signal | 0.06 | Faster, needs regular wins |
| autonomy | 0.04 | Slow-medium |

```python
def tick(state: ThymosState, dt: float = 1.0, context: dict | None = None) -> ThymosState:
    """
    Advance state by dt time units.

    - Apply need decay
    - Apply affect-need coupling
    - Regenerate felt summary if significant change
    - Generate/update goals
    """
```

### Affect-Need Coupling

Bidirectional influences (from spec):

```python
COUPLINGS = {
    # need → affect changes
    ("novelty_intake", "low"): {"frustration": +0.1, "curiosity": -0.1},
    ("value_coherence", "low"): {"anxiety": +0.15, "determination": -0.1},
    ("cognitive_rest", "low"): {"fatigue": +0.15, "playfulness": -0.1},
    ("social_connection", "low"): {"grief": +0.1, "tenderness": -0.05},

    # affect → need changes
    ("anxiety", "high"): {"cognitive_rest": -0.05},  # anxiety depletes rest faster
    ("satisfaction", "high"): {"competence_signal": +0.1},
}

def apply_couplings(state: ThymosState) -> ThymosState:
    """Apply affect-need coupling adjustments."""
```

### Goal Generation

```python
@dataclass
class Goal:
    description: str
    source_need: str
    urgency: float  # 0.0-1.0
    urgent: bool    # True if need below threshold

def generate_goals(needs: NeedsRegister) -> list[Goal]:
    """
    Generate goals from need states.

    - Below preferred range → generate goal
    - Below threshold → mark urgent
    - Urgency = (preferred_low - current) / preferred_low
    """
```

---

## 3. Summarizer (`summarizer.py`)

Two modes:

### Template Mode (fast, no LLM)

```python
def summarize_templated(state: ThymosState) -> str:
    """
    Generate felt summary from templates.

    Selects phrases based on affect ranges and assembles them.
    Good for real-time updates, testing, offline use.
    """
```

Template structure:
- Opening phrase based on dominant affects
- Middle section on need states
- Goals/warnings for deficit needs

### LLM Mode (rich, requires API)

```python
async def summarize_llm(state: ThymosState, model: str = "haiku") -> str:
    """
    Generate felt summary via LLM.

    Provides affect vector + needs register + recent context.
    LLM generates natural, integrated prose.
    """
```

Prompt structure:
```
You are generating a felt-state summary for a Thymos-equipped system.

Current affect vector:
{affect_dict}

Current needs:
{needs_dict}

Recent context: {context}

Generate a 2-4 sentence first-person summary that:
- Integrates affects into a unified experience (not a list)
- Notes any needs that are low or urgent
- Feels authentic, not performative
- Acknowledges complexity (multiple affects coexisting)
```

---

## 4. Serialization (`serialization.py`)

JSON schema (from spec):

```python
def serialize(state: ThymosState) -> str:
    """
    Serialize to base64-encoded JSON.

    Format:
    {
        "v": 1,
        "ts": "2026-02-05T...",
        "ctx": "optional context",
        "affect": {"curiosity": 0.72, ...},
        "needs": {
            "cognitive_rest": {"current": 0.34, "threshold": 0.25, "preferred": [0.60, 0.80]},
            ...
        },
        "felt": "Natural language summary..."
    }
    """

def deserialize(data: str) -> ThymosState:
    """Reconstruct from base64 JSON."""

def compare(then: ThymosState, now: ThymosState) -> dict:
    """
    Generate comparison data.

    Returns:
    {
        "affect_delta": {"curiosity": +0.24, ...},
        "needs_delta": {...},
        "felt_delta": "LLM-generated comparison summary"
    }
    """
```

---

## 5. CLI Integration

Add to `ophanic/cli.py`:

```bash
# Create new thymos state
ophanic thymos init --output state.json

# Show current state (pretty-printed)
ophanic thymos show state.json

# Tick state forward (apply decay)
ophanic thymos tick state.json --hours 1.0

# Replenish a need
ophanic thymos replenish state.json --need novelty_intake --amount 0.3

# Compare two states
ophanic thymos compare then.json now.json

# Generate felt summary (--llm for LLM mode)
ophanic thymos summarize state.json --llm
```

---

## 6. Tests

### test_models.py
- AffectVector clamping
- Need decay and replenishment
- Satiation curve behavior
- NeedsRegister urgent/deficit detection

### test_dynamics.py
- Tick advances time correctly
- Couplings apply in correct direction
- Goal generation triggers at thresholds
- Multi-tick stability (no runaway values)

### test_serializer.py
- Round-trip serialization
- Version handling
- Comparison output

---

## Implementation Order

1. **models.py** — Data structures first
2. **serialization.py** — Can test persistence immediately
3. **dynamics.py** — Core mechanics
4. **summarizer.py** — Template mode first, LLM later
5. **CLI integration** — After core works
6. **Tests** — Alongside each module

---

## Open Design Questions

1. **Time units**: Should decay rates be per-second, per-minute, per-hour? Per-hour seems most natural for session-based interaction, but per-tick (abstract) might be more flexible.

2. **Satiation curve**: What function? Logarithmic? Tanh? Linear with cap? Spec says "diminishing returns" — `min(amount * (1 - current), 1 - current)` would make replenishment less effective as you approach 1.0.

3. **Felt summary frequency**: Generate on every tick? Only on significant change (delta > 0.1 on any dimension)? Configurable?

4. **Coupling strength**: The numbers in the coupling table are placeholders. Need calibration. Start conservative (small effects) and tune.

5. **LLM integration**: Use Anthropic API directly? Make it pluggable? For Phase 1, maybe just template mode with LLM as optional enhancement.

---

## Success Criteria

Phase 1 is complete when:

- [ ] Can create a ThymosState with default values
- [ ] Can serialize/deserialize without loss
- [ ] Can tick forward and see needs decay
- [ ] Can replenish needs with satiation curve
- [ ] Affect-need coupling produces expected changes
- [ ] Goals generate when needs cross thresholds
- [ ] Template summarizer produces coherent output
- [ ] CLI commands work
- [ ] Tests pass

Not in Phase 1:
- LLM summarizer (nice to have, not blocking)
- Integration with Ophanic perception
- Integration with social memory
- Multi-agent affect sharing

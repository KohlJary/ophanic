# Social Memory Phase 2: Implementation Plan

## Scope

Implement spatial text encoding as a memory substrate for social environments,
integrated with Thymos affect tracking.

```
social_memory/
├── __init__.py           # Public API
├── models.py             # Entity, Relationship, Snapshot, SocialMemory
├── rendering.py          # Ophanic diagram generation
├── tools.py              # Drill-down tools (/expand, /history, /nearby, etc.)
├── temporal.py           # Snapshot management, compression, pattern detection
├── thymos_integration.py # Affect annotation, affective geography
└── tests/
    └── test_social_memory.py
```

---

## 1. Data Models (`models.py`)

### Entity

```python
@dataclass
class Entity:
    """A person, organization, or other social entity."""

    slug: str                    # 4-char hex (a3f2) or prefixed (█O01)
    name: str                    # Display name
    entity_type: str             # "individual" | "organization"

    # Metadata
    first_met: datetime | None
    pronouns: str | None
    role: str | None             # "friend", "acquaintance", "colleague", etc.
    notes: list[str]

    # For organizations
    members: list[str] | None    # Entity slugs
    aggregate_affect: dict | None

    def to_legend_line(self) -> str:
        """Single-line legend entry."""
```

### Relationship

```python
@dataclass
class Relationship:
    """A directed relationship between entities."""

    slug: str                    # █R04
    source: str                  # Entity slug
    target: str                  # Entity slug

    rel_type: str                # "friendly", "tense", "romantic", etc.
    status: str                  # "stable", "warming", "cooling", "⚠ needs attention"
    direction: str               # "mutual", "source→target", "target→source"

    summary: str                 # Brief description
    timeline: list[RelationshipEvent]

    def to_legend_line(self) -> str:
        """Single-line legend entry."""
```

### RelationshipEvent

```python
@dataclass
class RelationshipEvent:
    """A timestamped event in a relationship's history."""

    timestamp: datetime
    location: str | None
    context: str
    quality: str                 # "positive", "negative", "neutral", "shift"
    affect_delta: dict | None    # How this event affected Thymos
    notes: str | None
    thymos_ref: str | None       # █T0047 reference to full serialized state
```

### SpatialSnapshot

```python
@dataclass
class EntityPosition:
    """An entity's position in a spatial snapshot."""
    slug: str
    x: int                       # Grid position
    y: int

@dataclass
class RelationshipEdge:
    """A visible relationship edge in the snapshot."""
    rel_slug: str
    source_slug: str
    target_slug: str

@dataclass
class SpatialSnapshot:
    """A point-in-time spatial encoding of social topology."""

    timestamp: datetime
    location: str                # "The Velvet, second floor lounge"
    location_slug: str | None    # █L01
    mood: str | None             # "relaxed-social", "tense", etc.

    entities: list[EntityPosition]
    edges: list[RelationshipEdge]
    self_position: tuple[int, int] | None

    # Thymos annotation
    affect_summary: dict | None  # {"curiosity": 0.6, "anxiety": 0.25}
    needs_summary: dict | None   # {"social_connection": "OK", "cognitive_rest": "⚠ LOW"}
    thymos_ref: str | None       # Full serialized state reference

    def render(self, width: int = 50) -> str:
        """Render as Ophanic box-drawing diagram."""
```

### SocialMemory

```python
@dataclass
class SocialMemory:
    """Complete social memory store."""

    entities: dict[str, Entity]
    relationships: dict[str, Relationship]
    snapshots: list[SpatialSnapshot]  # Ordered by timestamp

    # Index structures
    _entity_by_name: dict[str, str]
    _relationships_by_entity: dict[str, list[str]]

    def add_entity(self, entity: Entity) -> None
    def add_relationship(self, rel: Relationship) -> None
    def add_snapshot(self, snapshot: SpatialSnapshot) -> None

    def get_entity(self, slug_or_name: str) -> Entity | None
    def get_relationship(self, slug: str) -> Relationship | None
    def get_relationships_for(self, entity_slug: str) -> list[Relationship]

    def current_snapshot(self) -> SpatialSnapshot | None
    def snapshots_at_location(self, location: str) -> list[SpatialSnapshot]

    def render_current(self) -> str:
        """Render current snapshot with legend."""

    def to_context(self) -> str:
        """Generate minimal context load (~300 tokens)."""
```

---

## 2. Rendering (`rendering.py`)

### Spatial Diagram Generation

```python
def render_snapshot(
    snapshot: SpatialSnapshot,
    entities: dict[str, Entity],
    relationships: dict[str, Relationship],
    width: int = 50,
    height: int = 15,
) -> str:
    """
    Render a spatial snapshot as Ophanic box-drawing.

    Output:
    ┌──────────────────────────────────────────────────┐
    │                                                  │
    │  ┌──────┐                         ┌──────┐      │
    │  │ a3f2 │───█R04───┐    ┌────────│ 9e1c │      │
    │  └──────┘          │    │        └──────┘      │
    │                 ┌──▼────▼──┐                    │
    │  ┌──────┐       │   ☆ self │     ┌──────┐      │
    │  │ 7b08 │─█R11─▶│          │◀█R07│ d4a5 │      │
    │  └──────┘       └──────────┘     └──────┘      │
    │                                                  │
    └──────────────────────────────────────────────────┘
    """
```

### Legend Generation

```python
def render_legend(
    entities: list[Entity],
    relationships: list[Relationship],
) -> str:
    """
    Render entity and relationship legends.

    Output:
    ## Entities
    a3f2: Mika | met 2026-01-20 | friend | artist | they/them
    9e1c: Jude | met 2026-03-01 | new | quiet, observant
    ...

    ## Relationships (surface)
    █R04: a3f2↔self | friendly | stable | bonded over art
    █R11: 7b08→self | tense | was friendly, shifted ~03-02 | ⚠ needs attention
    """
```

### Full Context Rendering

```python
def render_context(memory: SocialMemory) -> str:
    """
    Render complete minimal context (~300 tokens).

    Includes:
    - Location header with timestamp and mood
    - Spatial snapshot diagram
    - Entity legend
    - Relationship legend (surface only)
    - Thymos annotation if present
    """
```

---

## 3. Drill-Down Tools (`tools.py`)

```python
def expand(
    memory: SocialMemory,
    slug: str,
    history: bool = False,
    affect: bool = False,
    timeline: bool = False,
) -> str:
    """
    Expand a slug into full detail.

    /expand a3f2              → Full entity profile
    /expand a3f2 --history    → Interaction timeline with self
    /expand a3f2 --affect     → How this entity has affected Thymos
    /expand █R11              → Full relationship record
    /expand █R11 --timeline   → Relationship trajectory
    """

def nearby(
    memory: SocialMemory,
    slug: str,
) -> str:
    """
    Show entities spatially close to the given slug in current snapshot.
    Includes their mutual relationships.
    """

def history(
    memory: SocialMemory,
    location: str | None = None,
    slug: str | None = None,
    last: int = 5,
) -> str:
    """
    Show temporal stack.

    /history █L01             → Last N snapshots at this location
    /history a3f2 --locations → Where has this entity been seen
    """

def cluster(memory: SocialMemory) -> str:
    """
    Detect and describe current social groupings.

    Based on spatial proximity and relationship edges in current snapshot.
    """

def delta(
    memory: SocialMemory,
    since: datetime | str,
) -> str:
    """
    What changed since the given timestamp.

    New entities, relationship changes, position shifts.
    """
```

---

## 4. Temporal Management (`temporal.py`)

### Snapshot Storage

```python
def add_snapshot(
    memory: SocialMemory,
    snapshot: SpatialSnapshot,
    compress_old: bool = True,
) -> None:
    """
    Add a snapshot to memory.

    If compress_old=True, apply compression to older snapshots
    based on age thresholds.
    """
```

### Compression

```python
def compress_snapshot(
    snapshot: SpatialSnapshot,
    level: str = "moderate",
) -> SpatialSnapshot:
    """
    Compress a snapshot for long-term storage.

    Levels:
    - "light": Keep all entities, remove affect details
    - "moderate": Keep entity slugs only, remove positions
    - "heavy": Keep entity list only as single line
    """

COMPRESSION_THRESHOLDS = {
    "light": timedelta(days=7),
    "moderate": timedelta(days=30),
    "heavy": timedelta(days=180),
}
```

### Pattern Detection

```python
def detect_regulars(
    memory: SocialMemory,
    location: str,
    min_appearances: int = 3,
) -> list[str]:
    """Entities that appear frequently at a location."""

def detect_orbit_shifts(
    memory: SocialMemory,
    entity_slug: str,
    window: int = 10,
) -> list[dict]:
    """How an entity's social clustering has changed."""

def detect_relationship_trajectory(
    memory: SocialMemory,
    rel_slug: str,
) -> str:
    """Summary of how a relationship has evolved."""
```

---

## 5. Thymos Integration (`thymos_integration.py`)

### Affect Annotation

```python
def annotate_snapshot(
    snapshot: SpatialSnapshot,
    thymos_state: ThymosState,
    full_serialize: bool = False,
) -> SpatialSnapshot:
    """
    Attach Thymos state to a snapshot.

    If full_serialize=True, store complete serialized state.
    Otherwise, store summary (top affects + need statuses).
    """
```

### Affective Geography

```python
@dataclass
class AffectiveAssociation:
    """Learned affect association with a location/entity/configuration."""

    target: str              # Location slug, entity slug, or config hash
    target_type: str         # "location", "entity", "configuration"
    affect_pattern: dict     # Average affect change when this target is present
    confidence: float        # Based on number of observations
    sample_count: int

def compute_affective_geography(
    memory: SocialMemory,
) -> list[AffectiveAssociation]:
    """
    Compute emergent affect associations from historical data.

    Returns associations like:
    - "The Velvet second floor consistently +0.15 social_connection"
    - "Presence of 7b08 and 9e1c together: +0.2 anxiety"
    - "1:1 with f1e3: +0.1 creative_expression"
    """

def predict_affect_impact(
    memory: SocialMemory,
    proposed_snapshot: SpatialSnapshot,
) -> dict:
    """
    Predict how a proposed social configuration would affect Thymos.

    Based on learned associations.
    """
```

---

## 6. GUID Slug Generation

```python
import secrets

def generate_entity_slug() -> str:
    """Generate 4-char hex slug for an entity."""
    return secrets.token_hex(2)  # e.g., "a3f2"

def generate_relationship_slug(counter: int) -> str:
    """Generate relationship slug."""
    return f"█R{counter:02d}"

def generate_location_slug(counter: int) -> str:
    """Generate location slug."""
    return f"█L{counter:02d}"

def generate_thymos_slug(counter: int) -> str:
    """Generate Thymos state reference slug."""
    return f"█T{counter:04d}"
```

---

## 7. Demo Script

Interactive demo similar to Thymos:
1. Create a social environment (The Velvet)
2. Add entities (Mika, Ren, Jude, etc.)
3. Create relationships
4. Generate spatial snapshots
5. Demonstrate drill-down tools
6. Show temporal stacking
7. Demonstrate affect annotation and geography

---

## Implementation Order

1. **models.py** - Data structures
2. **rendering.py** - Diagram generation
3. **tools.py** - Drill-down commands
4. **temporal.py** - Snapshot management
5. **thymos_integration.py** - Affect features
6. **Tests** - Alongside each module
7. **demo.py** - Interactive demonstration

---

## Success Criteria

Phase 2 is complete when:

- [ ] Can create entities with slugs and metadata
- [ ] Can create relationships between entities
- [ ] Can generate spatial snapshot diagrams
- [ ] Can render legend from entity/relationship data
- [ ] Can render ~300 token minimal context
- [ ] Drill-down tools work (/expand, /nearby, /history, /cluster, /delta)
- [ ] Temporal stacking preserves snapshot history
- [ ] Compression reduces old snapshot size
- [ ] Thymos states can be attached to snapshots
- [ ] Affective geography computes from historical data
- [ ] Demo script showcases all features
- [ ] Tests pass

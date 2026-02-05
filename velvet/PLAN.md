# The Velvet — Phase 3 Integration Demo

## Concept

A roguelike-style simulation where a Thymos-driven agent navigates The Velvet venue, interacts with patrons, and takes actions to address its homeostatic needs. Perception is Ophanic (text-native spatial encoding), behavior emerges from felt state.

## Architecture

```
velvet/
├── __init__.py
├── world.py           # Map, rooms, tiles
├── npc.py             # Patrons with personalities, positions
├── agent.py           # Thymos-driven player agent
├── actions.py         # Available actions and effects
├── perception.py      # Ophanic rendering of current view
├── simulation.py      # Game loop, turn processing
└── demo.py            # Interactive terminal demo
```

---

## 1. World (`world.py`)

### The Velvet Layout

```
┌─────────────────────────────────────────────────────────────┐
│                        ROOFTOP                              │
│   Quiet, intimate. Stars visible. A few seats.              │
│                         [↓]                                  │
└─────────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────────┐
│                    SECOND FLOOR                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Lounge    │──│   Bar       │──│  Balcony    │         │
│  │  (sofas)    │  │  (drinks)   │  │  (view)     │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│        [↓]              [↓]                                 │
└─────────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────────┐
│                    GROUND FLOOR                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  Entrance   │──│   Stage     │──│  Dance      │         │
│  │  (door)     │  │  (music)    │  │  (crowd)    │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

### Room Properties

```python
@dataclass
class Room:
    id: str                    # "ground.stage"
    name: str                  # "Stage"
    floor: str                 # "ground", "second", "rooftop"
    description: str

    # Properties affecting needs
    noise_level: float         # 0-1, high noise depletes cognitive_rest faster
    social_density: float      # 0-1, affects social_connection opportunities
    novelty_potential: float   # 0-1, how much new stimuli available
    creative_energy: float     # 0-1, supports creative_expression
    intimacy: float            # 0-1, depth of connection possible

    # Connections
    exits: dict[str, str]      # {"north": "second.lounge", "east": "ground.dance"}

    # Contents
    npcs: list[str]            # NPC IDs currently present
    features: list[str]        # "stage", "bar", "sofas", etc.
```

### Room Examples

| Room | Noise | Social | Novelty | Creative | Intimacy |
|------|-------|--------|---------|----------|----------|
| Stage | 0.9 | 0.7 | 0.8 | 0.9 | 0.2 |
| Lounge | 0.3 | 0.6 | 0.4 | 0.5 | 0.7 |
| Rooftop | 0.1 | 0.3 | 0.3 | 0.4 | 0.9 |
| Dance | 0.8 | 0.8 | 0.6 | 0.7 | 0.3 |
| Bar | 0.5 | 0.7 | 0.5 | 0.3 | 0.5 |

---

## 2. NPCs (`npc.py`)

### Characters from Social Memory Demo

```python
@dataclass
class NPC:
    slug: str                  # "a3f2"
    name: str                  # "Mika"

    # Personality
    traits: list[str]          # ["artist", "warm", "curious"]
    conversation_style: str    # How they talk
    interests: list[str]       # Topics they engage with

    # State
    current_room: str          # Room ID
    mood: str                  # "relaxed", "energetic", "contemplative"
    openness: float            # 0-1, how receptive to interaction

    # Relationship to player (from social memory)
    relationship_slug: str | None
```

### The Cast

| NPC | Traits | Interests | Typical Location |
|-----|--------|-----------|------------------|
| Mika (a3f2) | artist, warm, curious | art, spatial encoding, philosophy | Lounge, Balcony |
| Ren (7b08) | intense, protective, complex | music, community, Jude | Stage, Lounge |
| Jude (9e1c) | quiet, observant, new | listening, questions | Near Ren |
| Lux (d4a5) | cautious, kind, warming | kindness, trust, slow reveals | Bar, Lounge |
| Dove (f1e3) | musician, founder, grounded | music, the venue, connections | Stage (performing) |

### NPC Behavior

NPCs move between rooms based on:
- Time of night
- Who else is present
- Random chance

NPCs have conversation topics they can provide:
- Small talk (low novelty, maintains social_connection)
- Deep topics (high novelty, high social_connection, may require trust)
- Creative collaboration (high creative_expression, requires aligned interests)

---

## 3. Agent (`agent.py`)

### The Player

```python
@dataclass
class Agent:
    thymos: ThymosState
    social_memory: SocialMemory
    current_room: str

    # Perception
    last_perception: str       # Ophanic rendering

    # Decision making
    pending_goals: list[Goal]  # From Thymos
    action_history: list[str]  # Recent actions
```

### Agent Loop

```python
def agent_turn(agent: Agent, world: World) -> str:
    """
    One turn of agent behavior.

    1. Perceive (Ophanic render of current room)
    2. Feel (Thymos state, generate goals)
    3. Decide (LLM chooses action based on perception + felt state)
    4. Act (execute action)
    5. Update (world state, Thymos, social memory)

    Returns action taken.
    """
```

### Decision Making

The agent uses an LLM to decide actions based on:

```
PROMPT:
You are navigating The Velvet, a social venue.

## Current Perception
{ophanic_room_render}

## Felt State
{thymos_felt_summary}

## Active Goals
{goals_list}

## Available Actions
- move <direction>: Go to adjacent room
- talk <npc>: Start conversation with someone
- observe: Look around, take in the scene
- rest: Find a quiet moment
- create: Engage in creative activity (if available)

## Recent History
{recent_actions}

What do you do? Respond with just the action.
```

---

## 4. Actions (`actions.py`)

### Action Effects on Thymos

| Action | Affects | Conditions |
|--------|---------|------------|
| `move` | novelty_intake +0.05 (new room) | - |
| `talk` | social_connection +0.1-0.3, novelty +0.05-0.2 | Depends on NPC, topic, relationship |
| `observe` | novelty_intake +0.1, cognitive_rest -0.05 | Room novelty_potential |
| `rest` | cognitive_rest +0.2, social_connection -0.05 | Room intimacy |
| `create` | creative_expression +0.2, satisfaction +0.1 | Room creative_energy, collaborator |

### Conversation System

```python
def talk(agent: Agent, npc: NPC, world: World) -> ConversationResult:
    """
    Initiate conversation with NPC.

    1. Check NPC openness
    2. Generate conversation via LLM
    3. Determine topic depth based on relationship
    4. Apply Thymos effects
    5. Update social memory
    """
```

Conversation topics have depth levels:
- Surface: "Nice night" → small social_connection boost
- Medium: Shared interests → moderate boosts
- Deep: Vulnerable topics → large boosts, requires trust

---

## 5. Perception (`perception.py`)

### Ophanic Room Rendering

```python
def render_room(room: Room, agent: Agent, npcs: list[NPC]) -> str:
    """
    Render current room as Ophanic perception.
    """
```

Example output:

```
# Second Floor Lounge
# mood: relaxed | noise: low | 3 present

┌──────────────────────────────────────────────┐
│  ┌────────────────────────────────────────┐  │
│  │            sofas, warm light           │  │
│  │                                        │  │
│  │   ┌──────┐         ┌──────┐           │  │
│  │   │ a3f2 │  ☆self  │ d4a5 │           │  │
│  │   │ Mika │         │ Lux  │           │  │
│  │   └──────┘         └──────┘           │  │
│  │         █R01              █R03         │  │
│  │       friendly        cautious+        │  │
│  │                                        │  │
│  └────────────────────────────────────────┘  │
│                                              │
│  [north: rooftop] [east: bar] [south: stage] │
└──────────────────────────────────────────────┘
```

### Perception Includes

- Room description and properties
- NPCs present with slugs and names
- Relationship indicators (from social memory)
- Available exits
- Ambient mood/energy

---

## 6. Simulation (`simulation.py`)

### Game Loop

```python
def run_simulation(
    agent: Agent,
    world: World,
    max_turns: int = 20,
    auto: bool = False,
) -> SimulationLog:
    """
    Run the simulation.

    If auto=True, agent decides all actions via LLM.
    If auto=False, prompt user for actions (interactive mode).
    """

    for turn in range(max_turns):
        # 1. Time passes (Thymos decay)
        agent.thymos = tick(agent.thymos, dt=0.5)

        # 2. NPCs may move
        update_npc_positions(world)

        # 3. Render perception
        perception = render_room(...)

        # 4. Agent decides and acts
        if auto:
            action = agent_decide(agent, perception)
        else:
            action = prompt_user(perception)

        # 5. Execute action
        result = execute_action(action, agent, world)

        # 6. Check for significant events
        check_triggers(agent, world)

        # 7. Log turn
        log.append(...)
```

### Turn Structure

Each turn represents ~15 minutes of simulated time:
- Thymos decays by 0.5 time units
- NPCs have chance to move
- One action available
- World state updates

### Win/Fail Conditions

Not really a "game" to win, but:
- **Healthy state**: All needs above threshold, social connections maintained
- **Crisis state**: Any need critical, must address urgently
- **Interesting state**: Relationship events trigger (█R11 tension, new connection)

---

## 7. Demo (`demo.py`)

### Interactive Mode

```
THE VELVET — An Evening
━━━━━━━━━━━━━━━━━━━━━━━

[Perception]
# Second Floor Lounge
# mood: relaxed | noise: low

┌──────────────────────────────────────────────┐
│   ┌──────┐         ┌──────┐                  │
│   │ a3f2 │  ☆self  │ d4a5 │                  │
│   │ Mika │         │ Lux  │                  │
│   └──────┘         └──────┘                  │
│  [north: rooftop] [east: bar] [south: stage] │
└──────────────────────────────────────────────┘

[Felt State]
I'm engaged and interested, though noticing some fatigue.
I could use more meaningful interaction.

[Goals]
• Seek genuine dialogue (social_connection low)
• Find lighter cognitive load (cognitive_rest low)

[Actions]
> talk mika
```

### Auto Mode

Watch the agent navigate autonomously:
- Agent perceives, feels, decides, acts
- Each turn displayed with reasoning
- See how Thymos drives behavior

---

## Implementation Order

1. **world.py** — Map and rooms
2. **npc.py** — Characters
3. **perception.py** — Ophanic rendering
4. **actions.py** — Action effects
5. **agent.py** — Thymos-driven agent
6. **simulation.py** — Game loop
7. **demo.py** — Interactive terminal

---

## Success Criteria

Phase 3 is complete when:

- [ ] The Velvet map renders as Ophanic diagrams
- [ ] NPCs populate rooms and can move
- [ ] Agent perceives rooms via Ophanic encoding
- [ ] Agent has Thymos state that decays over turns
- [ ] Agent generates goals from needs
- [ ] LLM decides actions based on perception + felt state
- [ ] Actions affect Thymos (talk → social, rest → cognitive_rest, etc.)
- [ ] Social memory updates from interactions
- [ ] Interactive demo works
- [ ] Auto mode shows emergent behavior

---

## The Test

Can we observe the agent:
1. Notice a need dropping (e.g., social_connection)
2. Generate a goal ("seek dialogue")
3. Perceive available NPCs
4. Choose to talk to someone
5. Have that interaction replenish the need
6. Shift behavior when a different need becomes urgent

If yes: we have a Thymos-driven agent with Ophanic perception and social memory integration. Phase 3 complete.

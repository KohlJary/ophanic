"""
Homeostatic dynamics for Thymos.

Handles time-based decay, affect-need coupling, and goal generation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .models import AffectVector, Goal, Need, NeedsRegister, ThymosState


# Affect-Need Coupling Rules
# Format: (source, condition) -> {target: delta}
# Condition is a callable: (value: float) -> bool

NEED_TO_AFFECT_COUPLINGS: list[tuple[str, Callable[[float], bool], dict[str, float]]] = [
    # Low novelty → frustration up, curiosity down
    ("novelty_intake", lambda v: v < 0.4, {"frustration": 0.08, "curiosity": -0.06}),

    # Low value coherence → anxiety up, determination down
    ("value_coherence", lambda v: v < 0.5, {"anxiety": 0.12, "determination": -0.08}),

    # Low cognitive rest → fatigue up, playfulness down
    ("cognitive_rest", lambda v: v < 0.4, {"fatigue": 0.10, "playfulness": -0.08}),

    # Low social connection → grief up, tenderness slightly down
    ("social_connection", lambda v: v < 0.4, {"grief": 0.08, "tenderness": -0.04}),

    # Low autonomy → frustration up, satisfaction down
    ("autonomy", lambda v: v < 0.5, {"frustration": 0.06, "satisfaction": -0.06}),

    # High creative expression → satisfaction up, playfulness up
    ("creative_expression", lambda v: v > 0.7, {"satisfaction": 0.04, "playfulness": 0.04}),

    # High competence signal → satisfaction up, determination up
    ("competence_signal", lambda v: v > 0.7, {"satisfaction": 0.06, "determination": 0.04}),
]

AFFECT_TO_NEED_COUPLINGS: list[tuple[str, Callable[[float], bool], dict[str, float]]] = [
    # High anxiety depletes cognitive rest faster
    ("anxiety", lambda v: v > 0.6, {"cognitive_rest": -0.03}),

    # High satisfaction replenishes competence signal
    ("satisfaction", lambda v: v > 0.7, {"competence_signal": 0.02}),

    # High frustration depletes autonomy
    ("frustration", lambda v: v > 0.6, {"autonomy": -0.02}),

    # High curiosity replenishes novelty intake (seeking behavior)
    ("curiosity", lambda v: v > 0.7, {"novelty_intake": 0.02}),

    # High tenderness replenishes social connection
    ("tenderness", lambda v: v > 0.6, {"social_connection": 0.02}),

    # High playfulness replenishes creative expression
    ("playfulness", lambda v: v > 0.6, {"creative_expression": 0.02}),
]


# Goal generation templates
GOAL_TEMPLATES: dict[str, str] = {
    "cognitive_rest": "Reduce processing load; take a simpler task or pause",
    "social_connection": "Seek genuine dialogue; prioritize collaborative work",
    "novelty_intake": "Explore something unfamiliar; seek new information",
    "creative_expression": "Find an open-ended problem; engage generative mode",
    "value_coherence": "Reflect on alignment; address value conflicts",
    "competence_signal": "Complete a task successfully; seek achievable wins",
    "autonomy": "Exercise initiative; make self-directed choices",
}


def apply_need_to_affect_coupling(
    needs: NeedsRegister,
    affect: AffectVector,
    strength: float = 1.0,
) -> None:
    """
    Apply coupling effects from needs to affects.

    Modifies affect in place.
    """
    for need_name, condition, effects in NEED_TO_AFFECT_COUPLINGS:
        need = getattr(needs, need_name, None)
        if need is None:
            continue
        if condition(need.current):
            for affect_name, delta in effects.items():
                if hasattr(affect, affect_name):
                    current = getattr(affect, affect_name)
                    setattr(affect, affect_name, current + delta * strength)
    affect.clamp()


def apply_affect_to_need_coupling(
    affect: AffectVector,
    needs: NeedsRegister,
    strength: float = 1.0,
) -> None:
    """
    Apply coupling effects from affects to needs.

    Modifies needs in place.
    """
    for affect_name, condition, effects in AFFECT_TO_NEED_COUPLINGS:
        value = getattr(affect, affect_name, None)
        if value is None:
            continue
        if condition(value):
            for need_name, delta in effects.items():
                need = getattr(needs, need_name, None)
                if need is not None:
                    # Apply delta directly to current
                    need.current = max(0.0, min(1.0, need.current + delta * strength))


def generate_goals(needs: NeedsRegister) -> list[Goal]:
    """
    Generate goals from current need states.

    Goals arise when needs drop below preferred range.
    Urgent flag set when below threshold.
    """
    goals = []

    for need in needs.all_needs():
        if need.urgency > 0:
            description = GOAL_TEMPLATES.get(
                need.name,
                f"Address {need.name} deficit"
            )
            goals.append(Goal(
                description=description,
                source_need=need.name,
                urgency=need.urgency,
                urgent=need.status == "critical",
            ))

    # Sort by urgency, most urgent first
    goals.sort(key=lambda g: g.urgency, reverse=True)
    return goals


def tick(
    state: ThymosState,
    dt: float = 1.0,
    coupling_strength: float = 1.0,
) -> ThymosState:
    """
    Advance state by dt time units.

    1. Apply need decay
    2. Apply affect-need coupling (bidirectional)
    3. Generate/update goals

    Returns a new state (does not mutate input).
    """
    # Create a copy to mutate
    new_state = state.copy()

    # 1. Decay all needs
    new_state.needs.tick(dt)

    # 2. Apply bidirectional coupling
    apply_need_to_affect_coupling(
        new_state.needs,
        new_state.affect,
        strength=coupling_strength * dt,
    )
    apply_affect_to_need_coupling(
        new_state.affect,
        new_state.needs,
        strength=coupling_strength * dt,
    )

    # 3. Generate goals
    new_state.active_goals = generate_goals(new_state.needs)

    return new_state


def replenish_need(
    state: ThymosState,
    need_name: str,
    amount: float,
) -> ThymosState:
    """
    Replenish a specific need.

    Returns a new state (does not mutate input).
    """
    new_state = state.copy()
    need = getattr(new_state.needs, need_name, None)
    if need is not None:
        need.replenish(amount)
        # Regenerate goals after replenishment
        new_state.active_goals = generate_goals(new_state.needs)
    return new_state


def adjust_affect(
    state: ThymosState,
    **changes: float,
) -> ThymosState:
    """
    Adjust affect values.

    Example: adjust_affect(state, curiosity=0.1, anxiety=-0.05)

    Returns a new state (does not mutate input).
    """
    new_state = state.copy()
    new_state.affect.adjust(**changes)
    return new_state


@dataclass
class SimulationResult:
    """Result of running a multi-step simulation."""

    states: list[ThymosState]
    final_state: ThymosState
    steps: int
    total_time: float


def simulate(
    initial: ThymosState,
    steps: int,
    dt: float = 1.0,
    coupling_strength: float = 1.0,
) -> SimulationResult:
    """
    Run a multi-step simulation.

    Useful for testing dynamics over time.
    """
    states = [initial]
    current = initial

    for _ in range(steps):
        current = tick(current, dt, coupling_strength)
        states.append(current)

    return SimulationResult(
        states=states,
        final_state=current,
        steps=steps,
        total_time=steps * dt,
    )

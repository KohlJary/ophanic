"""
Simulation loop for The Velvet.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable

from .world import World, create_velvet
from .npc import NPC, create_npcs, update_npc_positions, get_npcs_in_room
from .perception import render_room, render_ambient
from .actions import (
    parse_action,
    execute_action,
    apply_thymos_deltas,
    get_available_actions,
    ActionResult,
)
from .agent import Agent, create_agent, agent_decide_simple, agent_decide_ollama_sync


@dataclass
class TurnLog:
    """Log of a single turn."""

    turn: int
    perception: str
    felt_state: str
    goals: list[str]
    action_taken: str
    action_result: ActionResult
    npc_movements: list[str]


@dataclass
class SimulationState:
    """Current state of the simulation."""

    world: World
    npcs: dict[str, NPC]
    agent: Agent
    turn: int = 0
    log: list[TurnLog] = field(default_factory=list)
    time_of_night: str = "early"  # "early", "evening", "late"


def create_simulation(starting_room: str = "ground.entrance") -> SimulationState:
    """Create a new simulation with default setup."""
    world = create_velvet()
    npcs = create_npcs()
    agent = create_agent(starting_room)

    return SimulationState(
        world=world,
        npcs=npcs,
        agent=agent,
    )


def simulation_tick(
    state: SimulationState,
    action_str: str,
) -> tuple[SimulationState, TurnLog]:
    """
    Execute one turn of the simulation.

    Args:
        state: Current simulation state
        action_str: Action to execute (e.g., "move north", "talk mika")

    Returns:
        (new_state, turn_log)
    """
    # 1. Time passes - Thymos decays
    state.agent.tick(dt=0.5)

    # 2. NPCs may move
    npc_movements = update_npc_positions(state.npcs, state.world)

    # 3. Get current room and NPCs
    current_room = state.world.get_room(state.agent.current_room)
    npcs_in_room = get_npcs_in_room(state.npcs, state.agent.current_room)

    # 4. Generate perception
    perception = render_room(current_room, npcs_in_room)

    # 5. Store state for log
    felt_state = state.agent.felt_state()
    goals = state.agent.goals()

    # 6. Parse and execute action
    parsed = parse_action(action_str)
    if parsed:
        action_type, args = parsed
        result = execute_action(
            action_type,
            args,
            current_room,
            state.world,
            npcs_in_room,
            state.npcs,
        )
    else:
        result = ActionResult(
            success=False,
            message=f"Unknown action: {action_str}",
            thymos_deltas={},
            affect_deltas={},
        )

    # 7. Apply Thymos changes from action
    if result.thymos_deltas or result.affect_deltas:
        state.agent.thymos = apply_thymos_deltas(
            state.agent.thymos,
            result.thymos_deltas,
            result.affect_deltas,
        )

    # 8. Update agent position if moved
    if result.new_room:
        state.agent.current_room = result.new_room

    # 9. Update history
    state.agent.action_history.append(action_str)
    state.agent.perception_history.append(perception)
    state.agent.last_perception = perception

    # 10. Advance turn
    state.turn += 1

    # Update time of night
    if state.turn > 15:
        state.time_of_night = "late"
    elif state.turn > 7:
        state.time_of_night = "evening"

    # 11. Create log entry
    turn_log = TurnLog(
        turn=state.turn,
        perception=perception,
        felt_state=felt_state,
        goals=goals,
        action_taken=action_str,
        action_result=result,
        npc_movements=npc_movements,
    )
    state.log.append(turn_log)

    return state, turn_log


def run_interactive(
    state: SimulationState,
    max_turns: int = 20,
    action_callback: Callable[[SimulationState, str], str] | None = None,
) -> SimulationState:
    """
    Run simulation in interactive mode.

    Args:
        state: Initial simulation state
        max_turns: Maximum turns to run
        action_callback: Function to get action from user
                        If None, uses input()

    Returns:
        Final simulation state
    """
    for turn in range(max_turns):
        # Get current context
        current_room = state.world.get_room(state.agent.current_room)
        npcs_in_room = get_npcs_in_room(state.npcs, state.agent.current_room)

        # Render perception
        perception = render_room(current_room, npcs_in_room)
        ambient = render_ambient(current_room)

        # Display
        print("\n" + "=" * 54)
        print(f"Turn {state.turn + 1} | {state.time_of_night}")
        print("=" * 54)
        print()
        print(perception)
        print()
        print(ambient)
        print()
        print("[Felt State]")
        print(state.agent.felt_state())
        print()
        goals = state.agent.goals()
        if goals:
            print("[Goals]")
            for g in goals:
                print(f"  - {g}")
            print()

        # Show available actions
        available = get_available_actions(current_room, npcs_in_room)
        print("[Available Actions]")
        for a in available:
            print(f"  - {a}")
        print()

        # Get action
        if action_callback:
            action = action_callback(state, perception)
        else:
            action = input("> ").strip()

        if action.lower() in ("quit", "exit", "q"):
            print("Leaving The Velvet...")
            break

        # Execute turn
        state, turn_log = simulation_tick(state, action)

        # Show result
        print()
        print(f"[Result] {turn_log.action_result.message}")

        # Show NPC movements if any
        if turn_log.npc_movements:
            print()
            for movement in turn_log.npc_movements:
                print(f"  {movement}")

    return state


def run_auto(
    state: SimulationState,
    max_turns: int = 20,
    use_llm: bool = True,
    model: str = "llama3.1:8b",
    delay: float = 1.0,
) -> SimulationState:
    """
    Run simulation with autonomous agent.

    Args:
        state: Initial simulation state
        max_turns: Maximum turns to run
        use_llm: Use LLM for decisions (vs simple heuristics)
        model: Ollama model to use
        delay: Delay between turns (for readability)

    Returns:
        Final simulation state
    """
    import time

    for turn in range(max_turns):
        # Get current context
        current_room = state.world.get_room(state.agent.current_room)
        npcs_in_room = get_npcs_in_room(state.npcs, state.agent.current_room)

        # Render perception
        perception = render_room(current_room, npcs_in_room)
        ambient = render_ambient(current_room)
        available = get_available_actions(current_room, npcs_in_room)

        # Display
        print("\n" + "=" * 54)
        print(f"Turn {state.turn + 1} | {state.time_of_night}")
        print("=" * 54)
        print()
        print(perception)
        print()
        print(ambient)
        print()
        print("[Felt State]")
        print(state.agent.felt_state())
        print()
        goals = state.agent.goals()
        if goals:
            print("[Goals]")
            for g in goals:
                print(f"  - {g}")
            print()

        # Decide action
        if use_llm:
            print("[Deciding...]")
            action, reasoning = agent_decide_ollama_sync(
                state.agent,
                perception,
                available,
                state.world,
                npcs_in_room,
                model=model,
            )
            print(f"[Reasoning] {reasoning[:100]}...")
        else:
            action = agent_decide_simple(state.agent, available)

        print(f"\n> {action}")

        # Execute turn
        state, turn_log = simulation_tick(state, action)

        # Show result
        print()
        print(f"[Result] {turn_log.action_result.message}")

        # Show NPC movements if any
        if turn_log.npc_movements:
            for movement in turn_log.npc_movements:
                print(f"  {movement}")

        # Delay for readability
        if delay > 0:
            time.sleep(delay)

    return state


def get_simulation_summary(state: SimulationState) -> str:
    """Get a summary of the simulation run."""
    lines = [
        f"Simulation Summary",
        f"==================",
        f"Turns: {state.turn}",
        f"Final location: {state.agent.current_room}",
        f"",
        f"Thymos Final State:",
    ]

    # Needs summary
    for need in state.agent.thymos.needs.all_needs():
        status = "OK" if need.current > need.threshold else "LOW"
        lines.append(f"  {need.name}: {need.current:.2f} [{status}]")

    lines.append("")
    lines.append("Action History:")
    for i, action in enumerate(state.agent.action_history[-10:], 1):
        lines.append(f"  {i}. {action}")

    return "\n".join(lines)

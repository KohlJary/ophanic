"""
Thymos-driven agent for The Velvet.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from thymos.models import ThymosState
from thymos.dynamics import tick, generate_goals
from thymos.summarizer import summarize

if TYPE_CHECKING:
    from .world import World
    from .npc import NPC


@dataclass
class Agent:
    """
    A Thymos-driven agent navigating The Velvet.
    """

    name: str = "you"
    thymos: ThymosState = field(default_factory=ThymosState)
    current_room: str = "ground.entrance"

    # History
    action_history: list[str] = field(default_factory=list)
    perception_history: list[str] = field(default_factory=list)

    # Decision making
    last_perception: str = ""
    last_decision_reason: str = ""

    def felt_state(self, mode: str = "template") -> str:
        """Get felt state summary."""
        updated = summarize(self.thymos, mode=mode)
        return updated.felt_summary

    def goals(self) -> list[str]:
        """Get current goals from Thymos."""
        goals = generate_goals(self.thymos.needs)
        return [g.description for g in goals]

    def tick(self, dt: float = 0.5) -> None:
        """Advance Thymos by one time step."""
        self.thymos = tick(self.thymos, dt=dt)


def create_agent(starting_room: str = "ground.entrance") -> Agent:
    """Create a new agent with default state."""
    return Agent(current_room=starting_room)


def build_decision_prompt(
    agent: Agent,
    perception: str,
    available_actions: list[str],
    world: "World",
    npcs_in_room: list["NPC"],
) -> str:
    """
    Build the prompt for LLM decision making.
    """
    felt = agent.felt_state(mode="template")
    goals = agent.goals()

    recent = agent.action_history[-5:] if agent.action_history else ["(just arrived)"]

    # Add hint about moving to find people
    movement_hint = ""
    if not npcs_in_room and any("dialogue" in g.lower() or "social" in g.lower() for g in goals):
        movement_hint = "\nNote: No one is here. Move to another room to find people to talk to."

    prompt = f"""You are navigating The Velvet, a social venue at night.

## Current Perception
{perception}

## Felt State
{felt}

## Current Goals
{chr(10).join(f"- {g}" for g in goals) if goals else "- No urgent needs"}

## Available Actions
{chr(10).join(f"- {a}" for a in available_actions)}

## Recent Actions
{chr(10).join(f"- {a}" for a in recent)}

## NPCs Present
{_format_npcs(npcs_in_room)}{movement_hint}

What do you do? Pick ONE action from the list above.
Respond with ONLY the action command (e.g., "move east" or "talk dove").
If you have social goals but no one is around, MOVE to find people."""

    return prompt


def _format_npcs(npcs: list["NPC"]) -> str:
    """Format NPC list for prompt."""
    if not npcs:
        return "No one here."

    lines = []
    for npc in npcs:
        traits = ", ".join(npc.traits[:2])
        lines.append(f"- {npc.name} ({npc.slug}): {traits}, mood: {npc.mood}")
    return "\n".join(lines)


async def agent_decide_ollama(
    agent: Agent,
    perception: str,
    available_actions: list[str],
    world: "World",
    npcs_in_room: list["NPC"],
    model: str = "llama3.1:8b",
    base_url: str = "http://localhost:11434",
) -> tuple[str, str]:
    """
    Use Ollama to decide agent's next action.

    Returns (action_string, reasoning).
    """
    import httpx

    prompt = build_decision_prompt(agent, perception, available_actions, world, npcs_in_room)

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 50,  # Short response
                    },
                },
            )
            response.raise_for_status()
            result = response.json()
            action_text = result.get("response", "").strip()

            # Extract just the action (first line, strip any explanation)
            action_line = action_text.split("\n")[0].strip().lower()
            # Remove quotes or other artifacts
            action_line = action_line.strip('"\'')

            return action_line, action_text

    except Exception as e:
        # Fallback to simple heuristic
        return _fallback_decision(agent, available_actions), f"(fallback due to: {e})"


def agent_decide_ollama_sync(
    agent: Agent,
    perception: str,
    available_actions: list[str],
    world: "World",
    npcs_in_room: list["NPC"],
    model: str = "llama3.1:8b",
    base_url: str = "http://localhost:11434",
) -> tuple[str, str]:
    """
    Synchronous version of agent_decide_ollama.
    """
    import httpx

    prompt = build_decision_prompt(agent, perception, available_actions, world, npcs_in_room)

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 50,
                    },
                },
            )
            response.raise_for_status()
            result = response.json()
            action_text = result.get("response", "").strip()

            action_line = action_text.split("\n")[0].strip().lower()
            action_line = action_line.strip('"\'')

            return action_line, action_text

    except Exception as e:
        return _fallback_decision(agent, available_actions), f"(fallback due to: {e})"


def _fallback_decision(agent: Agent, available_actions: list[str]) -> str:
    """
    Simple heuristic fallback when LLM unavailable.
    """
    import random

    goals = agent.goals()
    talk_actions = [a for a in available_actions if a.startswith("talk")]
    move_actions = [a for a in available_actions if "move" in a]

    # Check for social goal - try to talk or move to find people
    if any("social" in g.lower() or "dialogue" in g.lower() for g in goals):
        if talk_actions:
            return talk_actions[0].split("(")[0].strip()
        # No one here - move to find people
        if move_actions:
            return random.choice(move_actions).split("(")[0].strip()

    # Check for rest goal - prefer up (usually quieter)
    if any("rest" in g.lower() or "quiet" in g.lower() or "cognitive" in g.lower() for g in goals):
        if "rest" in available_actions:
            return "rest"
        if move_actions:
            up_moves = [a for a in move_actions if "up" in a]
            if up_moves:
                return up_moves[0].split("(")[0].strip()

    # Check for novelty/explore goal
    if any("novelty" in g.lower() or "explore" in g.lower() for g in goals):
        if move_actions:
            return random.choice(move_actions).split("(")[0].strip()

    # If no goals or nothing specific, explore or socialize
    if talk_actions:
        return talk_actions[0].split("(")[0].strip()
    if move_actions and random.random() < 0.6:  # 60% chance to explore
        return random.choice(move_actions).split("(")[0].strip()

    # Default: observe
    return "observe"


def agent_decide_simple(
    agent: Agent,
    available_actions: list[str],
) -> str:
    """
    Simple rule-based decision making (no LLM).
    """
    return _fallback_decision(agent, available_actions)

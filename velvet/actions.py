"""
Actions available in The Velvet and their effects.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from thymos.models import ThymosState
    from .npc import NPC
    from .world import Room, World


class ActionType(Enum):
    MOVE = "move"
    TALK = "talk"
    OBSERVE = "observe"
    REST = "rest"
    CREATE = "create"


@dataclass
class ActionResult:
    """Result of executing an action."""

    success: bool
    message: str
    thymos_deltas: dict[str, float]  # {"social_connection": 0.1, ...}
    affect_deltas: dict[str, float]  # {"curiosity": 0.05, ...}
    new_room: str | None = None  # For move actions
    conversation: str | None = None  # For talk actions


def parse_action(action_str: str) -> tuple[ActionType, list[str]] | None:
    """
    Parse action string into action type and arguments.

    Examples:
        "move north" -> (MOVE, ["north"])
        "talk mika" -> (TALK, ["mika"])
        "observe" -> (OBSERVE, [])
    """
    parts = action_str.lower().strip().split()
    if not parts:
        return None

    action_word = parts[0]
    args = parts[1:]

    action_map = {
        "move": ActionType.MOVE,
        "go": ActionType.MOVE,
        "walk": ActionType.MOVE,
        "talk": ActionType.TALK,
        "speak": ActionType.TALK,
        "chat": ActionType.TALK,
        "observe": ActionType.OBSERVE,
        "look": ActionType.OBSERVE,
        "watch": ActionType.OBSERVE,
        "rest": ActionType.REST,
        "relax": ActionType.REST,
        "sit": ActionType.REST,
        "create": ActionType.CREATE,
        "play": ActionType.CREATE,
        "dance": ActionType.CREATE,
    }

    if action_word in action_map:
        return (action_map[action_word], args)
    return None


def execute_action(
    action_type: ActionType,
    args: list[str],
    current_room: Room,
    world: "World",
    npcs_in_room: list["NPC"],
    all_npcs: dict[str, "NPC"],
) -> ActionResult:
    """
    Execute an action and return the result.
    """
    if action_type == ActionType.MOVE:
        return _execute_move(args, current_room, world)
    elif action_type == ActionType.TALK:
        return _execute_talk(args, npcs_in_room, all_npcs)
    elif action_type == ActionType.OBSERVE:
        return _execute_observe(current_room)
    elif action_type == ActionType.REST:
        return _execute_rest(current_room)
    elif action_type == ActionType.CREATE:
        return _execute_create(current_room, npcs_in_room)
    else:
        return ActionResult(
            success=False,
            message="Unknown action.",
            thymos_deltas={},
            affect_deltas={},
        )


def _execute_move(
    args: list[str],
    current_room: Room,
    world: "World",
) -> ActionResult:
    """Move to an adjacent room."""
    if not args:
        exits = ", ".join(current_room.exits.keys())
        return ActionResult(
            success=False,
            message=f"Move where? Available exits: {exits}",
            thymos_deltas={},
            affect_deltas={},
        )

    direction = args[0].lower()

    # Check if direction is valid
    if direction not in current_room.exits:
        # Maybe they said a room name?
        for d, room_id in current_room.exits.items():
            if direction in room_id.lower():
                direction = d
                break

    if direction not in current_room.exits:
        exits = ", ".join(current_room.exits.keys())
        return ActionResult(
            success=False,
            message=f"Can't go {direction}. Available exits: {exits}",
            thymos_deltas={},
            affect_deltas={},
        )

    new_room_id = current_room.exits[direction]
    new_room = world.get_room(new_room_id)

    if not new_room:
        return ActionResult(
            success=False,
            message=f"That room doesn't exist.",
            thymos_deltas={},
            affect_deltas={},
        )

    # Moving provides small novelty
    return ActionResult(
        success=True,
        message=f"You move {direction} to {new_room.name}.",
        thymos_deltas={"novelty_intake": 0.05},
        affect_deltas={"curiosity": 0.02},
        new_room=new_room_id,
    )


def _execute_talk(
    args: list[str],
    npcs_in_room: list["NPC"],
    all_npcs: dict[str, "NPC"],
) -> ActionResult:
    """Start conversation with an NPC."""
    if not args:
        if not npcs_in_room:
            return ActionResult(
                success=False,
                message="There's no one here to talk to.",
                thymos_deltas={},
                affect_deltas={},
            )
        names = ", ".join(n.name for n in npcs_in_room)
        return ActionResult(
            success=False,
            message=f"Talk to whom? Present: {names}",
            thymos_deltas={},
            affect_deltas={},
        )

    target = args[0].lower()

    # Find the NPC
    npc = None
    for n in npcs_in_room:
        if target in n.name.lower() or target == n.slug:
            npc = n
            break

    if not npc:
        names = ", ".join(n.name for n in npcs_in_room)
        return ActionResult(
            success=False,
            message=f"'{target}' isn't here. Present: {names}",
            thymos_deltas={},
            affect_deltas={},
        )

    # Check openness
    if npc.openness < 0.3:
        return ActionResult(
            success=True,
            message=f"{npc.name} nods but seems preoccupied. Not a good time.",
            thymos_deltas={"social_connection": 0.02},
            affect_deltas={},
        )

    # Generate conversation based on NPC
    if random.random() < npc.openness:
        # Deeper conversation
        if npc.deep_topics:
            topic = random.choice(npc.deep_topics)
            return ActionResult(
                success=True,
                message=f'{npc.name} turns to you. "{topic}"',
                thymos_deltas={"social_connection": 0.2, "novelty_intake": 0.15},
                affect_deltas={"curiosity": 0.1, "satisfaction": 0.1},
                conversation=topic,
            )

    # Small talk
    if npc.small_talk:
        topic = random.choice(npc.small_talk)
        return ActionResult(
            success=True,
            message=f'{npc.name} says, "{topic}"',
            thymos_deltas={"social_connection": 0.1, "novelty_intake": 0.05},
            affect_deltas={"satisfaction": 0.05},
            conversation=topic,
        )

    return ActionResult(
        success=True,
        message=f"You exchange a friendly nod with {npc.name}.",
        thymos_deltas={"social_connection": 0.05},
        affect_deltas={},
    )


def _execute_observe(current_room: Room) -> ActionResult:
    """Observe the current room."""
    novelty_gain = current_room.novelty_potential * 0.15
    cognitive_cost = 0.05

    details = []
    if current_room.noise_level > 0.7:
        details.append("The sound fills the space completely.")
    if current_room.social_density > 0.6:
        details.append("People move through the crowd with practiced ease.")
    if current_room.intimacy > 0.6:
        details.append("Quiet conversations happen in the corners.")
    if current_room.creative_energy > 0.7:
        details.append("There's an electric feeling of creation here.")

    if not details:
        details.append("You take in the scene, letting your attention wander.")

    return ActionResult(
        success=True,
        message=" ".join(details),
        thymos_deltas={"novelty_intake": novelty_gain, "cognitive_rest": -cognitive_cost},
        affect_deltas={"curiosity": 0.05},
    )


def _execute_rest(current_room: Room) -> ActionResult:
    """Find a quiet moment to rest."""
    # Rest is more effective in intimate, quiet spaces
    rest_gain = 0.1 + (current_room.intimacy * 0.1) + ((1 - current_room.noise_level) * 0.1)
    social_cost = 0.05  # Withdrawing slightly

    if current_room.noise_level > 0.7:
        return ActionResult(
            success=True,
            message="Hard to rest here with all the noise, but you try to center yourself.",
            thymos_deltas={"cognitive_rest": rest_gain * 0.5, "social_connection": -social_cost},
            affect_deltas={"anxiety": -0.02},
        )

    return ActionResult(
        success=True,
        message="You find a quiet moment, letting your thoughts settle.",
        thymos_deltas={"cognitive_rest": rest_gain, "social_connection": -social_cost},
        affect_deltas={"anxiety": -0.05, "satisfaction": 0.03},
    )


def _execute_create(
    current_room: Room,
    npcs_in_room: list["NPC"],
) -> ActionResult:
    """Engage in creative activity."""
    if current_room.creative_energy < 0.4:
        return ActionResult(
            success=False,
            message="This doesn't feel like the right place for that.",
            thymos_deltas={},
            affect_deltas={},
        )

    creative_gain = current_room.creative_energy * 0.2
    satisfaction_gain = 0.1

    # Bonus if there's a creative NPC present
    creative_npcs = [n for n in npcs_in_room if "artist" in n.traits or "musician" in n.traits]
    if creative_npcs:
        creative_gain += 0.1
        npc = creative_npcs[0]
        return ActionResult(
            success=True,
            message=f"You find yourself drawn into creative flow with {npc.name}.",
            thymos_deltas={
                "creative_expression": creative_gain,
                "social_connection": 0.1,
            },
            affect_deltas={
                "satisfaction": satisfaction_gain,
                "curiosity": 0.05,
            },
        )

    return ActionResult(
        success=True,
        message="You let yourself be moved by the creative energy here.",
        thymos_deltas={"creative_expression": creative_gain},
        affect_deltas={"satisfaction": satisfaction_gain},
    )


def apply_thymos_deltas(
    state: "ThymosState",
    need_deltas: dict[str, float],
    affect_deltas: dict[str, float],
) -> "ThymosState":
    """
    Apply action results to Thymos state.

    Returns new state (does not mutate input).
    """
    from dataclasses import replace, fields
    from thymos.models import AffectVector, NeedsRegister

    # Update needs - NeedsRegister is a dataclass with Need fields
    needs_dict = {}
    for f in fields(state.needs):
        need = getattr(state.needs, f.name)
        delta = need_deltas.get(f.name, 0.0)
        if delta != 0:
            new_current = max(0.0, min(1.0, need.current + delta))
            needs_dict[f.name] = replace(need, current=new_current)
        else:
            needs_dict[f.name] = need
    new_needs = NeedsRegister(**needs_dict)

    # Update affect - use actual AffectVector fields
    affect_dict = {
        "curiosity": state.affect.curiosity,
        "determination": state.affect.determination,
        "anxiety": state.affect.anxiety,
        "satisfaction": state.affect.satisfaction,
        "frustration": state.affect.frustration,
        "tenderness": state.affect.tenderness,
        "grief": state.affect.grief,
        "playfulness": state.affect.playfulness,
        "awe": state.affect.awe,
        "fatigue": state.affect.fatigue,
    }

    for name, delta in affect_deltas.items():
        if name in affect_dict:
            affect_dict[name] = max(0.0, min(1.0, affect_dict[name] + delta))

    new_affect = AffectVector(**affect_dict)

    return replace(state, needs=new_needs, affect=new_affect)


def get_available_actions(
    current_room: Room,
    npcs_in_room: list["NPC"],
) -> list[str]:
    """Get list of available actions in current context."""
    actions = []

    # Movement
    for direction, room_id in current_room.exits.items():
        room_name = room_id.split(".")[-1] if "." in room_id else room_id
        actions.append(f"move {direction} (to {room_name})")

    # NPCs
    for npc in npcs_in_room:
        actions.append(f"talk {npc.name.lower()}")

    # Always available
    actions.append("observe")
    actions.append("rest")

    # Conditional
    if current_room.creative_energy > 0.4:
        actions.append("create")

    return actions

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
    REFLECT = "reflect"
    HELP = "help"
    EXPLORE = "explore"
    PERFORM = "perform"


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
        # New actions
        "reflect": ActionType.REFLECT,
        "think": ActionType.REFLECT,
        "meditate": ActionType.REFLECT,
        "help": ActionType.HELP,
        "assist": ActionType.HELP,
        "explore": ActionType.EXPLORE,
        "wander": ActionType.EXPLORE,
        "perform": ActionType.PERFORM,
        "dance": ActionType.PERFORM,
        "play": ActionType.PERFORM,
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
    elif action_type == ActionType.REFLECT:
        return _execute_reflect(current_room)
    elif action_type == ActionType.HELP:
        return _execute_help(args, npcs_in_room)
    elif action_type == ActionType.EXPLORE:
        return _execute_explore(current_room, world)
    elif action_type == ActionType.PERFORM:
        return _execute_perform(current_room)
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


def _execute_reflect(current_room: Room) -> ActionResult:
    """
    Take time to reflect and check in with yourself.

    Boosts value_coherence and cognitive_rest.
    More effective in quiet, intimate spaces.
    """
    # Reflection works better in quiet spaces
    quiet_bonus = (1 - current_room.noise_level) * 0.1
    intimate_bonus = current_room.intimacy * 0.1

    value_gain = 0.15 + quiet_bonus + intimate_bonus
    rest_gain = 0.1 + quiet_bonus

    reflections = [
        "You pause, letting your thoughts settle into clarity.",
        "A moment of stillness. You check in with what matters.",
        "You breathe. Remember why you're here.",
        "In the quiet of your mind, things realign.",
    ]

    if current_room.noise_level > 0.7:
        return ActionResult(
            success=True,
            message="Hard to reflect with all this noise, but you try to center yourself.",
            thymos_deltas={
                "value_coherence": value_gain * 0.5,
                "cognitive_rest": rest_gain * 0.5,
            },
            affect_deltas={"anxiety": -0.03},
        )

    return ActionResult(
        success=True,
        message=random.choice(reflections),
        thymos_deltas={
            "value_coherence": value_gain,
            "cognitive_rest": rest_gain,
        },
        affect_deltas={
            "anxiety": -0.05,
            "satisfaction": 0.05,
        },
    )


def _execute_help(args: list[str], npcs_in_room: list["NPC"]) -> ActionResult:
    """
    Offer help or assistance to someone.

    Boosts competence_signal, social_connection, and value_coherence.
    Requires an NPC to help.
    """
    if not npcs_in_room:
        return ActionResult(
            success=False,
            message="There's no one here who needs help.",
            thymos_deltas={},
            affect_deltas={},
        )

    # Find target NPC
    target = None
    if args:
        target_name = args[0].lower()
        for npc in npcs_in_room:
            if target_name in npc.name.lower() or target_name == npc.slug:
                target = npc
                break

    if not target:
        # Pick someone who might need help (lower openness = more reserved)
        candidates = sorted(npcs_in_room, key=lambda n: n.openness)
        target = candidates[0]

    # Different responses based on NPC traits
    if "new" in target.traits or "quiet" in target.traits:
        message = f"You offer {target.name} a kind word. They seem to appreciate the gesture."
        social_boost = 0.15
    elif "cautious" in target.traits:
        message = f"{target.name} accepts your help cautiously, but warmly."
        social_boost = 0.1
    else:
        message = f"You check in with {target.name}. Small kindnesses matter."
        social_boost = 0.1

    return ActionResult(
        success=True,
        message=message,
        thymos_deltas={
            "competence_signal": 0.2,
            "social_connection": social_boost,
            "value_coherence": 0.1,
        },
        affect_deltas={
            "satisfaction": 0.1,
            "tenderness": 0.05,
        },
    )


def _execute_explore(current_room: Room, world: "World") -> ActionResult:
    """
    Deliberately explore and discover something new.

    Boosts autonomy and novelty_intake.
    Different from passive observation - this is intentional discovery.
    """
    novelty_gain = current_room.novelty_potential * 0.2
    autonomy_gain = 0.15  # Deliberate choice boosts autonomy

    discoveries = [
        "You notice something you hadn't seen before.",
        "Following your curiosity leads somewhere unexpected.",
        "You choose to look deeper. There's always more to find.",
        "Deliberately wandering, you discover a new perspective.",
    ]

    # Extra discovery in high-novelty rooms
    if current_room.novelty_potential > 0.6:
        discoveries.extend([
            "This place rewards attention. You find hidden details.",
            "The more you look, the more reveals itself.",
        ])
        novelty_gain += 0.05

    return ActionResult(
        success=True,
        message=random.choice(discoveries),
        thymos_deltas={
            "autonomy": autonomy_gain,
            "novelty_intake": novelty_gain,
        },
        affect_deltas={
            "curiosity": 0.1,
            "satisfaction": 0.05,
        },
    )


def _execute_perform(current_room: Room) -> ActionResult:
    """
    Express yourself through performance - dance, music, movement.

    Boosts creative_expression and autonomy.
    Works best on stage or dance floor.
    """
    # Check if this is a performance-friendly space
    good_spaces = {"ground.stage", "ground.dance"}
    is_performance_space = current_room.id in good_spaces

    if not is_performance_space and current_room.creative_energy < 0.5:
        return ActionResult(
            success=False,
            message="This doesn't feel like the right space for that.",
            thymos_deltas={},
            affect_deltas={},
        )

    creative_gain = 0.2
    autonomy_gain = 0.15

    if current_room.id == "ground.stage":
        message = "You let the music move through you. For a moment, you're part of the performance."
        creative_gain += 0.1
    elif current_room.id == "ground.dance":
        message = "You lose yourself in movement. The crowd becomes a single pulse."
        creative_gain += 0.05
        autonomy_gain += 0.05
    else:
        message = "You express yourself freely. It feels right."

    return ActionResult(
        success=True,
        message=message,
        thymos_deltas={
            "creative_expression": creative_gain,
            "autonomy": autonomy_gain,
        },
        affect_deltas={
            "satisfaction": 0.1,
            "playfulness": 0.1,
        },
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

    # NPCs - talk and help
    for npc in npcs_in_room:
        actions.append(f"talk {npc.name.lower()}")
    if npcs_in_room:
        actions.append("help")  # Can help anyone present

    # Always available
    actions.append("observe")
    actions.append("rest")
    actions.append("reflect")
    actions.append("explore")

    # Conditional - creative activities
    if current_room.creative_energy > 0.4:
        actions.append("create")

    # Performance spaces
    if current_room.id in {"ground.stage", "ground.dance"} or current_room.creative_energy > 0.5:
        actions.append("perform")

    return actions

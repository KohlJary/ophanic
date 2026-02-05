"""
NPCs (patrons) for The Velvet.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .world import World


@dataclass
class NPC:
    """A patron of The Velvet."""

    slug: str                  # "a3f2"
    name: str                  # "Mika"

    # Personality
    traits: list[str] = field(default_factory=list)
    conversation_style: str = ""
    interests: list[str] = field(default_factory=list)

    # Conversation capabilities
    small_talk: list[str] = field(default_factory=list)
    deep_topics: list[str] = field(default_factory=list)

    # State
    current_room: str = ""
    mood: str = "relaxed"
    openness: float = 0.7      # How receptive to interaction

    # Preferred locations
    preferred_rooms: list[str] = field(default_factory=list)

    def describe(self) -> str:
        """Brief description for perception."""
        return f"{self.name} ({', '.join(self.traits[:2])})"


def create_npcs() -> dict[str, NPC]:
    """Create the cast of The Velvet."""
    npcs = {}

    # Mika - the artist friend
    npcs["a3f2"] = NPC(
        slug="a3f2",
        name="Mika",
        traits=["artist", "warm", "curious", "thoughtful"],
        conversation_style="Speaks with enthusiasm about ideas, asks genuine questions",
        interests=["art", "spatial encoding", "philosophy", "perception"],
        small_talk=[
            "Love what Dove's doing with the set tonight.",
            "Have you seen the new piece on the wall? Someone local.",
            "The light in here is perfect, isn't it?",
        ],
        deep_topics=[
            "Do you think AI can really perceive space, or just process it?",
            "I've been thinking about how we encode meaning in arrangements...",
            "What does it feel like when you understand something new?",
        ],
        current_room="second.lounge",
        mood="engaged",
        openness=0.8,
        preferred_rooms=["second.lounge", "second.balcony", "rooftop"],
    )

    # Ren - the complicated one
    npcs["7b08"] = NPC(
        slug="7b08",
        name="Ren",
        traits=["intense", "protective", "complex", "musical"],
        conversation_style="Direct, sometimes guarded, passionate about community",
        interests=["music", "the venue", "community", "Jude"],
        small_talk=[
            "Dove's in good form tonight.",
            "Busy night. Good crowd.",
            "The sound system finally got fixed.",
        ],
        deep_topics=[
            "This place matters, you know? It's not just a venue.",
            "I've been here since the beginning. Seen it change.",
            "Some people just take without giving back.",
        ],
        current_room="ground.stage",
        mood="watchful",
        openness=0.5,  # Lower - there's tension
        preferred_rooms=["ground.stage", "second.lounge"],
    )

    # Jude - the new one
    npcs["9e1c"] = NPC(
        slug="9e1c",
        name="Jude",
        traits=["quiet", "observant", "new", "thoughtful"],
        conversation_style="Listens more than speaks, asks careful questions",
        interests=["listening", "questions", "understanding dynamics"],
        small_talk=[
            "I'm still learning the geography of this place.",
            "Ren brought me here. It's... a lot to take in.",
            "Everyone seems to know each other.",
        ],
        deep_topics=[
            "What draws people to a place like this?",
            "I notice you watching things carefully too.",
            "Is it always this complicated, or am I just new?",
        ],
        current_room="ground.stage",  # Near Ren
        mood="observant",
        openness=0.6,
        preferred_rooms=["ground.stage", "second.lounge", "second.bar"],
    )

    # Lux - the cautious one
    npcs["d4a5"] = NPC(
        slug="d4a5",
        name="Lux",
        traits=["cautious", "kind", "warming", "gentle"],
        conversation_style="Gentle, takes time to open up, genuinely caring",
        interests=["kindness", "trust", "slow reveals", "helping"],
        small_talk=[
            "The balcony's nice if you need air.",
            "The bartender makes a good lavender thing. If you like that.",
            "First time here? It grows on you.",
        ],
        deep_topics=[
            "Trust takes time. I don't mind taking time.",
            "Some people are worth the patience.",
            "What do you need? Not want—need.",
        ],
        current_room="second.bar",
        mood="calm",
        openness=0.65,
        preferred_rooms=["second.bar", "second.lounge", "second.balcony"],
    )

    # Dove - the founder/performer
    npcs["f1e3"] = NPC(
        slug="f1e3",
        name="Dove",
        traits=["musician", "founder", "grounded", "nurturing"],
        conversation_style="Warm but focused when performing, deep listener off-stage",
        interests=["music", "the venue", "connections", "community"],
        small_talk=[
            "Thanks for being here tonight.",
            "The crowd's energy is good.",
            "Take care of yourself, okay?",
        ],
        deep_topics=[
            "I built this place for moments like these.",
            "Music is just organized vibration. Connection is harder.",
            "What do you need from tonight?",
        ],
        current_room="ground.stage",  # Performing
        mood="performing",
        openness=0.4,  # Busy performing
        preferred_rooms=["ground.stage", "second.lounge", "rooftop"],
    )

    return npcs


def update_npc_positions(npcs: dict[str, NPC], world: "World") -> list[str]:
    """
    Possibly move NPCs between rooms.

    Returns list of movement descriptions.
    """
    movements = []

    for slug, npc in npcs.items():
        # Dove stays on stage while performing
        if npc.name == "Dove" and npc.mood == "performing":
            continue

        # Jude tends to stay near Ren
        if npc.name == "Jude":
            ren = npcs.get("7b08")
            if ren and random.random() < 0.7:  # 70% chance to follow Ren
                if npc.current_room != ren.current_room:
                    old_room = npc.current_room
                    npc.current_room = ren.current_room
                    movements.append(f"{npc.name} moved to {world.get_room(npc.current_room).name}")
                continue

        # Random chance to move (20%)
        if random.random() < 0.2:
            current = world.get_room(npc.current_room)
            if current and current.exits:
                # Prefer preferred rooms
                options = list(current.exits.values())
                preferred = [r for r in options if r in npc.preferred_rooms]
                if preferred and random.random() < 0.6:
                    new_room = random.choice(preferred)
                else:
                    new_room = random.choice(options)

                old_room = npc.current_room
                npc.current_room = new_room
                new_room_obj = world.get_room(new_room)
                if new_room_obj:
                    movements.append(f"{npc.name} moved to {new_room_obj.name}")

    return movements


def get_npcs_in_room(npcs: dict[str, NPC], room_id: str) -> list[NPC]:
    """Get all NPCs currently in a room."""
    return [npc for npc in npcs.values() if npc.current_room == room_id]

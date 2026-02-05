"""
The Velvet world map and rooms.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Room:
    """A room in The Velvet."""

    id: str                    # "ground.stage"
    name: str                  # "Stage"
    floor: str                 # "ground", "second", "rooftop"
    description: str

    # Properties affecting needs
    noise_level: float = 0.5       # High noise depletes cognitive_rest
    social_density: float = 0.5    # Affects social_connection opportunities
    novelty_potential: float = 0.5 # How much new stimuli available
    creative_energy: float = 0.5   # Supports creative_expression
    intimacy: float = 0.5          # Depth of connection possible

    # Connections
    exits: dict[str, str] = field(default_factory=dict)  # {"north": "second.lounge"}

    # Features in this room
    features: list[str] = field(default_factory=list)

    def mood_description(self) -> str:
        """Get mood descriptor based on properties."""
        if self.noise_level > 0.7:
            energy = "energetic"
        elif self.noise_level < 0.3:
            energy = "quiet"
        else:
            energy = "moderate"

        if self.intimacy > 0.7:
            vibe = "intimate"
        elif self.social_density > 0.7:
            vibe = "crowded"
        else:
            vibe = "relaxed"

        return f"{vibe}, {energy}"


@dataclass
class World:
    """The complete Velvet venue."""

    rooms: dict[str, Room] = field(default_factory=dict)
    time_of_night: str = "evening"  # "early", "evening", "late"

    def get_room(self, room_id: str) -> Room | None:
        return self.rooms.get(room_id)

    def get_adjacent_rooms(self, room_id: str) -> list[tuple[str, str]]:
        """Get (direction, room_id) pairs for adjacent rooms."""
        room = self.get_room(room_id)
        if not room:
            return []
        return list(room.exits.items())


def create_velvet() -> World:
    """Create The Velvet venue with all rooms."""
    world = World()

    # Ground Floor
    world.rooms["ground.entrance"] = Room(
        id="ground.entrance",
        name="Entrance",
        floor="ground",
        description="The front door of The Velvet. A small vestibule with coat hooks and the muffled thrum of music from inside.",
        noise_level=0.4,
        social_density=0.3,
        novelty_potential=0.3,
        creative_energy=0.2,
        intimacy=0.2,
        exits={"east": "ground.stage"},
        features=["door", "coat hooks", "doorperson"],
    )

    world.rooms["ground.stage"] = Room(
        id="ground.stage",
        name="Stage",
        floor="ground",
        description="The heart of The Velvet. A small stage with warm lights, surrounded by standing room. Tonight, live music fills the space.",
        noise_level=0.9,
        social_density=0.7,
        novelty_potential=0.8,
        creative_energy=0.9,
        intimacy=0.2,
        exits={"west": "ground.entrance", "east": "ground.dance", "up": "second.bar"},
        features=["stage", "speakers", "lights", "standing crowd"],
    )

    world.rooms["ground.dance"] = Room(
        id="ground.dance",
        name="Dance Floor",
        floor="ground",
        description="Bodies moving in the dim light. The bass travels through the floor. Conversation is nearly impossible here.",
        noise_level=0.95,
        social_density=0.9,
        novelty_potential=0.6,
        creative_energy=0.7,
        intimacy=0.3,
        exits={"west": "ground.stage"},
        features=["dance floor", "moving lights", "crowd"],
    )

    # Second Floor
    world.rooms["second.bar"] = Room(
        id="second.bar",
        name="Bar",
        floor="second",
        description="A long wooden bar with warm amber lighting. The bartender moves with practiced ease. Quieter than downstairs, but still lively.",
        noise_level=0.5,
        social_density=0.6,
        novelty_potential=0.5,
        creative_energy=0.3,
        intimacy=0.5,
        exits={"down": "ground.stage", "west": "second.lounge", "east": "second.balcony"},
        features=["bar", "stools", "drinks", "bartender"],
    )

    world.rooms["second.lounge"] = Room(
        id="second.lounge",
        name="Lounge",
        floor="second",
        description="Deep sofas arranged in conversation clusters. Soft lighting, the music a distant pulse. This is where real conversations happen.",
        noise_level=0.3,
        social_density=0.5,
        novelty_potential=0.4,
        creative_energy=0.5,
        intimacy=0.7,
        exits={"east": "second.bar", "up": "rooftop"},
        features=["sofas", "low tables", "warm light", "art on walls"],
    )

    world.rooms["second.balcony"] = Room(
        id="second.balcony",
        name="Balcony",
        floor="second",
        description="An outdoor balcony overlooking the street. City lights glitter below. The air is cool and the music is muffled.",
        noise_level=0.2,
        social_density=0.3,
        novelty_potential=0.4,
        creative_energy=0.4,
        intimacy=0.6,
        exits={"west": "second.bar"},
        features=["railing", "city view", "cool air", "string lights"],
    )

    # Rooftop
    world.rooms["rooftop"] = Room(
        id="rooftop",
        name="Rooftop",
        floor="rooftop",
        description="The top of The Velvet. Stars visible above the city glow. A few scattered seats, plants in pots. The quietest place in the building.",
        noise_level=0.1,
        social_density=0.2,
        novelty_potential=0.3,
        creative_energy=0.4,
        intimacy=0.9,
        exits={"down": "second.lounge"},
        features=["stars", "plants", "scattered seating", "city skyline"],
    )

    return world


# Direction mappings for display
DIRECTION_ARROWS = {
    "north": "↑",
    "south": "↓",
    "east": "→",
    "west": "←",
    "up": "↑↑",
    "down": "↓↓",
}

DIRECTION_NAMES = {
    "north": "North",
    "south": "South",
    "east": "East",
    "west": "West",
    "up": "Upstairs",
    "down": "Downstairs",
}

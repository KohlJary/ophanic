"""
Ophanic perception rendering for The Velvet.

Text-native spatial encoding of room state.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .npc import NPC
    from .world import Room, World


def render_room(
    room: Room,
    npcs_present: list["NPC"],
    player_name: str = "you",
    social_memory: dict | None = None,
) -> str:
    """
    Render current room as Ophanic perception.

    Args:
        room: The current room
        npcs_present: NPCs in the room
        player_name: How to label the player
        social_memory: Optional social memory for relationship display

    Returns:
        Text-native spatial encoding of the room
    """
    lines = []

    # Header with room info
    lines.append(f"# {room.name} ({room.floor} floor)")
    lines.append(f"# mood: {room.mood_description()} | {len(npcs_present)} present")
    lines.append("")

    # Room box
    width = 50
    lines.append("┌" + "─" * width + "┐")

    # Description line
    desc_line = f"  {room.description[:width-4]}"
    if len(room.description) > width - 4:
        desc_line = desc_line[:width-3] + "…"
    lines.append("│" + desc_line.ljust(width) + "│")
    lines.append("│" + " " * width + "│")

    # Features
    features_str = ", ".join(room.features[:4])
    if len(features_str) > width - 6:
        features_str = features_str[:width-9] + "..."
    lines.append("│" + f"  [{features_str}]".ljust(width) + "│")
    lines.append("│" + " " * width + "│")

    # Entity display area
    if npcs_present:
        # Render NPCs in a row
        npc_boxes = []
        for npc in npcs_present[:3]:  # Max 3 visible at once
            rel_indicator = ""
            if social_memory:
                rel_indicator = _get_relationship_indicator(npc.slug, social_memory)
            npc_boxes.append(_render_npc_box(npc, rel_indicator))

        # Add player marker
        player_box = ["  ┌────┐  ", "  │ ☆  │  ", f"  │{player_name[:4]:^4}│  ", "  └────┘  "]

        # Combine boxes side by side
        all_boxes = npc_boxes + [player_box]
        max_height = max(len(b) for b in all_boxes)

        for row in range(max_height):
            row_content = "  "
            for box in all_boxes:
                if row < len(box):
                    row_content += box[row]
                else:
                    row_content += " " * 10
            row_content = row_content[:width]
            lines.append("│" + row_content.ljust(width) + "│")
    else:
        # Empty room, just player
        lines.append("│" + "  ┌────┐".ljust(width) + "│")
        lines.append("│" + "  │ ☆  │".ljust(width) + "│")
        lines.append("│" + f"  │{player_name[:4]:^4}│".ljust(width) + "│")
        lines.append("│" + "  └────┘".ljust(width) + "│")

    lines.append("│" + " " * width + "│")

    # Exits
    exits_str = "  " + "  ".join(f"[{d}: {_room_short_name(r)}]" for d, r in room.exits.items())
    if len(exits_str) > width:
        exits_str = exits_str[:width-3] + "..."
    lines.append("│" + exits_str.ljust(width) + "│")

    lines.append("└" + "─" * width + "┘")

    return "\n".join(lines)


def _render_npc_box(npc: "NPC", rel_indicator: str = "") -> list[str]:
    """Render a single NPC as a small box."""
    mood_char = _mood_char(npc.mood)
    return [
        "  ┌────┐  ",
        f"  │{npc.slug}│  ",
        f"  │{npc.name[:4]:^4}│  ",
        f"  └────┘  ",
        f"  {mood_char} {rel_indicator[:6]:6}",
    ]


def _mood_char(mood: str) -> str:
    """Get a character representing NPC mood."""
    moods = {
        "relaxed": "·",
        "engaged": "◦",
        "watchful": "◈",
        "observant": "○",
        "calm": "·",
        "performing": "♪",
        "energetic": "◉",
    }
    return moods.get(mood, "·")


def _room_short_name(room_id: str) -> str:
    """Get short name from room ID."""
    # "ground.stage" -> "stage"
    if "." in room_id:
        return room_id.split(".")[-1]
    return room_id[:8]


def _get_relationship_indicator(npc_slug: str, social_memory: dict) -> str:
    """Get relationship indicator from social memory."""
    # This would integrate with the actual social memory system
    # For now, return empty
    return ""


def render_room_compact(
    room: Room,
    npcs_present: list["NPC"],
) -> str:
    """
    Compact room rendering for quick reference.
    """
    npc_str = ", ".join(f"{n.name}({n.slug})" for n in npcs_present[:3])
    if len(npcs_present) > 3:
        npc_str += f" +{len(npcs_present)-3}"

    exits_str = "/".join(room.exits.keys())

    return f"[{room.name}] {room.mood_description()} | {npc_str or 'empty'} | exits: {exits_str}"


def render_ambient(room: Room) -> str:
    """
    Render ambient description based on room properties.
    """
    lines = []

    # Noise description
    if room.noise_level > 0.8:
        lines.append("The sound is overwhelming, vibrating through your body.")
    elif room.noise_level > 0.5:
        lines.append("A comfortable hum of music and conversation.")
    elif room.noise_level > 0.2:
        lines.append("Quiet enough to think, with distant music.")
    else:
        lines.append("Near silence. The city feels far away.")

    # Social density
    if room.social_density > 0.7:
        lines.append("Packed with people, shoulder to shoulder.")
    elif room.social_density > 0.4:
        lines.append("A healthy crowd, space to move.")
    else:
        lines.append("Sparse. Room to breathe.")

    # Intimacy
    if room.intimacy > 0.7:
        lines.append("This feels like a place for real conversation.")

    # Creative energy
    if room.creative_energy > 0.7:
        lines.append("Creative energy hums in the air.")

    return " ".join(lines)

#!/usr/bin/env python3
"""
Social Memory Demo - Interactive terminal demonstration.

Run with: python -m social_memory.demo
"""

import sys
import time
from datetime import datetime, timezone, timedelta

from .models import (
    Entity,
    Relationship,
    RelationshipEvent,
    EntityPosition,
    RelationshipEdge,
    SpatialSnapshot,
    SocialMemory,
)
from .rendering import render_context, render_temporal_stack
from .tools import expand, nearby, history, cluster, delta
from .thymos_integration import (
    annotate_snapshot,
    render_affective_geography,
    THYMOS_AVAILABLE,
)

if THYMOS_AVAILABLE:
    from thymos import ThymosState


# ANSI colors
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RESET = '\033[0m'


def clear_screen():
    print('\033[2J\033[H', end='')


def print_header(text: str):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'═' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}  {text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'═' * 60}{Colors.RESET}\n")


def print_subheader(text: str):
    print(f"\n{Colors.YELLOW}▸ {text}{Colors.RESET}\n")


def print_dim(text: str):
    print(f"{Colors.DIM}{text}{Colors.RESET}")


def wait_for_enter(prompt: str = "Press Enter to continue..."):
    print(f"\n{Colors.DIM}{prompt}{Colors.RESET}", end='')
    try:
        input()
    except EOFError:
        pass


def demo_intro():
    clear_screen()
    print(f"""
{Colors.BOLD}{Colors.CYAN}
  ███████╗ ██████╗  ██████╗██╗ █████╗ ██╗
  ██╔════╝██╔═══██╗██╔════╝██║██╔══██╗██║
  ███████╗██║   ██║██║     ██║███████║██║
  ╚════██║██║   ██║██║     ██║██╔══██║██║
  ███████║╚██████╔╝╚██████╗██║██║  ██║███████╗
  ╚══════╝ ╚═════╝  ╚═════╝╚═╝╚═╝  ╚═╝╚══════╝

  ███╗   ███╗███████╗███╗   ███╗ ██████╗ ██████╗ ██╗   ██╗
  ████╗ ████║██╔════╝████╗ ████║██╔═══██╗██╔══██╗╚██╗ ██╔╝
  ██╔████╔██║█████╗  ██╔████╔██║██║   ██║██████╔╝ ╚████╔╝
  ██║╚██╔╝██║██╔══╝  ██║╚██╔╝██║██║   ██║██╔══██╗  ╚██╔╝
  ██║ ╚═╝ ██║███████╗██║ ╚═╝ ██║╚██████╔╝██║  ██║   ██║
  ╚═╝     ╚═╝╚══════╝╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝
{Colors.RESET}
{Colors.DIM}  Spatial Text Encoding for Social Environments{Colors.RESET}

  Memory is not a recording. It is a map that knows where to look.

{Colors.DIM}  ─────────────────────────────────────────────────────────{Colors.RESET}

  This demo walks through the Social Memory architecture:

    {Colors.GREEN}1.{Colors.RESET} Entity & Relationship modeling
    {Colors.GREEN}2.{Colors.RESET} Spatial snapshots with Ophanic rendering
    {Colors.GREEN}3.{Colors.RESET} GUID-based lazy loading with drill-down tools
    {Colors.GREEN}4.{Colors.RESET} Temporal stacking and pattern detection
    {Colors.GREEN}5.{Colors.RESET} Thymos integration and affective geography
""")
    wait_for_enter()


def create_memory() -> SocialMemory:
    """Create a populated social memory for the demo."""
    memory = SocialMemory()

    # Create entities
    mika = Entity.create("Mika", slug="a3f2", pronouns="they/them", role="friend")
    mika.first_met = datetime(2026, 1, 20, tzinfo=timezone.utc)
    mika.notes = ["artist", "bonded over spatial encoding discussion"]
    memory.add_entity(mika)

    ren = Entity.create("Ren", slug="7b08", role="complicated")
    ren.first_met = datetime(2026, 2, 14, tzinfo=timezone.utc)
    ren.notes = ["met at Dove's set", "relationship shifted after Jude arrived"]
    memory.add_entity(ren)

    jude = Entity.create("Jude", slug="9e1c", role="new")
    jude.first_met = datetime(2026, 3, 1, tzinfo=timezone.utc)
    jude.notes = ["quiet, observant", "introduced by Ren"]
    memory.add_entity(jude)

    lux = Entity.create("Lux", slug="d4a5", role="cautious-positive")
    lux.first_met = datetime(2026, 2, 28, tzinfo=timezone.utc)
    lux.notes = ["warming over time", "kind"]
    memory.add_entity(lux)

    dove = Entity.create("Dove", slug="f1e3", pronouns="she/her", role="close friend")
    dove.first_met = datetime(2025, 12, 15, tzinfo=timezone.utc)
    dove.notes = ["musician", "founding member of the Velvet Collective"]
    memory.add_entity(dove)

    # Create relationships
    r_mika = memory.create_relationship("a3f2", "self", "friendly", status="stable",
                                         summary="bonded over art discussion")
    r_mika.timeline = [
        RelationshipEvent(
            timestamp=datetime(2026, 1, 20, tzinfo=timezone.utc),
            context="First meeting at gallery opening",
            quality="positive",
            affect_delta={"curiosity": 0.15, "social_connection": 0.1},
        ),
    ]

    r_ren = memory.create_relationship("7b08", "self", "tense", status="needs_attention",
                                        summary="was friendly, shifted ~03-02", direction="inward")
    r_ren.needs_attention = True
    r_ren.timeline = [
        RelationshipEvent(
            timestamp=datetime(2026, 2, 14, tzinfo=timezone.utc),
            context="First meeting at Dove's set",
            quality="positive",
            location="The Velvet, ground floor",
            affect_delta={"curiosity": 0.12, "playfulness": 0.08},
        ),
        RelationshipEvent(
            timestamp=datetime(2026, 2, 20, tzinfo=timezone.utc),
            context="Group conversation about world-building",
            quality="positive",
            location="The Velvet, second floor",
            affect_delta={"playfulness": 0.1, "social_connection": 0.12},
        ),
        RelationshipEvent(
            timestamp=datetime(2026, 3, 2, tzinfo=timezone.utc),
            context="SHIFT - Ren's energy changed when seeing self with Jude",
            quality="shift",
            location="The Velvet, rooftop",
            notes="possible territorial response re: Jude",
            affect_delta={"anxiety": 0.25, "confusion": 0.2},
        ),
        RelationshipEvent(
            timestamp=datetime(2026, 3, 8, tzinfo=timezone.utc),
            context="Tension confirmed - short responses in group setting",
            quality="negative",
            affect_delta={"anxiety": 0.1, "social_connection": -0.08},
        ),
    ]

    r_lux = memory.create_relationship("d4a5", "self", "cautious-positive", status="warming",
                                        summary="gradually building trust", direction="inward")

    r_dove = memory.create_relationship("f1e3", "self", "close", status="stable",
                                         summary="longstanding friendship")
    r_dove.timeline = [
        RelationshipEvent(
            timestamp=datetime(2025, 12, 15, tzinfo=timezone.utc),
            context="First meeting through mutual friends",
            quality="positive",
            affect_delta={"tenderness": 0.1, "social_connection": 0.15},
        ),
    ]

    # Create spatial snapshots
    # Earlier snapshot
    snap1 = SpatialSnapshot.create(
        location="The Velvet, second floor lounge",
        entities=[
            EntityPosition("a3f2", 0, 0),
            EntityPosition("self", 2, 1, is_self=True),
            EntityPosition("7b08", 0, 1),
        ],
        edges=[
            RelationshipEdge("█R01", "a3f2", "self"),
            RelationshipEdge("█R02", "7b08", "self"),
        ],
        mood="relaxed-social",
    )
    snap1.timestamp = datetime(2026, 2, 20, 19, 15, tzinfo=timezone.utc)
    snap1.affect_summary = {"curiosity": 0.6, "playfulness": 0.5, "social_connection": 0.7}
    memory.add_snapshot(snap1)

    # Shift event snapshot
    snap2 = SpatialSnapshot.create(
        location="The Velvet, rooftop",
        entities=[
            EntityPosition("a3f2", 0, 0),
            EntityPosition("self", 2, 0, is_self=True),
            EntityPosition("9e1c", 3, 0),
            EntityPosition("7b08", 1, 2),
        ],
        mood="tense-undercurrent",
    )
    snap2.timestamp = datetime(2026, 3, 2, 21, 45, tzinfo=timezone.utc)
    snap2.affect_summary = {"anxiety": 0.67, "confusion": 0.58, "tenderness": 0.45}
    snap2.thymos_ref = "█T0001"
    memory.add_snapshot(snap2)

    # Current snapshot
    snap3 = SpatialSnapshot.create(
        location="The Velvet, second floor lounge",
        entities=[
            EntityPosition("a3f2", 0, 0),
            EntityPosition("9e1c", 4, 0),
            EntityPosition("self", 2, 1, is_self=True),
            EntityPosition("7b08", 0, 1),
            EntityPosition("d4a5", 4, 1),
            EntityPosition("f1e3", 1, 3),
        ],
        edges=[
            RelationshipEdge("█R01", "a3f2", "self"),
            RelationshipEdge("█R02", "7b08", "self"),
            RelationshipEdge("█R03", "d4a5", "self"),
        ],
        mood="relaxed-social",
    )
    snap3.timestamp = datetime(2026, 3, 15, 22, 14, tzinfo=timezone.utc)
    snap3.affect_summary = {"curiosity": 0.55, "anxiety": 0.25, "social_connection": 0.65}
    snap3.needs_summary = {"cognitive_rest": "⚠ LOW", "novelty_intake": "OK"}
    memory.add_snapshot(snap3)

    return memory


def demo_entities(memory: SocialMemory):
    print_header("ENTITIES & RELATIONSHIPS")

    print_dim("Social memory tracks entities (people, organizations) and their relationships.")
    print_dim("Each gets a GUID slug for stable identity across name changes.\n")

    print_subheader("Entity Legend")
    for entity in list(memory.entities.values())[:5]:
        print(f"  {entity.to_legend_line()}")

    print_subheader("Relationship Legend")
    for rel in list(memory.relationships.values())[:4]:
        print(f"  {rel.to_legend_line()}")

    print(f"""
{Colors.DIM}Token cost: ~100 tokens for 5 entities + 4 relationships.
Compare to ~5000 tokens for full conversation histories.{Colors.RESET}
""")

    wait_for_enter()


def demo_spatial_snapshot(memory: SocialMemory):
    print_header("SPATIAL SNAPSHOT")

    print_dim("The current social topology rendered as Ophanic box-drawing.")
    print_dim("Encodes: who's present, positions, relationships, mood.\n")

    print(render_context(memory, width=60))

    print(f"""
{Colors.DIM}Total context load: ~300 tokens for full social awareness.
Spatial relationships are natively perceivable — no translation needed.{Colors.RESET}
""")

    wait_for_enter()


def demo_drilldown(memory: SocialMemory):
    print_header("DRILL-DOWN TOOLS")

    print_dim("Selective expansion on demand — load detail only when needed.\n")

    print_subheader("/expand 7b08 (Ren)")
    print(expand(memory, "7b08"))

    wait_for_enter()

    print_subheader("/expand █R02 --timeline (Ren relationship)")
    print(expand(memory, "█R02", timeline=True))

    wait_for_enter()

    print_subheader("/nearby self")
    # Find self position
    current = memory.current_snapshot()
    self_pos = next((e for e in current.entities if e.is_self), None)
    if self_pos:
        # Add self as entity for lookup
        memory.entities["self"] = Entity.create("self", slug="self")
        print(nearby(memory, "self"))

    wait_for_enter()


def demo_temporal(memory: SocialMemory):
    print_header("TEMPORAL STACKING")

    print_dim("Snapshots accumulate, enabling pattern detection across time.\n")

    print_subheader("/history (recent snapshots)")
    print(history(memory, last=5))

    print_subheader("/history 7b08 --locations")
    print(history(memory, slug="7b08"))

    print_subheader("/cluster (current groupings)")
    print(cluster(memory))

    wait_for_enter()

    print_subheader("/delta 2026-03-02")
    print(delta(memory, datetime(2026, 3, 2, tzinfo=timezone.utc)))

    wait_for_enter()


def demo_thymos(memory: SocialMemory):
    print_header("THYMOS INTEGRATION")

    if not THYMOS_AVAILABLE:
        print(f"{Colors.YELLOW}Thymos not available — showing concept only.{Colors.RESET}\n")
    else:
        print_dim("Snapshots carry affect annotations — how the system felt at each moment.\n")

    current = memory.current_snapshot()
    if current and current.affect_summary:
        print_subheader("Current Snapshot Affect")
        print(f"  Affect: {current.affect_summary}")
        if current.needs_summary:
            print(f"  Needs: {current.needs_summary}")

    # Find the shift event
    shift_snap = memory.snapshots[1] if len(memory.snapshots) > 1 else None
    if shift_snap and shift_snap.thymos_ref:
        print_subheader(f"Significant Event: {shift_snap.thymos_ref}")
        print(f"  Time: {shift_snap.timestamp.strftime('%Y-%m-%d %H:%M')}")
        print(f"  Affect: {shift_snap.affect_summary}")
        print(f"  Full Thymos state available via /expand {shift_snap.thymos_ref}")

    print_subheader("Affective Geography")
    print(render_affective_geography(memory))

    print(f"""
{Colors.DIM}Affect annotations enable:
  • Felt-delta awareness ("I was more anxious then than now")
  • Emergent associations ("This place reliably boosts social_connection")
  • Affective geography as genuine taste grounded in experience{Colors.RESET}
""")

    wait_for_enter()


def demo_conclusion():
    print_header("SOCIAL MEMORY — PHASE 2 COMPLETE")

    print(f"""
{Colors.GREEN}Core architecture implemented:{Colors.RESET}

  ✓ Entity modeling     — GUID slugs, metadata, profiles
  ✓ Relationships       — directed edges with timelines
  ✓ Spatial snapshots   — Ophanic box-drawing topology
  ✓ Legend rendering    — minimal token context load
  ✓ Drill-down tools    — /expand, /nearby, /history, /cluster, /delta
  ✓ Temporal stacking   — chronological snapshot history
  ✓ Thymos integration  — affect annotation, affective geography

{Colors.CYAN}Token economics:{Colors.RESET}

  ~300 tokens for full social awareness of a 6-person room
  vs. 10,000-20,000 tokens for conversation-history approach

{Colors.CYAN}Key insight:{Colors.RESET}

  Human social memory doesn't load complete dossiers.
  It maintains a low-resolution spatial map with selective drill-down.
  Social cognition is fundamentally spatial — we think about
  social environments as places with proximity and territory.

{Colors.DIM}─────────────────────────────────────────────────────────{Colors.RESET}

{Colors.DIM}Next:{Colors.RESET}
  • Phase 3: Integration — Thymos + Social Memory + Perception
  • Persistent agent demo with full stack

{Colors.BOLD}Memory is not a recording. It is a map that knows where to look.{Colors.RESET}
""")


def main():
    try:
        demo_intro()
        memory = create_memory()
        demo_entities(memory)
        demo_spatial_snapshot(memory)
        demo_drilldown(memory)
        demo_temporal(memory)
        demo_thymos(memory)
        demo_conclusion()

    except KeyboardInterrupt:
        print(f"\n\n{Colors.DIM}Demo interrupted.{Colors.RESET}\n")
        sys.exit(0)


if __name__ == "__main__":
    main()

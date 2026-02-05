#!/usr/bin/env python3
"""
The Velvet — Interactive Demo

A roguelike simulation where a Thymos-driven agent navigates
The Velvet venue, interacts with patrons, and addresses its
homeostatic needs through Ophanic perception.

Usage:
    python -m velvet.demo              # Interactive mode
    python -m velvet.demo --auto       # Watch agent autonomously
    python -m velvet.demo --auto --no-llm  # Auto mode without LLM
"""

from __future__ import annotations

import argparse
import sys

from .simulation import (
    create_simulation,
    run_interactive,
    run_auto,
    get_simulation_summary,
)


BANNER = """
╔══════════════════════════════════════════════════════╗
║                                                      ║
║            ✦  T H E   V E L V E T  ✦                ║
║                                                      ║
║        A night at the lounge. Live music.           ║
║        Familiar faces. Your needs are real.         ║
║                                                      ║
╚══════════════════════════════════════════════════════╝
"""

HELP_TEXT = """
Commands:
  move <direction>  - Move to adjacent room (north, south, east, west, up, down)
  talk <name>       - Start conversation with someone
  observe           - Take in the scene
  rest              - Find a quiet moment
  create            - Engage in creative activity (where available)

  help              - Show this help
  status            - Show detailed Thymos state
  map               - Show venue map
  quit              - Leave The Velvet
"""

MAP_TEXT = """
                    ┌─────────────┐
                    │   ROOFTOP   │
                    │   (quiet)   │
                    └──────┬──────┘
                           │
    ┌─────────────┬────────┴───────┬─────────────┐
    │   LOUNGE    │      BAR       │   BALCONY   │
    │  (intimate) │   (social)     │   (view)    │
    └─────────────┴───────┬────────┴─────────────┘
                          │
    ┌─────────────┬───────┴────────┬─────────────┐
    │  ENTRANCE   │     STAGE      │    DANCE    │
    │   (entry)   │   (music)      │   (crowd)   │
    └─────────────┴────────────────┴─────────────┘
"""


def print_header():
    """Print the game header."""
    print(BANNER)


def print_help():
    """Print help text."""
    print(HELP_TEXT)


def print_map():
    """Print venue map."""
    print(MAP_TEXT)


def print_thymos_status(state):
    """Print detailed Thymos state."""
    print("\n[Thymos State]")
    print("-" * 40)

    print("\nAffect Vector:")
    affect = state.agent.thymos.affect
    # Use actual AffectVector fields
    for name in ["curiosity", "determination", "anxiety", "satisfaction",
                 "frustration", "tenderness", "grief", "playfulness",
                 "awe", "fatigue"]:
        value = getattr(affect, name)
        bar = "█" * int(value * 10) + "░" * (10 - int(value * 10))
        print(f"  {name:14} [{bar}] {value:.2f}")

    print("\nNeeds:")
    for need in state.agent.thymos.needs.all_needs():
        bar = "█" * int(need.current * 10) + "░" * (10 - int(need.current * 10))
        status = "LOW!" if need.current < need.threshold else ""
        print(f"  {need.name:20} [{bar}] {need.current:.2f} {status}")

    print()


def interactive_callback(state, perception):
    """Get action from user with special commands."""
    while True:
        action = input("> ").strip().lower()

        if action == "help":
            print_help()
            continue
        elif action == "status":
            print_thymos_status(state)
            continue
        elif action == "map":
            print_map()
            continue
        elif action in ("quit", "exit", "q"):
            return "quit"
        else:
            return action


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="The Velvet — A Thymos-driven roguelike demo"
    )
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Watch agent navigate autonomously",
    )
    parser.add_argument(
        "--no-llm",
        action="store_true",
        help="Use simple heuristics instead of LLM (faster)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="llama3.1:8b",
        help="Ollama model to use for agent decisions",
    )
    parser.add_argument(
        "--turns",
        type=int,
        default=20,
        help="Maximum turns to run",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.5,
        help="Delay between turns in auto mode (seconds)",
    )
    parser.add_argument(
        "--start",
        type=str,
        default="ground.entrance",
        help="Starting room",
    )

    args = parser.parse_args()

    # Print header
    print_header()

    # Create simulation
    print("Initializing The Velvet...")
    state = create_simulation(starting_room=args.start)
    print("Done.\n")

    if args.auto:
        print("=" * 54)
        print("AUTO MODE — Watching agent navigate")
        if args.no_llm:
            print("Using simple heuristics (no LLM)")
        else:
            print(f"Using LLM: {args.model}")
        print("=" * 54)
        print()
        print("Press Ctrl+C to stop early.\n")

        try:
            state = run_auto(
                state,
                max_turns=args.turns,
                use_llm=not args.no_llm,
                model=args.model,
                delay=args.delay,
            )
        except KeyboardInterrupt:
            print("\n\nStopped early.")
    else:
        print("INTERACTIVE MODE")
        print("Type 'help' for commands, 'quit' to exit.\n")

        state = run_interactive(
            state,
            max_turns=args.turns,
            action_callback=interactive_callback,
        )

    # Show summary
    print("\n")
    print(get_simulation_summary(state))
    print("\n✦ Thanks for visiting The Velvet. ✦\n")


if __name__ == "__main__":
    main()

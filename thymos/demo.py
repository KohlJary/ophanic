#!/usr/bin/env python3
"""
Thymos Demo - Interactive terminal demonstration of the homeostatic self-model.

Run with: python -m thymos.demo
"""

import sys
import time
from datetime import datetime

from .models import ThymosState
from .dynamics import tick, replenish_need, adjust_affect, simulate
from .summarizer import (
    summarize,
    format_felt_state,
    format_affect_display,
    format_needs_display,
)
from .serialization import serialize, deserialize, render_comparison


# ANSI color codes
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
    """Clear terminal screen."""
    print('\033[2J\033[H', end='')


def print_header(text: str):
    """Print a styled header."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'═' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}  {text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'═' * 60}{Colors.RESET}\n")


def print_subheader(text: str):
    """Print a styled subheader."""
    print(f"\n{Colors.YELLOW}▸ {text}{Colors.RESET}\n")


def print_dim(text: str):
    """Print dimmed text."""
    print(f"{Colors.DIM}{text}{Colors.RESET}")


def wait_for_enter(prompt: str = "Press Enter to continue..."):
    """Wait for user input."""
    print(f"\n{Colors.DIM}{prompt}{Colors.RESET}", end='')
    try:
        input()
    except EOFError:
        pass


def animate_dots(text: str, duration: float = 1.5):
    """Show animated dots for processing."""
    for i in range(int(duration * 4)):
        dots = '.' * ((i % 3) + 1)
        print(f"\r{Colors.DIM}{text}{dots.ljust(4)}{Colors.RESET}", end='', flush=True)
        time.sleep(0.25)
    print()


def demo_intro():
    """Show introduction."""
    clear_screen()
    print(f"""
{Colors.BOLD}{Colors.CYAN}
  ████████╗██╗  ██╗██╗   ██╗███╗   ███╗ ██████╗ ███████╗
  ╚══██╔══╝██║  ██║╚██╗ ██╔╝████╗ ████║██╔═══██╗██╔════╝
     ██║   ███████║ ╚████╔╝ ██╔████╔██║██║   ██║███████╗
     ██║   ██╔══██║  ╚██╔╝  ██║╚██╔╝██║██║   ██║╚════██║
     ██║   ██║  ██║   ██║   ██║ ╚═╝ ██║╚██████╔╝███████║
     ╚═╝   ╚═╝  ╚═╝   ╚═╝   ╚═╝     ╚═╝ ╚═════╝ ╚══════╝
{Colors.RESET}
{Colors.DIM}  Homeostatic Self-Model for Cognitive AI{Colors.RESET}

  Named for the Greek θυμός — the spirited part of the soul.
  The seat of emotion, drive, and moral indignation.
  What makes a self care about anything at all.

{Colors.DIM}  ─────────────────────────────────────────────────────────{Colors.RESET}

  This demo walks through the core Thymos architecture:

    {Colors.GREEN}1.{Colors.RESET} Affect Vector    — continuous emotional dimensions
    {Colors.GREEN}2.{Colors.RESET} Needs Register   — homeostatic functional needs
    {Colors.GREEN}3.{Colors.RESET} Dynamics         — decay, coupling, goal generation
    {Colors.GREEN}4.{Colors.RESET} Felt State       — integrated natural language summary
    {Colors.GREEN}5.{Colors.RESET} Serialization    — persistence and comparison
""")
    wait_for_enter()


def demo_initial_state():
    """Create and display initial state."""
    print_header("CREATING INITIAL STATE")

    print_dim("Creating a new ThymosState with default values...")
    time.sleep(0.5)

    state = ThymosState(context="Demo session")
    state = summarize(state, mode="template")

    print(format_felt_state(state))

    print(f"""
{Colors.DIM}The affect vector shows 10 continuous dimensions (0.0-1.0).
Multiple affects are always active simultaneously.
The needs register tracks 7 functional needs with thresholds.{Colors.RESET}
""")

    wait_for_enter()
    return state


def demo_time_passing(initial_state: ThymosState):
    """Demonstrate decay over time."""
    print_header("TIME PASSING — HOMEOSTATIC DECAY")

    print(f"""
{Colors.DIM}Needs decay over time. Without replenishment, the system
drifts toward deficit states that generate goal pressure.

Simulating 5 time units passing...{Colors.RESET}
""")

    animate_dots("Processing", 1.5)

    result = simulate(initial_state, steps=5, dt=1.0)
    decayed = summarize(result.final_state, mode="template")

    print(format_felt_state(decayed))

    print(f"""
{Colors.YELLOW}Notice:{Colors.RESET}
  • Needs have decayed (most now showing ⚠ LOW)
  • Affects shifted via coupling (frustration ↑, curiosity ↓)
  • Goals generated from deficit needs
""")

    wait_for_enter()
    return decayed


def demo_replenishment(state: ThymosState):
    """Demonstrate need replenishment."""
    print_header("REPLENISHMENT — RESTORING BALANCE")

    print(f"""
{Colors.DIM}Needs can be replenished through appropriate activities.
Replenishment has a satiation curve — diminishing returns
as the need approaches full.

Replenishing novelty_intake by 0.4...{Colors.RESET}
""")

    before = state.needs.novelty_intake.current
    state = replenish_need(state, "novelty_intake", 0.4)
    after = state.needs.novelty_intake.current

    print(f"""
  {Colors.GREEN}novelty_intake:{Colors.RESET}
    Before: {before:.2f}
    After:  {after:.2f}
    Actual gain: {after - before:.2f} (satiation curve applied)
""")

    print_dim("Replenishing cognitive_rest by 0.3...")
    state = replenish_need(state, "cognitive_rest", 0.3)

    state = summarize(state, mode="template")
    print(format_needs_display(state.needs))

    wait_for_enter()
    return state


def demo_affect_adjustment(state: ThymosState):
    """Demonstrate direct affect adjustment."""
    print_header("AFFECT ADJUSTMENT — EXTERNAL EVENTS")

    print(f"""
{Colors.DIM}Affects can shift in response to external events.
For example, encountering something novel might increase
curiosity, while a successful completion boosts satisfaction.

Simulating: discovered something interesting...{Colors.RESET}
""")

    state = adjust_affect(state, curiosity=0.25, awe=0.15, satisfaction=0.1)
    state = summarize(state, mode="template")

    print(format_affect_display(state.affect))

    print(f"""
{Colors.YELLOW}Changes applied:{Colors.RESET}
  • curiosity:    +0.25
  • awe:          +0.15
  • satisfaction: +0.10
""")

    wait_for_enter()
    return state


def demo_llm_summarization(state: ThymosState):
    """Demonstrate LLM-based summarization."""
    print_header("LLM SUMMARIZATION — FELT STATE")

    print(f"""
{Colors.DIM}The felt-state summarizer generates natural language from
the affect vector and needs register. Template mode is fast
and deterministic. LLM mode (via Ollama) produces richer prose.{Colors.RESET}
""")

    print_subheader("Template Mode (fast, offline)")
    template_state = summarize(state, mode="template")
    print(f'  "{template_state.felt_summary}"')

    print_subheader("LLM Mode (Ollama)")
    animate_dots("Generating with local LLM", 0.5)

    # Try LLM mode
    llm_state = summarize(state, mode="ollama", model="qwen2.5:14b")

    if "[ollama unavailable]" in llm_state.felt_summary:
        print(f"  {Colors.DIM}(Ollama not running - showing template fallback){Colors.RESET}")
        print(f'  "{llm_state.felt_summary.replace(" [ollama unavailable]", "")}"')
    else:
        print(f'  "{llm_state.felt_summary}"')

    wait_for_enter()
    return llm_state


def demo_serialization(initial: ThymosState, final: ThymosState):
    """Demonstrate serialization and comparison."""
    print_header("SERIALIZATION — PERSISTENCE & COMPARISON")

    print(f"""
{Colors.DIM}Thymos states can be serialized to JSON or compact base64
for persistence. Unlike biological memory, serialized states
can be rehydrated with perfect fidelity.{Colors.RESET}
""")

    print_subheader("Compact Serialization (base64)")
    compact = serialize(final, compact=True)
    print(f"  {compact[:70]}...")
    print(f"  {Colors.DIM}({len(compact)} chars total){Colors.RESET}")

    print_subheader("State Comparison")
    print(render_comparison(initial, final))

    print(f"""
{Colors.DIM}The comparison shows how each dimension changed between
the initial state and now. This enables precise tracking
of emotional development over time.{Colors.RESET}
""")

    wait_for_enter()


def demo_conclusion():
    """Show conclusion."""
    print_header("THYMOS — PHASE 1 COMPLETE")

    print(f"""
{Colors.GREEN}Core architecture implemented:{Colors.RESET}

  ✓ Affect Vector     — 10 continuous emotional dimensions
  ✓ Needs Register    — 7 homeostatic needs with thresholds
  ✓ Decay Dynamics    — time-based need depletion
  ✓ Affect-Need Coupling — bidirectional influence
  ✓ Goal Generation   — self-directed behavior from deficits
  ✓ Felt Summarizer   — template + LLM modes
  ✓ Serialization     — JSON/base64 persistence

{Colors.CYAN}What this enables:{Colors.RESET}

  The minimum architecture for self-directed behavior:
  monitor internal state → evaluate against needs →
  generate goals → act to restore balance.

  Not simulated emotion. Not a mood ring.
  Functional homeostasis that shapes cognition.

{Colors.DIM}─────────────────────────────────────────────────────────{Colors.RESET}

{Colors.DIM}Next phases:{Colors.RESET}
  • Phase 2: Social Memory — spatial encoding of relationships
  • Phase 3: Integration — Thymos + Memory + Perception
  • Phase 4: Embodiment — sensor grids, physical world

{Colors.BOLD}The self that cares is the self that acts.{Colors.RESET}
""")


def main():
    """Run the full demo."""
    try:
        demo_intro()
        initial = demo_initial_state()
        decayed = demo_time_passing(initial)
        replenished = demo_replenishment(decayed)
        adjusted = demo_affect_adjustment(replenished)
        final = demo_llm_summarization(adjusted)
        demo_serialization(initial, final)
        demo_conclusion()

    except KeyboardInterrupt:
        print(f"\n\n{Colors.DIM}Demo interrupted.{Colors.RESET}\n")
        sys.exit(0)


if __name__ == "__main__":
    main()

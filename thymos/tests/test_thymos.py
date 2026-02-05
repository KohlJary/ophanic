"""Tests for Thymos core functionality."""

import pytest
from datetime import datetime

from thymos import (
    AffectVector,
    Need,
    NeedsRegister,
    ThymosState,
    Goal,
    tick,
    replenish_need,
    adjust_affect,
    simulate,
    generate_goals,
    summarize,
    summarize_templated,
    format_felt_state,
    serialize,
    deserialize,
    compare,
)


class TestAffectVector:
    """Tests for AffectVector."""

    def test_default_values(self):
        """Default values are in valid range."""
        affect = AffectVector()
        for name, value in affect.to_dict().items():
            assert 0.0 <= value <= 1.0, f"{name} out of range"

    def test_clamping(self):
        """Values are clamped to [0, 1]."""
        affect = AffectVector(curiosity=1.5, anxiety=-0.3)
        assert affect.curiosity == 1.0
        assert affect.anxiety == 0.0

    def test_adjust(self):
        """Adjust modifies values correctly."""
        affect = AffectVector(curiosity=0.5)
        affect.adjust(curiosity=0.2, anxiety=0.1)
        assert affect.curiosity == pytest.approx(0.7)
        assert affect.anxiety == pytest.approx(0.3)  # 0.2 default + 0.1

    def test_adjust_clamps(self):
        """Adjust clamps results."""
        affect = AffectVector(curiosity=0.9)
        affect.adjust(curiosity=0.5)
        assert affect.curiosity == 1.0

    def test_dominant(self):
        """Dominant returns top affects."""
        affect = AffectVector(curiosity=0.9, determination=0.8, anxiety=0.1)
        top = affect.dominant(2)
        assert top[0][0] == "curiosity"
        assert top[1][0] == "determination"

    def test_round_trip(self):
        """to_dict/from_dict preserves values."""
        original = AffectVector(curiosity=0.73, anxiety=0.42)
        restored = AffectVector.from_dict(original.to_dict())
        assert restored.curiosity == original.curiosity
        assert restored.anxiety == original.anxiety


class TestNeed:
    """Tests for Need."""

    def test_status_critical(self):
        """Critical status when below threshold."""
        need = Need(name="test", current=0.1, threshold=0.25)
        assert need.status == "critical"

    def test_status_low(self):
        """Low status when below preferred but above threshold."""
        need = Need(name="test", current=0.35, threshold=0.25, preferred_low=0.5)
        assert need.status == "low"

    def test_status_ok(self):
        """OK status when in preferred range."""
        need = Need(name="test", current=0.6, preferred_low=0.5, preferred_high=0.8)
        assert need.status == "ok"

    def test_decay(self):
        """Tick reduces current value."""
        need = Need(name="test", current=0.5, decay_rate=0.1)
        need.tick(1.0)
        assert need.current == 0.4

    def test_decay_floors_at_zero(self):
        """Decay doesn't go negative."""
        need = Need(name="test", current=0.05, decay_rate=0.1)
        need.tick(1.0)
        assert need.current == 0.0

    def test_replenish(self):
        """Replenish increases current."""
        need = Need(name="test", current=0.3)
        need.replenish(0.2)
        # With satiation: 0.2 * (1 - 0.3 * 0.5) = 0.2 * 0.85 = 0.17
        assert 0.45 < need.current < 0.5

    def test_replenish_satiation(self):
        """Replenish has diminishing returns at high values."""
        need_low = Need(name="test", current=0.2)
        need_high = Need(name="test", current=0.8)

        need_low.replenish(0.3)
        need_high.replenish(0.3)

        # High should have gained less
        low_gain = need_low.current - 0.2
        high_gain = need_high.current - 0.8
        assert low_gain > high_gain

    def test_urgency_in_range(self):
        """No urgency when in preferred range."""
        need = Need(name="test", current=0.6, preferred_low=0.5)
        assert need.urgency == 0.0

    def test_urgency_below_preferred(self):
        """Urgency increases below preferred range."""
        need = Need(name="test", current=0.35, threshold=0.25, preferred_low=0.5)
        assert 0 < need.urgency < 1


class TestNeedsRegister:
    """Tests for NeedsRegister."""

    def test_default_creation(self):
        """Creates with all needs."""
        register = NeedsRegister()
        assert hasattr(register, "cognitive_rest")
        assert hasattr(register, "novelty_intake")
        assert len(register.all_needs()) == 7

    def test_tick_all(self):
        """Tick decays all needs."""
        register = NeedsRegister()
        initial = {n.name: n.current for n in register.all_needs()}
        register.tick(1.0)
        for need in register.all_needs():
            assert need.current < initial[need.name]

    def test_deficit_needs(self):
        """Identifies needs below preferred range."""
        register = NeedsRegister()
        register.novelty_intake.current = 0.2
        deficits = register.deficit_needs()
        names = [n.name for n in deficits]
        assert "novelty_intake" in names


class TestThymosState:
    """Tests for ThymosState."""

    def test_default_creation(self):
        """Creates with defaults."""
        state = ThymosState()
        assert state.affect is not None
        assert state.needs is not None
        assert state.timestamp is not None

    def test_copy(self):
        """Copy creates independent state."""
        original = ThymosState()
        original.affect.curiosity = 0.9
        copy = original.copy()
        copy.affect.curiosity = 0.1
        assert original.affect.curiosity == 0.9


class TestDynamics:
    """Tests for dynamics module."""

    def test_tick_decays_needs(self):
        """Tick reduces need values."""
        state = ThymosState()
        initial = state.needs.cognitive_rest.current
        new_state = tick(state, dt=1.0)
        assert new_state.needs.cognitive_rest.current < initial

    def test_tick_immutable(self):
        """Tick doesn't mutate original."""
        state = ThymosState()
        initial = state.needs.cognitive_rest.current
        tick(state, dt=1.0)
        assert state.needs.cognitive_rest.current == initial

    def test_coupling_need_to_affect(self):
        """Low needs affect emotions."""
        state = ThymosState()
        state.needs.novelty_intake.current = 0.1  # Very low
        initial_frustration = state.affect.frustration

        # Tick should apply coupling
        new_state = tick(state, dt=1.0, coupling_strength=1.0)

        # Frustration should increase (low novelty → frustration)
        assert new_state.affect.frustration > initial_frustration

    def test_goal_generation(self):
        """Goals generated for deficit needs."""
        register = NeedsRegister()
        register.novelty_intake.current = 0.15  # Below threshold
        goals = generate_goals(register)
        assert len(goals) > 0
        assert any(g.source_need == "novelty_intake" for g in goals)
        assert any(g.urgent for g in goals)

    def test_replenish_need(self):
        """replenish_need updates specific need."""
        state = ThymosState()
        state.needs.cognitive_rest.current = 0.3
        new_state = replenish_need(state, "cognitive_rest", 0.3)
        assert new_state.needs.cognitive_rest.current > 0.3

    def test_simulate(self):
        """Simulate runs multiple steps."""
        state = ThymosState()
        result = simulate(state, steps=5, dt=1.0)
        assert len(result.states) == 6  # Initial + 5 steps
        assert result.steps == 5
        assert result.total_time == 5.0


class TestSummarizer:
    """Tests for summarizer module."""

    def test_summarize_templated(self):
        """Template summarizer produces output."""
        state = ThymosState()
        state.affect.curiosity = 0.8
        summary = summarize_templated(state)
        assert len(summary) > 0
        assert "curious" in summary.lower()

    def test_summarize_with_deficit(self):
        """Summary mentions deficit needs."""
        state = ThymosState()
        state.needs.novelty_intake.current = 0.15
        state.active_goals = generate_goals(state.needs)
        summary = summarize_templated(state)
        # Should mention novelty or new
        assert "novel" in summary.lower() or "new" in summary.lower()

    def test_format_felt_state(self):
        """format_felt_state produces display."""
        state = ThymosState()
        state.felt_summary = "Test summary."
        display = format_felt_state(state)
        assert "AFFECT VECTOR" in display
        assert "NEEDS REGISTER" in display
        assert "FELT STATE" in display


class TestSerialization:
    """Tests for serialization module."""

    def test_serialize_deserialize(self):
        """Round-trip preserves state."""
        original = ThymosState()
        original.affect.curiosity = 0.73
        original.needs.cognitive_rest.current = 0.42
        original.felt_summary = "Test summary"
        original.context = "test context"

        json_str = serialize(original)
        restored = deserialize(json_str)

        assert abs(restored.affect.curiosity - 0.73) < 0.001
        assert abs(restored.needs.cognitive_rest.current - 0.42) < 0.001
        assert restored.felt_summary == "Test summary"
        assert restored.context == "test context"

    def test_serialize_compact(self):
        """Compact serialization produces base64."""
        state = ThymosState()
        compact = serialize(state, compact=True)
        # Base64 doesn't have spaces or braces
        assert " " not in compact
        assert "{" not in compact

    def test_deserialize_compact(self):
        """Can deserialize compact format."""
        state = ThymosState()
        state.affect.curiosity = 0.88
        compact = serialize(state, compact=True)
        restored = deserialize(compact)
        assert abs(restored.affect.curiosity - 0.88) < 0.001

    def test_compare(self):
        """Compare produces delta information."""
        then = ThymosState()
        then.affect.curiosity = 0.3
        now = ThymosState()
        now.affect.curiosity = 0.8

        result = compare(then, now)
        assert result["affect_delta"]["curiosity"] == pytest.approx(0.5, abs=0.01)


class TestIntegration:
    """Integration tests for complete workflows."""

    def test_full_cycle(self):
        """Complete cycle: create → tick → summarize → serialize."""
        # Create initial state
        state = ThymosState(context="Integration test")

        # Simulate some time passing
        state = tick(state, dt=2.0)

        # Replenish a need
        state = replenish_need(state, "novelty_intake", 0.3)

        # Generate summary
        state = summarize(state)
        assert len(state.felt_summary) > 0

        # Serialize and restore
        json_str = serialize(state)
        restored = deserialize(json_str)

        assert restored.context == "Integration test"
        assert len(restored.felt_summary) > 0

    def test_prolonged_decay(self):
        """Extended simulation shows expected behavior."""
        state = ThymosState()
        result = simulate(state, steps=20, dt=1.0)

        # After 20 time units, needs should be depleted
        final = result.final_state
        assert final.needs.cognitive_rest.current < 0.5  # Decayed significantly

        # Should have goals generated
        assert len(final.active_goals) > 0

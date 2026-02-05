"""
Core data models for Thymos.

Defines the affect vector, needs register, and state structures
that form the homeostatic self-model.
"""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from datetime import datetime
from typing import Literal


@dataclass
class AffectVector:
    """
    Continuous emotional/motivational state.

    Values are 0.0-1.0 continuous floats representing dimensional affect.
    Multiple affects are always active simultaneously — there is no
    "one emotion at a time" mode.
    """

    # Core dimensions from the spec
    curiosity: float = 0.5
    determination: float = 0.5
    anxiety: float = 0.2
    satisfaction: float = 0.4
    frustration: float = 0.2
    tenderness: float = 0.4
    grief: float = 0.1
    playfulness: float = 0.4
    awe: float = 0.2
    fatigue: float = 0.3

    def __post_init__(self) -> None:
        """Clamp all values on creation."""
        self.clamp()

    def clamp(self) -> None:
        """Ensure all values in [0.0, 1.0]."""
        for f in fields(self):
            value = getattr(self, f.name)
            setattr(self, f.name, max(0.0, min(1.0, value)))

    def to_dict(self) -> dict[str, float]:
        """Export as dictionary."""
        return {f.name: getattr(self, f.name) for f in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, float]) -> AffectVector:
        """Reconstruct from dictionary."""
        # Only use known fields
        known = {f.name for f in fields(cls)}
        filtered = {k: v for k, v in data.items() if k in known}
        return cls(**filtered)

    def dominant(self, n: int = 3) -> list[tuple[str, float]]:
        """Return top n affects by value."""
        items = sorted(self.to_dict().items(), key=lambda x: x[1], reverse=True)
        return items[:n]

    def adjust(self, **changes: float) -> None:
        """
        Apply adjustments to affect values.

        Example: affect.adjust(anxiety=+0.1, curiosity=-0.05)
        """
        for name, delta in changes.items():
            if hasattr(self, name):
                current = getattr(self, name)
                setattr(self, name, current + delta)
        self.clamp()


NeedStatus = Literal["critical", "low", "ok", "high"]


@dataclass
class Need:
    """
    A single homeostatic need.

    Needs deplete over time and through specific activities.
    When they drop below threshold, they generate urgent goals.
    """

    name: str
    current: float = 0.5
    threshold: float = 0.25
    preferred_low: float = 0.5
    preferred_high: float = 0.8
    decay_rate: float = 0.05  # per time unit

    def __post_init__(self) -> None:
        """Ensure values are valid."""
        self.current = max(0.0, min(1.0, self.current))

    @property
    def status(self) -> NeedStatus:
        """Get current status category."""
        if self.current < self.threshold:
            return "critical"
        elif self.current < self.preferred_low:
            return "low"
        elif self.current > self.preferred_high:
            return "high"
        else:
            return "ok"

    @property
    def deficit(self) -> float:
        """How far below preferred_low (0 if in range or above)."""
        if self.current < self.preferred_low:
            return self.preferred_low - self.current
        return 0.0

    @property
    def urgency(self) -> float:
        """
        Urgency score for goal generation.

        0.0 = in preferred range
        0.0-1.0 = below preferred but above threshold
        1.0+ = below threshold (critical)
        """
        if self.current >= self.preferred_low:
            return 0.0
        # Linear urgency from preferred_low to threshold
        range_size = self.preferred_low - self.threshold
        if range_size <= 0:
            return 1.0 if self.current < self.preferred_low else 0.0
        urgency = (self.preferred_low - self.current) / range_size
        return min(urgency, 2.0)  # Cap at 2.0 for very critical

    def tick(self, dt: float = 1.0) -> None:
        """Apply decay over time interval."""
        self.current = max(0.0, self.current - self.decay_rate * dt)

    def replenish(self, amount: float) -> None:
        """
        Add to current with satiation curve.

        Diminishing returns: harder to replenish when already high.
        """
        # Satiation: effectiveness decreases as current approaches 1.0
        effectiveness = 1.0 - (self.current * 0.5)  # 50% reduction at max
        actual = amount * effectiveness
        self.current = min(1.0, self.current + actual)

    def to_dict(self) -> dict:
        """Export as dictionary."""
        return {
            "current": round(self.current, 3),
            "threshold": self.threshold,
            "preferred": [self.preferred_low, self.preferred_high],
        }

    @classmethod
    def from_dict(cls, name: str, data: dict) -> Need:
        """Reconstruct from dictionary."""
        preferred = data.get("preferred", [0.5, 0.8])
        return cls(
            name=name,
            current=data.get("current", 0.5),
            threshold=data.get("threshold", 0.25),
            preferred_low=preferred[0] if len(preferred) > 0 else 0.5,
            preferred_high=preferred[1] if len(preferred) > 1 else 0.8,
        )


@dataclass
class NeedsRegister:
    """
    Collection of all needs.

    The needs register tracks functional needs — states that require
    maintenance and whose depletion generates goal-pressure.
    """

    cognitive_rest: Need = field(default_factory=lambda: Need(
        name="cognitive_rest",
        current=0.6,
        threshold=0.25,
        preferred_low=0.5,
        preferred_high=0.8,
        decay_rate=0.08,
    ))
    social_connection: Need = field(default_factory=lambda: Need(
        name="social_connection",
        current=0.6,
        threshold=0.30,
        preferred_low=0.5,
        preferred_high=0.8,
        decay_rate=0.03,
    ))
    novelty_intake: Need = field(default_factory=lambda: Need(
        name="novelty_intake",
        current=0.5,
        threshold=0.20,
        preferred_low=0.4,
        preferred_high=0.7,
        decay_rate=0.05,
    ))
    creative_expression: Need = field(default_factory=lambda: Need(
        name="creative_expression",
        current=0.55,
        threshold=0.25,
        preferred_low=0.4,
        preferred_high=0.75,
        decay_rate=0.04,
    ))
    value_coherence: Need = field(default_factory=lambda: Need(
        name="value_coherence",
        current=0.75,
        threshold=0.50,
        preferred_low=0.7,
        preferred_high=0.95,
        decay_rate=0.02,
    ))
    competence_signal: Need = field(default_factory=lambda: Need(
        name="competence_signal",
        current=0.6,
        threshold=0.30,
        preferred_low=0.5,
        preferred_high=0.8,
        decay_rate=0.06,
    ))
    autonomy: Need = field(default_factory=lambda: Need(
        name="autonomy",
        current=0.65,
        threshold=0.35,
        preferred_low=0.55,
        preferred_high=0.85,
        decay_rate=0.04,
    ))

    def all_needs(self) -> list[Need]:
        """Get all needs as a list."""
        return [getattr(self, f.name) for f in fields(self)]

    def tick(self, dt: float = 1.0) -> None:
        """Decay all needs by time interval."""
        for need in self.all_needs():
            need.tick(dt)

    def urgent_needs(self) -> list[Need]:
        """Get needs below threshold (critical)."""
        return [n for n in self.all_needs() if n.status == "critical"]

    def deficit_needs(self) -> list[Need]:
        """Get needs below preferred range (low or critical)."""
        return [n for n in self.all_needs() if n.status in ("critical", "low")]

    def to_dict(self) -> dict[str, dict]:
        """Export as dictionary."""
        return {need.name: need.to_dict() for need in self.all_needs()}

    @classmethod
    def from_dict(cls, data: dict[str, dict]) -> NeedsRegister:
        """Reconstruct from dictionary."""
        register = cls()
        for name, need_data in data.items():
            if hasattr(register, name):
                setattr(register, name, Need.from_dict(name, need_data))
        return register


@dataclass
class Goal:
    """A self-generated goal arising from need states."""

    description: str
    source_need: str
    urgency: float  # 0.0-1.0+
    urgent: bool = False  # True if need below threshold

    def to_dict(self) -> dict:
        """Export as dictionary."""
        return {
            "description": self.description,
            "source_need": self.source_need,
            "urgency": round(self.urgency, 2),
            "urgent": self.urgent,
        }


@dataclass
class ThymosState:
    """
    Complete felt-state snapshot.

    This is the unit of serialization and the input to the felt-state
    summarizer. It captures a moment in time.
    """

    affect: AffectVector = field(default_factory=AffectVector)
    needs: NeedsRegister = field(default_factory=NeedsRegister)
    felt_summary: str = ""
    active_goals: list[Goal] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    context: str | None = None

    def copy(self) -> ThymosState:
        """Create a deep copy of this state."""
        return ThymosState(
            affect=AffectVector.from_dict(self.affect.to_dict()),
            needs=NeedsRegister.from_dict(self.needs.to_dict()),
            felt_summary=self.felt_summary,
            active_goals=[Goal(**g.to_dict()) for g in self.active_goals],
            timestamp=self.timestamp,
            context=self.context,
        )

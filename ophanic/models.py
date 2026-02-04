"""IR data models for Ophanic parser."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Direction(str, Enum):
    """Layout direction for containers."""

    ROW = "row"
    COLUMN = "column"


class NodeType(str, Enum):
    """Type of layout node."""

    CONTAINER = "container"
    COMPONENT_REF = "component_ref"
    LABEL = "label"


@dataclass
class BoundingBox:
    """Character grid coordinates for a box."""

    top: int  # Line number (0-indexed)
    left: int  # Column number (0-indexed)
    bottom: int
    right: int

    @property
    def width(self) -> int:
        """Width in characters."""
        return self.right - self.left + 1

    @property
    def height(self) -> int:
        """Height in lines."""
        return self.bottom - self.top + 1

    @property
    def area(self) -> int:
        """Area in character cells."""
        return self.width * self.height

    def contains(self, other: BoundingBox) -> bool:
        """Check if this box fully contains another box."""
        return (
            self.top < other.top
            and self.left < other.left
            and self.bottom > other.bottom
            and self.right > other.right
        )

    def to_dict(self) -> dict[str, int]:
        return {
            "top": self.top,
            "left": self.left,
            "bottom": self.bottom,
            "right": self.right,
        }


@dataclass
class Proportion:
    """Represents proportional sizing."""

    value: float  # e.g., 0.65 for 65%
    char_count: int  # Original character count (for debugging)

    def to_dict(self) -> dict[str, Any]:
        return {"value": self.value, "char_count": self.char_count}


@dataclass
class LayoutNode:
    """A node in the layout tree."""

    type: NodeType
    name: str | None = None  # Label text or component name
    direction: Direction | None = None  # For containers only
    width_proportion: Proportion | None = None
    height_proportion: Proportion | None = None
    children: list[LayoutNode] = field(default_factory=list)
    source_bounds: BoundingBox | None = None  # For error messages/debugging

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {"type": self.type.value}
        if self.name:
            result["name"] = self.name
        if self.direction:
            result["direction"] = self.direction.value
        if self.width_proportion:
            result["width"] = self.width_proportion.to_dict()
        if self.height_proportion:
            result["height"] = self.height_proportion.to_dict()
        if self.children:
            result["children"] = [c.to_dict() for c in self.children]
        return result


@dataclass
class BreakpointLayout:
    """Layout for a specific breakpoint."""

    breakpoint: str  # e.g., "desktop", "tablet", "mobile"
    root: LayoutNode

    def to_dict(self) -> dict[str, Any]:
        return {
            "breakpoint": self.breakpoint,
            "layout": self.root.to_dict(),
        }


@dataclass
class ComponentDefinition:
    """A reusable component with state variants."""

    name: str
    states: dict[str, LayoutNode] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "states": {k: v.to_dict() for k, v in self.states.items()},
        }


@dataclass
class OphanicDocument:
    """The complete parsed document."""

    title: str | None = None
    breakpoints: list[BreakpointLayout] = field(default_factory=list)
    components: list[ComponentDefinition] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "breakpoints": [b.to_dict() for b in self.breakpoints],
            "components": [c.to_dict() for c in self.components],
        }

    def to_json(self, **kwargs: Any) -> str:
        import json

        return json.dumps(self.to_dict(), **kwargs)

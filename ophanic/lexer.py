"""Document segmentation for Ophanic files."""

from __future__ import annotations

from dataclasses import dataclass, field

# Box-drawing characters used in diagrams
BOX_CHARS = set("┌┐└┘─│├┤┬┴┼")


def has_box_chars(line: str) -> bool:
    """Check if a line contains box-drawing characters."""
    return any(c in BOX_CHARS for c in line)


@dataclass
class DiagramSection:
    """A section of diagram content."""

    tag: str  # e.g., "desktop", "default", "hover"
    lines: list[tuple[int, str]] = field(default_factory=list)  # (line_num, content)
    start_line: int = 0

    def add_line(self, line_num: int, content: str) -> None:
        if not self.lines:
            self.start_line = line_num
        self.lines.append((line_num, content))

    def get_content(self) -> list[str]:
        """Get just the line content without line numbers."""
        return [content for _, content in self.lines]


@dataclass
class BreakpointSection:
    """A top-level breakpoint section."""

    name: str  # e.g., "desktop", "tablet", "mobile"
    diagrams: list[DiagramSection] = field(default_factory=list)

    def add_diagram(self, tag: str) -> DiagramSection:
        diagram = DiagramSection(tag=tag)
        self.diagrams.append(diagram)
        return diagram


@dataclass
class ComponentSection:
    """A component definition section."""

    name: str  # e.g., "MetricCard", "ActivityFeed"
    states: list[DiagramSection] = field(default_factory=list)

    def add_state(self, tag: str) -> DiagramSection:
        state = DiagramSection(tag=tag)
        self.states.append(state)
        return state


@dataclass
class DocumentSegments:
    """Segmented document ready for parsing."""

    title: str | None = None
    breakpoints: list[BreakpointSection] = field(default_factory=list)
    components: list[ComponentSection] = field(default_factory=list)
    _has_content: bool = field(default=False, repr=False)

    @property
    def has_content(self) -> bool:
        return self._has_content


def segment_document(text: str) -> DocumentSegments:
    """Split document into sections by markers.

    Markers:
    - `# Title` at start = document title
    - `@breakpoint` = top-level breakpoint section
    - `## ◆ComponentName` = component definition
    - `@state` within component = state variant
    - `# comment` = ignored (after content starts)
    """
    segments = DocumentSegments()
    lines = text.split("\n")

    current_breakpoint: BreakpointSection | None = None
    current_component: ComponentSection | None = None
    current_diagram: DiagramSection | None = None

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Title detection (only at very start, before any content)
        if not segments._has_content and stripped.startswith("# ") and not stripped.startswith("## "):
            # Make sure it's not a comment after content
            potential_title = stripped[2:].strip()
            # Check if this looks like a title (no @, no box chars)
            if not potential_title.startswith("@") and not has_box_chars(potential_title):
                segments.title = potential_title
                continue

        # Component definition: ## ◆ComponentName
        if stripped.startswith("## ◆"):
            component_name = stripped[4:].strip()
            current_component = ComponentSection(name=component_name)
            segments.components.append(current_component)
            current_breakpoint = None  # Exit breakpoint context
            current_diagram = None
            segments._has_content = True
            continue

        # Breakpoint/state tag: @tag
        if stripped.startswith("@"):
            tag = stripped[1:].split()[0]  # Handle @hover [transition: ...]
            segments._has_content = True

            if current_component is not None:
                # State within component
                current_diagram = current_component.add_state(tag)
            else:
                # Top-level breakpoint
                current_breakpoint = BreakpointSection(name=tag)
                segments.breakpoints.append(current_breakpoint)
                current_diagram = current_breakpoint.add_diagram(tag)
            continue

        # Comment line (after content has started)
        if stripped.startswith("#"):
            continue  # Skip comments

        # Empty line
        if not stripped:
            continue

        # Diagram content (lines with box chars or content within a diagram)
        if current_diagram is not None:
            if has_box_chars(line) or line.strip():
                current_diagram.add_line(i, line)
                segments._has_content = True

    return segments

"""Figma adapter: Import Figma designs to Ophanic IR and diagrams.

This module handles:
- Figma REST API authentication and file fetching
- Converting Figma auto-layout frames to Ophanic IR
- Extracting proportions from FILL sizing and layoutGrow
- Component instance detection
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from typing import Any
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import json

from ..models import (
    Direction,
    LayoutNode,
    NodeType,
    OphanicDocument,
    BreakpointLayout,
    Proportion,
)
from .react_reverse import DiagramGenerator, ReverseOptions


FIGMA_API_BASE = "https://api.figma.com/v1"


@dataclass
class FigmaOptions:
    """Options for Figma import."""

    token: str | None = None  # Personal access token (or from FIGMA_TOKEN env)
    depth: int | None = None  # Limit traversal depth (None = full tree)
    node_ids: list[str] = field(default_factory=list)  # Specific nodes to fetch
    include_pages: list[str] = field(default_factory=list)  # Filter by page names
    diagram_width: int = 80


class FigmaAPIError(Exception):
    """Error from Figma API."""

    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message
        super().__init__(f"Figma API error ({status}): {message}")


class FigmaClient:
    """Client for Figma REST API."""

    def __init__(self, token: str | None = None):
        self.token = token or os.environ.get("FIGMA_TOKEN")
        if not self.token:
            raise ValueError(
                "Figma token required. Set FIGMA_TOKEN env var or pass token parameter."
            )

    def get_file(
        self,
        file_key: str,
        depth: int | None = None,
        node_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        """Fetch a Figma file.

        Args:
            file_key: The file key from the Figma URL
            depth: Limit traversal depth (1=pages only, 2=pages+top-level, etc.)
            node_ids: Specific node IDs to fetch (comma-separated in API)

        Returns:
            Figma file JSON response
        """
        url = f"{FIGMA_API_BASE}/files/{file_key}"

        params = []
        if depth is not None:
            params.append(f"depth={depth}")
        if node_ids:
            params.append(f"ids={','.join(node_ids)}")

        if params:
            url += "?" + "&".join(params)

        return self._request(url)

    def get_node(self, file_key: str, node_id: str) -> dict[str, Any]:
        """Fetch a specific node from a Figma file.

        Args:
            file_key: The file key from the Figma URL
            node_id: The node ID to fetch

        Returns:
            Node data from the nodes endpoint
        """
        url = f"{FIGMA_API_BASE}/files/{file_key}/nodes?ids={node_id}"
        return self._request(url)

    def _request(self, url: str) -> dict[str, Any]:
        """Make an authenticated request to the Figma API."""
        req = Request(url)
        req.add_header("X-Figma-Token", self.token or "")

        try:
            with urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as e:
            body = e.read().decode("utf-8") if e.fp else str(e)
            raise FigmaAPIError(e.code, body) from e


def extract_file_key(url_or_key: str) -> str:
    """Extract file key from a Figma URL or return as-is if already a key.

    Handles URLs like:
    - https://www.figma.com/file/abc123XYZ/MyDesign
    - https://www.figma.com/design/abc123XYZ/MyDesign
    - abc123XYZ (already a key)
    """
    # Check if it's a URL
    match = re.search(r"figma\.com/(?:file|design)/([a-zA-Z0-9]+)", url_or_key)
    if match:
        return match.group(1)

    # Assume it's already a file key
    return url_or_key


def figma_to_ophanic(
    file_key_or_url: str,
    options: FigmaOptions | None = None,
) -> OphanicDocument:
    """Convert a Figma file to an Ophanic document.

    Args:
        file_key_or_url: Figma file key or URL
        options: Import options

    Returns:
        OphanicDocument with layout structure
    """
    if options is None:
        options = FigmaOptions()

    file_key = extract_file_key(file_key_or_url)
    client = FigmaClient(token=options.token)

    # Fetch the file
    file_data = client.get_file(
        file_key,
        depth=options.depth,
        node_ids=options.node_ids if options.node_ids else None,
    )

    # Convert to Ophanic
    converter = FigmaConverter(options)
    return converter.convert(file_data)


def figma_to_diagram(
    file_key_or_url: str,
    options: FigmaOptions | None = None,
) -> str:
    """Convert a Figma file directly to an Ophanic diagram.

    Args:
        file_key_or_url: Figma file key or URL
        options: Import options

    Returns:
        .ophanic file content
    """
    if options is None:
        options = FigmaOptions()

    doc = figma_to_ophanic(file_key_or_url, options)

    reverse_options = ReverseOptions(diagram_width=options.diagram_width)
    generator = DiagramGenerator(reverse_options)
    return generator.generate(doc)


class FigmaConverter:
    """Converts Figma file data to Ophanic IR."""

    # Node types that represent layout containers
    CONTAINER_TYPES = {"FRAME", "COMPONENT", "COMPONENT_SET", "SECTION", "GROUP"}

    # Node types to skip (non-layout elements)
    SKIP_TYPES = {"VECTOR", "BOOLEAN_OPERATION", "STAR", "LINE", "ELLIPSE", "POLYGON", "SLICE"}

    def __init__(self, options: FigmaOptions):
        self.options = options
        self.components: dict[str, dict] = {}  # componentId -> component node

    def convert(self, file_data: dict[str, Any]) -> OphanicDocument:
        """Convert Figma file data to OphanicDocument."""
        doc = OphanicDocument()
        doc.title = file_data.get("name", "Untitled")

        # Store component definitions for instance resolution
        if "components" in file_data:
            self.components = file_data["components"]

        # Process document
        document = file_data.get("document", {})
        pages = document.get("children", [])

        # Filter pages if specified
        if self.options.include_pages:
            pages = [
                p for p in pages
                if p.get("name") in self.options.include_pages
            ]

        # Process each page
        for page in pages:
            page_name = page.get("name", "Page")

            # Get top-level frames from the page
            for child in page.get("children", []):
                if child.get("type") in self.CONTAINER_TYPES:
                    layout = self._convert_node(child)
                    if layout:
                        # Use frame name as breakpoint identifier
                        bp_name = self._to_breakpoint_name(child.get("name", "default"))
                        doc.breakpoints.append(
                            BreakpointLayout(breakpoint=bp_name, root=layout)
                        )

        return doc

    def _convert_node(self, node: dict[str, Any]) -> LayoutNode | None:
        """Convert a Figma node to a LayoutNode."""
        node_type = node.get("type", "")

        # Skip non-layout nodes
        if node_type in self.SKIP_TYPES:
            return None

        # Handle component instances
        if node_type == "INSTANCE":
            component_id = node.get("componentId")
            component_name = self._get_component_name(component_id, node)
            return LayoutNode(
                type=NodeType.COMPONENT_REF,
                name=component_name,
            )

        # Handle text nodes as labels
        if node_type == "TEXT":
            characters = node.get("characters", "")
            if characters.strip():
                return LayoutNode(
                    type=NodeType.LABEL,
                    name=self._truncate(characters, 30),
                )
            return None

        # Handle rectangles and other shapes as simple containers
        if node_type == "RECTANGLE":
            name = node.get("name", "")
            if name and not name.startswith("Rectangle"):
                return LayoutNode(type=NodeType.LABEL, name=self._truncate(name, 30))
            return None

        # Handle containers (FRAME, COMPONENT, GROUP, etc.)
        if node_type in self.CONTAINER_TYPES:
            return self._convert_container(node)

        return None

    def _convert_container(self, node: dict[str, Any]) -> LayoutNode:
        """Convert a container node (FRAME, COMPONENT, etc.) to a LayoutNode."""
        layout_mode = node.get("layoutMode", "NONE")

        # Determine direction
        if layout_mode == "HORIZONTAL":
            direction = Direction.ROW
        elif layout_mode == "VERTICAL":
            direction = Direction.COLUMN
        else:
            # No auto-layout - try to infer from children positions
            direction = self._infer_direction(node)

        # Create container node
        container = LayoutNode(
            type=NodeType.CONTAINER,
            direction=direction,
        )

        # Process children
        children = node.get("children", [])
        if children:
            child_nodes = []
            for child in children:
                # Skip absolutely positioned children in auto-layout
                if child.get("layoutPositioning") == "ABSOLUTE":
                    continue

                child_node = self._convert_node(child)
                if child_node:
                    # Calculate proportion for FILL children
                    self._apply_proportions(child, child_node, direction)
                    child_nodes.append(child_node)

            container.children = child_nodes

            # Normalize FILL proportions among siblings
            self._normalize_fill_proportions(container)

        # If container has no children and has a meaningful name, make it a label
        if not container.children:
            name = node.get("name", "")
            if name and not self._is_generic_name(name):
                return LayoutNode(
                    type=NodeType.LABEL,
                    name=self._truncate(name, 30),
                )

        return container

    def _apply_proportions(
        self,
        figma_node: dict[str, Any],
        layout_node: LayoutNode,
        parent_direction: Direction | None,
    ) -> None:
        """Apply width/height proportions based on Figma sizing."""
        h_sizing = figma_node.get("layoutSizingHorizontal", "FIXED")
        v_sizing = figma_node.get("layoutSizingVertical", "FIXED")
        layout_grow = figma_node.get("layoutGrow", 0)

        # For row layouts, horizontal sizing matters
        if parent_direction == Direction.ROW:
            if h_sizing == "FILL":
                # Use layoutGrow as relative weight (default to 1 if FILL but no grow)
                grow = layout_grow if layout_grow > 0 else 1
                layout_node.width_proportion = Proportion(
                    value=grow,  # Will be normalized later
                    char_count=int(grow),
                )
            elif h_sizing == "FIXED":
                # Could use absolute width, but for now just mark as fixed
                width = figma_node.get("absoluteBoundingBox", {}).get("width", 0)
                if width > 0:
                    layout_node.width_proportion = Proportion(
                        value=width,
                        char_count=int(width),
                    )

        # For column layouts, vertical sizing matters
        if parent_direction == Direction.COLUMN:
            if v_sizing == "FILL":
                grow = layout_grow if layout_grow > 0 else 1
                layout_node.height_proportion = Proportion(
                    value=grow,
                    char_count=int(grow),
                )

    def _normalize_fill_proportions(self, container: LayoutNode) -> None:
        """Normalize FILL proportions among siblings to sum to 1.0."""
        if not container.children:
            return

        if container.direction == Direction.ROW:
            # Normalize width proportions
            fill_children = [
                c for c in container.children
                if c.width_proportion is not None
            ]
            if fill_children:
                total = sum(c.width_proportion.value for c in fill_children if c.width_proportion)
                if total > 0:
                    for child in fill_children:
                        if child.width_proportion:
                            child.width_proportion = Proportion(
                                value=child.width_proportion.value / total,
                                char_count=int(child.width_proportion.value),
                            )

        elif container.direction == Direction.COLUMN:
            # Normalize height proportions
            fill_children = [
                c for c in container.children
                if c.height_proportion is not None
            ]
            if fill_children:
                total = sum(c.height_proportion.value for c in fill_children if c.height_proportion)
                if total > 0:
                    for child in fill_children:
                        if child.height_proportion:
                            child.height_proportion = Proportion(
                                value=child.height_proportion.value / total,
                                char_count=int(child.height_proportion.value),
                            )

    def _infer_direction(self, node: dict[str, Any]) -> Direction | None:
        """Infer layout direction from children positions when no auto-layout."""
        children = node.get("children", [])
        if len(children) < 2:
            return Direction.ROW  # Default

        # Get bounding boxes
        boxes = []
        for child in children[:4]:  # Check first few children
            bbox = child.get("absoluteBoundingBox")
            if bbox:
                boxes.append(bbox)

        if len(boxes) < 2:
            return Direction.ROW

        # Check if children are arranged horizontally or vertically
        # by comparing position variance
        x_positions = [b["x"] for b in boxes]
        y_positions = [b["y"] for b in boxes]

        x_variance = max(x_positions) - min(x_positions)
        y_variance = max(y_positions) - min(y_positions)

        # If more horizontal spread, it's a row; otherwise column
        if x_variance > y_variance:
            return Direction.ROW
        else:
            return Direction.COLUMN

    def _get_component_name(
        self,
        component_id: str | None,
        instance_node: dict[str, Any],
    ) -> str:
        """Get the name for a component instance."""
        # First try the instance's own name
        instance_name = instance_node.get("name", "")

        # Try to get from components map
        if component_id and component_id in self.components:
            comp = self.components[component_id]
            return comp.get("name", instance_name or "Component")

        # Fall back to instance name or generic
        return instance_name or "Component"

    def _to_breakpoint_name(self, name: str) -> str:
        """Convert a frame name to a breakpoint identifier."""
        # Common patterns
        name_lower = name.lower()

        if any(k in name_lower for k in ["mobile", "phone", "sm", "small"]):
            return "mobile"
        if any(k in name_lower for k in ["tablet", "md", "medium", "ipad"]):
            return "tablet"
        if any(k in name_lower for k in ["desktop", "lg", "large", "web"]):
            return "desktop"

        # Clean up the name for use as breakpoint
        clean = re.sub(r"[^a-zA-Z0-9]+", "-", name.lower()).strip("-")
        return clean or "default"

    def _is_generic_name(self, name: str) -> bool:
        """Check if a name is generic (auto-generated by Figma)."""
        generic_patterns = [
            r"^Frame\s*\d*$",
            r"^Group\s*\d*$",
            r"^Rectangle\s*\d*$",
            r"^Component\s*\d*$",
            r"^Instance\s*\d*$",
        ]
        return any(re.match(p, name) for p in generic_patterns)

    def _truncate(self, text: str, max_len: int) -> str:
        """Truncate text at word boundary."""
        text = " ".join(text.split())  # Normalize whitespace
        if len(text) <= max_len:
            return text
        truncate_at = max_len - 3
        last_space = text[:truncate_at].rfind(" ")
        if last_space > truncate_at // 2:
            return text[:last_space] + "..."
        return text[:truncate_at] + "..."

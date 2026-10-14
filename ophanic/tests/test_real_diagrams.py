"""Regression tests: parse real diagrams from the repo and check the tree shape."""

from pathlib import Path

import pytest

from ophanic import parse_file
from ophanic.models import Direction, NodeType

REPO = Path(__file__).parent.parent.parent
BOX_DRAWING = {chr(c) for c in range(0x2500, 0x2580)}


def shape(node):
    """Compact structural summary: names for leaves, (direction, [children]) for containers."""
    if not node.children:
        return node.name
    return (node.direction.value, [shape(c) for c in node.children])


def breakpoint(doc, name):
    return next(bp.root for bp in doc.breakpoints if bp.breakpoint == name)


def all_nodes(node):
    yield node
    for c in node.children:
        yield from all_nodes(c)


class TestABDashboard:
    @pytest.fixture
    def doc(self):
        return parse_file(REPO / "ab-test" / "dashboard.ophanic")

    def test_desktop_structure(self, doc):
        root = breakpoint(doc, "desktop")
        assert shape(root) == (
            "column",
            [
                "LOGO                                                      🔔[3]  ◯avatar",
                (
                    "row",
                    [
                        "SIDEBAR",
                        (
                            "column",
                            [
                                ("row", ["MetricCard", "MetricCard", "MetricCard"]),
                                ("row", ["CHART", "ActivityFeed"]),
                                ("row", ["TABLE", "Calendar"]),
                            ],
                        ),
                    ],
                ),
            ],
        )

    def test_desktop_proportions(self, doc):
        root = breakpoint(doc, "desktop")
        main = root.children[1]
        sidebar, content = main.children
        assert sidebar.width_proportion.value < 0.3 < content.width_proportion.value
        chart, feed = content.children[1].children
        assert chart.width_proportion.value == pytest.approx(0.65, abs=0.03)
        table, calendar = content.children[2].children
        assert table.width_proportion.value == pytest.approx(0.70, abs=0.03)

    def test_tablet_structure(self, doc):
        # The 📊 icon column is emoji (2 display columns), so string indices
        # drift from visual columns on those lines; borders must still line up.
        root = breakpoint(doc, "tablet")
        header, main = root.children
        assert header.name.startswith("LOGO")
        assert main.direction == Direction.ROW
        icons, content = main.children
        assert icons.name.startswith("📊")
        assert shape(content) == (
            "column",
            [
                ("row", ["MetricCard", "MetricCard", "MetricCard"]),
                ("row", ["CHART", "ActivityFeed"]),
            ],
        )

    def test_mobile_structure(self, doc):
        root = breakpoint(doc, "mobile")
        assert root.direction == Direction.COLUMN
        assert [c.name for c in root.children][1:6] == [
            "MetricCard", "MetricCard", "MetricCard", "CHART", "ActivityFeed",
        ]
        assert root.children[-1].name == "📊    📈    📋    ⚙️"

    def test_metric_card_icon_beside_text(self, doc):
        card = next(c for c in doc.components if c.name == "MetricCard")
        assert shape(card.states["default"]) == ("row", ["📈", "label"])

def test_admin_dashboard_has_no_box_drawing_labels():
    doc = parse_file(REPO / "layouts" / "admin-frontend" / "dashboard.oph")
    root = doc.breakpoints[0].root
    names = [n.name for n in all_nodes(root) if n.name]
    assert all(not (set(name) & BOX_DRAWING) for name in names), names


@pytest.mark.parametrize(
    "path",
    sorted((REPO / "layouts").rglob("*.oph")) + [REPO / "ab-test" / "dashboard.ophanic"],
    ids=lambda p: str(p.relative_to(REPO)),
)
def test_labels_never_contain_box_drawing(path):
    doc = parse_file(path)
    roots = [bp.root for bp in doc.breakpoints] + [
        st for c in doc.components for st in c.states.values()
    ]
    for root in filter(None, roots):
        for node in all_nodes(root):
            if node.type in (NodeType.LABEL, NodeType.COMPONENT_REF) and node.name:
                assert not (set(node.name) & BOX_DRAWING), node.name

"""
Tests for Widget base class.

Widget is the base class for all UI elements.

Layer: 6 (UI)
"""

from core.object import Object
from core.guid import GUID
from core.reflection import get_properties
from ui.widget import Widget


class TestWidgetInheritance:
    """Test that Widget inherits from Object."""

    def test_widget_is_object(self):
        """Widget should be an instance of Object."""
        widget = Widget()
        assert isinstance(widget, Object)

    def test_widget_has_guid(self):
        """Widget should have a GUID."""
        widget = Widget()
        assert hasattr(widget, "guid")
        assert isinstance(widget.guid, GUID)

    def test_widget_has_name(self):
        """Widget should have a name."""
        widget = Widget(name="TestWidget")
        assert widget.name == "TestWidget"


class TestWidgetPosition:
    """Test Widget position."""

    def test_widget_has_x(self):
        """Widget should have x property."""
        widget = Widget()
        assert hasattr(widget, "x")

    def test_widget_has_y(self):
        """Widget should have y property."""
        widget = Widget()
        assert hasattr(widget, "y")

    def test_position_defaults_to_zero(self):
        """Position should default to (0, 0)."""
        widget = Widget()
        assert widget.x == 0
        assert widget.y == 0

    def test_position_can_be_set(self):
        """Position can be set."""
        widget = Widget()
        widget.x = 100
        widget.y = 200
        assert widget.x == 100
        assert widget.y == 200


class TestWidgetSize:
    """Test Widget size."""

    def test_widget_has_width(self):
        """Widget should have width property."""
        widget = Widget()
        assert hasattr(widget, "width")

    def test_widget_has_height(self):
        """Widget should have height property."""
        widget = Widget()
        assert hasattr(widget, "height")

    def test_size_defaults(self):
        """Size should default to (100, 100)."""
        widget = Widget()
        assert widget.width == 100
        assert widget.height == 100

    def test_size_can_be_set(self):
        """Size can be set."""
        widget = Widget()
        widget.width = 200
        widget.height = 150
        assert widget.width == 200
        assert widget.height == 150


class TestWidgetEnabled:
    """Test Widget enabled state."""

    def test_widget_has_enabled(self):
        """Widget should have enabled property."""
        widget = Widget()
        assert hasattr(widget, "enabled")

    def test_widget_enabled_by_default(self):
        """Widget should be enabled by default."""
        widget = Widget()
        assert widget.enabled is True

    def test_widget_can_be_disabled(self):
        """Widget can be disabled."""
        widget = Widget()
        widget.enabled = False
        assert widget.enabled is False


class TestWidgetVisible:
    """Test Widget visibility."""

    def test_widget_has_visible(self):
        """Widget should have visible property."""
        widget = Widget()
        assert hasattr(widget, "visible")

    def test_widget_visible_by_default(self):
        """Widget should be visible by default."""
        widget = Widget()
        assert widget.visible is True

    def test_widget_can_be_hidden(self):
        """Widget can be hidden."""
        widget = Widget()
        widget.visible = False
        assert widget.visible is False


class TestWidgetHierarchy:
    """Test Widget parent-child hierarchy."""

    def test_widget_has_parent(self):
        """Widget should have parent property."""
        widget = Widget()
        assert hasattr(widget, "parent")

    def test_parent_default_none(self):
        """Parent should default to None."""
        widget = Widget()
        assert widget.parent is None

    def test_parent_can_be_set(self):
        """Parent can be set."""
        parent = Widget()
        child = Widget()
        child.parent = parent
        assert child.parent is parent

    def test_widget_has_children(self):
        """Widget should have children property."""
        widget = Widget()
        assert hasattr(widget, "children")

    def test_children_default_empty(self):
        """Children should default to empty list."""
        widget = Widget()
        assert widget.children == []

    def test_add_child(self):
        """Widget can add child."""
        parent = Widget()
        child = Widget()
        parent.add_child(child)
        assert child in parent.children
        assert child.parent is parent

    def test_remove_child(self):
        """Widget can remove child."""
        parent = Widget()
        child = Widget()
        parent.add_child(child)
        parent.remove_child(child)
        assert child not in parent.children
        assert child.parent is None


class TestWidgetLifecycle:
    """Test Widget lifecycle hooks."""

    def test_widget_has_on_tick(self):
        """Widget should have on_tick method."""
        widget = Widget()
        assert hasattr(widget, "on_tick")
        assert callable(widget.on_tick)

    def test_widget_has_on_draw(self):
        """Widget should have on_draw method."""
        widget = Widget()
        assert hasattr(widget, "on_draw")
        assert callable(widget.on_draw)

    def test_tick_propagates_to_children(self):
        """tick() should propagate to children."""
        results = []

        class CustomWidget(Widget):
            def on_tick(self, delta_time: float):
                results.append(delta_time)

        parent = Widget()
        child = CustomWidget()
        parent.add_child(child)
        parent.tick(0.016)

        assert 0.016 in results

    def test_tick_skips_disabled_widgets(self):
        """tick() should skip disabled widgets."""
        results = []

        class CustomWidget(Widget):
            def on_tick(self, delta_time: float):
                results.append(delta_time)

        widget = CustomWidget()
        widget.enabled = False
        widget.tick(0.016)

        assert len(results) == 0


class TestWidgetReflection:
    """Test Widget with reflection system."""

    def test_widget_properties_are_reflected(self):
        """Widget properties should be reflected."""
        widget = Widget()
        props = get_properties(widget)
        prop_names = [p.name for p in props]

        assert "x" in prop_names
        assert "y" in prop_names
        assert "width" in prop_names
        assert "height" in prop_names


class TestWidgetSerialization:
    """Test Widget serialization."""

    def test_widget_serialize(self):
        """Widget should serialize basic properties."""
        widget = Widget(name="TestWidget")
        widget.x = 100
        widget.y = 200
        data = widget.serialize()

        assert data["name"] == "TestWidget"
        assert data["x"] == 100
        assert data["y"] == 200

    def test_widget_deserialize(self):
        """Widget should deserialize basic properties."""
        widget = Widget()
        data = {
            "name": "DeserializedWidget",
            "x": 50,
            "y": 75,
            "width": 200,
            "height": 150
        }
        widget.deserialize(data)

        assert widget.name == "DeserializedWidget"
        assert widget.x == 50
        assert widget.y == 75
        assert widget.width == 200
        assert widget.height == 150


class TestWidgetRepr:
    """Test Widget string representation."""

    def test_widget_repr(self):
        """Widget should have useful repr."""
        widget = Widget(name="TestWidget")
        widget.x = 100
        widget.y = 200
        repr_str = repr(widget)

        assert "Widget" in repr_str
        assert "TestWidget" in repr_str


class TestWidgetBounds:
    """Test Widget bounds checking."""

    def test_widget_has_contains_point(self):
        """Widget should have contains_point method."""
        widget = Widget()
        assert hasattr(widget, "contains_point")
        assert callable(widget.contains_point)

    def test_contains_point_inside(self):
        """contains_point should return True for inside points."""
        widget = Widget()
        widget.x = 100
        widget.y = 100
        widget.width = 200
        widget.height = 150

        assert widget.contains_point(150, 150) is True
        assert widget.contains_point(100, 100) is True  # Top-left corner

    def test_contains_point_outside(self):
        """contains_point should return False for outside points."""
        widget = Widget()
        widget.x = 100
        widget.y = 100
        widget.width = 200
        widget.height = 150

        assert widget.contains_point(50, 50) is False
        assert widget.contains_point(400, 400) is False

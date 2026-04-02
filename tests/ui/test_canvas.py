"""
Tests for Canvas container.

Canvas is the root container for UI widgets.

Layer: 6 (UI)
"""

from ui.widget import Widget
from ui.canvas import Canvas


class TestCanvasInheritance:
    """Test that Canvas inherits from Widget."""

    def test_canvas_is_widget(self):
        """Canvas should be a Widget."""
        canvas = Canvas()
        assert isinstance(canvas, Widget)

    def test_canvas_has_name(self):
        """Canvas should have a name."""
        canvas = Canvas(name="MainCanvas")
        assert canvas.name == "MainCanvas"


class TestCanvasRoot:
    """Test Canvas as root container."""

    def test_canvas_is_root(self):
        """Canvas is always a root (parent is None)."""
        canvas = Canvas()
        assert canvas.parent is None

    def test_canvas_parent_cannot_be_set(self):
        """Canvas parent should remain None even if set."""
        canvas = Canvas()
        other = Widget()
        canvas.parent = other  # Should be ignored or cleared
        assert canvas.parent is None


class TestCanvasChildren:
    """Test Canvas child management."""

    def test_canvas_has_children(self):
        """Canvas should have children property."""
        canvas = Canvas()
        assert hasattr(canvas, "children")

    def test_canvas_children_default_empty(self):
        """Canvas children should default to empty."""
        canvas = Canvas()
        assert canvas.children == []

    def test_canvas_can_add_widget(self):
        """Canvas can add a widget."""
        canvas = Canvas()
        widget = Widget()
        canvas.add_widget(widget)
        assert widget in canvas.children

    def test_add_widget_sets_parent(self):
        """Adding widget sets its parent to canvas."""
        canvas = Canvas()
        widget = Widget()
        canvas.add_widget(widget)
        assert widget.parent is canvas

    def test_canvas_can_remove_widget(self):
        """Canvas can remove a widget."""
        canvas = Canvas()
        widget = Widget()
        canvas.add_widget(widget)
        canvas.remove_widget(widget)
        assert widget not in canvas.children

    def test_remove_widget_clears_parent(self):
        """Removing widget clears its parent."""
        canvas = Canvas()
        widget = Widget()
        canvas.add_widget(widget)
        canvas.remove_widget(widget)
        assert widget.parent is None


class TestCanvasSize:
    """Test Canvas size management."""

    def test_canvas_has_set_size(self):
        """Canvas should have set_size method."""
        canvas = Canvas()
        assert hasattr(canvas, "set_size")
        assert callable(canvas.set_size)

    def test_set_size_updates_width_height(self):
        """set_size should update width and height."""
        canvas = Canvas()
        canvas.set_size(800, 600)
        assert canvas.width == 800
        assert canvas.height == 600


class TestCanvasTick:
    """Test Canvas tick functionality."""

    def test_canvas_has_tick(self):
        """Canvas should have tick method (inherited from Widget)."""
        canvas = Canvas()
        assert hasattr(canvas, "tick")
        assert callable(canvas.tick)

    def test_canvas_tick_propagates(self):
        """Canvas tick should propagate to children."""
        results = []

        class CustomWidget(Widget):
            def on_tick(self, delta_time: float):
                results.append(delta_time)

        canvas = Canvas()
        widget = CustomWidget()
        canvas.add_widget(widget)
        canvas.tick(0.016)

        assert 0.016 in results


class TestCanvasFindWidget:
    """Test Canvas widget finding."""

    def test_canvas_has_find_by_name(self):
        """Canvas should have find_widget_by_name method."""
        canvas = Canvas()
        assert hasattr(canvas, "find_widget_by_name")
        assert callable(canvas.find_widget_by_name)

    def test_find_widget_by_name(self):
        """find_widget_by_name should find widget by name."""
        canvas = Canvas()
        widget1 = Widget(name="Button1")
        widget2 = Widget(name="Button2")
        canvas.add_widget(widget1)
        canvas.add_widget(widget2)

        found = canvas.find_widget_by_name("Button1")
        assert found is widget1

    def test_find_widget_by_name_returns_none_if_not_found(self):
        """find_widget_by_name should return None if not found."""
        canvas = Canvas()
        found = canvas.find_widget_by_name("NonExistent")
        assert found is None

    def test_canvas_has_find_at_point(self):
        """Canvas should have find_widget_at_point method."""
        canvas = Canvas()
        assert hasattr(canvas, "find_widget_at_point")
        assert callable(canvas.find_widget_at_point)

    def test_find_widget_at_point(self):
        """find_widget_at_point should find widget at coordinates."""
        canvas = Canvas()
        canvas.set_size(800, 600)

        widget = Widget(name="TestWidget")
        widget.x = 100
        widget.y = 100
        widget.width = 200
        widget.height = 150
        canvas.add_widget(widget)

        found = canvas.find_widget_at_point(150, 150)
        assert found is widget

    def test_find_widget_at_point_returns_none_if_not_found(self):
        """find_widget_at_point should return None if no widget at point."""
        canvas = Canvas()
        canvas.set_size(800, 600)

        widget = Widget()
        widget.x = 100
        widget.y = 100
        widget.width = 50
        widget.height = 50
        canvas.add_widget(widget)

        found = canvas.find_widget_at_point(500, 500)
        assert found is None


class TestCanvasClear:
    """Test Canvas clear functionality."""

    def test_canvas_has_clear(self):
        """Canvas should have clear method."""
        canvas = Canvas()
        assert hasattr(canvas, "clear")
        assert callable(canvas.clear)

    def test_clear_removes_all_widgets(self):
        """clear should remove all widgets."""
        canvas = Canvas()
        canvas.add_widget(Widget())
        canvas.add_widget(Widget())
        canvas.add_widget(Widget())
        canvas.clear()
        assert len(canvas.children) == 0

    def test_clear_clears_parents(self):
        """clear should clear parent references."""
        canvas = Canvas()
        widget = Widget()
        canvas.add_widget(widget)
        canvas.clear()
        assert widget.parent is None


class TestCanvasSerialization:
    """Test Canvas serialization."""

    def test_canvas_serialize(self):
        """Canvas should serialize basic properties."""
        canvas = Canvas(name="MainCanvas")
        canvas.set_size(1024, 768)
        data = canvas.serialize()

        assert data["name"] == "MainCanvas"
        assert data["width"] == 1024
        assert data["height"] == 768

    def test_canvas_deserialize(self):
        """Canvas should deserialize basic properties."""
        canvas = Canvas()
        data = {
            "name": "DeserializedCanvas",
            "width": 1920,
            "height": 1080
        }
        canvas.deserialize(data)

        assert canvas.name == "DeserializedCanvas"
        assert canvas.width == 1920
        assert canvas.height == 1080


class TestCanvasRepr:
    """Test Canvas string representation."""

    def test_canvas_repr(self):
        """Canvas should have useful repr."""
        canvas = Canvas(name="MainCanvas")
        canvas.set_size(800, 600)
        repr_str = repr(canvas)

        assert "Canvas" in repr_str
        assert "MainCanvas" in repr_str

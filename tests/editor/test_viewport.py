"""Tests for Viewport panel."""

import pytest
from editor.main import Editor, EditorPanel


class TestViewport:
    """Test suite for Viewport panel."""

    def test_viewport_is_panel(self):
        """Viewport should inherit from EditorPanel."""
        from editor.viewport import Viewport
        assert issubclass(Viewport, EditorPanel)

    def test_viewport_creation(self):
        """Viewport should be created with default settings."""
        from editor.viewport import Viewport

        viewport = Viewport()
        assert viewport is not None
        assert viewport.name == "Viewport"

    def test_viewport_has_width_height(self):
        """Viewport should have width and height."""
        from editor.viewport import Viewport

        viewport = Viewport()
        assert hasattr(viewport, 'width')
        assert hasattr(viewport, 'height')

    def test_viewport_default_size(self):
        """Viewport should have default size."""
        from editor.viewport import Viewport

        viewport = Viewport()
        assert viewport.width > 0
        assert viewport.height > 0

    def test_viewport_custom_size(self):
        """Viewport should accept custom size."""
        from editor.viewport import Viewport

        viewport = Viewport(width=1024, height=768)
        assert viewport.width == 1024
        assert viewport.height == 768

    def test_viewport_has_render_method(self):
        """Viewport should have render method."""
        from editor.viewport import Viewport

        viewport = Viewport()
        assert hasattr(viewport, 'render')
        assert callable(viewport.render)

    def test_viewport_has_camera(self):
        """Viewport should have camera reference."""
        from editor.viewport import Viewport

        viewport = Viewport()
        assert hasattr(viewport, 'camera')

    def test_viewport_has_zoom(self):
        """Viewport should have zoom level."""
        from editor.viewport import Viewport

        viewport = Viewport()
        assert hasattr(viewport, 'zoom')
        assert viewport.zoom == 1.0

    def test_viewport_set_zoom(self):
        """Viewport zoom should be settable."""
        from editor.viewport import Viewport

        viewport = Viewport()
        viewport.zoom = 2.0
        assert viewport.zoom == 2.0

    def test_viewport_has_offset(self):
        """Viewport should have pan offset."""
        from editor.viewport import Viewport

        viewport = Viewport()
        assert hasattr(viewport, 'offset_x')
        assert hasattr(viewport, 'offset_y')

    def test_viewport_default_offset(self):
        """Viewport offset should default to zero."""
        from editor.viewport import Viewport

        viewport = Viewport()
        assert viewport.offset_x == 0
        assert viewport.offset_y == 0

    def test_viewport_with_editor(self):
        """Viewport should accept editor reference."""
        from editor.viewport import Viewport

        editor = Editor()
        viewport = Viewport(editor=editor)
        assert viewport.editor is editor

    def test_viewport_world_to_screen(self):
        """Viewport should convert world coords to screen."""
        from editor.viewport import Viewport

        viewport = Viewport(width=800, height=600)
        # Center of viewport should be (400, 300) in screen coords
        screen_x, screen_y = viewport.world_to_screen(0, 0)
        assert screen_x == 400
        assert screen_y == 300

    def test_viewport_screen_to_world(self):
        """Viewport should convert screen coords to world."""
        from editor.viewport import Viewport

        viewport = Viewport(width=800, height=600)
        # Center of screen should be (0, 0) in world coords
        world_x, world_y = viewport.screen_to_world(400, 300)
        assert world_x == 0
        assert world_y == 0

    def test_viewport_world_to_screen_with_offset(self):
        """Viewport should apply offset in conversion."""
        from editor.viewport import Viewport

        viewport = Viewport(width=800, height=600)
        viewport.offset_x = 100
        viewport.offset_y = 50

        # World (0, 0) should appear at screen (500, 350) with offset
        screen_x, screen_y = viewport.world_to_screen(0, 0)
        assert screen_x == 500
        assert screen_y == 350

    def test_viewport_world_to_screen_with_zoom(self):
        """Viewport should apply zoom in conversion."""
        from editor.viewport import Viewport

        viewport = Viewport(width=800, height=600)
        viewport.zoom = 2.0

        # World (100, 100) should appear at screen (600, 500) with 2x zoom
        screen_x, screen_y = viewport.world_to_screen(100, 100)
        assert screen_x == 600  # 400 + 100 * 2
        assert screen_y == 500  # 300 + 100 * 2

    def test_viewport_pan(self):
        """Viewport should have pan method."""
        from editor.viewport import Viewport

        viewport = Viewport()
        assert hasattr(viewport, 'pan')
        viewport.pan(10, 20)
        assert viewport.offset_x == 10
        assert viewport.offset_y == 20

    def test_viewport_reset_view(self):
        """Viewport should have reset_view method."""
        from editor.viewport import Viewport

        viewport = Viewport()
        viewport.zoom = 2.0
        viewport.offset_x = 100
        viewport.offset_y = 50

        viewport.reset_view()
        assert viewport.zoom == 1.0
        assert viewport.offset_x == 0
        assert viewport.offset_y == 0


class TestViewportGrid:
    """Test suite for Viewport grid display."""

    def test_viewport_has_grid_enabled(self):
        """Viewport should have grid visibility flag."""
        from editor.viewport import Viewport

        viewport = Viewport()
        assert hasattr(viewport, 'show_grid')

    def test_viewport_grid_default_on(self):
        """Viewport grid should be enabled by default."""
        from editor.viewport import Viewport

        viewport = Viewport()
        assert viewport.show_grid is True

    def test_viewport_grid_size(self):
        """Viewport should have grid size setting."""
        from editor.viewport import Viewport

        viewport = Viewport()
        assert hasattr(viewport, 'grid_size')
        assert viewport.grid_size > 0

    def test_viewport_toggle_grid(self):
        """Viewport grid should be toggleable."""
        from editor.viewport import Viewport

        viewport = Viewport()
        viewport.show_grid = False
        assert viewport.show_grid is False


class TestViewportSelection:
    """Test suite for Viewport selection features."""

    def test_viewport_has_selection_rect(self):
        """Viewport should track selection rectangle."""
        from editor.viewport import Viewport

        viewport = Viewport()
        assert hasattr(viewport, 'selection_rect')

    def test_viewport_selection_rect_default_none(self):
        """Viewport selection rect should default to None."""
        from editor.viewport import Viewport

        viewport = Viewport()
        assert viewport.selection_rect is None

    def test_viewport_begin_selection(self):
        """Viewport should have begin_selection method."""
        from editor.viewport import Viewport

        viewport = Viewport()
        assert hasattr(viewport, 'begin_selection')
        viewport.begin_selection(100, 100)
        assert viewport.selection_rect is not None

    def test_viewport_update_selection(self):
        """Viewport should have update_selection method."""
        from editor.viewport import Viewport

        viewport = Viewport()
        viewport.begin_selection(100, 100)
        viewport.update_selection(200, 200)
        rect = viewport.selection_rect
        assert rect is not None

    def test_viewport_end_selection(self):
        """Viewport should have end_selection method."""
        from editor.viewport import Viewport

        viewport = Viewport()
        viewport.begin_selection(100, 100)
        viewport.end_selection()
        assert viewport.selection_rect is None

    def test_viewport_get_selection_bounds(self):
        """Viewport should return selection world bounds."""
        from editor.viewport import Viewport

        viewport = Viewport(width=800, height=600)
        viewport.begin_selection(100, 100)
        viewport.update_selection(300, 400)

        bounds = viewport.get_selection_bounds()
        assert bounds is not None
        # Should return (min_x, min_y, max_x, max_y) in world coords
        assert len(bounds) == 4

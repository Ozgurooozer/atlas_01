"""Viewport panel for scene viewing.

DearPyGui-based viewport that displays the game world.
Provides camera controls, grid overlay, and selection.

Layer: 7 (Editor)
Dependencies: editor.main
"""

from __future__ import annotations

from typing import Optional, Tuple, TYPE_CHECKING

from editor.main import EditorPanel

if TYPE_CHECKING:
    from world.actor import Actor
    from editor.main import Editor


class Viewport(EditorPanel):
    """
    Scene viewport panel.

    Displays the game world with camera controls.
    Supports pan, zoom, grid overlay, and selection.

    Attributes:
        width: Viewport width in pixels.
        height: Viewport height in pixels.
        zoom: Camera zoom level.
        offset_x: Camera pan offset X.
        offset_y: Camera pan offset Y.
        show_grid: Whether to show grid overlay.
        grid_size: Grid cell size in world units.
    """

    def __init__(
        self,
        name: str = "Viewport",
        editor: Optional[Editor] = None,
        width: int = 800,
        height: int = 600
    ) -> None:
        """Initialize viewport panel.

        Args:
            name: Panel display name.
            editor: Optional parent editor reference.
            width: Viewport width in pixels.
            height: Viewport height in pixels.
        """
        super().__init__(name=name, editor=editor)
        self._width = width
        self._height = height
        self._zoom: float = 1.0
        self._offset_x: float = 0.0
        self._offset_y: float = 0.0
        self._show_grid: bool = True
        self._grid_size: int = 32
        self._camera = None  # Camera reference placeholder
        self._selection_rect: Optional[Tuple[int, int, int, int]] = None

    @property
    def width(self) -> int:
        """Get viewport width."""
        return self._width

    @width.setter
    def width(self, value: int) -> None:
        """Set viewport width."""
        self._width = value

    @property
    def height(self) -> int:
        """Get viewport height."""
        return self._height

    @height.setter
    def height(self, value: int) -> None:
        """Set viewport height."""
        self._height = value

    @property
    def zoom(self) -> float:
        """Get zoom level."""
        return self._zoom

    @zoom.setter
    def zoom(self, value: float) -> None:
        """Set zoom level."""
        self._zoom = max(0.1, value)  # Minimum zoom

    @property
    def offset_x(self) -> float:
        """Get pan offset X."""
        return self._offset_x

    @offset_x.setter
    def offset_x(self, value: float) -> None:
        """Set pan offset X."""
        self._offset_x = value

    @property
    def offset_y(self) -> float:
        """Get pan offset Y."""
        return self._offset_y

    @offset_y.setter
    def offset_y(self, value: float) -> None:
        """Set pan offset Y."""
        self._offset_y = value

    @property
    def camera(self):
        """Get camera reference."""
        return self._camera

    @camera.setter
    def camera(self, value) -> None:
        """Set camera reference."""
        self._camera = value

    @property
    def show_grid(self) -> bool:
        """Get grid visibility."""
        return self._show_grid

    @show_grid.setter
    def show_grid(self, value: bool) -> None:
        """Set grid visibility."""
        self._show_grid = value

    @property
    def grid_size(self) -> int:
        """Get grid cell size."""
        return self._grid_size

    @grid_size.setter
    def grid_size(self, value: int) -> None:
        """Set grid cell size."""
        self._grid_size = max(1, value)

    @property
    def selection_rect(self) -> Optional[Tuple[int, int, int, int]]:
        """Get current selection rectangle (x1, y1, x2, y2)."""
        return self._selection_rect

    def world_to_screen(
        self,
        world_x: float,
        world_y: float
    ) -> Tuple[int, int]:
        """Convert world coordinates to screen coordinates.

        Args:
            world_x: World X coordinate.
            world_y: World Y coordinate.

        Returns:
            Tuple of (screen_x, screen_y).
        """
        center_x = self._width / 2
        center_y = self._height / 2

        screen_x = int(center_x + (world_x * self._zoom) + self._offset_x)
        screen_y = int(center_y + (world_y * self._zoom) + self._offset_y)

        return (screen_x, screen_y)

    def screen_to_world(
        self,
        screen_x: int,
        screen_y: int
    ) -> Tuple[float, float]:
        """Convert screen coordinates to world coordinates.

        Args:
            screen_x: Screen X coordinate.
            screen_y: Screen Y coordinate.

        Returns:
            Tuple of (world_x, world_y).
        """
        center_x = self._width / 2
        center_y = self._height / 2

        world_x = (screen_x - center_x - self._offset_x) / self._zoom
        world_y = (screen_y - center_y - self._offset_y) / self._zoom

        return (world_x, world_y)

    def pan(self, dx: float, dy: float) -> None:
        """Pan the viewport by delta.

        Args:
            dx: Delta X in world units.
            dy: Delta Y in world units.
        """
        self._offset_x += dx
        self._offset_y += dy

    def reset_view(self) -> None:
        """Reset viewport to default view."""
        self._zoom = 1.0
        self._offset_x = 0.0
        self._offset_y = 0.0

    def begin_selection(self, x: int, y: int) -> None:
        """Begin selection rectangle at screen position.

        Args:
            x: Screen X coordinate.
            y: Screen Y coordinate.
        """
        self._selection_rect = (x, y, x, y)

    def update_selection(self, x: int, y: int) -> None:
        """Update selection rectangle end point.

        Args:
            x: Current screen X coordinate.
            y: Current screen Y coordinate.
        """
        if self._selection_rect is not None:
            x1, y1, _, _ = self._selection_rect
            self._selection_rect = (x1, y1, x, y)

    def end_selection(self) -> None:
        """End selection rectangle."""
        self._selection_rect = None

    def get_selection_bounds(
        self
    ) -> Optional[Tuple[float, float, float, float]]:
        """Get selection bounds in world coordinates.

        Returns:
            Tuple of (min_x, min_y, max_x, max_y) in world coords,
            or None if no selection.
        """
        if self._selection_rect is None:
            return None

        x1, y1, x2, y2 = self._selection_rect

        # Convert to world coordinates
        min_x, min_y = self.screen_to_world(min(x1, x2), min(y1, y2))
        max_x, max_y = self.screen_to_world(max(x1, x2), max(y1, y2))

        return (min_x, min_y, max_x, max_y)

    def render(self) -> None:
        """Render viewport content.

        In a real implementation, this would use DearPyGui
        to render the scene, grid, and selection.
        """
        if not self.visible:
            return

        # DearPyGui rendering would go here
        # For headless testing, this is a no-op
        pass

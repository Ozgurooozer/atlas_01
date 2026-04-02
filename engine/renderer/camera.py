"""
Camera for 2D view transformation.

Provides view position, zoom, rotation, and follow functionality.
Generates view and projection matrices for rendering.

Layer: 2 (Engine)
Dependencies: core.vec
"""

from __future__ import annotations

from typing import Optional, Tuple, TYPE_CHECKING

from core.vec import Vec2

if TYPE_CHECKING:
    pass


class Camera:
    """
    2D Camera for view transformation.

    Controls the visible area of the game world.
    Supports position, zoom, rotation, bounds, and follow target.

    Example:
        >>> camera = Camera()
        >>> camera.viewport_width = 800
        >>> camera.viewport_height = 600
        >>> camera.position = Vec2(100.0, 100.0)
        >>> screen_pos = camera.world_to_screen(150.0, 150.0)

    Attributes:
        position: Camera position in world coordinates.
        zoom: Zoom level (1.0 = normal, 2.0 = 2x zoom).
        rotation: Camera rotation in degrees.
        viewport_width: Viewport width in pixels.
        viewport_height: Viewport height in pixels.
        bounds: Optional bounds (x, y, width, height).
        follow_target: Optional target to follow.
        follow_speed: Speed for following (0-1, higher = faster).
    """

    def __init__(self) -> None:
        """Create a new Camera."""
        self._position: Vec2 = Vec2(0.0, 0.0)
        self._zoom: float = 1.0
        self._rotation: float = 0.0
        self._viewport_width: int = 800
        self._viewport_height: int = 600
        self._bounds: Optional[Tuple[float, float, float, float]] = None
        self._follow_target: Optional[object] = None
        self._follow_speed: float = 0.1
        self._mode: str = "side_scroll"  # "side_scroll" | "isometric"

    @property
    def position(self) -> Vec2:
        """Get camera position."""
        return self._position

    @position.setter
    def position(self, value: Vec2) -> None:
        """Set camera position."""
        self._position = value

    @property
    def zoom(self) -> float:
        """Get zoom level."""
        return self._zoom

    @zoom.setter
    def zoom(self, value: float) -> None:
        """Set zoom level."""
        self._zoom = max(0.1, value)  # Prevent zero or negative zoom

    @property
    def rotation(self) -> float:
        """Get rotation in degrees."""
        return self._rotation

    @rotation.setter
    def rotation(self, value: float) -> None:
        """Set rotation in degrees."""
        self._rotation = value

    @property
    def viewport_width(self) -> int:
        """Get viewport width."""
        return self._viewport_width

    @viewport_width.setter
    def viewport_width(self, value: int) -> None:
        """Set viewport width."""
        self._viewport_width = max(1, value)

    @property
    def viewport_height(self) -> int:
        """Get viewport height."""
        return self._viewport_height

    @viewport_height.setter
    def viewport_height(self, value: int) -> None:
        """Set viewport height."""
        self._viewport_height = max(1, value)

    @property
    def viewport_size(self) -> Tuple[int, int]:
        """Get viewport size as (width, height)."""
        return (self._viewport_width, self._viewport_height)

    @property
    def bounds(self) -> Optional[Tuple[float, float, float, float]]:
        """Get bounds (x, y, width, height)."""
        return self._bounds

    @bounds.setter
    def bounds(self, value: Optional[Tuple[float, float, float, float]]) -> None:
        """Set bounds."""
        self._bounds = value

    @property
    def follow_target(self) -> Optional[object]:
        """Get follow target."""
        return self._follow_target

    @follow_target.setter
    def follow_target(self, value: Optional[object]) -> None:
        """Set follow target."""
        self._follow_target = value

    @property
    def follow_speed(self) -> float:
        """Get follow speed."""
        return self._follow_speed

    @follow_speed.setter
    def follow_speed(self, value: float) -> None:
        """Set follow speed."""
        self._follow_speed = max(0.0, min(1.0, value))

    @property
    def mode(self) -> str:
        """Get camera mode."""
        return self._mode

    @mode.setter
    def mode(self, value: str) -> None:
        """Set camera mode."""
        if value not in ("side_scroll", "isometric"):
            raise ValueError("Invalid camera mode")
        self._mode = value

    def world_to_screen(self, world_x: float, world_y: float) -> Tuple[float, float]:
        """
        Convert world coordinates to screen coordinates.

        Args:
            world_x: World X coordinate.
            world_y: World Y coordinate.

        Returns:
            (screen_x, screen_y) tuple.
        """
        # Offset by camera position
        dx = world_x - self._position.x
        dy = world_y - self._position.y

        # Apply zoom
        dx *= self._zoom
        dy *= self._zoom

        # Convert to screen space (center of screen)
        screen_x = (self._viewport_width / 2.0) + dx
        screen_y = (self._viewport_height / 2.0) + dy

        return (screen_x, screen_y)

    def screen_to_world(self, screen_x: float, screen_y: float) -> Tuple[float, float]:
        """
        Convert screen coordinates to world coordinates.

        Args:
            screen_x: Screen X coordinate.
            screen_y: Screen Y coordinate.

        Returns:
            (world_x, world_y) tuple.
        """
        # Convert from screen space (center of screen)
        dx = screen_x - (self._viewport_width / 2.0)
        dy = screen_y - (self._viewport_height / 2.0)

        # Apply inverse zoom
        dx /= self._zoom
        dy /= self._zoom

        # Add camera position
        world_x = dx + self._position.x
        world_y = dy + self._position.y

        return (world_x, world_y)

    def clamp_to_bounds(self) -> None:
        """
        Clamp camera position to bounds.

        Ensures camera doesn't go outside defined bounds.
        """
        if self._bounds is None:
            return

        bounds_x, bounds_y, bounds_w, bounds_h = self._bounds

        # Calculate visible area
        visible_w = self._viewport_width / self._zoom
        visible_h = self._viewport_height / self._zoom

        # Calculate min/max camera position
        min_x = bounds_x + visible_w / 2.0
        max_x = bounds_x + bounds_w - visible_w / 2.0
        min_y = bounds_y + visible_h / 2.0
        max_y = bounds_y + bounds_h - visible_h / 2.0

        # Clamp position
        new_x = max(min_x, min(max_x, self._position.x))
        new_y = max(min_y, min(max_y, self._position.y))

        self._position = Vec2(new_x, new_y)

    def update(self, dt: float) -> None:
        """
        Update camera for one frame.

        Handles following target.

        Args:
            dt: Delta time in seconds.
        """
        if self._follow_target is None:
            return

        # Get target position
        target_pos = getattr(self._follow_target, 'position', None)
        if target_pos is None:
            return

        # Smooth follow (lerp)
        lerp_factor = self._follow_speed
        if lerp_factor >= 1.0:
            # Instant follow
            self._position = Vec2(target_pos.x, target_pos.y)
        else:
            # Smooth interpolation
            new_x = self._position.x + (target_pos.x - self._position.x) * lerp_factor
            new_y = self._position.y + (target_pos.y - self._position.y) * lerp_factor
            self._position = Vec2(new_x, new_y)

    @property
    def view_matrix(self) -> Tuple[float, ...]:
        """
        Get the view matrix (4x4).

        Returns:
            16 floats representing a 4x4 matrix.
        """
        import math

        # Create translation matrix (negative camera position)
        tx = -self._position.x
        ty = -self._position.y

        # Create rotation matrix
        rad = math.radians(self._rotation)
        cos_r = math.cos(rad)
        sin_r = math.sin(rad)

        # Create scale matrix (zoom)
        z = self._zoom

        # Combine: scale * rotate * translate
        # 4x4 matrix in column-major order
        return (
            z * cos_r, z * sin_r, 0.0, 0.0,
            -z * sin_r, z * cos_r, 0.0, 0.0,
            0.0, 0.0, 1.0, 0.0,
            tx * z * cos_r - ty * z * sin_r, tx * z * sin_r + ty * z * cos_r, 0.0, 1.0
        )

    @property
    def projection_matrix(self) -> Tuple[float, ...]:
        """
        Get the projection matrix (orthographic, 4x4).

        Returns:
            16 floats representing a 4x4 matrix.
        """
        if self._mode == "isometric":
            return IsometricProjection.get_matrix(self._viewport_width, self._viewport_height, self._zoom)

        # Orthographic projection
        # Maps (0, 0) to (-1, -1) and (width, height) to (1, 1)
        w = self._viewport_width
        h = self._viewport_height

        return (
            2.0 / w, 0.0, 0.0, 0.0,
            0.0, -2.0 / h, 0.0, 0.0,
            0.0, 0.0, 1.0, 0.0,
            -1.0, 1.0, 0.0, 1.0
        )


class IsometricProjection:
    """Helper for isometric projection matrices."""

    @staticmethod
    def get_matrix(width: int, height: int, zoom: float) -> Tuple[float, ...]:
        """
        Get isometric projection matrix (4x4).

        Args:
            width: Viewport width.
            height: Viewport height.
            zoom: Zoom level.

        Returns:
            16 floats representing a 4x4 matrix.
        """
        # Isometric transformation:
        # x' = (x - y) * cos(30)
        # y' = (x + y) * sin(30)
        import math
        cos30 = math.cos(math.radians(30))
        sin30 = math.sin(math.radians(30))

        # Scale by zoom and normalize to clip space
        sx = (2.0 / width) * zoom
        sy = (2.0 / height) * zoom

        return (
            cos30 * sx, -sin30 * sy, 0.0, 0.0,
            -cos30 * sx, -sin30 * sy, 0.0, 0.0,
            0.0, 0.0, 1.0, 0.0,
            0.0, 0.0, 0.0, 1.0
        )

    def look_at(self, x: float, y: float) -> None:
        """
        Set camera position to look at a point.

        Args:
            x: World X coordinate.
            y: World Y coordinate.
        """
        self._position = Vec2(x, y)

    def move(self, dx: float, dy: float) -> None:
        """
        Move camera by offset.

        Args:
            dx: X offset.
            dy: Y offset.
        """
        self._position = Vec2(self._position.x + dx, self._position.y + dy)

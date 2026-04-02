"""
Sprite bounds and collision utilities.

Provides bounding box calculations and point containment
tests for sprites.

Layer: 2 (Engine)
Dependencies: core.vec
"""

from __future__ import annotations

from typing import Dict


class SpriteBoundsMixin:
    """
    Mixin class for sprite bounds calculations.

    Requires: position, scale_x, scale_y, anchor_x, anchor_y
    Provides: width, height, get_bounds(), contains_point()
    """

    def _get_base_width(self) -> int:
        """Get base width from texture or region. Must be implemented by subclass."""
        raise NotImplementedError

    def _get_base_height(self) -> int:
        """Get base height from texture or region. Must be implemented by subclass."""
        raise NotImplementedError

    @property
    def width(self) -> float:
        """Get sprite width (including scale)."""
        base_width = self._get_base_width()
        return base_width * abs(self.scale_x)  # type: ignore[attr-defined]

    @property
    def height(self) -> float:
        """Get sprite height (including scale)."""
        base_height = self._get_base_height()
        return base_height * abs(self.scale_y)  # type: ignore[attr-defined]

    def get_bounds(self) -> Dict[str, float]:
        """
        Get axis-aligned bounding box.

        Returns:
            Dictionary with x, y, width, height.
        """
        w = self.width
        h = self.height

        # Offset by anchor
        offset_x = w * self.anchor_x  # type: ignore[attr-defined]
        offset_y = h * self.anchor_y  # type: ignore[attr-defined]

        return {
            'x': self.position.x - offset_x,  # type: ignore[attr-defined]
            'y': self.position.y - offset_y,  # type: ignore[attr-defined]
            'width': w,
            'height': h
        }

    def contains_point(self, x: float, y: float) -> bool:
        """
        Check if point is inside sprite bounds.

        Args:
            x: Point X coordinate.
            y: Point Y coordinate.

        Returns:
            True if point is inside sprite.
        """
        bounds = self.get_bounds()

        return (
            bounds['x'] <= x <= bounds['x'] + bounds['width'] and
            bounds['y'] <= y <= bounds['y'] + bounds['height']
        )

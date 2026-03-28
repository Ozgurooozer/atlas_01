"""
AABB (Axis-Aligned Bounding Box).

Simple 2D bounding box for collision detection.

Layer: 2 (Engine)
Dependencies: None
"""

from __future__ import annotations


class AABB:
    """
    Axis-Aligned Bounding Box for 2D collision detection.

    An AABB is a rectangle aligned with the coordinate axes.
    It's defined by its bottom-left corner (x, y) and dimensions.

    Example:
        >>> aabb = AABB(x=0, y=0, width=100, height=50)
        >>> aabb.contains_point(50, 25)
        True
        >>> other = AABB(x=50, y=25, width=100, height=50)
        >>> aabb.overlaps(other)
        True

    Attributes:
        x: Bottom-left X coordinate.
        y: Bottom-left Y coordinate.
        width: Box width.
        height: Box height.
    """

    def __init__(self, x: float, y: float, width: float, height: float):
        """
        Create an AABB.

        Args:
            x: Bottom-left X coordinate.
            y: Bottom-left Y coordinate.
            width: Box width.
            height: Box height.
        """
        self.x = float(x)
        self.y = float(y)
        self.width = float(width)
        self.height = float(height)

    @classmethod
    def from_center(
        cls,
        center_x: float,
        center_y: float,
        width: float,
        height: float
    ) -> AABB:
        """
        Create an AABB from center point.

        Args:
            center_x: Center X coordinate.
            center_y: Center Y coordinate.
            width: Box width.
            height: Box height.

        Returns:
            New AABB instance.
        """
        x = center_x - width / 2
        y = center_y - height / 2
        return cls(x, y, width, height)

    @property
    def left(self) -> float:
        """Get left edge (x coordinate)."""
        return self.x

    @property
    def right(self) -> float:
        """Get right edge."""
        return self.x + self.width

    @property
    def bottom(self) -> float:
        """Get bottom edge (y coordinate)."""
        return self.y

    @property
    def top(self) -> float:
        """Get top edge."""
        return self.y + self.height

    @property
    def center_x(self) -> float:
        """Get center X coordinate."""
        return self.x + self.width / 2

    @property
    def center_y(self) -> float:
        """Get center Y coordinate."""
        return self.y + self.height / 2

    def contains_point(self, px: float, py: float) -> bool:
        """
        Check if a point is inside this AABB.

        Points on the edge are considered inside.

        Args:
            px: Point X coordinate.
            py: Point Y coordinate.

        Returns:
            True if point is inside or on edge.
        """
        return (
            self.left <= px <= self.right and
            self.bottom <= py <= self.top
        )

    def overlaps(self, other: AABB) -> bool:
        """
        Check if this AABB overlaps another AABB.

        Edge-touching boxes are NOT considered overlapping.
        This is useful for physics where resting contact
        shouldn't trigger overlap events.

        Args:
            other: Another AABB to check.

        Returns:
            True if boxes overlap (interiors intersect).
        """
        # Separating Axis Theorem for AABBs
        # No overlap if separated on any axis
        if self.right <= other.left:  # self is left of other
            return False
        if self.left >= other.right:  # self is right of other
            return False
        if self.top <= other.bottom:  # self is below other
            return False
        if self.bottom >= other.top:  # self is above other
            return False

        # Overlapping on both axes
        return True

    def __repr__(self) -> str:
        """Return string representation."""
        return f"AABB(x={self.x}, y={self.y}, w={self.width}, h={self.height})"

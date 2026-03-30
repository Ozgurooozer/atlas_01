"""
TransformComponent.

Stores position, rotation, and scale for an Actor.
Every spatial Actor should have a TransformComponent.

Features:
- 2D position (x, y)
- Rotation in degrees
- Scale (uniform or non-uniform)
- Helper methods for common operations
- Reflected properties for Editor

Layer: 3 (World)
Dependencies: world.component, core.reflection
"""

from __future__ import annotations
from typing import Any, Dict, Optional, Tuple, Union

from world.component import Component
from core.reflection import reflect


class TransformComponent(Component):
    """
    Component that stores position, rotation, and scale.

    Every Actor that exists in 2D space should have a TransformComponent.
    It provides the spatial properties needed for rendering and physics.

    Example:
        >>> transform = TransformComponent()
        >>> transform.position = (100, 200)
        >>> transform.rotation = 45.0
        >>> transform.scale = (2.0, 2.0)
        >>> transform.translate(10, 0)  # Move right

    Attributes:
        position: (x, y) tuple for 2D position
        rotation: Rotation in degrees
        scale: (scale_x, scale_y) tuple for 2D scale
    """

    def __init__(self, name: str = None):
        """
        Create a new TransformComponent.

        Args:
            name: Optional name. Defaults to class name.
        """
        super().__init__(name)
        self._x: float = 0.0
        self._y: float = 0.0
        self._rotation: float = 0.0
        self._scale_x: float = 1.0
        self._scale_y: float = 1.0
        self._parent: Optional[TransformComponent] = None

    # Position properties
    @property
    def position(self) -> Tuple[float, float]:
        """Get position as (x, y) tuple."""
        return (self._x, self._y)

    @position.setter
    def position(self, value: Union[Tuple[float, float], list]) -> None:
        """Set position from tuple or list."""
        self._x = float(value[0])
        self._y = float(value[1])

    @reflect("float", category="Transform", description="X position in world space")
    def x(self) -> float:
        """Get X position."""
        return self._x

    @x.setter
    def x(self, value: float) -> None:
        """Set X position."""
        self._x = float(value)

    @reflect("float", category="Transform", description="Y position in world space")
    def y(self) -> float:
        """Get Y position."""
        return self._y

    @y.setter
    def y(self, value: float) -> None:
        """Set Y position."""
        self._y = float(value)

    # Rotation property
    @reflect("float", category="Transform", min=-360, max=360, description="Rotation in degrees")
    def rotation(self) -> float:
        """Get rotation in degrees."""
        return self._rotation

    @rotation.setter
    def rotation(self, value: float) -> None:
        """Set rotation in degrees."""
        self._rotation = float(value)

    # Scale properties
    @property
    def scale(self) -> Tuple[float, float]:
        """Get scale as (scale_x, scale_y) tuple."""
        return (self._scale_x, self._scale_y)

    @scale.setter
    def scale(self, value: Union[Tuple[float, float], list]) -> None:
        """Set scale from tuple or list."""
        self._scale_x = float(value[0])
        self._scale_y = float(value[1])

    @reflect("float", category="Transform", min=0.01, description="X scale factor")
    def scale_x(self) -> float:
        """Get X scale."""
        return self._scale_x

    @scale_x.setter
    def scale_x(self, value: float) -> None:
        """Set X scale."""
        self._scale_x = float(value)

    @reflect("float", category="Transform", min=0.01, description="Y scale factor")
    def scale_y(self) -> float:
        """Get Y scale."""
        return self._scale_y

    @scale_y.setter
    def scale_y(self, value: float) -> None:
        """Set Y scale."""
        self._scale_y = float(value)

    # Parent-Child hierarchy
    @property
    def parent(self) -> Optional[TransformComponent]:
        """Get parent transform."""
        return self._parent

    @parent.setter
    def parent(self, value: Optional[TransformComponent]) -> None:
        """Set parent transform."""
        self._parent = value

    @property
    def world_position(self) -> Tuple[float, float]:
        """Get world position (recursive)."""
        if self._parent is None:
            return self.position
        
        import math
        px, py = self._parent.world_position
        pr = math.radians(self._parent.world_rotation)
        psx, psy = self._parent.world_scale
        
        # Apply parent scale and rotation to local position
        lx = self._x * psx
        ly = self._y * psy
        
        cos_r = math.cos(pr)
        sin_r = math.sin(pr)
        
        rx = lx * cos_r - ly * sin_r
        ry = lx * sin_r + ly * cos_r
        
        return (px + rx, py + ry)

    @property
    def world_rotation(self) -> float:
        """Get world rotation (recursive)."""
        if self._parent is None:
            return self._rotation
        return self._parent.world_rotation + self._rotation

    @property
    def world_scale(self) -> Tuple[float, float]:
        """Get world scale (recursive)."""
        if self._parent is None:
            return self.scale
        psx, psy = self._parent.world_scale
        return (psx * self._scale_x, psy * self._scale_y)

    # Helper methods
    def set_uniform_scale(self, value: float) -> None:
        """
        Set uniform scale for both axes.

        Args:
            value: Scale factor for both X and Y
        """
        self._scale_x = float(value)
        self._scale_y = float(value)

    def translate(self, dx: float, dy: float) -> None:
        """
        Move the transform by the given offset.

        Args:
            dx: Distance to move on X axis
            dy: Distance to move on Y axis
        """
        self._x += dx
        self._y += dy

    def rotate(self, degrees: float) -> None:
        """
        Rotate the transform by the given angle.

        Args:
            degrees: Angle to rotate in degrees
        """
        self._rotation += degrees

    def reset(self) -> None:
        """Reset all transform values to default."""
        self._x = 0.0
        self._y = 0.0
        self._rotation = 0.0
        self._scale_x = 1.0
        self._scale_y = 1.0

    # Serialization
    def serialize(self) -> Dict[str, Any]:
        """
        Serialize this TransformComponent to a dictionary.

        Returns:
            Dictionary containing transform data
        """
        data = super().serialize()
        data["x"] = self._x
        data["y"] = self._y
        data["rotation"] = self._rotation
        data["scale_x"] = self._scale_x
        data["scale_y"] = self._scale_y
        return data

    def deserialize(self, data: Dict[str, Any]) -> None:
        """
        Deserialize this TransformComponent from a dictionary.

        Args:
            data: Dictionary containing transform data
        """
        super().deserialize(data)
        if "x" in data:
            self._x = float(data["x"])
        if "y" in data:
            self._y = float(data["y"])
        if "rotation" in data:
            self._rotation = float(data["rotation"])
        if "scale_x" in data:
            self._scale_x = float(data["scale_x"])
        if "scale_y" in data:
            self._scale_y = float(data["scale_y"])

    def __repr__(self) -> str:
        """Return string representation for debugging."""
        return (
            f"{self.__class__.__name__}"
            f"(name={self._name!r}, "
            f"position=({self._x:.1f}, {self._y:.1f}), "
            f"rotation={self._rotation:.1f}°, "
            f"scale=({self._scale_x:.1f}, {self._scale_y:.1f}))"
        )

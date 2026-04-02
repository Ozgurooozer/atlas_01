"""
Base Sprite class with transform properties.

This is the core Sprite class containing position, scale,
rotation, and basic lifecycle methods.

Layer: 2 (Engine)
Dependencies: core.object, core.vec
"""

from __future__ import annotations

from typing import Optional, Tuple, Union

from core.object import Object
from core.vec import Vec2


class SpriteBase(Object):
    """
    Base sprite with transform properties.

    Attributes:
        position: World position (Vec2).
        scale_x: Horizontal scale factor.
        scale_y: Vertical scale factor.
        rotation: Rotation in degrees.
        visible: Whether sprite should be rendered.
        z_index: Rendering order (higher = in front).
    """

    def __init__(
        self,
        position: Union[Vec2, Tuple[float, float]] = None,
        rotation: float = 0.0,
        scale: float = 1.0,
        name: Optional[str] = None
    ) -> None:
        """
        Create a base sprite.

        Args:
            position: Initial position (default 0, 0).
            rotation: Initial rotation in degrees.
            scale: Initial uniform scale.
            name: Optional sprite name.
        """
        super().__init__(name=name or "SpriteBase")

        # Position
        if position is None:
            self._position = Vec2(0.0, 0.0)
        elif isinstance(position, Vec2):
            self._position = position.copy()
        else:
            self._position = Vec2(position[0], position[1])

        # Scale
        self._scale_x: float = scale
        self._scale_y: float = scale

        # Rotation in degrees
        self._rotation: float = rotation

        # Visibility
        self._visible: bool = True

        # Z-order
        self._z_index: int = 0

        # Anchor point (0-1, default center)
        self._anchor_x: float = 0.5
        self._anchor_y: float = 0.5

    @property
    def position(self) -> Vec2:
        """Get position."""
        return self._position

    @position.setter
    def position(self, value: Union[Vec2, Tuple[float, float]]) -> None:
        """Set position."""
        if isinstance(value, Vec2):
            self._position = value.copy()
        else:
            self._position = Vec2(value[0], value[1])

    @property
    def scale_x(self) -> float:
        """Get X scale."""
        return self._scale_x

    @scale_x.setter
    def scale_x(self, value: float) -> None:
        """Set X scale."""
        self._scale_x = value

    @property
    def scale_y(self) -> float:
        """Get Y scale."""
        return self._scale_y

    @scale_y.setter
    def scale_y(self, value: float) -> None:
        """Set Y scale."""
        self._scale_y = value

    @property
    def rotation(self) -> float:
        """Get rotation in degrees."""
        return self._rotation

    @rotation.setter
    def rotation(self, value: float) -> None:
        """Set rotation in degrees."""
        self._rotation = value

    @property
    def visible(self) -> bool:
        """Get visibility."""
        return self._visible

    @visible.setter
    def visible(self, value: bool) -> None:
        """Set visibility."""
        self._visible = value

    @property
    def z_index(self) -> int:
        """Get z-index."""
        return self._z_index

    @z_index.setter
    def z_index(self, value: int) -> None:
        """Set z-index."""
        self._z_index = value

    @property
    def anchor_x(self) -> float:
        """Get X anchor."""
        return self._anchor_x

    @anchor_x.setter
    def anchor_x(self, value: float) -> None:
        """Set X anchor."""
        self._anchor_x = value

    @property
    def anchor_y(self) -> float:
        """Get Y anchor."""
        return self._anchor_y

    @anchor_y.setter
    def anchor_y(self, value: float) -> None:
        """Set Y anchor."""
        self._anchor_y = value

    def translate(self, dx: float, dy: float) -> None:
        """
        Move sprite by offset.

        Args:
            dx: X offset.
            dy: Y offset.
        """
        self._position = Vec2(
            self._position.x + dx,
            self._position.y + dy
        )

    def rotate(self, degrees: float) -> None:
        """
        Rotate sprite by angle.

        Args:
            degrees: Angle to add in degrees.
        """
        self._rotation += degrees

    def scale_by(self, factor: float) -> None:
        """
        Scale sprite uniformly.

        Args:
            factor: Scale factor to multiply.
        """
        self._scale_x *= factor
        self._scale_y *= factor

    def set_scale(self, value: float) -> None:
        """
        Set uniform scale.

        Args:
            value: New scale value.
        """
        self._scale_x = value
        self._scale_y = value

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"SpriteBase(pos=({self._position.x:.1f}, {self._position.y:.1f}), "
            f"scale=({self._scale_x:.2f}, {self._scale_y:.2f}), "
            f"rot={self._rotation:.1f}°)"
        )

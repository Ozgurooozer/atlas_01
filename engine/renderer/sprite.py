"""
Sprite class for rendering textured quads.

A Sprite represents a textured quad that can be rendered
by the renderer. Supports position, scale, rotation,
color tinting, and texture regions.

Layer: 2 (Engine)
Dependencies: core.object, core.vec, engine.renderer.texture
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple, Union, TYPE_CHECKING

from core.object import Object
from core.vec import Vec2

if TYPE_CHECKING:
    from engine.renderer.texture import Texture


class Sprite(Object):
    """
    Renderable sprite with transform and appearance properties.

    A Sprite combines a Texture with position, scale, rotation,
    and color properties for rendering.

    Attributes:
        texture: The texture to render.
        position: World position (Vec2).
        scale_x: Horizontal scale factor.
        scale_y: Vertical scale factor.
        rotation: Rotation in degrees.
        color: RGBA color tint (0-255 each).
        visible: Whether sprite should be rendered.
        z_index: Rendering order (higher = in front).
    """

    def __init__(
        self,
        texture: Optional[Texture] = None,
        position: Union[Vec2, Tuple[float, float]] = None,
        rotation: float = 0.0,
        scale: float = 1.0,
        region: Optional[Dict[str, Any]] = None,
        name: Optional[str] = None
    ) -> None:
        """
        Create a sprite.

        Args:
            texture: Texture to use.
            position: Initial position (default 0, 0).
            rotation: Initial rotation in degrees.
            scale: Initial uniform scale.
            region: Optional texture region dict.
            name: Optional sprite name.
        """
        super().__init__(name=name or "Sprite")
        self._texture: Optional[Texture] = texture
        self._region: Optional[Dict[str, Any]] = region

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

        # Color tint (RGBA, 0-255)
        self._color: Tuple[int, int, int, int] = (255, 255, 255, 255)

        # Visibility
        self._visible: bool = True

        # Z-order
        self._z_index: int = 0

        # Anchor point (0-1, default center)
        self._anchor_x: float = 0.5
        self._anchor_y: float = 0.5

        # Flip flags
        self._flip_x: bool = False
        self._flip_y: bool = False

    @property
    def texture(self) -> Optional[Texture]:
        """Get texture."""
        return self._texture

    @texture.setter
    def texture(self, value: Optional[Texture]) -> None:
        """Set texture."""
        self._texture = value

    @property
    def region(self) -> Optional[Dict[str, Any]]:
        """Get texture region."""
        return self._region

    @region.setter
    def region(self, value: Optional[Dict[str, Any]]) -> None:
        """Set texture region."""
        self._region = value

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
    def color(self) -> Tuple[int, int, int, int]:
        """Get color tint."""
        return self._color

    @color.setter
    def color(self, value: Tuple[int, int, int, int]) -> None:
        """Set color tint."""
        self._color = value

    @property
    def alpha(self) -> float:
        """Get alpha (0-1)."""
        return self._color[3] / 255.0

    @alpha.setter
    def alpha(self, value: float) -> None:
        """Set alpha (0-1)."""
        r, g, b, _ = self._color
        self._color = (r, g, b, int(value * 255))

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

    @property
    def flip_x(self) -> bool:
        """Get X flip."""
        return self._flip_x

    @flip_x.setter
    def flip_x(self, value: bool) -> None:
        """Set X flip."""
        self._flip_x = value

    @property
    def flip_y(self) -> bool:
        """Get Y flip."""
        return self._flip_y

    @flip_y.setter
    def flip_y(self, value: bool) -> None:
        """Set Y flip."""
        self._flip_y = value

    @property
    def width(self) -> float:
        """Get sprite width (including scale)."""
        base_width = self._get_base_width()
        return base_width * abs(self._scale_x)

    @property
    def height(self) -> float:
        """Get sprite height (including scale)."""
        base_height = self._get_base_height()
        return base_height * abs(self._scale_y)

    def _get_base_width(self) -> int:
        """Get base width from texture or region."""
        if self._region:
            return self._region['width']
        if self._texture:
            return self._texture.width
        return 0

    def _get_base_height(self) -> int:
        """Get base height from texture or region."""
        if self._region:
            return self._region['height']
        if self._texture:
            return self._texture.height
        return 0

    def get_bounds(self) -> Dict[str, float]:
        """
        Get axis-aligned bounding box.

        Returns:
            Dictionary with x, y, width, height.
        """
        w = self.width
        h = self.height

        # Offset by anchor
        offset_x = w * self._anchor_x
        offset_y = h * self._anchor_y

        return {
            'x': self._position.x - offset_x,
            'y': self._position.y - offset_y,
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

    def serialize(self) -> Dict[str, Any]:
        """Serialize sprite data."""
        data = super().serialize()
        data['position_x'] = self._position.x
        data['position_y'] = self._position.y
        data['scale_x'] = self._scale_x
        data['scale_y'] = self._scale_y
        data['rotation'] = self._rotation
        data['color'] = self._color
        data['visible'] = self._visible
        data['z_index'] = self._z_index
        return data

    def deserialize(self, data: Dict[str, Any]) -> None:
        """Deserialize sprite data."""
        super().deserialize(data)
        if 'position_x' in data:
            self._position = Vec2(data['position_x'], data.get('position_y', 0))
        if 'scale_x' in data:
            self._scale_x = data['scale_x']
        if 'scale_y' in data:
            self._scale_y = data['scale_y']
        if 'rotation' in data:
            self._rotation = data['rotation']
        if 'color' in data:
            self._color = tuple(data['color'])
        if 'visible' in data:
            self._visible = data['visible']
        if 'z_index' in data:
            self._z_index = data['z_index']

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"Sprite(pos=({self._position.x:.1f}, {self._position.y:.1f}), "
            f"scale=({self._scale_x:.2f}, {self._scale_y:.2f}), "
            f"rot={self._rotation:.1f}°, visible={self._visible})"
        )

"""
Sprite appearance properties mixin.

Contains texture, color, material, and rendering-related
properties for sprites.

Layer: 2 (Engine)
Dependencies: core.object, engine.renderer.texture
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from engine.renderer.texture import Texture
    from engine.renderer.material import Material


class SpriteAppearanceMixin:
    """
    Mixin class for sprite appearance properties.

    Attributes:
        texture: The texture to render.
        color: RGBA color tint (0-255 each).
        material: Optional material for advanced rendering.
        normal_map: Normal map texture ID for lighting.
        uv_offset: UV offset for texture atlas sampling.
        uv_size: UV size for texture atlas sampling.
        flip_x: Horizontal flip flag.
        flip_y: Vertical flip flag.
    """

    def __init__(self) -> None:
        """Initialize appearance properties."""
        # Texture
        self._texture: Optional[Texture] = None
        self._region: Optional[Dict[str, Any]] = None

        # Color tint (RGBA, 0-255)
        self._color: Tuple[int, int, int, int] = (255, 255, 255, 255)

        # Material and Normal Map
        self._material: Optional["Material"] = None
        self._normal_map: Optional[int] = None

        # UV region for texture atlases / tilemaps
        self._uv_offset: Tuple[float, float] = (0.0, 0.0)
        self._uv_size: Tuple[float, float] = (1.0, 1.0)

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
    def material(self) -> Optional["Material"]:
        """Get material."""
        return self._material

    @material.setter
    def material(self, value: Optional["Material"]) -> None:
        """Set material."""
        self._material = value

    @property
    def normal_map(self) -> Optional[int]:
        """Get normal map texture ID."""
        return self._normal_map

    @normal_map.setter
    def normal_map(self, value: Optional[int]) -> None:
        """Set normal map texture ID."""
        self._normal_map = value

    @property
    def uv_offset(self) -> Tuple[float, float]:
        """Get UV offset (normalized 0-1) for texture atlas sampling."""
        return self._uv_offset

    @uv_offset.setter
    def uv_offset(self, value: Tuple[float, float]) -> None:
        """Set UV offset."""
        self._uv_offset = value

    @property
    def uv_size(self) -> Tuple[float, float]:
        """Get UV size (normalized 0-1) for texture atlas sampling."""
        return self._uv_size

    @uv_size.setter
    def uv_size(self, value: Tuple[float, float]) -> None:
        """Set UV size."""
        self._uv_size = value

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

    def set_uv_region(self, u0: float, v0: float, u1: float, v1: float) -> None:
        """
        Set UV region directly from normalized coordinates.

        Args:
            u0: Left U (0-1)
            v0: Top V (0-1)
            u1: Right U (0-1)
            v1: Bottom V (0-1)
        """
        self._uv_offset = (u0, v0)
        self._uv_size = (u1 - u0, v1 - v0)

    def _get_base_width(self) -> int:
        """Get base width from texture or region."""
        if self._region:
            return self._region['width']
        if self._texture:
            return self._texture.width  # type: ignore[union-attr]
        return 0

    def _get_base_height(self) -> int:
        """Get base height from texture or region."""
        if self._region:
            return self._region['height']
        if self._texture:
            return self._texture.height  # type: ignore[union-attr]
        return 0

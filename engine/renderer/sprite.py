"""
Sprite class for rendering textured quads.

A Sprite represents a textured quad that can be rendered
by the renderer. Supports position, scale, rotation,
color tinting, and texture regions.

Layer: 2 (Engine)
Dependencies: core.object, core.vec, engine.renderer.texture

This module re-exports the composed Sprite class.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple, Union, TYPE_CHECKING

from core.vec import Vec2
from engine.renderer.sprite_base import SpriteBase
from engine.renderer.sprite_appearance import SpriteAppearanceMixin
from engine.renderer.sprite_bounds import SpriteBoundsMixin
from engine.renderer.sprite_serialization import SpriteSerializationMixin

if TYPE_CHECKING:
    from engine.renderer.texture import Texture


class Sprite(SpriteBase, SpriteAppearanceMixin, SpriteBoundsMixin, SpriteSerializationMixin):
    """
    Renderable sprite with transform and appearance properties.

    A Sprite combines a Texture with position, scale, rotation,
    and color properties for rendering.

    Composition of:
        - SpriteBase: Transform (position, scale, rotation, visibility)
        - SpriteAppearanceMixin: Appearance (texture, color, material, UV)
        - SpriteBoundsMixin: Bounds calculations (width, height, collision)
        - SpriteSerializationMixin: Save/load support

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
        # Initialize base (transform)
        SpriteBase.__init__(self, position=position, rotation=rotation, scale=scale, name=name)
        
        # Initialize appearance
        SpriteAppearanceMixin.__init__(self)
        
        # Set texture and region after appearance init
        self._texture = texture
        self._region = region

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"Sprite(pos=({self._position.x:.1f}, {self._position.y:.1f}), "
            f"scale=({self._scale_x:.2f}, {self._scale_y:.2f}), "
            f"rot={self._rotation:.1f}°, visible={self._visible})"
        )

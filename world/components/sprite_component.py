"""
SpriteComponent for 2D rendering.

Provides a way to attach a Sprite to an Actor and render it
using the Renderer2D system.

Layer: 3 (World)
Dependencies: world.component, engine.renderer.sprite
"""

from __future__ import annotations
from typing import Any, Dict, Optional, TYPE_CHECKING

from world.component import Component
from world.transform import TransformComponent

if TYPE_CHECKING:
    from engine.renderer.sprite import Sprite
    from engine.renderer.texture import Texture


class SpriteComponent(Component):
    """
    Component that renders a Sprite at the Actor's transform position.
    
    Attributes:
        sprite: The Sprite instance to render.
        renderer: The Renderer2D instance (injected).
    """

    def __init__(self, sprite: Optional[Sprite] = None, name: str = None) -> None:
        """
        Initialize the SpriteComponent.
        
        Args:
            sprite: The Sprite instance to render.
            name: Optional name.
        """
        super().__init__(name)
        self.sprite = sprite
        self.renderer: Any = None  # Injected by EngineContext

    @property
    def z_index(self) -> int:
        """Get sprite z-index."""
        return self.sprite.z_index if self.sprite else 0

    @z_index.setter
    def z_index(self, value: int) -> None:
        """Set sprite z-index."""
        if self.sprite:
            self.sprite.z_index = value

    @property
    def color(self) -> tuple:
        """Get sprite color (r, g, b, a)."""
        return self.sprite.color if self.sprite else (255, 255, 255, 255)

    @color.setter
    def color(self, value: tuple) -> None:
        """Set sprite color (r, g, b, a)."""
        if self.sprite:
            self.sprite.color = value

    @property
    def flip_x(self) -> bool:
        """Get sprite horizontal flip."""
        return self.sprite.flip_x if self.sprite else False

    @flip_x.setter
    def flip_x(self, value: bool) -> None:
        """Set sprite horizontal flip."""
        if self.sprite:
            self.sprite.flip_x = value

    @property
    def flip_y(self) -> bool:
        """Get sprite vertical flip."""
        return self.sprite.flip_y if self.sprite else False

    @flip_y.setter
    def flip_y(self, value: bool) -> None:
        """Set sprite vertical flip."""
        if self.sprite:
            self.sprite.flip_y = value

    @property
    def texture(self) -> Optional[Texture]:
        """Get sprite texture."""
        return self.sprite.texture if self.sprite else None

    @texture.setter
    def texture(self, value: Texture) -> None:
        """Set sprite texture."""
        if self.sprite:
            self.sprite.texture = value

    def on_tick(self, dt: float) -> None:
        """
        Update and render the sprite.
        
        Args:
            dt: Delta time in seconds.
        """
        if not self.sprite or not self.renderer or not self.owner:
            return

        # Synchronize with TransformComponent if available
        transform = self.owner.get_component(TransformComponent)
        if transform:
            # Use world position for rendering
            wx, wy = transform.world_position
            self.sprite.position = (wx, wy)
            self.sprite.rotation = transform.world_rotation
            
            # Apply world scale
            wsx, wsy = transform.world_scale
            # Note: Sprite width/height are usually based on texture size * scale
            # We assume the sprite's internal scale is handled or we set it here
            # For now, we just sync position and rotation as per requirements
            
        # Render the sprite
        if self.sprite.visible:
            self.renderer.draw_sprite(self.sprite)

    def serialize(self) -> Dict[str, Any]:
        """Serialize the component."""
        data = super().serialize()
        if self.sprite:
            data["z_index"] = self.sprite.z_index
            data["color"] = self.sprite.color
            data["flip_x"] = self.sprite.flip_x
            data["flip_y"] = self.sprite.flip_y
            # Texture serialization would normally be a path or ID
        return data

    def deserialize(self, data: Dict[str, Any]) -> None:
        """Deserialize the component."""
        super().deserialize(data)
        if self.sprite:
            if "z_index" in data:
                self.sprite.z_index = data["z_index"]
            if "color" in data:
                self.sprite.color = tuple(data["color"])
            if "flip_x" in data:
                self.sprite.flip_x = data["flip_x"]
            if "flip_y" in data:
                self.sprite.flip_y = data["flip_y"]

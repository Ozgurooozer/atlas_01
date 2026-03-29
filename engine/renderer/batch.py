"""
SpriteBatch for efficient sprite rendering.

Batches sprites by texture for efficient GPU rendering.
Sorts sprites by z-index for correct layering.

Layer: 2 (Engine)
Dependencies: engine.renderer.sprite, engine.renderer.texture
"""

from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING

from engine.renderer.sprite import Sprite

if TYPE_CHECKING:
    from engine.renderer.renderer import Renderer2D
    from engine.renderer.texture import Texture


class SpriteBatch:
    """
    Batch renderer for sprites.

    Collects sprites during begin()/end() block and renders
    them efficiently by sorting and texture batching.

    Example:
        >>> batch = SpriteBatch(renderer)
        >>> batch.begin()
        >>> batch.draw(sprite1)
        >>> batch.draw(sprite2)
        >>> batch.end()  # Renders all sprites

    Attributes:
        renderer: The Renderer2D to submit draws to.
        max_sprites: Maximum sprites per batch.
        flush_count: Number of flushes in current batch.
        texture_changes: Number of texture changes in current batch.
    """

    def __init__(
        self,
        renderer: Optional["Renderer2D"] = None,
        max_sprites: int = 1000,
        instancing_enabled: bool = False
    ) -> None:
        """
        Create a new SpriteBatch.

        Args:
            renderer: Optional Renderer2D to submit to.
            max_sprites: Maximum sprites per batch.
            instancing_enabled: Whether to use GPU instancing.
        """
        self._renderer: Optional["Renderer2D"] = renderer
        self._max_sprites: int = max_sprites
        self._instancing_enabled: bool = instancing_enabled
        self._sprites: List[Sprite] = []
        self._in_batch: bool = False
        self._flush_count: int = 0
        self._texture_changes: int = 0
        self._sorted_sprites: List[Sprite] = []

    @property
    def instancing_enabled(self) -> bool:
        """Get whether instancing is enabled."""
        return self._instancing_enabled

    @instancing_enabled.setter
    def instancing_enabled(self, value: bool) -> None:
        """Set whether instancing is enabled."""
        if self._instancing_enabled != value:
            if self._in_batch:
                self.flush()
            self._instancing_enabled = value

    @property
    def renderer(self) -> Optional["Renderer2D"]:
        """Get the renderer."""
        return self._renderer

    @renderer.setter
    def renderer(self, value: Optional["Renderer2D"]) -> None:
        """Set the renderer."""
        self._renderer = value

    @property
    def max_sprites(self) -> int:
        """Get max sprites per batch."""
        return self._max_sprites

    @property
    def flush_count(self) -> int:
        """Get number of flushes in current batch."""
        return self._flush_count

    @property
    def texture_changes(self) -> int:
        """Get number of texture changes in current batch."""
        return self._texture_changes

    @property
    def sprite_count(self) -> int:
        """Get number of sprites in current batch."""
        return len(self._sprites)

    @property
    def sorted_sprites(self) -> List[Sprite]:
        """Get sorted sprites (available after end())."""
        return self._sorted_sprites

    def begin(self) -> None:
        """
        Begin a new batch.

        Clears previous sprites and prepares for drawing.
        """
        self._sprites.clear()
        self._sorted_sprites.clear()
        self._in_batch = True
        self._flush_count = 0
        self._texture_changes = 0

    def draw(self, sprite: Sprite) -> None:
        """
        Add a sprite to the batch.

        Args:
            sprite: The Sprite to add.

        Raises:
            RuntimeError: If called outside begin()/end().
        """
        if not self._in_batch:
            raise RuntimeError("draw() must be called between begin() and end()")

        # Check if we need to flush before adding
        if len(self._sprites) >= self._max_sprites:
            self.flush()

        self._sprites.append(sprite)

    def end(self) -> None:
        """
        End the batch and render all sprites.

        Sorts sprites by z-index and submits to renderer.
        """
        if not self._in_batch:
            return

        self._in_batch = False
        self.flush()

    def flush(self) -> None:
        """
        Flush current batch to renderer.

        Sorts by z-index, then groups by texture and material.
        """
        if not self._sprites:
            return

        # 1. Sort by z_index (Gereksinim 3.4)
        self._sorted_sprites = sorted(self._sprites, key=lambda s: s.z_index)

        if self._instancing_enabled:
            self._flush_instanced()
        else:
            self._flush_legacy()

        self._sprites.clear()
        self._flush_count += 1

    def _flush_legacy(self) -> None:
        """Standard non-instanced flush."""
        current_texture: Optional["Texture"] = None
        current_material: Optional[object] = None

        for sprite in self._sorted_sprites:
            texture_changed = sprite.texture != current_texture
            material_changed = sprite.material != current_material

            if texture_changed or material_changed:
                current_texture = sprite.texture
                current_material = sprite.material
                self._texture_changes += 1

            if self._renderer:
                self._renderer.draw_sprite(sprite)

    def _flush_instanced(self) -> None:
        """GPU instanced flush."""
        if not self._renderer or not self._renderer.gpu_device:
            self._flush_legacy()
            return

        from engine.renderer.instance_data import InstanceData
        
        # Group by texture (Instancing currently only supports single texture per call)
        # Note: Material support for instancing would require more complex shader/uniform management
        groups = {}
        for sprite in self._sorted_sprites:
            tex = sprite.texture
            if tex not in groups:
                groups[tex] = []
            groups[tex].append(sprite)

        self._texture_changes = len(groups)
        
        view_matrix = self._renderer._camera.view_matrix if self._renderer._camera else None
        projection_matrix = self._renderer._camera.projection_matrix if self._renderer._camera else None

        for tex, sprites in groups.items():
            self._renderer._ensure_uploaded(tex)
            
            instance_bytes = bytearray()
            for s in sprites:
                # Convert color from 0-255 to 0.0-1.0
                r, g, b, a = s.color
                gpu_color = (r / 255.0, g / 255.0, b / 255.0, a / 255.0)
                
                data = InstanceData(
                    position=(s.position.x, s.position.y),
                    size=(s.width, s.height),
                    rotation=s.rotation,
                    color=gpu_color,
                    anchor=(s.anchor_x, s.anchor_y),
                    flip=(1.0 if s.flip_x else 0.0, 1.0 if s.flip_y else 0.0),
                    uv_offset=getattr(s, 'uv_offset', (0.0, 0.0)),
                    uv_size=getattr(s, 'uv_size', (1.0, 1.0)),
                )
                instance_bytes.extend(data.to_bytes())
            
            self._renderer.gpu_device.draw_instanced(
                tex.gpu_id,
                bytes(instance_bytes),
                len(sprites),
                view_matrix=view_matrix,
                projection_matrix=projection_matrix
            )

    def __enter__(self) -> "SpriteBatch":
        """Context manager entry."""
        self.begin()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.end()

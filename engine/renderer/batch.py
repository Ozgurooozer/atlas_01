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
        max_sprites: int = 1000
    ) -> None:
        """
        Create a new SpriteBatch.

        Args:
            renderer: Optional Renderer2D to submit to.
            max_sprites: Maximum sprites per batch.
        """
        self._renderer: Optional["Renderer2D"] = renderer
        self._max_sprites: int = max_sprites
        self._sprites: List[Sprite] = []
        self._in_batch: bool = False
        self._flush_count: int = 0
        self._texture_changes: int = 0
        self._sorted_sprites: List[Sprite] = []

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

        if len(self._sprites) < self._max_sprites:
            self._sprites.append(sprite)

    def end(self) -> None:
        """
        End the batch and render all sprites.

        Sorts sprites by z-index and submits to renderer.
        """
        if not self._in_batch:
            return

        self._in_batch = False

        if not self._sprites:
            return

        # Sort by z_index
        self._sorted_sprites = sorted(self._sprites, key=lambda s: s.z_index)

        # Track texture changes for batching stats
        current_texture: Optional["Texture"] = None
        self._texture_changes = 0

        # Count texture changes and submit to renderer
        for sprite in self._sorted_sprites:
            if sprite.texture != current_texture:
                current_texture = sprite.texture
                self._texture_changes += 1
            if self._renderer:
                self._renderer.draw_sprite(sprite)

        self._flush_count = 1

    def flush(self) -> None:
        """
        Flush current batch to renderer.

        Allows for mid-batch rendering (e.g., for layering).
        """
        if not self._sprites:
            return

        # Sort and render
        sorted_sprites = sorted(self._sprites, key=lambda s: s.z_index)

        current_texture: Optional["Texture"] = None

        if self._renderer:
            for sprite in sorted_sprites:
                if sprite.texture != current_texture:
                    current_texture = sprite.texture
                    self._texture_changes += 1
                self._renderer.draw_sprite(sprite)

        self._sprites.clear()
        self._flush_count += 1

    def __enter__(self) -> "SpriteBatch":
        """Context manager entry."""
        self.begin()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.end()

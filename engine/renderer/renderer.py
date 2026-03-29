"""
Renderer Subsystem.

Provides 2D rendering using GPU device abstraction.
Uses ModernGL in production, HeadlessGPU for tests.

Layer: 2 (Engine)
Dependencies: engine.subsystem, hal.interfaces
"""

from __future__ import annotations
from abc import abstractmethod
from typing import Optional, Set, Tuple, TYPE_CHECKING

from engine.subsystem import ISubsystem

if TYPE_CHECKING:
    from engine.engine import Engine
    from engine.renderer.sprite import Sprite
    from engine.renderer.texture import Texture
    from hal.interfaces import IGPUDevice


class IRenderer(ISubsystem):
    """
    Interface for rendering subsystems.

    Extends ISubsystem with rendering-specific methods.
    All renderers must implement clear() and present().
    """

    @abstractmethod
    def clear(self, r: float = 0.0, g: float = 0.0, b: float = 0.0, a: float = 1.0) -> None:
        """
        Clear the screen with the given color.

        Args:
            r: Red component (0.0 - 1.0)
            g: Green component (0.0 - 1.0)
            b: Blue component (0.0 - 1.0)
            a: Alpha component (0.0 - 1.0)
        """
        pass

    @abstractmethod
    def present(self) -> None:
        """
        Present the rendered frame.

        Swaps buffers or presents to screen.
        """
        pass


class Renderer2D(IRenderer):
    """
    2D Renderer implementation.

    Provides basic 2D rendering capabilities:
    - Clear screen with background color
    - Present frame to display
    - Viewport management
    - Sprite and texture drawing

    Uses IGPUDevice abstraction for GPU operations.
    Works with HeadlessGPU for testing.

    Example:
        >>> renderer = Renderer2D()
        >>> renderer.gpu_device = HeadlessGPU()
        >>> renderer.initialize(engine)
        >>> renderer.clear(0.1, 0.1, 0.1, 1.0)
        >>> # Draw sprites here...
        >>> renderer.present()

    Attributes:
        gpu_device: The GPU device to use for rendering
        background_color: Default clear color (rgba tuple)
        viewport: Viewport rectangle (x, y, width, height)
        enabled: Whether rendering is active
        draw_count: Number of draw calls this frame
        texture_count: Number of unique textures used this frame
    """

    def __init__(self):
        """Create a new Renderer2D."""
        self._gpu_device: Optional["IGPUDevice"] = None
        self._background_color: Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 1.0)
        self._viewport: Tuple[int, int, int, int] = (0, 0, 800, 600)
        self._enabled: bool = True
        self._draw_count: int = 0
        self._texture_count: int = 0
        self._used_textures: Set[int] = set()

    @property
    def name(self) -> str:
        """Get subsystem name."""
        return "renderer"

    @property
    def gpu_device(self) -> Optional["IGPUDevice"]:
        """Get the GPU device."""
        return self._gpu_device

    @gpu_device.setter
    def gpu_device(self, value: Optional["IGPUDevice"]) -> None:
        """Set the GPU device."""
        self._gpu_device = value

    @property
    def background_color(self) -> Tuple[float, float, float, float]:
        """Get the background color."""
        return self._background_color

    @background_color.setter
    def background_color(self, value: Tuple[float, float, float, float]) -> None:
        """Set the background color."""
        self._background_color = value

    @property
    def viewport(self) -> Tuple[int, int, int, int]:
        """Get the viewport."""
        return self._viewport

    @viewport.setter
    def viewport(self, value: Tuple[int, int, int, int]) -> None:
        """Set the viewport."""
        self._viewport = value

    @property
    def enabled(self) -> bool:
        """Get whether rendering is enabled."""
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """Set whether rendering is enabled."""
        self._enabled = value

    @property
    def draw_count(self) -> int:
        """Get number of draw calls this frame."""
        return self._draw_count

    @property
    def texture_count(self) -> int:
        """Get number of unique textures used this frame."""
        return self._texture_count

    def initialize(self, engine: "Engine") -> None:
        """
        Initialize the renderer.

        Args:
            engine: Reference to the Engine instance
        """
        # Renderer is ready to use after initialization
        # GPU device should be set before or after
        pass

    def tick(self, dt: float) -> None:
        """
        Update the renderer for one frame.

        Resets draw statistics and clears the screen.

        Args:
            dt: Delta time in seconds
        """
        if not self._enabled:
            return

        # Reset frame statistics
        self._draw_count = 0
        self._texture_count = 0
        self._used_textures.clear()

        # Clear with background color at start of frame
        if self._gpu_device:
            r, g, b, a = self._background_color
            self._gpu_device.clear(r, g, b, a)

    def shutdown(self) -> None:
        """
        Clean up renderer resources.

        Clears GPU device reference.
        """
        self._gpu_device = None

    def clear(self, r: float = 0.0, g: float = 0.0, b: float = 0.0, a: float = 1.0) -> None:
        """
        Clear the screen with the given color.

        Args:
            r: Red component (0.0 - 1.0)
            g: Green component (0.0 - 1.0)
            b: Blue component (0.0 - 1.0)
            a: Alpha component (0.0 - 1.0)
        """
        if self._gpu_device:
            self._gpu_device.clear(r, g, b, a)

    def present(self) -> None:
        """
        Present the rendered frame.

        Flushes GPU commands.
        """
        if self._gpu_device:
            self._gpu_device.flush()

    def _ensure_uploaded(self, texture: "Texture") -> None:
        """Texture GPU'ya yüklenmemişse yükle."""
        if not texture.is_uploaded and self._gpu_device:
            gpu_id = self._gpu_device.create_texture(
                texture.width, texture.height, texture.data
            )
            texture.mark_uploaded(gpu_id)

    def _track_texture(self, texture: "Texture") -> None:
        """Draw istatistiklerini güncelle."""
        self._draw_count += 1
        if texture.gpu_id not in self._used_textures:
            self._used_textures.add(texture.gpu_id)
            self._texture_count += 1

    def draw_sprite(self, sprite: "Sprite") -> None:
        """
        Draw a sprite.

        Handles texture upload, position, scale, rotation, and visibility.

        Args:
            sprite: The Sprite to draw.
        """
        # Skip if no GPU device
        if not self._gpu_device:
            return

        # Skip if sprite is not visible
        if not sprite.visible:
            return

        # Skip if sprite has no texture
        if sprite.texture is None:
            return

        # Upload texture to GPU if needed
        texture = sprite.texture
        self._ensure_uploaded(texture)

        # Calculate draw parameters
        x = sprite.position.x
        y = sprite.position.y
        width = sprite.width
        height = sprite.height

        self._gpu_device.draw(texture.gpu_id, x, y, width, height)
        self._track_texture(texture)

    def draw_texture(
        self,
        texture: "Texture",
        x: float,
        y: float,
        width: Optional[float] = None,
        height: Optional[float] = None
    ) -> None:
        """
        Draw a texture at the specified position.

        Args:
            texture: The Texture to draw.
            x: X position in screen coordinates.
            y: Y position in screen coordinates.
            width: Optional width (defaults to texture width).
            height: Optional height (defaults to texture height).
        """
        # Skip if no GPU device
        if not self._gpu_device:
            return

        # Upload texture to GPU if needed
        self._ensure_uploaded(texture)

        if width is None:
            width = float(texture.width)
        if height is None:
            height = float(texture.height)

        self._gpu_device.draw(texture.gpu_id, x, y, width, height)
        self._track_texture(texture)

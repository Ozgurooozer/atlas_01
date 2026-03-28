"""
Pyglet Backend - Real Window and GPU implementations.

This module provides real implementations of IWindow and IGPUDevice
using pyglet for windowing and moderngl for GPU operations.

Layer: 0 (HAL)
Dependencies: hal.interfaces, pyglet, moderngl
"""

from __future__ import annotations
from typing import Tuple, Optional, List, TYPE_CHECKING

from hal.interfaces import IWindow, IGPUDevice

if TYPE_CHECKING:
    import moderngl


class PygletWindow(IWindow):
    """
    Pyglet-based window implementation.

    Uses pyglet for window management and event handling.
    Works on Windows, macOS, and Linux with a display.

    Example:
        >>> window = PygletWindow(800, 600, "My Game")
        >>> while not window.should_close():
        ...     events = window.poll_events()
        ...     # process events
        ...     window.swap_buffers()
    """

    def __init__(self, width: int = 800, height: int = 600, title: str = "Engine"):
        """
        Create a pyglet window.

        Args:
            width: Window width in pixels
            height: Window height in pixels
            title: Window title
        """
        import pyglet

        self._width = width
        self._height = height
        self._title = title
        self._events: List = []
        self._should_close = False

        # Create pyglet window
        self._window = pyglet.window.Window(
            width=width,
            height=height,
            caption=title,
            resizable=True
        )

        # Set up event handlers
        @self._window.event
        def on_close():
            self._should_close = True

        @self._window.event
        def on_resize(w, h):
            self._width = w
            self._height = h
            self._events.append({
                "type": "resize",
                "width": w,
                "height": h
            })

        @self._window.event
        def on_key_press(symbol, modifiers):
            self._events.append({
                "type": "key_press",
                "symbol": symbol,
                "modifiers": modifiers
            })

        @self._window.event
        def on_key_release(symbol, modifiers):
            self._events.append({
                "type": "key_release",
                "symbol": symbol,
                "modifiers": modifiers
            })

        @self._window.event
        def on_mouse_press(x, y, button, modifiers):
            self._events.append({
                "type": "mouse_press",
                "x": x,
                "y": y,
                "button": button,
                "modifiers": modifiers
            })

        @self._window.event
        def on_mouse_release(x, y, button, modifiers):
            self._events.append({
                "type": "mouse_release",
                "x": x,
                "y": y,
                "button": button,
                "modifiers": modifiers
            })

        @self._window.event
        def on_mouse_motion(x, y, dx, dy):
            self._events.append({
                "type": "mouse_motion",
                "x": x,
                "y": y,
                "dx": dx,
                "dy": dy
            })

    def poll_events(self) -> list:
        """
        Poll and return pending window events.

        Returns:
            List of event dictionaries
        """
        import pyglet

        # Dispatch pending events
        pyglet.clock.tick()
        self._window.dispatch_events()

        # Return and clear collected events
        events = self._events.copy()
        self._events.clear()
        return events

    def swap_buffers(self) -> None:
        """Swap front and back buffers."""
        self._window.flip()

    def should_close(self) -> bool:
        """
        Check if window should close.

        Returns:
            True if window should close
        """
        return self._should_close or self._window.has_exit

    def get_size(self) -> Tuple[int, int]:
        """
        Get window size in pixels.

        Returns:
            Tuple of (width, height)
        """
        return (self._width, self._height)

    def close(self) -> None:
        """Close the window."""
        self._should_close = True
        self._window.close()

    @property
    def pyglet_window(self):
        """Get the underlying pyglet window."""
        return self._window


class ModernGLDevice(IGPUDevice):
    """
    ModernGL-based GPU device implementation.

    Uses moderngl for GPU operations. Requires a pyglet window
    for the OpenGL context.

    Example:
        >>> window = PygletWindow(800, 600)
        >>> gpu = ModernGLDevice(window)
        >>> texture_id = gpu.create_texture(64, 64)
    """

    def __init__(self, window: PygletWindow):
        """
        Create a ModernGL device.

        Args:
            window: PygletWindow to get GL context from
        """
        import moderngl

        self._window = window
        self._ctx = moderngl.create_context()
        self._textures = {}  # id -> Texture
        self._next_texture_id = 1

    def create_texture(self, width: int, height: int, data: bytes = None) -> int:
        """
        Create a texture on the GPU.

        Args:
            width: Texture width in pixels
            height: Texture height in pixels
            data: Optional initial pixel data (RGBA)

        Returns:
            Texture handle/ID
        """
        texture = self._ctx.texture((width, height), 4, data)
        texture_id = self._next_texture_id
        self._next_texture_id += 1
        self._textures[texture_id] = texture
        return texture_id

    def clear(self, r: float = 0.0, g: float = 0.0, b: float = 0.0, a: float = 1.0) -> None:
        """
        Clear the screen with specified color.

        Args:
            r: Red component (0.0 - 1.0)
            g: Green component (0.0 - 1.0)
            b: Blue component (0.0 - 1.0)
            a: Alpha component (0.0 - 1.0)
        """
        self._ctx.clear(r, g, b, a)

    def draw(self, texture_id: int, x: float, y: float, width: float = None, height: float = None) -> None:
        """
        Draw a texture at specified position.

        Note: This is a simplified implementation. A full implementation
        would use a sprite batch for efficient rendering.

        Args:
            texture_id: Texture handle from create_texture
            x: X position in screen coordinates
            y: Y position in screen coordinates
            width: Optional width (defaults to texture width)
            height: Optional height (defaults to texture height)
        """
        if texture_id not in self._textures:
            return

        texture = self._textures[texture_id]
        # Full sprite rendering would go here
        # For now, this is a placeholder
        texture.use(location=0)

    def get_texture(self, texture_id: int) -> Optional["moderngl.Texture"]:
        """
        Get a texture by ID.

        Args:
            texture_id: Texture handle

        Returns:
            ModernGL Texture or None
        """
        return self._textures.get(texture_id)

    def delete_texture(self, texture_id: int) -> None:
        """
        Delete a texture from GPU memory.

        Args:
            texture_id: Texture handle to delete
        """
        if texture_id in self._textures:
            self._textures[texture_id].release()
            del self._textures[texture_id]

    @property
    def context(self) -> "moderngl.Context":
        """Get the ModernGL context."""
        return self._ctx

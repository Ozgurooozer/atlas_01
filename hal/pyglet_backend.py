"""
Pyglet Backend - Real Window and GPU implementations.

This module provides real implementations of IWindow and IGPUDevice
using pyglet for windowing and moderngl for GPU operations.

Layer: 0 (HAL)
Dependencies: hal.interfaces, pyglet, moderngl
"""

from __future__ import annotations
import struct
from typing import Dict, Tuple, Optional, List, TYPE_CHECKING

from hal.interfaces import IWindow, IGPUDevice, IFramebuffer

if TYPE_CHECKING:
    import moderngl


class ShaderCompileError(Exception):
    """Raised when GLSL shader compilation fails."""


DEFAULT_SPRITE_VERTEX_SRC = """
#version 330 core

in vec2 a_position;
in vec2 a_texcoord;
in vec4 a_color;

out vec2 v_texcoord;
out vec4 v_color;

void main() {
    gl_Position = vec4(a_position, 0.0, 1.0);
    v_texcoord = a_texcoord;
    v_color = a_color;
}
"""

DEFAULT_SPRITE_FRAGMENT_SRC = """
#version 330 core

uniform sampler2D u_texture;

in vec2 v_texcoord;
in vec4 v_color;

out vec4 f_color;

void main() {
    f_color = texture(u_texture, v_texcoord) * v_color;
}
"""


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

    def __init__(
        self,
        window: PygletWindow,
        vertex_src: str = DEFAULT_SPRITE_VERTEX_SRC,
        fragment_src: str = DEFAULT_SPRITE_FRAGMENT_SRC,
    ):
        """
        Create a ModernGL device.

        Args:
            window: PygletWindow to get GL context from
            vertex_src: GLSL vertex shader source (DI, defaults to DEFAULT_SPRITE_VERTEX_SRC)
            fragment_src: GLSL fragment shader source (DI, defaults to DEFAULT_SPRITE_FRAGMENT_SRC)
        """
        import moderngl  # lazy import — only when real GPU context needed

        self._ctx = moderngl.create_context()

        # Alpha blending — şeffaf texture'lar için
        self._ctx.enable(moderngl.BLEND)
        self._ctx.blend_func = (moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA)

        self._program = self._compile_program(vertex_src, fragment_src)
        self._vbo = self._ctx.buffer(reserve=4 * 8 * 4)  # 4 vertices × 8 floats × 4 bytes
        self._vao = self._ctx.vertex_array(
            self._program,
            [(self._vbo, "2f 2f 4f", "a_position", "a_texcoord", "a_color")]
        )
        self._textures: Dict[int, "moderngl.Texture"] = {}
        self._next_id = 1
        self._window = window
        self._viewport: Tuple[int, int] = window.get_size()

    def _compile_program(self, vert: str, frag: str) -> "moderngl.Program":
        """
        Compile and link a GLSL shader program.

        Args:
            vert: Vertex shader source
            frag: Fragment shader source

        Returns:
            Compiled moderngl.Program

        Raises:
            ShaderCompileError: If compilation or linking fails
        """
        try:
            return self._ctx.program(vertex_shader=vert, fragment_shader=frag)
        except Exception as e:
            raise ShaderCompileError(str(e)) from e

    def create_texture(self, width: int, height: int, data: bytes = None) -> int:
        if data is None:
            data = bytes(width * height * 4)
        texture = self._ctx.texture((width, height), 4, data)
        # Linear filtering — scale edildiğinde smooth görünüm
        import moderngl
        texture.filter = (moderngl.LINEAR, moderngl.LINEAR)
        texture_id = self._next_id
        self._next_id += 1
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

        Converts screen coordinates to NDC, builds quad vertices,
        writes to VBO, binds texture, and issues a draw call.

        Args:
            texture_id: Texture handle from create_texture
            x: X position in screen coordinates
            y: Y position in screen coordinates
            width: Optional width (defaults to texture width)
            height: Optional height (defaults to texture height)
        """
        # Req 3.2 — silently return for invalid texture_id
        if texture_id not in self._textures:
            return

        texture = self._textures[texture_id]

        # Req 3.3 — use texture's actual pixel dimensions when w/h is None
        if width is None:
            width = texture.size[0]
        if height is None:
            height = texture.size[1]

        # Viewport'u her draw'da güncel tut (resize desteği)
        self._viewport = self._window.get_size()
        vp_w, vp_h = self._viewport

        # Req 3.4 — screen coords → NDC
        # Y ekseni: OpenGL Y aşağıdan yukarı, ekran Y yukarıdan aşağı → flip
        ndc_x = (x / vp_w) * 2.0 - 1.0
        ndc_y = 1.0 - ((y + height) / vp_h) * 2.0   # flip + top-left origin
        ndc_w = (width / vp_w) * 2.0
        ndc_h = (height / vp_h) * 2.0

        # 4 vertex, triangle strip: position(vec2), texcoord(vec2), color(vec4)
        # top-left, bottom-left, top-right, bottom-right
        vertices = [
            ndc_x,         ndc_y + ndc_h,  0.0, 0.0,  1.0, 1.0, 1.0, 1.0,
            ndc_x,         ndc_y,          0.0, 1.0,  1.0, 1.0, 1.0, 1.0,
            ndc_x + ndc_w, ndc_y + ndc_h,  1.0, 0.0,  1.0, 1.0, 1.0, 1.0,
            ndc_x + ndc_w, ndc_y,          1.0, 1.0,  1.0, 1.0, 1.0, 1.0,
        ]

        import moderngl
        self._vbo.write(struct.pack("32f", *vertices))
        texture.use(location=0)
        self._vao.render(moderngl.TRIANGLE_STRIP)

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

    def flush(self) -> None:
        """Flush pending GPU commands."""
        self._ctx.finish()

    def create_framebuffer(self, width: int, height: int) -> "IFramebuffer":
        """
        Create an off-screen framebuffer.

        Args:
            width: Framebuffer width in pixels
            height: Framebuffer height in pixels

        Returns:
            ModernGLFramebuffer instance
        """
        return ModernGLFramebuffer(self._ctx, width, height)

    @property
    def context(self) -> "moderngl.Context":
        """Get the ModernGL context."""
        return self._ctx


class ModernGLFramebuffer(IFramebuffer):
    """
    ModernGL-based framebuffer implementation.

    Provides off-screen render-to-texture capability.
    Implements IFramebuffer (Requirements 4.1–4.5).
    """

    def __init__(self, ctx: "moderngl.Context", width: int, height: int):
        self._ctx = ctx
        self._width = width
        self._height = height
        self._fbo = self._create(width, height)

    def _create(self, w: int, h: int):
        color = self._ctx.texture((w, h), 4)
        depth = self._ctx.depth_renderbuffer((w, h))
        return self._ctx.framebuffer(color_attachments=[color], depth_attachment=depth)

    def bind(self) -> None:
        """Bind framebuffer for rendering."""
        self._fbo.use()

    def unbind(self) -> None:
        """Unbind framebuffer (restore default)."""
        self._ctx.screen.use()

    def resize(self, width: int, height: int) -> None:
        """Resize framebuffer."""
        self._fbo.release()
        self._width = width
        self._height = height
        self._fbo = self._create(width, height)

    def dispose(self) -> None:
        """Release framebuffer resources."""
        self._fbo.release()

    @property
    def width(self) -> int:
        """Framebuffer width."""
        return self._width

    @property
    def height(self) -> int:
        """Framebuffer height."""
        return self._height

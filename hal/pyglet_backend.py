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

uniform mat4 u_view;
uniform mat4 u_projection;
uniform vec2 u_position;
uniform float u_rotation;
uniform vec2 u_anchor;
uniform vec2 u_size;

out vec2 v_texcoord;
out vec4 v_color;

void main() {
    // Anchor-based rotation in local space
    vec2 anchor_offset = (a_position - u_anchor) * u_size;
    float cos_r = cos(u_rotation);
    float sin_r = sin(u_rotation);
    vec2 rotated = vec2(
        anchor_offset.x * cos_r - anchor_offset.y * sin_r,
        anchor_offset.x * sin_r + anchor_offset.y * cos_r
    );
    // u_position is the sprite anchor in world space.
    vec2 world_pos = rotated + u_position;
    gl_Position = u_projection * u_view * vec4(world_pos, 0.0, 1.0);
    v_texcoord = a_texcoord;
    v_color = a_color;
}
"""

DEFAULT_SPRITE_FRAGMENT_SRC = """
#version 330 core

uniform sampler2D u_texture;
uniform vec4 u_color;

in vec2 v_texcoord;
in vec4 v_color;

out vec4 f_color;

void main() {
    f_color = texture(u_texture, v_texcoord) * v_color * u_color;
    if (f_color.a < 0.01) discard;
}
"""

DEFAULT_LIGHT_VERTEX_SRC = """
#version 330 core
in vec2 a_position;
out vec2 v_world_pos;
uniform mat4 u_projection;
void main() {
    gl_Position = u_projection * vec4(a_position, 0.0, 1.0);
    v_world_pos = a_position;
}
"""

DEFAULT_LIGHT_FRAGMENT_SRC = """
#version 330 core
in vec2 v_world_pos;
out vec4 f_color;
uniform vec2 u_light_pos;
uniform vec4 u_light_color;
uniform float u_light_intensity;
uniform float u_light_radius;
uniform float u_light_falloff;
void main() {
    float dist = length(v_world_pos - u_light_pos);
    if (dist >= u_light_radius) discard;
    float t = 1.0 - (dist / u_light_radius);
    float attenuation = pow(t, u_light_falloff) * u_light_intensity;
    f_color = vec4(u_light_color.rgb * attenuation, attenuation);
}
"""

INSTANCE_VERTEX_SRC = """
#version 330 core

in vec2 a_position;
in vec2 a_texcoord;

// Per-instance attributes
in vec2 a_inst_pos;
in vec2 a_inst_size;
in float a_inst_rotation;
in vec4 a_inst_color;
in vec2 a_inst_anchor;
in vec2 a_inst_flip;
in vec2 a_inst_uv_offset;
in vec2 a_inst_uv_size;

uniform mat4 u_view;
uniform mat4 u_projection;

out vec2 v_texcoord;
out vec4 v_color;

void main() {
    vec2 pos = a_position;
    if (a_inst_flip.x > 0.5) pos.x = 1.0 - pos.x;
    if (a_inst_flip.y > 0.5) pos.y = 1.0 - pos.y;

    vec2 local_pos = (pos - a_inst_anchor) * a_inst_size;
    float rad = radians(a_inst_rotation);
    float cos_r = cos(rad);
    float sin_r = sin(rad);
    vec2 rotated = vec2(
        local_pos.x * cos_r - local_pos.y * sin_r,
        local_pos.x * sin_r + local_pos.y * cos_r
    );
    
    vec2 world_pos = rotated + a_inst_pos;
    gl_Position = u_projection * u_view * vec4(world_pos, 0.0, 1.0);
    
    v_texcoord = a_inst_uv_offset + a_texcoord * a_inst_uv_size;
    v_color = a_inst_color;
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
        light_vertex_src: str = DEFAULT_LIGHT_VERTEX_SRC,
        light_fragment_src: str = DEFAULT_LIGHT_FRAGMENT_SRC,
        normal_map_vertex_src: str = None,
        normal_map_fragment_src: str = None,
        instance_vertex_src: str = INSTANCE_VERTEX_SRC,
    ):
        import moderngl

        self._ctx = moderngl.create_context()
        self._ctx.enable(moderngl.BLEND)
        self._ctx.blend_func = (moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA)

        self._program = self._compile_program(vertex_src, fragment_src)
        # Quad: 4 vertices × (pos2 + uv2 + color4) = 4 × 8 floats × 4 bytes
        self._vbo = self._ctx.buffer(reserve=4 * 8 * 4)
        self._vao = self._ctx.vertex_array(
            self._program,
            [(self._vbo, "2f 2f 4f", "a_position", "a_texcoord", "a_color")]
        )

        # Light shader program
        self._light_vertex_src = light_vertex_src
        self._light_fragment_src = light_fragment_src
        self._light_program = None
        self._light_vbo = None
        self._light_vao = None

        # Normal map shader program
        self._nm_vertex_src = normal_map_vertex_src
        self._nm_fragment_src = normal_map_fragment_src
        self._nm_program = None
        self._nm_vbo = None
        self._nm_vao = None

        # Instance rendering
        self._inst_program = self._compile_program(instance_vertex_src, fragment_src)
        # Static quad VBO (pos2 + uv2)
        quad_data = struct.pack("16f", 0,0, 0,0, 1,0, 1,0, 0,1, 0,1, 1,1, 1,1)
        self._quad_vbo = self._ctx.buffer(quad_data)
        # Instance VBO (17 floats per instance, initial 10,000)
        self._inst_capacity = 10000
        self._inst_vbo = self._ctx.buffer(reserve=self._inst_capacity * 17 * 4)
        self._inst_vao = self._ctx.vertex_array(
            self._inst_program,
            [
                (self._quad_vbo, "2f 2f", "a_position", "a_texcoord"),
                (self._inst_vbo, "2f 2f 1f 4f 2f 2f 2f 2f /i", 
                 "a_inst_pos", "a_inst_size", "a_inst_rotation", "a_inst_color", 
                 "a_inst_anchor", "a_inst_flip", "a_inst_uv_offset", "a_inst_uv_size")
            ]
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

    def _ensure_light_program(self):
        """Lazy initialization of light shader program."""
        if self._light_program is not None:
            return
        self._light_program = self._compile_program(self._light_vertex_src, self._light_fragment_src)
        # Quad: 4 vertices × (pos2) = 4 × 2 floats × 4 bytes
        self._light_vbo = self._ctx.buffer(reserve=4 * 2 * 4)
        self._light_vao = self._ctx.vertex_array(
            self._light_program,
            [(self._light_vbo, "2f", "a_position")]
        )

    def _ensure_normal_map_program(self):
        """Lazy initialization of normal map shader program."""
        if self._nm_program is not None:
            return
        # Use defaults from engine.renderer.shader if not provided
        if self._nm_vertex_src is None or self._nm_fragment_src is None:
            from engine.renderer.shader import NORMAL_MAP_VERTEX_SRC, NORMAL_MAP_FRAGMENT_SRC
            self._nm_vertex_src = self._nm_vertex_src or NORMAL_MAP_VERTEX_SRC
            self._nm_fragment_src = self._nm_fragment_src or NORMAL_MAP_FRAGMENT_SRC
            
        self._nm_program = self._compile_program(self._nm_vertex_src, self._nm_fragment_src)
        # Quad: 4 vertices × (pos2 + uv2 + color4) = 4 × 8 floats × 4 bytes
        self._nm_vbo = self._ctx.buffer(reserve=4 * 8 * 4)
        self._nm_vao = self._ctx.vertex_array(
            self._nm_program,
            [(self._nm_vbo, "2f 2f 4f", "a_position", "a_texcoord", "a_color")]
        )

    def draw(
        self,
        texture_id: int,
        x: float,
        y: float,
        width: float = None,
        height: float = None,
        rotation: float = 0.0,
        color: Tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0),
        flip_x: bool = False,
        flip_y: bool = False,
        anchor_x: float = 0.5,
        anchor_y: float = 0.5,
        view_matrix: Tuple[float, ...] = None,
        projection_matrix: Tuple[float, ...] = None,
    ) -> None:
        """Draw a texture with full transform support."""
        if texture_id not in self._textures:
            return

        import moderngl
        import math

        texture = self._textures[texture_id]

        if width is None:
            width = texture.size[0]
        if height is None:
            height = texture.size[1]

        self._viewport = self._window.get_size()
        vp_w, vp_h = self._viewport

        # Default orthographic projection if none provided
        if projection_matrix is None:
            projection_matrix = (
                2.0 / vp_w, 0.0, 0.0, 0.0,
                0.0, -2.0 / vp_h, 0.0, 0.0,
                0.0, 0.0, 1.0, 0.0,
                -1.0, 1.0, 0.0, 1.0,
            )

        # Identity view if none provided
        if view_matrix is None:
            view_matrix = (
                1.0, 0.0, 0.0, 0.0,
                0.0, 1.0, 0.0, 0.0,
                0.0, 0.0, 1.0, 0.0,
                0.0, 0.0, 0.0, 1.0,
            )

        # UV flip
        u0, u1 = (1.0, 0.0) if flip_x else (0.0, 1.0)
        v0, v1 = (1.0, 0.0) if flip_y else (0.0, 1.0)

        # Quad in local [0,1] space — shader handles rotation + anchor
        vertices = [
            0.0, 0.0,  u0, v0,  1.0, 1.0, 1.0, 1.0,
            1.0, 0.0,  u1, v0,  1.0, 1.0, 1.0, 1.0,
            0.0, 1.0,  u0, v1,  1.0, 1.0, 1.0, 1.0,
            1.0, 1.0,  u1, v1,  1.0, 1.0, 1.0, 1.0,
        ]

        self._vbo.write(struct.pack("32f", *vertices))

        # Upload uniforms
        if "u_rotation" in self._program:
            self._program["u_rotation"].value = math.radians(rotation)
        if "u_anchor" in self._program:
            self._program["u_anchor"].value = (anchor_x, anchor_y)
        if "u_size" in self._program:
            self._program["u_size"].value = (width, height)
        if "u_color" in self._program:
            self._program["u_color"].value = color
        if "u_view" in self._program:
            self._program["u_view"].write(struct.pack("16f", *view_matrix))
        if "u_projection" in self._program:
            self._program["u_projection"].write(struct.pack("16f", *projection_matrix))
        if "u_position" in self._program:
            self._program["u_position"].value = (x, y)

        texture.use(location=0)
        if "u_texture" in self._program:
            self._program["u_texture"].value = 0

        self._vao.render(moderngl.TRIANGLE_STRIP)

    def draw_with_normal_map(
        self,
        texture_id: int,
        normal_map_id: int,
        x: float,
        y: float,
        width: float | None = None,
        height: float | None = None,
        rotation: float = 0.0,
        color: Tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0),
        flip_x: bool = False,
        flip_y: bool = False,
        anchor_x: float = 0.5,
        anchor_y: float = 0.5,
        view_matrix: Tuple[float, ...] | None = None,
        projection_matrix: Tuple[float, ...] | None = None,
        lights: list | None = None,
        ambient: Tuple[float, float, float] = (0.1, 0.1, 0.1),
    ) -> None:
        """Draw a quad with normal mapping and point lights."""
        if texture_id not in self._textures or normal_map_id not in self._textures:
            return

        import moderngl
        import math

        self._ensure_normal_map_program()
        texture = self._textures[texture_id]
        normal_map = self._textures[normal_map_id]

        if width is None: width = texture.size[0]
        if height is None: height = texture.size[1]

        self._viewport = self._window.get_size()
        vp_w, vp_h = self._viewport

        if projection_matrix is None:
            projection_matrix = (2.0/vp_w, 0.0, 0.0, 0.0, 0.0, -2.0/vp_h, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, -1.0, 1.0, 0.0, 1.0)
        if view_matrix is None:
            view_matrix = (1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0)

        u0, u1 = (1.0, 0.0) if flip_x else (0.0, 1.0)
        v0, v1 = (1.0, 0.0) if flip_y else (0.0, 1.0)

        # Vertices in local space, shader will transform to world then clip
        # We need world positions for lighting, so we pass them in a_position
        # For simplicity, we'll calculate world positions here and pass them
        
        # Local quad corners
        corners = [(-anchor_x * width, -anchor_y * height), ((1-anchor_x) * width, -anchor_y * height),
                   (-anchor_x * width, (1-anchor_y) * height), ((1-anchor_x) * width, (1-anchor_y) * height)]
        
        rad = math.radians(rotation)
        cos_r, sin_r = math.cos(rad), math.sin(rad)
        
        world_verts = []
        for cx, cy in corners:
            wx = x + cx * cos_r - cy * sin_r
            wy = y + cx * sin_r + cy * cos_r
            world_verts.append((wx, wy))

        vertices = [
            world_verts[0][0], world_verts[0][1],  u0, v0,  1.0, 1.0, 1.0, 1.0,
            world_verts[1][0], world_verts[1][1],  u1, v0,  1.0, 1.0, 1.0, 1.0,
            world_verts[2][0], world_verts[2][1],  u0, v1,  1.0, 1.0, 1.0, 1.0,
            world_verts[3][0], world_verts[3][1],  u1, v1,  1.0, 1.0, 1.0, 1.0,
        ]

        self._nm_vbo.write(struct.pack("32f", *vertices))

        # Uniforms
        self._nm_program["u_view"].write(struct.pack("16f", *view_matrix))
        self._nm_program["u_projection"].write(struct.pack("16f", *projection_matrix))
        self._nm_program["u_ambient"].value = ambient
        
        # Lights
        if lights:
            count = min(len(lights), 8)
            self._nm_program["u_light_count"].value = count
            for i in range(count):
                l = lights[i]
                self._nm_program[f"u_lights[{i}].position"].value = l["position"]
                self._nm_program[f"u_lights[{i}].color"].value = l["color"]
                self._nm_program[f"u_lights[{i}].intensity"].value = l["intensity"]
                self._nm_program[f"u_lights[{i}].radius"].value = l["radius"]
                self._nm_program[f"u_lights[{i}].falloff"].value = l["falloff"]
        else:
            self._nm_program["u_light_count"].value = 0

        texture.use(location=0)
        self._nm_program["u_texture"].value = 0
        normal_map.use(location=1)
        self._nm_program["u_normal_map"].value = 1

        self._nm_vao.render(moderngl.TRIANGLE_STRIP)

    def draw_light(
        self,
        x: float,
        y: float,
        color: Tuple[float, float, float],
        intensity: float,
        radius: float,
        falloff: float,
        projection_matrix: Tuple[float, ...] | None = None,
    ) -> None:
        """Draw a light pass quad (additive)."""
        import moderngl
        self._ensure_light_program()
        
        self._viewport = self._window.get_size()
        vp_w, vp_h = self._viewport
        
        if projection_matrix is None:
            projection_matrix = (2.0/vp_w, 0.0, 0.0, 0.0, 0.0, -2.0/vp_h, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, -1.0, 1.0, 0.0, 1.0)

        # Full screen quad or light-sized quad? 
        # For point lights, a quad covering the radius is more efficient.
        vertices = [
            x - radius, y - radius,
            x + radius, y - radius,
            x - radius, y + radius,
            x + radius, y + radius,
        ]
        self._light_vbo.write(struct.pack("8f", *vertices))

        self._light_program["u_projection"].write(struct.pack("16f", *projection_matrix))
        self._light_program["u_light_pos"].value = (x, y)
        self._light_program["u_light_color"].value = (*color, 1.0)
        self._light_program["u_light_intensity"].value = intensity
        self._light_program["u_light_radius"].value = radius
        self._light_program["u_light_falloff"].value = falloff

        # Additive blending for light pass
        prev_blend = self._ctx.blend_func
        self._ctx.blend_func = (moderngl.ONE, moderngl.ONE)
        self._light_vao.render(moderngl.TRIANGLE_STRIP)
        self._ctx.blend_func = prev_blend

    def draw_instanced(
        self,
        texture_id: int,
        instance_data: bytes,
        instance_count: int,
        view_matrix: Tuple[float, ...] | None = None,
        projection_matrix: Tuple[float, ...] | None = None,
    ) -> None:
        """Draw multiple instances of a quad with per-instance data."""
        if texture_id not in self._textures or instance_count == 0:
            return

        import moderngl
        texture = self._textures[texture_id]

        # Reallocate buffer if needed
        if instance_count > self._inst_capacity:
            while self._inst_capacity < instance_count:
                self._inst_capacity *= 2
            self._inst_vbo.release()
            self._inst_vbo = self._ctx.buffer(reserve=self._inst_capacity * 17 * 4)
            # Re-create VAO with new VBO
            self._inst_vao = self._ctx.vertex_array(
                self._inst_program,
                [
                    (self._quad_vbo, "2f 2f", "a_position", "a_texcoord"),
                    (self._inst_vbo, "2f 2f 1f 4f 2f 2f 2f 2f /i", 
                     "a_inst_pos", "a_inst_size", "a_inst_rotation", "a_inst_color", 
                     "a_inst_anchor", "a_inst_flip", "a_inst_uv_offset", "a_inst_uv_size")
                ]
            )

        self._inst_vbo.write(instance_data)

        self._viewport = self._window.get_size()
        vp_w, vp_h = self._viewport

        if projection_matrix is None:
            projection_matrix = (2.0/vp_w, 0.0, 0.0, 0.0, 0.0, -2.0/vp_h, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, -1.0, 1.0, 0.0, 1.0)
        if view_matrix is None:
            view_matrix = (1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0)

        self._inst_program["u_view"].write(struct.pack("16f", *view_matrix))
        self._inst_program["u_projection"].write(struct.pack("16f", *projection_matrix))

        texture.use(location=0)
        if "u_texture" in self._inst_program:
            self._inst_program["u_texture"].value = 0

        self._inst_vao.render(moderngl.TRIANGLE_STRIP, instances=instance_count)

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

    def draw_fullscreen_quad(
        self,
        program: "moderngl.Program",
        textures: dict,
    ) -> None:
        """
        Draw a fullscreen quad with the given program and texture bindings.

        Args:
            program: Compiled moderngl.Program to use.
            textures: Dict of {uniform_name: (texture_id, location)} bindings.
        """
        import moderngl

        # Lazy-init fullscreen quad VAO (NDC -1..1)
        if not hasattr(self, '_fsq_vbo'):
            fsq_data = struct.pack(
                "16f",
                -1.0, -1.0,  0.0, 0.0,
                 1.0, -1.0,  1.0, 0.0,
                -1.0,  1.0,  0.0, 1.0,
                 1.0,  1.0,  1.0, 1.0,
            )
            self._fsq_vbo = self._ctx.buffer(fsq_data)

        # Build VAO for this program
        vao = self._ctx.vertex_array(
            program,
            [(self._fsq_vbo, "2f 2f", "a_position", "a_texcoord")]
        )

        # Bind textures
        for uniform_name, (tex_id, location) in textures.items():
            if tex_id in self._textures:
                self._textures[tex_id].use(location=location)
                if uniform_name in program:
                    program[uniform_name].value = location

        vao.render(moderngl.TRIANGLE_STRIP)
        vao.release()

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

    def create_mrt_framebuffer(self, width: int, height: int, attachments: int) -> "IFramebuffer":
        """Create a Multiple Render Target (MRT) framebuffer."""
        return ModernGLFramebuffer(self._ctx, width, height, attachments=attachments)

    def create_depth_framebuffer(self, width: int, height: int) -> "IFramebuffer":
        """Create a depth-only framebuffer."""
        return ModernGLFramebuffer(self._ctx, width, height, depth_only=True)

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

    def __init__(self, ctx: "moderngl.Context", width: int, height: int, attachments: int = 1, depth_only: bool = False):
        self._ctx = ctx
        self._width = width
        self._height = height
        self._attachments = attachments
        self._depth_only = depth_only
        self._fbo = self._create(width, height)

    def _create(self, w: int, h: int):
        if self._depth_only:
            self._depth_tex = self._ctx.depth_texture((w, h))
            return self._ctx.framebuffer(depth_attachment=self._depth_tex)
        
        self._color_textures = [self._ctx.texture((w, h), 4) for _ in range(self._attachments)]
        self._depth_rb = self._ctx.depth_renderbuffer((w, h))
        return self._ctx.framebuffer(color_attachments=self._color_textures, depth_attachment=self._depth_rb)

    def get_color_texture(self, index: int = 0) -> Optional["moderngl.Texture"]:
        """Get color attachment texture by index."""
        textures = getattr(self, '_color_textures', [])
        if 0 <= index < len(textures):
            return textures[index]
        return None

    def get_depth_texture(self) -> Optional["moderngl.Texture"]:
        """Get depth attachment texture."""
        return getattr(self, '_depth_tex', None)

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

    @property
    def is_bound(self) -> bool:
        """Check if framebuffer is currently bound."""
        return False  # ModernGL doesn't track this easily; always returns False

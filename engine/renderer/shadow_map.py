"""
Shadow Map Renderer for 2D Soft Shadows.

Handles depth pass, PCF (Percentage Closer Filtering), and penumbra blur.

Layer: 2 (Engine)
Dependencies: hal.interfaces, engine.renderer.shader
"""

from __future__ import annotations
import struct
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from hal.interfaces import IGPUDevice, IFramebuffer
    from engine.renderer.light import Light2D
    from engine.renderer.sprite import Sprite


class ShadowMapRenderer:
    """
    Renders shadow maps for 2D lights.
    
    Workflow:
    1. render_shadow_map() -> depth pass
    2. apply_pcf() -> soft edges
    3. apply_penumbra_blur() -> variable softness
    """
    
    def __init__(self, gpu: IGPUDevice, resolution: int = 512):
        self._gpu = gpu
        self._resolution = resolution
        self._shadow_fbo: IFramebuffer = gpu.create_depth_framebuffer(resolution, resolution)
        self._pcf_fbo: IFramebuffer = gpu.create_framebuffer(resolution, resolution)
        self._blur_fbo: IFramebuffer = gpu.create_framebuffer(resolution, resolution)

        # Lazy-compiled shader programs (ModernGLDevice only)
        self._depth_program = None
        self._pcf_program = None
        self._blur_program = None

        # State tracking
        self._caster_count: int = 0
        self._pcf_applied: bool = False
        self._penumbra_applied: bool = False
        self._penumbra_radius: float = 0.0
        self._last_light = None

    def _ensure_programs(self):
        """Lazy-compile shadow shader programs on ModernGLDevice."""
        from hal.pyglet_backend import ModernGLDevice
        if not isinstance(self._gpu, ModernGLDevice):
            return
        if self._depth_program is not None:
            return

        from engine.renderer.shader import (
            SHADOW_MAP_VERTEX_SRC,
            SHADOW_MAP_FRAGMENT_SRC,
            POST_VERTEX_SRC,
            PCF_SHADOW_FRAGMENT_SRC,
            PENUMBRA_BLUR_FRAGMENT_SRC,
        )
        self._depth_program = self._gpu._compile_program(
            SHADOW_MAP_VERTEX_SRC, SHADOW_MAP_FRAGMENT_SRC
        )
        self._pcf_program = self._gpu._compile_program(
            POST_VERTEX_SRC, PCF_SHADOW_FRAGMENT_SRC
        )
        self._blur_program = self._gpu._compile_program(
            POST_VERTEX_SRC, PENUMBRA_BLUR_FRAGMENT_SRC
        )

    def _ensure_fsq(self):
        """Ensure fullscreen quad VBO exists on the GPU device."""
        if not hasattr(self._gpu, '_fsq_vbo'):
            fsq_data = struct.pack(
                "16f",
                -1.0, -1.0,  0.0, 0.0,
                 1.0, -1.0,  1.0, 0.0,
                -1.0,  1.0,  0.0, 1.0,
                 1.0,  1.0,  1.0, 1.0,
            )
            self._gpu._fsq_vbo = self._gpu._ctx.buffer(fsq_data)

    def render_shadow_map(self, light: Light2D, casters: List[Sprite]):
        """
        Perform depth pass for a single light.

        On ModernGLDevice: binds shadow depth shader, draws each caster quad.
        On HeadlessGPU: calls gpu.draw() for each caster (no-op but pipeline correct).
        """
        self._last_light = light
        self._caster_count = 0
        self._ensure_programs()

        self._shadow_fbo.bind()
        self._gpu.clear(1.0, 1.0, 1.0, 1.0)

        from hal.pyglet_backend import ModernGLDevice
        if isinstance(self._gpu, ModernGLDevice) and self._depth_program is not None:
            import moderngl
            prog = self._depth_program

            # Build view/projection from light position (orthographic)
            vp_w = vp_h = float(self._resolution)
            proj = (
                2.0 / vp_w, 0.0, 0.0, 0.0,
                0.0, -2.0 / vp_h, 0.0, 0.0,
                0.0, 0.0, 1.0, 0.0,
                -1.0, 1.0, 0.0, 1.0,
            )
            view = (
                1.0, 0.0, 0.0, 0.0,
                0.0, 1.0, 0.0, 0.0,
                0.0, 0.0, 1.0, 0.0,
                -light.position.x, -light.position.y, 0.0, 1.0,
            )
            if "u_projection" in prog:
                prog["u_projection"].write(struct.pack("16f", *proj))
            if "u_view" in prog:
                prog["u_view"].write(struct.pack("16f", *view))

            for sprite in casters:
                if sprite.texture is None or sprite.texture.gpu_id is None:
                    continue
                tex = self._gpu._textures.get(sprite.texture.gpu_id)
                if tex is None:
                    continue

                # Build quad vertices for this caster
                x, y = sprite.position.x, sprite.position.y
                w, h = sprite.width, sprite.height
                verts = struct.pack(
                    "8f",
                    x,     y,
                    x + w, y,
                    x,     y + h,
                    x + w, y + h,
                )
                vbo = self._gpu._ctx.buffer(verts)
                vao = self._gpu._ctx.vertex_array(prog, [(vbo, "2f", "a_position")])
                vao.render(moderngl.TRIANGLE_STRIP)
                vao.release()
                vbo.release()
                self._caster_count += 1
        else:
            # Headless path
            for sprite in casters:
                if sprite.texture is None:
                    continue
                self._gpu.draw(
                    sprite.texture.gpu_id if sprite.texture.gpu_id is not None else 0,
                    sprite.position.x,
                    sprite.position.y,
                    sprite.width,
                    sprite.height,
                )
                self._caster_count += 1

        self._shadow_fbo.unbind()
        
    def apply_pcf(self) -> IFramebuffer:
        """
        Apply Percentage Closer Filtering for soft edges.

        On ModernGLDevice: binds PCF shader, samples shadow map with 3x3 kernel.
        On HeadlessGPU: records state only.
        """
        self._ensure_programs()
        self._pcf_applied = True

        from hal.pyglet_backend import ModernGLDevice
        if isinstance(self._gpu, ModernGLDevice) and self._pcf_program is not None:
            import moderngl
            self._ensure_fsq()
            depth_tex = getattr(self._shadow_fbo, 'get_depth_texture', lambda: None)()

            self._pcf_fbo.bind()
            prog = self._pcf_program

            if depth_tex and "u_shadow_map" in prog:
                depth_tex.use(location=0)
                prog["u_shadow_map"].value = 0

            if self._last_light and "u_light_pos" in prog:
                prog["u_light_pos"].value = (
                    self._last_light.position.x,
                    self._last_light.position.y,
                )
            if self._last_light and "u_light_radius" in prog:
                prog["u_light_radius"].value = self._last_light.radius

            vao = self._gpu._ctx.vertex_array(
                prog,
                [(self._gpu._fsq_vbo, "2f 2f", "a_position", "a_texcoord")]
            )
            vao.render(moderngl.TRIANGLE_STRIP)
            vao.release()
            self._pcf_fbo.unbind()
        else:
            self._pcf_fbo.bind()
            self._pcf_fbo.unbind()

        return self._pcf_fbo
        
    def apply_penumbra_blur(self, radius: float) -> IFramebuffer:
        """
        Apply Gaussian blur for penumbra effect.

        On ModernGLDevice: binds blur shader with given radius, draws fullscreen quad.
        On HeadlessGPU: records state only.
        """
        self._penumbra_radius = radius
        self._penumbra_applied = True
        self._ensure_programs()

        from hal.pyglet_backend import ModernGLDevice
        if isinstance(self._gpu, ModernGLDevice) and self._blur_program is not None:
            import moderngl
            self._ensure_fsq()
            pcf_tex = getattr(self._pcf_fbo, 'get_color_texture', lambda: None)()

            self._blur_fbo.bind()
            prog = self._blur_program

            if pcf_tex and "u_image" in prog:
                pcf_tex.use(location=0)
                prog["u_image"].value = 0
            if "u_blur_radius" in prog:
                prog["u_blur_radius"].value = radius
            if "u_texel_size" in prog:
                prog["u_texel_size"].value = (
                    1.0 / self._resolution,
                    1.0 / self._resolution,
                )

            vao = self._gpu._ctx.vertex_array(
                prog,
                [(self._gpu._fsq_vbo, "2f 2f", "a_position", "a_texcoord")]
            )
            vao.render(moderngl.TRIANGLE_STRIP)
            vao.release()
            self._blur_fbo.unbind()
            return self._blur_fbo
        else:
            return self._pcf_fbo
        
    def resize(self, resolution: int):
        """Resize shadow map buffers."""
        self._resolution = resolution
        self._shadow_fbo.resize(resolution, resolution)
        self._pcf_fbo.resize(resolution, resolution)
        self._blur_fbo.resize(resolution, resolution)
        
    def dispose(self):
        """Release GPU resources."""
        self._shadow_fbo.dispose()
        self._pcf_fbo.dispose()
        self._blur_fbo.dispose()
        for prog in (self._depth_program, self._pcf_program, self._blur_program):
            if prog is not None:
                try:
                    prog.release()
                except Exception:
                    pass
        self._depth_program = None
        self._pcf_program = None
        self._blur_program = None

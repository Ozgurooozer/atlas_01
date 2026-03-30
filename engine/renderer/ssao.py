"""
SSAO (Screen Space Ambient Occlusion) Pass.

Calculates ambient occlusion based on depth and normal buffers.

Layer: 2 (Engine)
Dependencies: hal.interfaces, engine.renderer.gbuffer
"""

from __future__ import annotations
import random
import math
import struct
from typing import List, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from hal.interfaces import IGPUDevice, IFramebuffer
    from engine.renderer.gbuffer import GBuffer


class SSAOPass:
    """
    SSAO implementation using a hemisphere kernel.
    
    Workflow:
    1. render(gbuffer) -> SSAO factor FBO
    2. blur(ssao_fbo) -> smoothed SSAO
    """
    
    def __init__(self, gpu: IGPUDevice, width: int, height: int):
        self._gpu = gpu
        self._width = width
        self._height = height
        
        # 1. Generate 64 hemisphere kernel samples
        self._kernel = self._generate_kernel(64)
        
        # 2. Generate 4x4 noise texture
        self._noise_texture_id = self._generate_noise_texture()
        
        # 3. Create SSAO and Blur FBOs
        self._ssao_fbo = gpu.create_framebuffer(width, height)
        self._blur_fbo = gpu.create_framebuffer(width, height)

        # Lazy-compiled shader programs (ModernGLDevice only)
        self._ssao_program = None
        self._blur_program = None

        # State tracking
        self._kernel_uploaded: bool = False
        self._noise_bound: bool = False
        self._last_normal_fbo = None
        self._last_depth_fbo = None
        self._last_ssao_input = None

    def _ensure_programs(self):
        """Lazy-compile SSAO + blur shader programs on ModernGLDevice."""
        from hal.pyglet_backend import ModernGLDevice
        if not isinstance(self._gpu, ModernGLDevice):
            return
        if self._ssao_program is not None:
            return

        from engine.renderer.shader import (
            POST_VERTEX_SRC,
            SSAO_FRAGMENT_SRC,
            SSAO_BLUR_FRAGMENT_SRC,
        )
        self._ssao_program = self._gpu._compile_program(POST_VERTEX_SRC, SSAO_FRAGMENT_SRC)
        self._blur_program = self._gpu._compile_program(POST_VERTEX_SRC, SSAO_BLUR_FRAGMENT_SRC)
        
    def _generate_kernel(self, size: int) -> List[Tuple[float, float, float]]:
        """Generate a hemisphere kernel with samples clustered near the origin."""
        kernel = []
        for i in range(size):
            sample = (
                random.uniform(-1.0, 1.0),
                random.uniform(-1.0, 1.0),
                random.uniform(0.0, 1.0)
            )
            mag = math.sqrt(sample[0]**2 + sample[1]**2 + sample[2]**2)
            if mag > 0:
                sample = (sample[0]/mag, sample[1]/mag, sample[2]/mag)
            scale = i / size
            scale = 0.1 + 0.9 * (scale**2)
            kernel.append((sample[0]*scale, sample[1]*scale, sample[2]*scale))
        return kernel
        
    def _generate_noise_texture(self) -> int:
        """Generate a 4x4 noise texture for SSAO rotation."""
        noise_data = bytearray()
        for _ in range(16):
            nx = random.uniform(-1.0, 1.0)
            ny = random.uniform(-1.0, 1.0)
            noise_data.append(int((nx * 0.5 + 0.5) * 255))
            noise_data.append(int((ny * 0.5 + 0.5) * 255))
            noise_data.append(0)
            noise_data.append(255)
        return self._gpu.create_texture(4, 4, bytes(noise_data))
        
    def render(self, gbuffer: GBuffer) -> IFramebuffer:
        """
        Render SSAO factor using G-Buffer.
        
        On ModernGLDevice: compiles SSAO shader, binds normal + depth textures,
        uploads 64-sample kernel + noise texture, draws fullscreen quad.
        On HeadlessGPU: records state only (no-op draw).
        """
        self._last_normal_fbo = gbuffer.normal_fbo
        self._last_depth_fbo = gbuffer.depth_fbo

        self._ensure_programs()

        from hal.pyglet_backend import ModernGLDevice
        if isinstance(self._gpu, ModernGLDevice) and self._ssao_program is not None:
            # Get underlying moderngl textures from FBOs
            normal_tex = getattr(gbuffer.normal_fbo, 'get_color_texture', lambda: None)()
            depth_tex = getattr(gbuffer.depth_fbo, 'get_depth_texture', lambda: None)()
            noise_tex = self._gpu._textures.get(self._noise_texture_id)

            self._ssao_fbo.bind()

            prog = self._ssao_program
            # Upload kernel samples
            for i, (kx, ky, kz) in enumerate(self._kernel):
                key = f"u_samples[{i}]"
                if key in prog:
                    prog[key].value = (kx, ky, kz)

            if "u_radius" in prog:
                prog["u_radius"].value = 0.5
            if "u_bias" in prog:
                prog["u_bias"].value = 0.025
            if "u_noise_scale" in prog:
                prog["u_noise_scale"].value = (self._width / 4.0, self._height / 4.0)

            # Bind textures
            loc = 0
            if normal_tex and "u_normal" in prog:
                normal_tex.use(location=loc)
                prog["u_normal"].value = loc
                loc += 1
            if depth_tex and "u_depth" in prog:
                depth_tex.use(location=loc)
                prog["u_depth"].value = loc
                loc += 1
            if noise_tex and "u_noise" in prog:
                noise_tex.use(location=loc)
                prog["u_noise"].value = loc

            import moderngl
            if not hasattr(self._gpu, '_fsq_vbo'):
                fsq_data = struct.pack(
                    "16f",
                    -1.0, -1.0,  0.0, 0.0,
                     1.0, -1.0,  1.0, 0.0,
                    -1.0,  1.0,  0.0, 1.0,
                     1.0,  1.0,  1.0, 1.0,
                )
                self._gpu._fsq_vbo = self._gpu._ctx.buffer(fsq_data)

            vao = self._gpu._ctx.vertex_array(
                prog,
                [(self._gpu._fsq_vbo, "2f 2f", "a_position", "a_texcoord")]
            )
            vao.render(moderngl.TRIANGLE_STRIP)
            vao.release()

            self._ssao_fbo.unbind()
        else:
            # Headless / test path
            self._ssao_fbo.bind()
            self._ssao_fbo.unbind()

        self._kernel_uploaded = True
        self._noise_bound = True
        return self._ssao_fbo
        
    def blur(self, ssao_fbo: IFramebuffer) -> IFramebuffer:
        """
        Apply 4x4 box blur to SSAO factor.
        
        On ModernGLDevice: binds SSAO texture, draws fullscreen quad with blur shader.
        On HeadlessGPU: records state only.
        """
        self._last_ssao_input = ssao_fbo
        self._ensure_programs()

        from hal.pyglet_backend import ModernGLDevice
        if isinstance(self._gpu, ModernGLDevice) and self._blur_program is not None:
            ssao_tex = getattr(ssao_fbo, 'get_color_texture', lambda: None)()

            self._blur_fbo.bind()
            prog = self._blur_program

            if ssao_tex and "u_ssao" in prog:
                ssao_tex.use(location=0)
                prog["u_ssao"].value = 0

            import moderngl
            vao = self._gpu._ctx.vertex_array(
                prog,
                [(self._gpu._fsq_vbo, "2f 2f", "a_position", "a_texcoord")]
            )
            vao.render(moderngl.TRIANGLE_STRIP)
            vao.release()
            self._blur_fbo.unbind()
        else:
            self._blur_fbo.bind()
            self._blur_fbo.unbind()

        return self._blur_fbo
        
    def resize(self, width: int, height: int):
        """Resize SSAO buffers."""
        self._width = width
        self._height = height
        self._ssao_fbo.resize(width, height)
        self._blur_fbo.resize(width, height)
        
    def dispose(self):
        """Release GPU resources."""
        self._ssao_fbo.dispose()
        self._blur_fbo.dispose()
        if self._ssao_program is not None:
            self._ssao_program.release()
            self._ssao_program = None
        if self._blur_program is not None:
            self._blur_program.release()
            self._blur_program = None
        self._noise_texture_id = None
        
    @property
    def kernel(self) -> List[Tuple[float, float, float]]:
        return self._kernel

"""
G-Buffer for Deferred Rendering and SSAO.

Stores Albedo, Normal, and Depth in separate textures.

Layer: 2 (Engine)
Dependencies: hal.interfaces
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hal.interfaces import IGPUDevice, IFramebuffer


class GBuffer:
    """
    Geometry Buffer for deferred shading.
    
    Attachments:
    0: Albedo (RGBA)  -> _albedo_fbo
    1: Normal (RGB)   -> _normal_fbo  (ayrı FBO, MRT attachment 1)
    2: Depth          -> _depth_fbo
    """
    
    def __init__(self, gpu: IGPUDevice, width: int, height: int):
        self._gpu = gpu
        self._width = width
        self._height = height
        
        # Albedo attachment (MRT attachment 0)
        self._albedo_fbo = gpu.create_framebuffer(width, height)
        # Normal attachment (MRT attachment 1) — ayrı FBO, SSAO'ya bağımsız geçilir
        self._normal_fbo = gpu.create_framebuffer(width, height)
        # Depth-only FBO
        self._depth_fbo = gpu.create_depth_framebuffer(width, height)
        
    def bind(self):
        """Bind G-Buffer albedo FBO for writing."""
        self._albedo_fbo.bind()
        
    def unbind(self):
        """Unbind G-Buffer."""
        self._albedo_fbo.unbind()
        
    def resize(self, width: int, height: int):
        """Resize all G-Buffer textures."""
        self._width = width
        self._height = height
        self._albedo_fbo.resize(width, height)
        self._normal_fbo.resize(width, height)
        self._depth_fbo.resize(width, height)
        
    def dispose(self):
        """Release GPU resources."""
        self._albedo_fbo.dispose()
        self._normal_fbo.dispose()
        self._depth_fbo.dispose()
        
    @property
    def width(self) -> int: return self._width
    
    @property
    def height(self) -> int: return self._height
    
    @property
    def albedo_fbo(self) -> IFramebuffer: return self._albedo_fbo
    
    @property
    def normal_fbo(self) -> IFramebuffer: return self._normal_fbo
    
    @property
    def depth_fbo(self) -> IFramebuffer: return self._depth_fbo

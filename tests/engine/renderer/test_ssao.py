from engine.renderer.ssao import SSAOPass
from engine.renderer.gbuffer import GBuffer
from engine.renderer.renderer import Renderer2D

def test_ssao_pass_kernel_size():
    """Gereksinim 2.8.4: Kernel boyutu 64 olduğunu doğrula."""
    gpu = MockGPU()
    gpu.create_texture.return_value = 1
    ssao = SSAOPass(gpu, 800, 600)
    assert len(ssao.kernel) == 64

def test_gbuffer_resize():
    """Gereksinim 2.8.3: GBuffer.resize() sonrası boyut doğrulama."""
    gpu = MockGPU()
    gbuffer = GBuffer(gpu, 800, 600)
    gbuffer.resize(1024, 768)
    assert gbuffer.width == 1024
    assert gbuffer.height == 768

def test_renderer_ssao_toggle():
    """Gereksinim 2.7.1: ssao_enabled toggle testi."""
    gpu = MockGPU()
    renderer = Renderer2D()
    renderer.gpu_device = gpu
    renderer.viewport = (0, 0, 800, 600)
    
    # Kapalıyken G-Buffer oluşmamalı
    renderer.ssao_enabled = False
    renderer.begin_frame()
    assert renderer._gbuffer is None
    
    # Açıkken G-Buffer oluşmalı
    renderer.ssao_enabled = True
    renderer.begin_frame()
    assert renderer._gbuffer is not None

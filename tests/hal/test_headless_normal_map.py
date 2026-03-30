import pytest
from hal.headless import HeadlessGPU

def test_headless_gpu_normal_map_no_op():
    """Gereksinim 3.1, 3.2: HeadlessGPU no-op metodları hata vermemeli."""
    gpu = HeadlessGPU()
    tex_id = gpu.create_texture(64, 64)
    nm_id = gpu.create_texture(64, 64)
    
    # draw_with_normal_map no-op testi
    gpu.draw_with_normal_map(
        tex_id, nm_id, 100, 100, 64, 64,
        lights=[{"position": (0,0), "color": (1,1,1), "intensity": 1, "radius": 100, "falloff": 1}]
    )
    
    # draw_light no-op testi
    gpu.draw_light(100, 100, (1, 1, 1), 1.0, 100.0, 1.0)
    
    assert True # Hata fırlatılmadıysa başarılı

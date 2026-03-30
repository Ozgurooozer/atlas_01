import pytest
from unittest.mock import MagicMock
from engine.renderer.shadow_map import ShadowMapRenderer
from engine.renderer.light import LightRenderer, Light2D, LightType
from hal.interfaces import IGPUDevice

def test_shadow_map_renderer_lifecycle():
    """Gereksinim 1.2.4: ShadowMapRenderer kaynak yönetimi testi."""
    gpu = MagicMock(spec=IGPUDevice)
    smr = ShadowMapRenderer(gpu, resolution=256)
    
    # Resize testi
    smr.resize(512)
    
    # Dispose testi
    smr.dispose()
    assert True # Hata fırlatılmadıysa başarılı

def test_light_renderer_shadow_toggle():
    """Gereksinim 1.4.1, 1.4.3: shadows_enabled toggle testi."""
    gpu = MagicMock(spec=IGPUDevice)
    lr = LightRenderer(gpu, 800, 600)
    
    # Kapalıyken shadow renderer oluşmamalı
    lr.shadows_enabled = False
    lr.begin_light_pass()
    assert lr._shadow_renderer is None
    
    # Açıkken shadow renderer oluşmalı
    lr.shadows_enabled = True
    lr.begin_light_pass()
    assert lr._shadow_renderer is not None

def test_light_renderer_max_lights_preserved():
    """Gereksinim 1.5.3: shadows_enabled=False iken MAX_LIGHTS sınırı korunur."""
    gpu = MagicMock(spec=IGPUDevice)
    lr = LightRenderer(gpu, 800, 600)
    lr.shadows_enabled = False
    
    # 33 ışık ekle
    for _ in range(33):
        lr.submit(Light2D())
        
    assert lr.light_count == 32 # Sınır korunmalı

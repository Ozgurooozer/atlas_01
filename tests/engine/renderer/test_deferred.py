import pytest
from unittest.mock import MagicMock
from engine.renderer.light import LightRenderer, Light2D
from engine.renderer.renderer import Renderer2D
from hal.interfaces import IGPUDevice

def test_deferred_light_limit():
    """Gereksinim 3.2.1: Deferred enabled iken 50+ ışık eklenebilir."""
    gpu = MagicMock(spec=IGPUDevice)
    lr = LightRenderer(gpu, 800, 600)
    lr.deferred_enabled = True
    
    # 100 ışık ekle
    for _ in range(100):
        lr.submit(Light2D())
        
    assert lr.light_count == 100

def test_forward_deferred_mutex():
    """Gereksinim 3.3: Forward/Deferred mutex kontrolü."""
    gpu = MagicMock(spec=IGPUDevice)
    renderer = Renderer2D()
    renderer.gpu_device = gpu
    renderer.set_light_renderer(LightRenderer(gpu, 800, 600))
    
    # Başlangıçta forward açık (deferred kapalı)
    assert renderer.forward_enabled is True
    
    # Deferred aç
    renderer.deferred_enabled = True
    assert renderer.forward_enabled is False
    
    # Deferred açıkken forward açmaya çalış -> ValueError
    with pytest.raises(ValueError):
        renderer.forward_enabled = True
        
    # Forward aç (önce deferred kapatılmalı)
    renderer.deferred_enabled = False
    renderer.forward_enabled = True
    assert renderer.deferred_enabled is False
    
    # Forward açıkken deferred açmaya çalış -> ValueError
    # Not: Renderer2D.deferred_enabled setter'ı forward_enabled'ı kontrol ediyor.
    # Mevcut mantıkta forward_enabled her zaman not deferred_enabled olduğu için
    # setter'daki 'getattr(self, "forward_enabled", False)' her zaman True dönecektir.
    # Bu yüzden deferred_enabled = True her zaman hata verecektir (eğer forward_enabled=True ise).
    with pytest.raises(ValueError):
        renderer.deferred_enabled = True

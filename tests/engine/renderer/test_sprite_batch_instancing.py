from unittest.mock import MagicMock
from engine.renderer.batch import SpriteBatch
from engine.renderer.sprite import Sprite
from engine.renderer.texture import Texture
from engine.renderer.renderer import Renderer2D
from hal.interfaces import IGPUDevice

def test_sprite_batch_instancing_draw_call_count():
    """Gereksinim 1.2: N sprite, 1 texture -> draw_instanced() tam 1 kez çağrılır."""
    gpu = MagicMock(spec=IGPUDevice)
    renderer = MagicMock(spec=Renderer2D)
    renderer.gpu_device = gpu
    renderer._camera = None
    
    # Mock _ensure_uploaded to do nothing
    renderer._ensure_uploaded = MagicMock()
    
    batch = SpriteBatch(renderer, instancing_enabled=True)
    
    tex = Texture(64, 64)
    tex.mark_uploaded(1)
    
    batch.begin()
    for _ in range(10):
        batch.draw(Sprite(tex))
    batch.end()
    
    # draw_instanced tam 1 kez çağrılmış olmalı
    gpu.draw_instanced.assert_called_once()
    # draw_instanced parametrelerini kontrol et
    args, kwargs = gpu.draw_instanced.call_args
    assert args[0] == 1 # texture_id
    assert args[2] == 10 # instance_count

def test_sprite_batch_instancing_disabled_legacy_path():
    """Gereksinim 1.3: instancing_enabled=False -> eski davranış korunur."""
    gpu = MagicMock(spec=IGPUDevice)
    renderer = MagicMock(spec=Renderer2D)
    renderer.gpu_device = gpu
    
    batch = SpriteBatch(renderer, instancing_enabled=False)
    
    tex = Texture(64, 64)
    tex.mark_uploaded(1)
    
    batch.begin()
    for _ in range(5):
        batch.draw(Sprite(tex))
    batch.end()
    
    # draw_instanced hiç çağrılmamış olmalı
    gpu.draw_instanced.assert_not_called()
    # draw_sprite 5 kez çağrılmış olmalı (legacy path)
    assert renderer.draw_sprite.call_count == 5

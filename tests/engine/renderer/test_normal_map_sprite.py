from engine.renderer.renderer import Renderer2D
from engine.renderer.sprite import Sprite
from engine.renderer.texture import Texture

def test_renderer_draw_sprite_normal_map_branch():
    """Gereksinim 6.1, 6.2: Normal map varsa draw_with_normal_map çağrılmalı."""
    gpu = MockGPU()
    renderer = Renderer2D()
    renderer.gpu_device = gpu
    
    # Mock textures
    tex = Texture(64, 64)
    tex.mark_uploaded(1)
    nm = Texture(64, 64)
    nm.mark_uploaded(2)
    
    sprite = Sprite(tex)
    sprite.normal_map = nm
    
    renderer.draw_sprite(sprite)
    
    # draw_with_normal_map çağrılmış olmalı
    gpu.draw_with_normal_map.assert_called_once()
    # Standart draw çağrılmamış olmalı
    gpu.draw.assert_not_called()

def test_renderer_draw_sprite_standard_branch():
    """Gereksinim 6.4: Normal map yoksa standart draw çağrılmalı."""
    gpu = MockGPU()
    renderer = Renderer2D()
    renderer.gpu_device = gpu
    
    tex = Texture(64, 64)
    tex.mark_uploaded(1)
    
    sprite = Sprite(tex)
    sprite.normal_map = None
    
    renderer.draw_sprite(sprite)
    
    # Standart draw çağrılmış olmalı
    gpu.draw.assert_called_once()
    # draw_with_normal_map çağrılmamış olmalı
    gpu.draw_with_normal_map.assert_not_called()

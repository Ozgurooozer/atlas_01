from engine.renderer.light import LightRenderer, Light2D, LightType
from core.color import Color
from core.vec import Vec2
from hal.interfaces import IGPUDevice

def test_light_renderer_end_light_pass_draw_light_call():
    """Gereksinim 5.1, 5.2: end_light_pass() gpu.draw_light() çağırmalı."""
    gpu = MagicMock(spec=IGPUDevice)
    lr = LightRenderer(gpu, 800, 600)
    
    light = Light2D(
        light_type=LightType.POINT,
        color=Color(1, 0, 0, 1),
        intensity=0.8,
        position=Vec2(100, 200),
        radius=150,
        falloff=1.5
    )
    
    lr.begin_light_pass()
    lr.submit(light)
    lr.end_light_pass()
    
    # draw_light çağrılmış olmalı
    gpu.draw_light.assert_called_once_with(
        100.0, 200.0, (1.0, 0.0, 0.0), 0.8, 150.0, 1.5
    )

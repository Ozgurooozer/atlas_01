import pytest
from hypothesis import given, strategies as st
from world.components.sprite_component import SpriteComponent
from world.transform import TransformComponent
from world.actor import Actor

class MockSprite:
    def __init__(self):
        self.position = (0, 0)
        self.rotation = 0
        self.visible = True
        self.z_index = 0
        self.color = (255, 255, 255, 255)
        self.flip_x = False
        self.flip_y = False
        self.texture = None

class MockRenderer:
    def __init__(self):
        self.draw_calls = []
    def draw_sprite(self, sprite):
        self.draw_calls.append(sprite)

@given(
    visible=st.booleans(),
    has_renderer=st.booleans()
)
def test_sprite_component_visibility_and_draw_rule(visible, has_renderer):
    """
    Özellik 3: SpriteComponent Görünürlük ve Çizim Kuralı
    Gereksinim 2.2, 2.5
    """
    sprite = MockSprite()
    sprite.visible = visible
    
    comp = SpriteComponent(sprite)
    renderer = MockRenderer() if has_renderer else None
    comp.renderer = renderer
    
    # Mock owner
    actor = Actor("TestActor")
    actor.add_component(comp)
    
    comp.on_tick(0.016)
    
    if visible and has_renderer:
        assert len(renderer.draw_calls) == 1
    elif has_renderer:
        assert len(renderer.draw_calls) == 0

@given(
    wx=st.floats(min_value=-1000, max_value=1000),
    wy=st.floats(min_value=-1000, max_value=1000),
    wr=st.floats(min_value=-360, max_value=360)
)
def test_sprite_component_transform_sync(wx, wy, wr):
    """
    Özellik 4: SpriteComponent Transform Senkronizasyonu
    Gereksinim 2.3
    """
    sprite = MockSprite()
    comp = SpriteComponent(sprite)
    comp.renderer = MockRenderer()
    
    actor = Actor("TestActor")
    transform = TransformComponent()
    transform.position = (wx, wy)
    transform.rotation = wr
    
    actor.add_component(transform)
    actor.add_component(comp)
    
    comp.on_tick(0.016)
    
    assert sprite.position == (wx, wy)
    assert abs(sprite.rotation - wr) < 0.001

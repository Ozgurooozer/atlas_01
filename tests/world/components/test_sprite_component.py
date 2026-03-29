import pytest
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

def test_sprite_component_proxy_properties():
    """Gereksinim 2.4, 2.6"""
    sprite = MockSprite()
    comp = SpriteComponent(sprite)
    
    comp.z_index = 10
    assert sprite.z_index == 10
    
    comp.color = (255, 0, 0, 255)
    assert sprite.color == (255, 0, 0, 255)
    
    comp.flip_x = True
    assert sprite.flip_x == True
    
    comp.flip_y = True
    assert sprite.flip_y == True

def test_sprite_component_renderer_none_behavior():
    """Gereksinim 2.7"""
    sprite = MockSprite()
    comp = SpriteComponent(sprite)
    comp.renderer = None
    
    actor = Actor("TestActor")
    actor.add_component(comp)
    
    # Should not raise exception
    comp.on_tick(0.016)

def test_sprite_component_serialization():
    """Gereksinim 2.7"""
    sprite = MockSprite()
    sprite.z_index = 5
    sprite.color = (100, 100, 100, 255)
    
    comp = SpriteComponent(sprite)
    data = comp.serialize()
    
    assert data["z_index"] == 5
    assert data["color"] == (100, 100, 100, 255)
    
    new_sprite = MockSprite()
    new_comp = SpriteComponent(new_sprite)
    new_comp.deserialize(data)
    
    assert new_sprite.z_index == 5
    assert new_sprite.color == (100, 100, 100, 255)

import pytest
from hypothesis import given, strategies as st
from world.world import World
from world.actor import Actor
from world.components.engine_context import EngineContext
from world.components.sprite_component import SpriteComponent
from world.components.physics_component import PhysicsComponent

class MockRenderer: pass
class MockPhysics:
    def create_body(self, m, mo): return 1
    def remove_body(self, bid): pass
    def set_body_position(self, bid, x, y): pass

@given(
    has_renderer=st.booleans(),
    has_physics=st.booleans(),
    spawn_first=st.booleans()
)
def test_engine_context_injection_consistency(has_renderer, has_physics, spawn_first):
    """
    Özellik 9: EngineContext Enjeksiyon Tutarlılığı
    Gereksinim 6.3, 6.4
    """
    renderer = MockRenderer() if has_renderer else None
    physics = MockPhysics() if has_physics else None
    ctx = EngineContext(renderer=renderer, physics=physics)
    
    world = World()
    world.set_engine_context(ctx)
    
    actor = Actor("TestActor")
    sprite_comp = SpriteComponent()
    physics_comp = PhysicsComponent()
    
    if spawn_first:
        # Spawn actor then add components
        world.spawn_actor(actor)
        actor.add_component(sprite_comp)
        actor.add_component(physics_comp)
    else:
        # Add components then spawn actor
        actor.add_component(sprite_comp)
        actor.add_component(physics_comp)
        world.spawn_actor(actor)
        
    # Verify injection
    assert sprite_comp.renderer == renderer
    assert physics_comp.physics == physics

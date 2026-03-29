import pytest
from world.components.engine_context import EngineContext
from world.component import Component

class MockComponent(Component):
    def __init__(self):
        super().__init__()
        self.renderer = None
        self.physics = None

class MockRenderer:
    pass

class MockPhysics:
    pass

def test_engine_context_initialization():
    """Gereksinim 6.1, 6.5"""
    renderer = MockRenderer()
    physics = MockPhysics()
    ctx = EngineContext(renderer=renderer, physics=physics)
    
    assert ctx.renderer == renderer
    assert ctx.physics == physics

def test_engine_context_injection():
    """Gereksinim 6.6, 6.7"""
    renderer = MockRenderer()
    physics = MockPhysics()
    ctx = EngineContext(renderer=renderer, physics=physics)
    
    comp = MockComponent()
    ctx.inject(comp)
    
    assert comp.renderer == renderer
    assert comp.physics == physics

def test_engine_context_none_injection():
    """Gereksinim 6.8"""
    ctx = EngineContext(renderer=None, physics=None)
    comp = MockComponent()
    
    # Set some initial values to ensure they are cleared/set to None
    comp.renderer = "something"
    comp.physics = "something"
    
    ctx.inject(comp)
    
    assert comp.renderer is None
    assert comp.physics is None

def test_engine_context_partial_injection():
    """Gereksinim 6.6"""
    class PartialComponent:
        def __init__(self):
            self.renderer = None
            # No physics attribute
            
    renderer = MockRenderer()
    ctx = EngineContext(renderer=renderer)
    
    comp = PartialComponent()
    ctx.inject(comp)
    
    assert comp.renderer == renderer
    assert not hasattr(comp, "physics")

def test_world_engine_context_integration():
    """Gereksinim 6.2, 6.3, 6.4"""
    from world.world import World
    from world.actor import Actor
    
    renderer = MockRenderer()
    ctx = EngineContext(renderer=renderer)
    
    world = World()
    world.set_engine_context(ctx)
    
    actor = Actor("TestActor")
    comp = MockComponent()
    
    # Case 1: Add component before spawn
    actor.add_component(comp)
    assert comp.renderer is None # Not injected yet
    
    world.spawn_actor(actor)
    assert comp.renderer == renderer # Injected on spawn
    
    # Case 2: Add component after spawn
    comp2 = MockComponent()
    actor.add_component(comp2)
    assert comp2.renderer == renderer # Injected on add_component

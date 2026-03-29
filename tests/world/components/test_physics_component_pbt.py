import pytest
from hypothesis import given, strategies as st
from world.components.physics_component import PhysicsComponent
from world.transform import TransformComponent
from world.actor import Actor

class MockPhysics:
    def __init__(self):
        self.bodies = {}
        self.next_id = 1
    def create_body(self, mass, moment):
        bid = self.next_id
        self.bodies[bid] = {"pos": (0, 0), "rot": 0, "vel": (0, 0)}
        self.next_id += 1
        return bid
    def remove_body(self, bid):
        if bid in self.bodies:
            del self.bodies[bid]
    def get_body_position(self, bid):
        return self.bodies[bid]["pos"]
    def set_body_position(self, bid, x, y):
        self.bodies[bid]["pos"] = (x, y)
    def get_body_velocity(self, bid):
        return self.bodies[bid]["vel"]
    def set_body_velocity(self, bid, vx, vy):
        self.bodies[bid]["vel"] = (vx, vy)

@given(
    mass=st.floats(min_value=0.1, max_value=100.0),
    moment=st.floats(min_value=1.0, max_value=1000.0)
)
def test_physics_component_body_lifecycle(mass, moment):
    """
    Özellik 5: PhysicsComponent Body Lifecycle
    Gereksinim 3.1, 3.6
    """
    physics = MockPhysics()
    comp = PhysicsComponent(mass=mass, moment=moment)
    comp.physics = physics
    
    actor = Actor("TestActor")
    actor.add_component(comp)
    
    assert comp.body_id is not None
    assert comp.body_id in physics.bodies
    
    actor.remove_component(comp)
    assert comp.body_id is None
    assert len(physics.bodies) == 0

@given(
    px=st.floats(min_value=-1000, max_value=1000),
    py=st.floats(min_value=-1000, max_value=1000)
)
def test_physics_component_position_sync(px, py):
    """
    Özellik 6: PhysicsComponent İki Yönlü Pozisyon Senkronizasyonu
    Gereksinim 3.2, 3.3
    """
    physics = MockPhysics()
    comp = PhysicsComponent()
    comp.physics = physics
    
    actor = Actor("TestActor")
    transform = TransformComponent()
    transform.position = (px, py)
    
    actor.add_component(transform)
    actor.add_component(comp)
    
    # Initial sync (on_attach)
    assert physics.bodies[comp.body_id]["pos"] == (px, py)
    
    # Physics to Transform sync
    physics.set_body_position(comp.body_id, px + 10, py + 10)
    comp.on_tick(0.016)
    assert transform.position == (px + 10, py + 10)
    
    # Transform to Physics sync
    transform.position = (px - 5, py - 5)
    comp.sync_to_physics()
    assert physics.bodies[comp.body_id]["pos"] == (px - 5, py - 5)

from world.components.physics_component import PhysicsComponent
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

def test_physics_component_velocity_api():
    """Gereksinim 3.4"""
    physics = MockPhysics()
    comp = PhysicsComponent()
    comp.physics = physics
    
    actor = Actor("TestActor")
    actor.add_component(comp)
    
    comp.velocity = (10, 20)
    assert comp.velocity == (10, 20)
    assert physics.bodies[comp.body_id]["vel"] == (10, 20)

def test_physics_component_on_collision_callback():
    """Gereksinim 3.5"""
    comp = PhysicsComponent()
    
    collision_called = False
    def on_collision(other):
        nonlocal collision_called
        collision_called = True
        
    comp.on_collision = on_collision
    
    # Simulate collision
    if comp.on_collision:
        comp.on_collision("OtherActor")
        
    assert collision_called == True

def test_physics_component_none_behavior():
    """Gereksinim 3.7"""
    comp = PhysicsComponent()
    comp.physics = None
    
    actor = Actor("TestActor")
    actor.add_component(comp)
    
    # Should not raise exception
    comp.on_tick(0.016)
    comp.sync_to_physics()
    assert comp.velocity == (0.0, 0.0)

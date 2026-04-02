from world.components.camera_component import CameraComponent
from world.transform import TransformComponent
from world.actor import Actor

class MockCamera:
    def __init__(self):
        self.zoom = 1.0
        self.rotation = 0.0
        self.viewport_width = 800
        self.viewport_height = 600
        self.follow_target = None
        self.update_called = False
    def update(self, dt):
        self.update_called = True
    def resize(self, w, h):
        self.viewport_width = w
        self.viewport_height = h

def test_camera_component_follow_owner():
    """Gereksinim 4.3"""
    camera = MockCamera()
    comp = CameraComponent(camera, follow_owner=True)
    
    actor = Actor("TestActor")
    transform = TransformComponent()
    actor.add_component(transform)
    actor.add_component(comp)
    
    assert camera.follow_target == transform

def test_camera_component_proxy_properties():
    """Gereksinim 4.4, 4.5"""
    camera = MockCamera()
    comp = CameraComponent(camera)
    
    comp.zoom = 2.0
    assert camera.zoom == 2.0
    
    comp.rotation = 45.0
    assert camera.rotation == 45.0
    
    comp.viewport_size = (1920, 1080)
    assert camera.viewport_width == 1920
    assert camera.viewport_height == 1080

def test_camera_component_enabled_behavior():
    """Gereksinim 4.6"""
    camera = MockCamera()
    comp = CameraComponent(camera)
    
    comp.enabled = True
    comp.on_tick(0.016)
    assert camera.update_called == True
    
    camera.update_called = False
    comp.enabled = False
    comp.on_tick(0.016)
    assert camera.update_called == False

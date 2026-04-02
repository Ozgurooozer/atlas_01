import logging
from hypothesis import given, strategies as st
from world.components.script_component import ScriptComponent
from world.actor import Actor

class MockScript:
    def __init__(self):
        self.actor = None
        self.blackboard = None
        self.start_called = False
        self.tick_called = False
        self.destroy_called = False
        self.last_dt = 0.0
    def on_start(self):
        self.start_called = True
    def on_tick(self, dt):
        self.tick_called = True
        self.last_dt = dt
    def on_destroy(self):
        self.destroy_called = True

class CrashingScript:
    def on_start(self): raise Exception("Start Crash")
    def on_tick(self, dt): raise Exception("Tick Crash")
    def on_destroy(self): raise Exception("Destroy Crash")

@given(
    dt=st.floats(min_value=0.001, max_value=1.0)
)
def test_script_component_lifecycle_delegation(dt):
    """
    Özellik 7: ScriptComponent Lifecycle Delegation
    Gereksinim 5.2, 5.3, 5.4, 5.8
    """
    script = MockScript()
    blackboard = {"key": "value"}
    comp = ScriptComponent(script, blackboard=blackboard)
    
    actor = Actor("TestActor")
    actor.add_component(comp)
    
    assert script.actor == actor
    assert script.blackboard == blackboard
    assert script.start_called == True
    
    comp.on_tick(dt)
    assert script.tick_called == True
    assert script.last_dt == dt
    
    actor.remove_component(comp)
    assert script.destroy_called == True

def test_script_component_exception_isolation(caplog):
    """
    Özellik 8: ScriptComponent İstisna İzolasyonu
    Gereksinim 5.7
    """
    script = CrashingScript()
    comp = ScriptComponent(script)
    actor = Actor("TestActor")
    
    # Test on_attach isolation
    with caplog.at_level(logging.ERROR):
        actor.add_component(comp)
    assert "Error in script.on_start" in caplog.text
    
    # Test on_tick isolation
    caplog.clear()
    with caplog.at_level(logging.ERROR):
        comp.on_tick(0.016)
    assert "Error in script.on_tick" in caplog.text
    
    # Test on_detach isolation
    caplog.clear()
    with caplog.at_level(logging.ERROR):
        actor.remove_component(comp)
    assert "Error in script.on_destroy" in caplog.text

import pytest
from world.components.script_component import ScriptComponent
from world.actor import Actor

class DuckScript:
    """Script with only some methods."""
    def on_tick(self, dt):
        self.ticked = True

def test_script_component_duck_typing():
    """Gereksinim 5.1, 5.5"""
    script = DuckScript()
    comp = ScriptComponent(script)
    
    actor = Actor("TestActor")
    actor.add_component(comp)
    
    # Should not crash even if on_start is missing
    comp.on_tick(0.016)
    assert script.ticked == True
    
    # Should not crash even if on_destroy is missing
    actor.remove_component(comp)

def test_script_component_blackboard_access():
    """Gereksinim 5.6, 5.8"""
    class BlackboardScript:
        def on_start(self):
            self.blackboard["started"] = True
            
    script = BlackboardScript()
    blackboard = {"initial": 42}
    comp = ScriptComponent(script, blackboard=blackboard)
    
    actor = Actor("TestActor")
    actor.add_component(comp)
    
    assert script.blackboard["initial"] == 42
    assert script.blackboard["started"] == True
    assert blackboard["started"] == True

def test_script_component_serialization():
    """Gereksinim 5.8"""
    script = DuckScript()
    blackboard = {"score": 100}
    comp = ScriptComponent(script, blackboard=blackboard)
    
    data = comp.serialize()
    assert data["blackboard"] == {"score": 100}
    
    new_script = DuckScript()
    new_comp = ScriptComponent(new_script)
    new_comp.deserialize(data)
    assert new_comp.blackboard == {"score": 100}

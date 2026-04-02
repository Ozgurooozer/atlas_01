"""Tests for Prefab system.

class MockObject:
    """Simple mock for testing."""
    def __init__(self):
        self.call_count = 0
        self.call_args = None


Test-First Development for Prefab management
"""
import pytest
from world.prefab import Prefab, PrefabInstance, PrefabManager, ComponentData


class TestComponentData:
    """Test component data."""
    
    def test_initialization(self):
        """Test component data creation."""
        data = ComponentData("transform", {"x": 10, "y": 20})
        
        assert data.type == "transform"
        assert data.properties["x"] == 10
    
    def test_default_properties(self):
        """Test component data with defaults."""
        data = ComponentData("sprite")
        
        assert data.type == "sprite"
        assert data.properties == {}


class TestPrefab:
    """Test prefab."""
    
    def test_initialization(self):
        """Test prefab creation."""
        prefab = Prefab("enemy_basic")
        
        assert prefab.name == "enemy_basic"
        assert prefab.components == []
    
    def test_add_component(self):
        """Test adding component."""
        prefab = Prefab("player")
        comp = ComponentData("transform", {"x": 0, "y": 0})
        
        prefab.add_component(comp)
        
        assert len(prefab.components) == 1
        assert prefab.components[0] == comp
    
    def test_add_multiple_components(self):
        """Test adding multiple components."""
        prefab = Prefab("player")
        prefab.add_component(ComponentData("transform"))
        prefab.add_component(ComponentData("sprite"))
        prefab.add_component(ComponentData("health"))
        
        assert len(prefab.components) == 3
    
    def test_set_property(self):
        """Test setting property."""
        prefab = Prefab("enemy")
        prefab.set_property("health", 100)
        prefab.set_property("speed", 5.5)
        
        assert prefab.properties["health"] == 100
        assert prefab.properties["speed"] == 5.5
    
    def test_get_property(self):
        """Test getting property."""
        prefab = Prefab("enemy")
        prefab.set_property("health", 100)
        
        assert prefab.get_property("health") == 100
    
    def test_get_property_default(self):
        """Test getting missing property with default."""
        prefab = Prefab("enemy")
        
        assert prefab.get_property("missing", 50) == 50
    
    def test_get_property_missing_raises(self):
        """Test getting missing property raises if no default."""
        prefab = Prefab("enemy")
        
        with pytest.raises(KeyError):
            prefab.get_property("missing")
    
    def test_clone(self):
        """Test cloning prefab."""
        prefab = Prefab("original")
        prefab.add_component(ComponentData("transform", {"x": 10}))
        prefab.set_property("health", 100)
        
        clone = prefab.clone("clone")
        
        assert clone.name == "clone"
        assert len(clone.components) == 1
        assert clone.get_property("health") == 100
        # Should be independent copy
        clone.set_property("health", 50)
        assert prefab.get_property("health") == 100


class TestPrefabInstance:
    """Test prefab instance."""
    
    def test_initialization(self):
        """Test instance creation."""
        prefab = Prefab("enemy")
        instance = PrefabInstance(prefab)
        
        assert instance.prefab == prefab
        assert instance.overrides == {}
    
    def test_set_override(self):
        """Test setting property override."""
        prefab = Prefab("enemy")
        prefab.set_property("health", 100)
        
        instance = PrefabInstance(prefab)
        instance.set_override("health", 200)
        
        assert instance.overrides["health"] == 200
    
    def test_get_property_prefab_value(self):
        """Test getting prefab property."""
        prefab = Prefab("enemy")
        prefab.set_property("health", 100)
        
        instance = PrefabInstance(prefab)
        
        assert instance.get_property("health") == 100
    
    def test_get_property_override_value(self):
        """Test getting overridden property."""
        prefab = Prefab("enemy")
        prefab.set_property("health", 100)
        
        instance = PrefabInstance(prefab)
        instance.set_override("health", 200)
        
        assert instance.get_property("health") == 200
    
    def test_apply_to_object(self):
        """Test applying prefab to object."""
        prefab = Prefab("enemy")
        prefab.add_component(ComponentData("health", {"value": 100}))
        
        obj = MockObject()
        obj.components = []
        
        def add_component(type, **props):
            obj.components.append((type, props))
        
        obj.add_component = add_component
        
        instance = PrefabInstance(prefab)
        instance.apply_to(obj)
        
        assert len(obj.components) == 1
        assert obj.components[0][0] == "health"


class TestPrefabManager:
    """Test prefab manager."""
    
    def test_initialization(self):
        """Test manager creation."""
        manager = PrefabManager()
        assert manager.prefabs == {}
    
    def test_register_prefab(self):
        """Test registering prefab."""
        manager = PrefabManager()
        prefab = Prefab("enemy")
        
        manager.register(prefab)
        
        assert "enemy" in manager.prefabs
    
    def test_get_prefab(self):
        """Test getting prefab."""
        manager = PrefabManager()
        prefab = Prefab("enemy")
        manager.register(prefab)
        
        retrieved = manager.get("enemy")
        
        assert retrieved == prefab
    
    def test_get_prefab_missing(self):
        """Test getting missing prefab."""
        manager = PrefabManager()
        
        assert manager.get("nonexistent") is None
    
    def test_has_prefab(self):
        """Test checking prefab existence."""
        manager = PrefabManager()
        prefab = Prefab("enemy")
        manager.register(prefab)
        
        assert manager.has("enemy") is True
        assert manager.has("player") is False
    
    def test_create_instance(self):
        """Test creating prefab instance."""
        manager = PrefabManager()
        prefab = Prefab("enemy")
        prefab.set_property("health", 100)
        manager.register(prefab)
        
        instance = manager.create_instance("enemy")
        
        assert instance.prefab == prefab
        assert instance.get_property("health") == 100
    
    def test_create_instance_not_found(self):
        """Test creating instance of missing prefab."""
        manager = PrefabManager()
        
        with pytest.raises(KeyError):
            manager.create_instance("nonexistent")
    
    def test_unregister_prefab(self):
        """Test unregistering prefab."""
        manager = PrefabManager()
        prefab = Prefab("enemy")
        manager.register(prefab)
        
        manager.unregister("enemy")
        
        assert manager.has("enemy") is False
    
    def test_get_all_names(self):
        """Test getting all prefab names."""
        manager = PrefabManager()
        manager.register(Prefab("enemy"))
        manager.register(Prefab("player"))
        manager.register(Prefab("npc"))
        
        names = manager.get_all_names()
        
        assert "enemy" in names
        assert "player" in names
        assert "npc" in names
    
    def test_clear(self):
        """Test clearing all prefabs."""
        manager = PrefabManager()
        manager.register(Prefab("enemy"))
        
        manager.clear()
        
        assert manager.prefabs == {}

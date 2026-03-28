"""
Tests for Actor class.

Actor is an object that exists in the game world.
Actors contain Components that define their behavior.

Layer: 3 (World)
"""

import pytest
from core.object import Object
from core.guid import GUID
from core.reflection import reflect, get_properties, get_property_value, set_property_value
from world.component import Component
from world.actor import Actor


class TestActorInheritance:
    """Test that Actor properly inherits from Object."""

    def test_actor_is_object(self):
        """Actor should be an instance of Object."""
        actor = Actor()
        assert isinstance(actor, Object)

    def test_actor_has_guid(self):
        """Actor should have a GUID."""
        actor = Actor()
        assert hasattr(actor, "guid")
        assert isinstance(actor.guid, GUID)

    def test_actor_has_name(self):
        """Actor should have a name."""
        actor = Actor(name="TestActor")
        assert actor.name == "TestActor"

    def test_actor_default_name(self):
        """Actor default name should be class name."""
        actor = Actor()
        assert actor.name == "Actor"


class TestActorComponents:
    """Test Actor component management."""

    def test_actor_has_components_property(self):
        """Actor should have a components property."""
        actor = Actor()
        assert hasattr(actor, "components")

    def test_actor_components_default_empty(self):
        """Actor should have empty components list by default."""
        actor = Actor()
        assert actor.components == []

    def test_actor_add_component(self):
        """Actor can add a component."""
        actor = Actor()
        comp = Component()
        actor.add_component(comp)
        assert comp in actor.components

    def test_actor_add_component_sets_owner(self):
        """Adding component sets the owner."""
        actor = Actor()
        comp = Component()
        actor.add_component(comp)
        assert comp.owner is actor

    def test_actor_add_component_calls_on_attach(self):
        """Adding component calls on_attach."""
        results = []

        class TestComp(Component):
            def on_attach(self, owner):
                results.append(owner)

        actor = Actor()
        comp = TestComp()
        actor.add_component(comp)

        assert results[0] is actor

    def test_actor_remove_component(self):
        """Actor can remove a component."""
        actor = Actor()
        comp = Component()
        actor.add_component(comp)
        actor.remove_component(comp)
        assert comp not in actor.components

    def test_actor_remove_component_clears_owner(self):
        """Removing component clears owner."""
        actor = Actor()
        comp = Component()
        actor.add_component(comp)
        actor.remove_component(comp)
        assert comp.owner is None

    def test_actor_remove_component_calls_on_detach(self):
        """Removing component calls on_detach."""
        results = []

        class TestComp(Component):
            def on_detach(self):
                results.append("detached")

        actor = Actor()
        comp = TestComp()
        actor.add_component(comp)
        actor.remove_component(comp)

        assert "detached" in results

    def test_actor_get_component_by_type(self):
        """Actor can get component by type."""
        class HealthComponent(Component):
            pass

        class MovementComponent(Component):
            pass

        actor = Actor()
        health = HealthComponent()
        movement = MovementComponent()
        actor.add_component(health)
        actor.add_component(movement)

        found = actor.get_component(HealthComponent)
        assert found is health

    def test_actor_get_component_returns_none_if_not_found(self):
        """get_component returns None if type not found."""
        class HealthComponent(Component):
            pass

        actor = Actor()
        found = actor.get_component(HealthComponent)
        assert found is None


class TestActorTick:
    """Test Actor tick functionality."""

    def test_actor_has_tick_method(self):
        """Actor should have tick method."""
        actor = Actor()
        assert hasattr(actor, "tick")
        assert callable(actor.tick)

    def test_actor_tick_propagates_to_components(self):
        """Actor tick propagates to enabled components."""
        tick_results = []

        class TestComp(Component):
            def on_tick(self, delta_time: float):
                tick_results.append(delta_time)

        actor = Actor()
        comp = TestComp()
        actor.add_component(comp)
        actor.tick(0.016)

        assert 0.016 in tick_results

    def test_actor_tick_skips_disabled_components(self):
        """Actor tick should not call disabled components."""
        tick_results = []

        class TestComp(Component):
            def on_tick(self, delta_time: float):
                tick_results.append(delta_time)

        actor = Actor()
        comp = TestComp()
        comp.enabled = False
        actor.add_component(comp)
        actor.tick(0.016)

        assert len(tick_results) == 0


class TestActorWorld:
    """Test Actor-World relationship."""

    def test_actor_has_world_property(self):
        """Actor should have a world property."""
        actor = Actor()
        assert hasattr(actor, "world")

    def test_actor_world_default_none(self):
        """Actor world should default to None."""
        actor = Actor()
        assert actor.world is None

    def test_actor_world_can_be_set(self):
        """Actor world can be set."""
        actor = Actor()
        # Use mock object as world
        mock_world = object()
        actor.world = mock_world
        assert actor.world is mock_world


class TestActorEnabledState:
    """Test Actor enabled/disabled state."""

    def test_actor_has_enabled_property(self):
        """Actor should have an enabled property."""
        actor = Actor()
        assert hasattr(actor, "enabled")

    def test_actor_enabled_by_default(self):
        """Actor should be enabled by default."""
        actor = Actor()
        assert actor.enabled is True

    def test_actor_can_be_disabled(self):
        """Actor can be disabled."""
        actor = Actor()
        actor.enabled = False
        assert actor.enabled is False

    def test_disabled_actor_skips_tick(self):
        """Disabled actor should not tick components."""
        tick_results = []

        class TestComp(Component):
            def on_tick(self, delta_time: float):
                tick_results.append(delta_time)

        actor = Actor()
        comp = TestComp()
        actor.add_component(comp)
        actor.enabled = False
        actor.tick(0.016)

        assert len(tick_results) == 0


class TestActorSerialization:
    """Test Actor serialization."""

    def test_actor_serialize(self):
        """Actor should serialize basic properties."""
        actor = Actor(name="TestActor")
        actor.enabled = False

        data = actor.serialize()

        assert data["name"] == "TestActor"
        assert data["enabled"] is False

    def test_actor_deserialize(self):
        """Actor should deserialize basic properties."""
        actor = Actor()
        data = {
            "name": "DeserializedActor",
            "enabled": False,
            "guid": "00000000-0000-0000-0000-000000000002"
        }

        actor.deserialize(data)

        assert actor.name == "DeserializedActor"
        assert actor.enabled is False


class TestActorReflection:
    """Test Actor with reflection system."""

    def test_actor_can_use_reflect_decorator(self):
        """Actor subclasses can use @reflect decorator."""
        class PlayerActor(Actor):
            def __init__(self, name: str = None):
                super().__init__(name)
                self._speed = 100.0

            @reflect("float", min=0, max=500, category="Movement")
            def speed(self) -> float:
                return self._speed

            @speed.setter
            def speed(self, value: float):
                self._speed = value

        actor = PlayerActor()
        props = get_properties(actor)

        assert len(props) == 1
        assert props[0].name == "speed"
        assert props[0].type_hint == "float"


class TestActorRepr:
    """Test Actor string representation."""

    def test_actor_repr(self):
        """Actor should have useful repr."""
        actor = Actor(name="TestActor")
        repr_str = repr(actor)

        assert "Actor" in repr_str
        assert "TestActor" in repr_str


class TestActorLifecycle:
    """Test Actor lifecycle hooks."""

    def test_actor_has_on_created(self):
        """Actor inherits on_created from Object."""
        actor = Actor()
        assert hasattr(actor, "on_created")
        assert callable(actor.on_created)

    def test_actor_has_on_destroyed(self):
        """Actor inherits on_destroyed from Object."""
        actor = Actor()
        assert hasattr(actor, "on_destroyed")
        assert callable(actor.on_destroyed)

    def test_actor_on_destroyed_removes_components(self):
        """on_destroyed should remove all components."""
        actor = Actor()
        comp1 = Component()
        comp2 = Component()
        actor.add_component(comp1)
        actor.add_component(comp2)

        actor.on_destroyed()

        assert len(actor.components) == 0
        assert comp1.owner is None
        assert comp2.owner is None

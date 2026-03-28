"""
Tests for Component base class.

Component is the base class for all behaviors attached to Actors.
Components inherit from Object and provide modular functionality.

Layer: 3 (World)
"""

import pytest
from core.object import Object
from core.guid import GUID
from core.reflection import reflect, get_properties, get_property_value, set_property_value
from world.component import Component


class TestComponentInheritance:
    """Test that Component properly inherits from Object."""

    def test_component_is_object(self):
        """Component should be an instance of Object."""
        comp = Component()
        assert isinstance(comp, Object)

    def test_component_has_guid(self):
        """Component should have a GUID."""
        comp = Component()
        assert hasattr(comp, "guid")
        assert isinstance(comp.guid, GUID)

    def test_component_has_name(self):
        """Component should have a name."""
        comp = Component(name="TestComponent")
        assert comp.name == "TestComponent"

    def test_component_default_name(self):
        """Component default name should be class name."""
        comp = Component()
        assert comp.name == "Component"


class TestComponentOwner:
    """Test Component owner (Actor) reference."""

    def test_component_has_owner_property(self):
        """Component should have an owner property."""
        comp = Component()
        assert hasattr(comp, "owner")

    def test_component_owner_default_none(self):
        """Component owner should default to None."""
        comp = Component()
        assert comp.owner is None

    def test_component_owner_can_be_set(self):
        """Component owner can be set."""
        comp = Component()
        # Use a mock object as owner (will be Actor in production)
        mock_owner = object()
        comp.owner = mock_owner
        assert comp.owner is mock_owner


class TestComponentEnabledState:
    """Test Component enabled/disabled state."""

    def test_component_has_enabled_property(self):
        """Component should have an enabled property."""
        comp = Component()
        assert hasattr(comp, "enabled")

    def test_component_enabled_by_default(self):
        """Component should be enabled by default."""
        comp = Component()
        assert comp.enabled is True

    def test_component_can_be_disabled(self):
        """Component can be disabled."""
        comp = Component()
        comp.enabled = False
        assert comp.enabled is False

    def test_component_can_be_re_enabled(self):
        """Component can be re-enabled after disable."""
        comp = Component()
        comp.enabled = False
        comp.enabled = True
        assert comp.enabled is True


class TestComponentLifecycle:
    """Test Component lifecycle hooks."""

    def test_component_has_on_attach(self):
        """Component should have on_attach method."""
        comp = Component()
        assert hasattr(comp, "on_attach")
        assert callable(comp.on_attach)

    def test_component_has_on_detach(self):
        """Component should have on_detach method."""
        comp = Component()
        assert hasattr(comp, "on_detach")
        assert callable(comp.on_detach)

    def test_component_has_on_tick(self):
        """Component should have on_tick method."""
        comp = Component()
        assert hasattr(comp, "on_tick")
        assert callable(comp.on_tick)

    def test_on_attach_receives_owner(self):
        """on_attach should receive owner as parameter."""
        results = []

        class TestComp(Component):
            def on_attach(self, owner):
                results.append(owner)

        comp = TestComp()
        mock_owner = object()
        comp.on_attach(mock_owner)
        assert results[0] is mock_owner

    def test_on_tick_receives_delta_time(self):
        """on_tick should receive delta_time parameter."""
        results = []

        class TestComp(Component):
            def on_tick(self, delta_time: float):
                results.append(delta_time)

        comp = TestComp()
        comp.on_tick(0.016)
        assert results[0] == 0.016

    def test_lifecycle_hooks_can_be_overridden(self):
        """Lifecycle hooks can be overridden in subclasses."""
        call_order = []

        class CustomComponent(Component):
            def on_attach(self, owner):
                call_order.append("attach")

            def on_detach(self):
                call_order.append("detach")

            def on_tick(self, delta_time: float):
                call_order.append("tick")

        comp = CustomComponent()
        comp.on_attach(object())
        comp.on_tick(0.016)
        comp.on_detach()

        assert call_order == ["attach", "tick", "detach"]


class TestComponentSerialization:
    """Test Component serialization."""

    def test_component_serialize(self):
        """Component should serialize basic properties."""
        comp = Component(name="MyComponent")
        comp.enabled = False

        data = comp.serialize()

        assert data["name"] == "MyComponent"
        assert data["enabled"] is False

    def test_component_deserialize(self):
        """Component should deserialize basic properties."""
        comp = Component()
        data = {
            "name": "DeserializedComponent",
            "enabled": False,
            "guid": "00000000-0000-0000-0000-000000000001"
        }

        comp.deserialize(data)

        assert comp.name == "DeserializedComponent"
        assert comp.enabled is False


class TestComponentReflection:
    """Test Component with reflection system."""

    def test_component_can_use_reflect_decorator(self):
        """Component subclasses can use @reflect decorator."""
        class HealthComponent(Component):
            def __init__(self, name: str = None):
                super().__init__(name)
                self._health = 100.0

            @reflect("float", min=0, max=100, category="Stats")
            def health(self) -> float:
                return self._health

            @health.setter
            def health(self, value: float):
                self._health = value

        comp = HealthComponent()
        props = get_properties(comp)

        assert len(props) == 1
        assert props[0].name == "health"
        assert props[0].type_hint == "float"
        assert props[0].min == 0
        assert props[0].max == 100

    def test_reflected_property_can_be_accessed(self):
        """Reflected properties on Component can be accessed."""
        class HealthComponent(Component):
            def __init__(self, name: str = None):
                super().__init__(name)
                self._health = 100.0

            @reflect("float", min=0, max=100)
            def health(self) -> float:
                return self._health

            @health.setter
            def health(self, value: float):
                self._health = value

        comp = HealthComponent()

        # Get value
        assert get_property_value(comp, "health") == 100.0

        # Set value
        set_property_value(comp, "health", 50.0)
        assert comp.health == 50.0


class TestComponentRepr:
    """Test Component string representation."""

    def test_component_repr(self):
        """Component should have useful repr."""
        comp = Component(name="TestComp")
        repr_str = repr(comp)

        assert "Component" in repr_str
        assert "TestComp" in repr_str


class TestComponentFlags:
    """Test Component flags (inherited from Object)."""

    def test_component_has_flags(self):
        """Component should have flags from Object."""
        comp = Component()
        assert hasattr(comp, "flags")
        assert comp.flags == 0

    def test_component_flags_can_be_set(self):
        """Component flags can be set."""
        comp = Component()
        comp.flags = 0x01
        assert comp.flags == 0x01

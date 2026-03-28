"""
Object Base Class Tests.

Tests for the Object class - the foundation of everything in the engine.
Actor, Component, Widget, Asset all inherit from Object.
"""

import pytest


class TestObjectCreation:
    """Test Object creation and basic properties."""

    def test_object_creation(self):
        """Object should be creatable."""
        from core.object import Object
        obj = Object()
        assert obj is not None

    def test_object_has_guid(self):
        """Object should have a GUID."""
        from core.object import Object
        obj = Object()
        assert hasattr(obj, 'guid')
        assert obj.guid is not None

    def test_object_guid_is_guid_type(self):
        """Object GUID should be GUID type."""
        from core.object import Object
        from core.guid import GUID
        obj = Object()
        assert isinstance(obj.guid, GUID)

    def test_object_unique_guids(self):
        """Each Object should have unique GUID."""
        from core.object import Object
        obj1 = Object()
        obj2 = Object()
        assert obj1.guid != obj2.guid

    def test_object_has_name(self):
        """Object should have a name."""
        from core.object import Object
        obj = Object()
        assert hasattr(obj, 'name')
        assert obj.name is not None

    def test_object_default_name(self):
        """Object default name should be class name."""
        from core.object import Object
        obj = Object()
        assert obj.name == "Object"

    def test_object_custom_name(self):
        """Object can have custom name."""
        from core.object import Object
        obj = Object(name="MyObject")
        assert obj.name == "MyObject"

    def test_object_can_rename(self):
        """Object name can be changed."""
        from core.object import Object
        obj = Object()
        obj.name = "NewName"
        assert obj.name == "NewName"


class TestObjectSerialization:
    """Test Object serialization."""

    def test_object_serialize(self):
        """Object should be serializable."""
        from core.object import Object
        obj = Object(name="TestObject")
        data = obj.serialize()
        assert isinstance(data, dict)
        assert "guid" in data
        assert "name" in data
        assert data["name"] == "TestObject"

    def test_object_deserialize(self):
        """Object should be deserializable."""
        from core.object import Object
        obj1 = Object(name="Original")
        data = obj1.serialize()

        obj2 = Object()
        obj2.deserialize(data)
        assert obj2.name == "Original"

    def test_object_serialize_has_class_name(self):
        """Serialized object should have class name."""
        from core.object import Object
        obj = Object()
        data = obj.serialize()
        assert "__class__" in data
        assert data["__class__"] == "Object"


class TestObjectLifecycle:
    """Test Object lifecycle methods."""

    def test_object_has_on_created(self):
        """Object should have on_created method."""
        from core.object import Object
        obj = Object()
        assert hasattr(obj, 'on_created')
        # Should be callable without error
        obj.on_created()

    def test_object_has_on_destroyed(self):
        """Object should have on_destroyed method."""
        from core.object import Object
        obj = Object()
        assert hasattr(obj, 'on_destroyed')
        # Should be callable without error
        obj.on_destroyed()


class TestObjectFlags:
    """Test Object flags system."""

    def test_object_has_flags(self):
        """Object should have flags."""
        from core.object import Object
        obj = Object()
        assert hasattr(obj, 'flags')

    def test_object_flags_default_none(self):
        """Object flags default to NONE (0)."""
        from core.object import Object
        obj = Object()
        assert obj.flags == 0

    def test_object_can_set_flags(self):
        """Object flags can be set."""
        from core.object import Object
        obj = Object()
        obj.flags = 1
        assert obj.flags == 1


class TestObjectInheritance:
    """Test Object inheritance."""

    def test_subclass_has_own_name_default(self):
        """Subclass should use its class name as default name."""
        from core.object import Object

        class MyActor(Object):
            pass

        actor = MyActor()
        assert actor.name == "MyActor"

    def test_subclass_serialize_preserves_class(self):
        """Subclass serialization should preserve class name."""
        from core.object import Object

        class MyComponent(Object):
            pass

        comp = MyComponent(name="TestComponent")
        data = comp.serialize()
        assert data["__class__"] == "MyComponent"

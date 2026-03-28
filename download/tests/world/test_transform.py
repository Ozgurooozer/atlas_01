"""
Tests for TransformComponent.

TransformComponent stores position, rotation, and scale for an Actor.
It's a fundamental component for any spatial entity.

Layer: 3 (World)
"""

import pytest
import math
from world.component import Component
from world.transform import TransformComponent
from core.reflection import get_properties


class TestTransformInheritance:
    """Test that TransformComponent inherits from Component."""

    def test_transform_is_component(self):
        """TransformComponent should be a Component."""
        transform = TransformComponent()
        assert isinstance(transform, Component)

    def test_transform_has_guid(self):
        """TransformComponent should have a GUID from Object."""
        transform = TransformComponent()
        assert hasattr(transform, "guid")

    def test_transform_has_name(self):
        """TransformComponent should have a name."""
        transform = TransformComponent(name="MyTransform")
        assert transform.name == "MyTransform"


class TestTransformPosition:
    """Test Transform position property."""

    def test_transform_has_position(self):
        """TransformComponent should have position."""
        transform = TransformComponent()
        assert hasattr(transform, "position")

    def test_position_defaults_to_zero(self):
        """Position should default to (0, 0)."""
        transform = TransformComponent()
        assert transform.position == (0.0, 0.0)

    def test_position_can_be_set_tuple(self):
        """Position can be set with tuple."""
        transform = TransformComponent()
        transform.position = (100.0, 200.0)
        assert transform.position == (100.0, 200.0)

    def test_position_can_be_set_list(self):
        """Position can be set with list."""
        transform = TransformComponent()
        transform.position = [100.0, 200.0]
        assert transform.position == (100.0, 200.0)

    def test_position_stores_as_tuple(self):
        """Position should always be stored as tuple."""
        transform = TransformComponent()
        transform.position = [100.0, 200.0]
        assert isinstance(transform.position, tuple)

    def test_position_x_y_access(self):
        """Position can be accessed as x, y."""
        transform = TransformComponent()
        transform.position = (100.0, 200.0)
        assert transform.x == 100.0
        assert transform.y == 200.0

    def test_position_can_set_x_y_individually(self):
        """Position x and y can be set individually."""
        transform = TransformComponent()
        transform.x = 50.0
        transform.y = 75.0
        assert transform.position == (50.0, 75.0)


class TestTransformRotation:
    """Test Transform rotation property."""

    def test_transform_has_rotation(self):
        """TransformComponent should have rotation."""
        transform = TransformComponent()
        assert hasattr(transform, "rotation")

    def test_rotation_defaults_to_zero(self):
        """Rotation should default to 0."""
        transform = TransformComponent()
        assert transform.rotation == 0.0

    def test_rotation_can_be_set(self):
        """Rotation can be set in degrees."""
        transform = TransformComponent()
        transform.rotation = 90.0
        assert transform.rotation == 90.0

    def test_rotation_can_be_negative(self):
        """Rotation can be negative."""
        transform = TransformComponent()
        transform.rotation = -45.0
        assert transform.rotation == -45.0

    def test_rotation_can_exceed_360(self):
        """Rotation can exceed 360 degrees."""
        transform = TransformComponent()
        transform.rotation = 450.0
        assert transform.rotation == 450.0


class TestTransformScale:
    """Test Transform scale property."""

    def test_transform_has_scale(self):
        """TransformComponent should have scale."""
        transform = TransformComponent()
        assert hasattr(transform, "scale")

    def test_scale_defaults_to_one(self):
        """Scale should default to (1.0, 1.0)."""
        transform = TransformComponent()
        assert transform.scale == (1.0, 1.0)

    def test_scale_can_be_set_tuple(self):
        """Scale can be set with tuple."""
        transform = TransformComponent()
        transform.scale = (2.0, 3.0)
        assert transform.scale == (2.0, 3.0)

    def test_scale_can_be_uniform(self):
        """Scale can be set uniformly with single value."""
        transform = TransformComponent()
        transform.set_uniform_scale(2.0)
        assert transform.scale == (2.0, 2.0)

    def test_scale_x_y_access(self):
        """Scale can be accessed as scale_x, scale_y."""
        transform = TransformComponent()
        transform.scale = (2.0, 3.0)
        assert transform.scale_x == 2.0
        assert transform.scale_y == 3.0


class TestTransformReflection:
    """Test TransformComponent reflection properties."""

    def test_transform_properties_are_reflected(self):
        """Transform properties should be reflected."""
        transform = TransformComponent()
        props = get_properties(transform)
        prop_names = [p.name for p in props]

        assert "x" in prop_names
        assert "y" in prop_names
        assert "rotation" in prop_names
        assert "scale_x" in prop_names
        assert "scale_y" in prop_names

    def test_position_has_category(self):
        """Position properties should have Transform category."""
        transform = TransformComponent()
        props = get_properties(transform)

        x_prop = next(p for p in props if p.name == "x")
        assert x_prop.category == "Transform"


class TestTransformSerialization:
    """Test TransformComponent serialization."""

    def test_transform_serialize(self):
        """TransformComponent should serialize all properties."""
        transform = TransformComponent()
        transform.position = (100.0, 200.0)
        transform.rotation = 45.0
        transform.scale = (2.0, 3.0)

        data = transform.serialize()

        assert data["x"] == 100.0
        assert data["y"] == 200.0
        assert data["rotation"] == 45.0
        assert data["scale_x"] == 2.0
        assert data["scale_y"] == 3.0

    def test_transform_deserialize(self):
        """TransformComponent should deserialize all properties."""
        transform = TransformComponent()
        data = {
            "x": 100.0,
            "y": 200.0,
            "rotation": 45.0,
            "scale_x": 2.0,
            "scale_y": 3.0
        }

        transform.deserialize(data)

        assert transform.position == (100.0, 200.0)
        assert transform.rotation == 45.0
        assert transform.scale == (2.0, 3.0)


class TestTransformHelperMethods:
    """Test TransformComponent helper methods."""

    def test_transform_has_translate(self):
        """TransformComponent should have translate method."""
        transform = TransformComponent()
        assert hasattr(transform, "translate")
        assert callable(transform.translate)

    def test_translate_adds_to_position(self):
        """Translate should add to current position."""
        transform = TransformComponent()
        transform.position = (100.0, 200.0)
        transform.translate(50.0, -25.0)
        assert transform.position == (150.0, 175.0)

    def test_transform_has_rotate(self):
        """TransformComponent should have rotate method."""
        transform = TransformComponent()
        assert hasattr(transform, "rotate")
        assert callable(transform.rotate)

    def test_rotate_adds_to_rotation(self):
        """Rotate should add to current rotation."""
        transform = TransformComponent()
        transform.rotation = 45.0
        transform.rotate(15.0)
        assert transform.rotation == 60.0

    def test_transform_has_reset(self):
        """TransformComponent should have reset method."""
        transform = TransformComponent()
        assert hasattr(transform, "reset")
        assert callable(transform.reset)

    def test_reset_resets_all_values(self):
        """Reset should reset all values to default."""
        transform = TransformComponent()
        transform.position = (100.0, 200.0)
        transform.rotation = 45.0
        transform.scale = (2.0, 3.0)

        transform.reset()

        assert transform.position == (0.0, 0.0)
        assert transform.rotation == 0.0
        assert transform.scale == (1.0, 1.0)


class TestTransformRepr:
    """Test TransformComponent string representation."""

    def test_transform_repr(self):
        """TransformComponent should have useful repr."""
        transform = TransformComponent()
        transform.position = (100.0, 200.0)
        repr_str = repr(transform)

        assert "TransformComponent" in repr_str
        assert "100" in repr_str or "position" in repr_str.lower()

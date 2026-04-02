"""Tests for Vec2 and Vec3 math utilities."""

import math


class TestVec2:
    """Test suite for Vec2 class."""

    def test_vec2_creation(self):
        """Vec2 should be created with x, y components."""
        from core.vec import Vec2

        v = Vec2(3.0, 4.0)
        assert v.x == 3.0
        assert v.y == 4.0

    def test_vec2_default_zero(self):
        """Vec2 should default to zero."""
        from core.vec import Vec2

        v = Vec2()
        assert v.x == 0.0
        assert v.y == 0.0

    def test_vec2_addition(self):
        """Vec2 should support addition."""
        from core.vec import Vec2

        v1 = Vec2(1.0, 2.0)
        v2 = Vec2(3.0, 4.0)
        result = v1 + v2

        assert result.x == 4.0
        assert result.y == 6.0

    def test_vec2_subtraction(self):
        """Vec2 should support subtraction."""
        from core.vec import Vec2

        v1 = Vec2(5.0, 7.0)
        v2 = Vec2(2.0, 3.0)
        result = v1 - v2

        assert result.x == 3.0
        assert result.y == 4.0

    def test_vec2_scalar_multiplication(self):
        """Vec2 should support scalar multiplication."""
        from core.vec import Vec2

        v = Vec2(2.0, 3.0)
        result = v * 2.0

        assert result.x == 4.0
        assert result.y == 6.0

    def test_vec2_scalar_division(self):
        """Vec2 should support scalar division."""
        from core.vec import Vec2

        v = Vec2(6.0, 8.0)
        result = v / 2.0

        assert result.x == 3.0
        assert result.y == 4.0

    def test_vec2_negation(self):
        """Vec2 should support negation."""
        from core.vec import Vec2

        v = Vec2(3.0, 4.0)
        result = -v

        assert result.x == -3.0
        assert result.y == -4.0

    def test_vec2_length(self):
        """Vec2 should calculate length."""
        from core.vec import Vec2

        v = Vec2(3.0, 4.0)
        assert v.length() == 5.0

    def test_vec2_length_squared(self):
        """Vec2 should calculate length squared."""
        from core.vec import Vec2

        v = Vec2(3.0, 4.0)
        assert v.length_squared() == 25.0

    def test_vec2_normalized(self):
        """Vec2 should return normalized vector."""
        from core.vec import Vec2

        v = Vec2(3.0, 4.0)
        n = v.normalized()

        assert abs(n.x - 0.6) < 0.001
        assert abs(n.y - 0.8) < 0.001
        assert abs(n.length() - 1.0) < 0.001

    def test_vec2_dot_product(self):
        """Vec2 should calculate dot product."""
        from core.vec import Vec2

        v1 = Vec2(1.0, 2.0)
        v2 = Vec2(3.0, 4.0)

        assert v1.dot(v2) == 11.0

    def test_vec2_cross_product(self):
        """Vec2 should calculate 2D cross product (scalar)."""
        from core.vec import Vec2

        v1 = Vec2(1.0, 2.0)
        v2 = Vec2(3.0, 4.0)

        # 1*4 - 2*3 = -2
        assert v1.cross(v2) == -2.0

    def test_vec2_distance_to(self):
        """Vec2 should calculate distance to another vector."""
        from core.vec import Vec2

        v1 = Vec2(0.0, 0.0)
        v2 = Vec2(3.0, 4.0)

        assert v1.distance_to(v2) == 5.0

    def test_vec2_angle(self):
        """Vec2 should calculate angle in radians."""
        from core.vec import Vec2

        v = Vec2(1.0, 0.0)
        assert abs(v.angle() - 0.0) < 0.001

        v = Vec2(0.0, 1.0)
        assert abs(v.angle() - math.pi / 2) < 0.001

    def test_vec2_rotate(self):
        """Vec2 should rotate by angle."""
        from core.vec import Vec2

        v = Vec2(1.0, 0.0)
        rotated = v.rotate(math.pi / 2)

        assert abs(rotated.x - 0.0) < 0.001
        assert abs(rotated.y - 1.0) < 0.001

    def test_vec2_lerp(self):
        """Vec2 should interpolate between vectors."""
        from core.vec import Vec2

        v1 = Vec2(0.0, 0.0)
        v2 = Vec2(10.0, 10.0)
        result = v1.lerp(v2, 0.5)

        assert result.x == 5.0
        assert result.y == 5.0

    def test_vec2_equality(self):
        """Vec2 should support equality comparison."""
        from core.vec import Vec2

        v1 = Vec2(1.0, 2.0)
        v2 = Vec2(1.0, 2.0)
        v3 = Vec2(1.0, 3.0)

        assert v1 == v2
        assert v1 != v3

    def test_vec2_copy(self):
        """Vec2 should be copyable."""
        from core.vec import Vec2

        v1 = Vec2(1.0, 2.0)
        v2 = v1.copy()

        assert v1 == v2
        assert v1 is not v2

    def test_vec2_tuple_conversion(self):
        """Vec2 should convert to tuple."""
        from core.vec import Vec2

        v = Vec2(3.0, 4.0)
        t = v.to_tuple()

        assert t == (3.0, 4.0)

    def test_vec2_from_tuple(self):
        """Vec2 should be created from tuple."""
        from core.vec import Vec2

        v = Vec2.from_tuple((3.0, 4.0))

        assert v.x == 3.0
        assert v.y == 4.0

    def test_vec2_repr(self):
        """Vec2 should have string representation."""
        from core.vec import Vec2

        v = Vec2(1.0, 2.0)
        assert "Vec2" in repr(v)
        assert "1.0" in repr(v)
        assert "2.0" in repr(v)


class TestVec2Constants:
    """Test suite for Vec2 constants."""

    def test_vec2_zero(self):
        """Vec2.ZERO should be (0, 0)."""
        from core.vec import Vec2

        assert Vec2.ZERO.x == 0.0
        assert Vec2.ZERO.y == 0.0

    def test_vec2_one(self):
        """Vec2.ONE should be (1, 1)."""
        from core.vec import Vec2

        assert Vec2.ONE.x == 1.0
        assert Vec2.ONE.y == 1.0

    def test_vec2_up(self):
        """Vec2.UP should be (0, 1)."""
        from core.vec import Vec2

        assert Vec2.UP.x == 0.0
        assert Vec2.UP.y == 1.0

    def test_vec2_down(self):
        """Vec2.DOWN should be (0, -1)."""
        from core.vec import Vec2

        assert Vec2.DOWN.x == 0.0
        assert Vec2.DOWN.y == -1.0

    def test_vec2_left(self):
        """Vec2.LEFT should be (-1, 0)."""
        from core.vec import Vec2

        assert Vec2.LEFT.x == -1.0
        assert Vec2.LEFT.y == 0.0

    def test_vec2_right(self):
        """Vec2.RIGHT should be (1, 0)."""
        from core.vec import Vec2

        assert Vec2.RIGHT.x == 1.0
        assert Vec2.RIGHT.y == 0.0


class TestVec3:
    """Test suite for Vec3 class."""

    def test_vec3_creation(self):
        """Vec3 should be created with x, y, z components."""
        from core.vec import Vec3

        v = Vec3(1.0, 2.0, 3.0)
        assert v.x == 1.0
        assert v.y == 2.0
        assert v.z == 3.0

    def test_vec3_default_zero(self):
        """Vec3 should default to zero."""
        from core.vec import Vec3

        v = Vec3()
        assert v.x == 0.0
        assert v.y == 0.0
        assert v.z == 0.0

    def test_vec3_addition(self):
        """Vec3 should support addition."""
        from core.vec import Vec3

        v1 = Vec3(1.0, 2.0, 3.0)
        v2 = Vec3(4.0, 5.0, 6.0)
        result = v1 + v2

        assert result.x == 5.0
        assert result.y == 7.0
        assert result.z == 9.0

    def test_vec3_subtraction(self):
        """Vec3 should support subtraction."""
        from core.vec import Vec3

        v1 = Vec3(5.0, 7.0, 9.0)
        v2 = Vec3(2.0, 3.0, 4.0)
        result = v1 - v2

        assert result.x == 3.0
        assert result.y == 4.0
        assert result.z == 5.0

    def test_vec3_scalar_multiplication(self):
        """Vec3 should support scalar multiplication."""
        from core.vec import Vec3

        v = Vec3(1.0, 2.0, 3.0)
        result = v * 2.0

        assert result.x == 2.0
        assert result.y == 4.0
        assert result.z == 6.0

    def test_vec3_length(self):
        """Vec3 should calculate length."""
        from core.vec import Vec3

        v = Vec3(1.0, 2.0, 2.0)
        assert v.length() == 3.0

    def test_vec3_dot_product(self):
        """Vec3 should calculate dot product."""
        from core.vec import Vec3

        v1 = Vec3(1.0, 2.0, 3.0)
        v2 = Vec3(4.0, 5.0, 6.0)

        # 1*4 + 2*5 + 3*6 = 32
        assert v1.dot(v2) == 32.0

    def test_vec3_cross_product(self):
        """Vec3 should calculate cross product."""
        from core.vec import Vec3

        v1 = Vec3(1.0, 0.0, 0.0)
        v2 = Vec3(0.0, 1.0, 0.0)
        result = v1.cross(v2)

        # (1,0,0) x (0,1,0) = (0,0,1)
        assert result.x == 0.0
        assert result.y == 0.0
        assert result.z == 1.0

    def test_vec3_normalized(self):
        """Vec3 should return normalized vector."""
        from core.vec import Vec3

        v = Vec3(1.0, 2.0, 2.0)
        n = v.normalized()

        assert abs(n.length() - 1.0) < 0.001

    def test_vec3_to_vec2(self):
        """Vec3 should convert to Vec2 (drop z)."""
        from core.vec import Vec3, Vec2

        v3 = Vec3(1.0, 2.0, 3.0)
        v2 = v3.to_vec2()

        assert isinstance(v2, Vec2)
        assert v2.x == 1.0
        assert v2.y == 2.0

    def test_vec3_from_vec2(self):
        """Vec3 should be created from Vec2."""
        from core.vec import Vec3, Vec2

        v2 = Vec2(1.0, 2.0)
        v3 = Vec3.from_vec2(v2, z=5.0)

        assert v3.x == 1.0
        assert v3.y == 2.0
        assert v3.z == 5.0


class TestVec2Integration:
    """Integration tests for Vec2 with other systems."""

    def test_vec2_with_transform(self):
        """Vec2 should work with TransformComponent."""
        from core.vec import Vec2
        from world.transform import TransformComponent

        transform = TransformComponent()
        transform.position = Vec2(100.0, 200.0)

        # TransformComponent.position returns tuple
        assert transform.position == (100.0, 200.0)
        assert transform.x == 100.0
        assert transform.y == 200.0

    def test_vec2_physics_velocity(self):
        """Vec2 should work as velocity."""
        from core.vec import Vec2

        velocity = Vec2(10.0, 20.0)
        dt = 0.016
        position = Vec2(0.0, 0.0)

        new_position = position + velocity * dt

        assert abs(new_position.x - 0.16) < 0.001
        assert abs(new_position.y - 0.32) < 0.001

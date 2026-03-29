"""
Vector Math Utilities.

Provides Vec2 and Vec3 classes for 2D and 3D vector operations.

Layer: 1 (Core)
Dependencies: None
"""

from __future__ import annotations
import math
from typing import Tuple


class Vec2:
    """
    2D Vector class.

    Provides common vector operations for 2D game development.

    Attributes:
        x: X component.
        y: Y component.
    """

    # Class constants (initialized after class definition)
    ZERO: Vec2
    ONE: Vec2
    UP: Vec2
    DOWN: Vec2
    LEFT: Vec2
    RIGHT: Vec2

    def __init__(self, x: float = 0.0, y: float = 0.0) -> None:
        """
        Create a 2D vector.

        Args:
            x: X component (default 0).
            y: Y component (default 0).
        """
        self.x = float(x)
        self.y = float(y)

    def __add__(self, other: Vec2) -> Vec2:
        """Add two vectors."""
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Vec2) -> Vec2:
        """Subtract two vectors."""
        return Vec2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> Vec2:
        """Multiply vector by scalar."""
        return Vec2(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar: float) -> Vec2:
        """Right multiply vector by scalar."""
        return self.__mul__(scalar)

    def __truediv__(self, scalar: float) -> Vec2:
        """Divide vector by scalar."""
        return Vec2(self.x / scalar, self.y / scalar)

    def __neg__(self) -> Vec2:
        """Negate vector."""
        return Vec2(-self.x, -self.y)

    def __eq__(self, other: object) -> bool:
        """Check equality."""
        if not isinstance(other, Vec2):
            return False
        return self.x == other.x and self.y == other.y

    def __hash__(self) -> int:
        """Hash for use in sets/dicts."""
        return hash((self.x, self.y))

    def __getitem__(self, index: int) -> float:
        """Get component by index (0=x, 1=y)."""
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        raise IndexError(f"Vec2 index {index} out of range")

    def __len__(self) -> int:
        """Return number of components."""
        return 2

    def __repr__(self) -> str:
        """String representation."""
        return f"Vec2({self.x}, {self.y})"

    def length(self) -> float:
        """
        Calculate vector length (magnitude).

        Returns:
            Length of the vector.
        """
        return math.sqrt(self.x * self.x + self.y * self.y)

    def length_squared(self) -> float:
        """
        Calculate squared length.

        Faster than length() when only comparison is needed.

        Returns:
            Squared length of the vector.
        """
        return self.x * self.x + self.y * self.y

    def normalized(self) -> Vec2:
        """
        Return normalized (unit) vector.

        Returns:
            Normalized copy of this vector.
        """
        length = self.length()
        if length == 0:
            return Vec2(0, 0)
        return Vec2(self.x / length, self.y / length)

    def dot(self, other: Vec2) -> float:
        """
        Calculate dot product.

        Args:
            other: Other vector.

        Returns:
            Dot product scalar.
        """
        return self.x * other.x + self.y * other.y

    def cross(self, other: Vec2) -> float:
        """
        Calculate 2D cross product (scalar).

        Args:
            other: Other vector.

        Returns:
            Cross product scalar (z component of 3D cross).
        """
        return self.x * other.y - self.y * other.x

    def distance_to(self, other: Vec2) -> float:
        """
        Calculate distance to another vector.

        Args:
            other: Target vector.

        Returns:
            Distance between vectors.
        """
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx * dx + dy * dy)

    def angle(self) -> float:
        """
        Get angle in radians from positive X axis.

        Returns:
            Angle in radians.
        """
        return math.atan2(self.y, self.x)

    def rotate(self, angle: float) -> Vec2:
        """
        Rotate vector by angle.

        Args:
            angle: Rotation angle in radians.

        Returns:
            Rotated vector.
        """
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        return Vec2(
            self.x * cos_a - self.y * sin_a,
            self.x * sin_a + self.y * cos_a
        )

    def lerp(self, other: Vec2, t: float) -> Vec2:
        """
        Linear interpolation to another vector.

        Args:
            other: Target vector.
            t: Interpolation factor (0-1).

        Returns:
            Interpolated vector.
        """
        return Vec2(
            self.x + (other.x - self.x) * t,
            self.y + (other.y - self.y) * t
        )

    def copy(self) -> Vec2:
        """
        Create a copy of this vector.

        Returns:
            New vector with same components.
        """
        return Vec2(self.x, self.y)

    def to_tuple(self) -> Tuple[float, float]:
        """
        Convert to tuple.

        Returns:
            (x, y) tuple.
        """
        return (self.x, self.y)

    @classmethod
    def from_tuple(cls, t: Tuple[float, float]) -> Vec2:
        """
        Create Vec2 from tuple.

        Args:
            t: (x, y) tuple.

        Returns:
            New Vec2 instance.
        """
        return cls(t[0], t[1])

    @classmethod
    def zero(cls) -> Vec2:
        """
        Create zero vector.

        Returns:
            Vec2(0, 0).
        """
        return cls(0, 0)


# Initialize class constants
Vec2.ZERO = Vec2(0, 0)
Vec2.ONE = Vec2(1, 1)
Vec2.UP = Vec2(0, 1)
Vec2.DOWN = Vec2(0, -1)
Vec2.LEFT = Vec2(-1, 0)
Vec2.RIGHT = Vec2(1, 0)


class Vec3:
    """
    3D Vector class.

    Provides common vector operations for 3D game development.

    Attributes:
        x: X component.
        y: Y component.
        z: Z component.
    """

    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0) -> None:
        """
        Create a 3D vector.

        Args:
            x: X component (default 0).
            y: Y component (default 0).
            z: Z component (default 0).
        """
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def __add__(self, other: Vec3) -> Vec3:
        """Add two vectors."""
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: Vec3) -> Vec3:
        """Subtract two vectors."""
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar: float) -> Vec3:
        """Multiply vector by scalar."""
        return Vec3(self.x * scalar, self.y * scalar, self.z * scalar)

    def __rmul__(self, scalar: float) -> Vec3:
        """Right multiply vector by scalar."""
        return self.__mul__(scalar)

    def __truediv__(self, scalar: float) -> Vec3:
        """Divide vector by scalar."""
        return Vec3(self.x / scalar, self.y / scalar, self.z / scalar)

    def __neg__(self) -> Vec3:
        """Negate vector."""
        return Vec3(-self.x, -self.y, -self.z)

    def __eq__(self, other: object) -> bool:
        """Check equality."""
        if not isinstance(other, Vec3):
            return False
        return self.x == other.x and self.y == other.y and self.z == other.z

    def __hash__(self) -> int:
        """Hash for use in sets/dicts."""
        return hash((self.x, self.y, self.z))

    def __repr__(self) -> str:
        """String representation."""
        return f"Vec3({self.x}, {self.y}, {self.z})"

    def length(self) -> float:
        """
        Calculate vector length.

        Returns:
            Length of the vector.
        """
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

    def length_squared(self) -> float:
        """
        Calculate squared length.

        Returns:
            Squared length of the vector.
        """
        return self.x * self.x + self.y * self.y + self.z * self.z

    def normalized(self) -> Vec3:
        """
        Return normalized (unit) vector.

        Returns:
            Normalized copy of this vector.
        """
        length = self.length()
        if length == 0:
            return Vec3(0, 0, 0)
        return Vec3(self.x / length, self.y / length, self.z / length)

    def dot(self, other: Vec3) -> float:
        """
        Calculate dot product.

        Args:
            other: Other vector.

        Returns:
            Dot product scalar.
        """
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other: Vec3) -> Vec3:
        """
        Calculate cross product.

        Args:
            other: Other vector.

        Returns:
            Cross product vector.
        """
        return Vec3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )

    def to_vec2(self) -> Vec2:
        """
        Convert to Vec2 (drop z).

        Returns:
            Vec2 with x and y components.
        """
        return Vec2(self.x, self.y)

    @classmethod
    def from_vec2(cls, v: Vec2, z: float = 0.0) -> Vec3:
        """
        Create Vec3 from Vec2.

        Args:
            v: Vec2 instance.
            z: Z component (default 0).

        Returns:
            New Vec3 instance.
        """
        return cls(v.x, v.y, z)

    def copy(self) -> Vec3:
        """
        Create a copy of this vector.

        Returns:
            New vector with same components.
        """
        return Vec3(self.x, self.y, self.z)

    def to_tuple(self) -> Tuple[float, float, float]:
        """
        Convert to tuple.

        Returns:
            (x, y, z) tuple.
        """
        return (self.x, self.y, self.z)

    @classmethod
    def from_tuple(cls, t: Tuple[float, float, float]) -> Vec3:
        """
        Create Vec3 from tuple.

        Args:
            t: (x, y, z) tuple.

        Returns:
            New Vec3 instance.
        """
        return cls(t[0], t[1], t[2])

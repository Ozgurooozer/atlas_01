"""
Color utility class.

Layer: 1 (Core)
Dependencies: None
"""

from __future__ import annotations
from typing import Tuple


class Color:
    """
    RGBA color representation.

    Values are in 0.0 - 1.0 range.
    """

    __slots__ = ("r", "g", "b", "a")

    def __init__(
        self,
        r: float = 1.0,
        g: float = 1.0,
        b: float = 1.0,
        a: float = 1.0,
    ) -> None:
        self.r = max(0.0, min(1.0, r))
        self.g = max(0.0, min(1.0, g))
        self.b = max(0.0, min(1.0, b))
        self.a = max(0.0, min(1.0, a))

    @classmethod
    def white(cls) -> "Color":
        return cls(1.0, 1.0, 1.0, 1.0)

    @classmethod
    def black(cls) -> "Color":
        return cls(0.0, 0.0, 0.0, 1.0)

    @classmethod
    def red(cls) -> "Color":
        return cls(1.0, 0.0, 0.0, 1.0)

    @classmethod
    def green(cls) -> "Color":
        return cls(0.0, 1.0, 0.0, 1.0)

    @classmethod
    def blue(cls) -> "Color":
        return cls(0.0, 0.0, 1.0, 1.0)

    @classmethod
    def yellow(cls) -> "Color":
        return cls(1.0, 1.0, 0.0, 1.0)

    @classmethod
    def orange(cls) -> "Color":
        return cls(1.0, 0.5, 0.0, 1.0)

    @classmethod
    def from_bytes(cls, r: int, g: int, b: int, a: int = 255) -> "Color":
        """Create color from 0-255 byte values."""
        return cls(r / 255.0, g / 255.0, b / 255.0, a / 255.0)

    def to_bytes(self) -> Tuple[int, int, int, int]:
        """Convert to 0-255 byte values."""
        return (
            int(self.r * 255),
            int(self.g * 255),
            int(self.b * 255),
            int(self.a * 255),
        )

    def to_tuple(self) -> Tuple[float, float, float, float]:
        return (self.r, self.g, self.b, self.a)

    @staticmethod
    def lerp(a: "Color", b: "Color", t: float) -> "Color":
        """Linearly interpolate between two colors.

        Args:
            a: Start color
            b: End color
            t: Interpolation factor (0.0 to 1.0)

        Returns:
            Interpolated color
        """
        t = max(0.0, min(1.0, t))
        return Color(
            a.r + (b.r - a.r) * t,
            a.g + (b.g - a.g) * t,
            a.b + (b.b - a.b) * t,
            a.a + (b.a - a.a) * t,
        )

    def __repr__(self) -> str:
        return f"Color({self.r:.2f}, {self.g:.2f}, {self.b:.2f}, {self.a:.2f})"

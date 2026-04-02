"""Tests for Color class.

Layer: 1 (Core)
"""

from __future__ import annotations


from core.color import Color


class TestColor:
    """Test Color class."""

    def test_color_creation(self):
        """Test basic color creation."""
        c = Color(1.0, 0.5, 0.0, 1.0)

        assert c.r == 1.0
        assert c.g == 0.5
        assert c.b == 0.0
        assert c.a == 1.0

    def test_color_clamping(self):
        """Test color values are clamped to 0-1."""
        c = Color(-0.5, 1.5, 0.0, 2.0)

        assert c.r == 0.0
        assert c.g == 1.0
        assert c.b == 0.0
        assert c.a == 1.0

    def test_color_defaults(self):
        """Test color defaults to white."""
        c = Color()

        assert c.r == 1.0
        assert c.g == 1.0
        assert c.b == 1.0
        assert c.a == 1.0

    def test_color_from_bytes(self):
        """Test creating color from byte values."""
        c = Color.from_bytes(255, 128, 0, 255)

        assert c.r == 1.0
        assert abs(c.g - 0.5) < 0.01  # ~128/255
        assert c.b == 0.0
        assert c.a == 1.0

    def test_color_to_bytes(self):
        """Test converting color to bytes."""
        c = Color(1.0, 0.5, 0.0, 1.0)
        r, g, b, a = c.to_bytes()

        assert r == 255
        assert g == 127
        assert b == 0
        assert a == 255

    def test_color_presets(self):
        """Test preset color methods."""
        assert Color.white().to_tuple() == (1.0, 1.0, 1.0, 1.0)
        assert Color.black().to_tuple() == (0.0, 0.0, 0.0, 1.0)
        assert Color.red().to_tuple() == (1.0, 0.0, 0.0, 1.0)
        assert Color.green().to_tuple() == (0.0, 1.0, 0.0, 1.0)
        assert Color.blue().to_tuple() == (0.0, 0.0, 1.0, 1.0)

    def test_color_to_tuple(self):
        """Test converting color to tuple."""
        c = Color(0.5, 0.5, 0.5, 0.5)

        assert c.to_tuple() == (0.5, 0.5, 0.5, 0.5)

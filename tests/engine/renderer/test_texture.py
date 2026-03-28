"""Tests for Texture class."""

import pytest
from typing import Tuple


class TestTexture:
    """Test suite for Texture class."""

    def test_texture_creation(self):
        """Texture should be created with width, height, data."""
        from engine.renderer.texture import Texture

        # Create a 4x4 RGBA texture (4 bytes per pixel)
        data = bytes([255, 0, 0, 255] * 16)  # Red pixels
        texture = Texture(width=4, height=4, data=data)

        assert texture.width == 4
        assert texture.height == 4
        assert texture.data == data

    def test_texture_size(self):
        """Texture should have correct size."""
        from engine.renderer.texture import Texture

        texture = Texture(width=64, height=32, data=None)

        assert texture.width == 64
        assert texture.height == 32

    def test_texture_data_none(self):
        """Texture should allow None data."""
        from engine.renderer.texture import Texture

        texture = Texture(width=16, height=16)

        assert texture.data is None

    def test_texture_pixel_count(self):
        """Texture should have correct pixel count."""
        from engine.renderer.texture import Texture

        texture = Texture(width=10, height=20)

        assert texture.pixel_count == 200

    def test_texture_bytes_per_pixel(self):
        """Texture should have 4 bytes per pixel (RGBA)."""
        from engine.renderer.texture import Texture

        texture = Texture(width=2, height=2)

        assert texture.bytes_per_pixel == 4

    def test_texture_data_size(self):
        """Texture should calculate correct data size."""
        from engine.renderer.texture import Texture

        texture = Texture(width=8, height=4)

        # 8 * 4 * 4 = 128 bytes
        assert texture.data_size == 128

    def test_texture_get_pixel(self):
        """Texture should get pixel at position."""
        from engine.renderer.texture import Texture

        # Create 2x2 texture with different colors
        data = bytes([
            255, 0, 0, 255,    # Red
            0, 255, 0, 255,    # Green
            0, 0, 255, 255,    # Blue
            255, 255, 0, 255,  # Yellow
        ])
        texture = Texture(width=2, height=2, data=data)

        assert texture.get_pixel(0, 0) == (255, 0, 0, 255)
        assert texture.get_pixel(1, 0) == (0, 255, 0, 255)
        assert texture.get_pixel(0, 1) == (0, 0, 255, 255)
        assert texture.get_pixel(1, 1) == (255, 255, 0, 255)

    def test_texture_set_pixel(self):
        """Texture should set pixel at position."""
        from engine.renderer.texture import Texture

        texture = Texture(width=2, height=2)

        texture.set_pixel(0, 0, (255, 0, 0, 255))
        texture.set_pixel(1, 1, (0, 255, 0, 255))

        assert texture.get_pixel(0, 0) == (255, 0, 0, 255)
        assert texture.get_pixel(1, 1) == (0, 255, 0, 255)

    def test_texture_fill(self):
        """Texture should fill with color."""
        from engine.renderer.texture import Texture

        texture = Texture(width=2, height=2)
        texture.fill((128, 64, 32, 255))

        for y in range(2):
            for x in range(2):
                assert texture.get_pixel(x, y) == (128, 64, 32, 255)

    def test_texture_has_transparency(self):
        """Texture should detect transparency."""
        from engine.renderer.texture import Texture

        # Fully opaque
        opaque_data = bytes([255, 0, 0, 255] * 4)
        opaque = Texture(width=2, height=2, data=opaque_data)
        assert opaque.has_transparency is False

        # Has transparency
        transparent_data = bytes([255, 0, 0, 128] * 4)
        transparent = Texture(width=2, height=2, data=transparent_data)
        assert transparent.has_transparency is True

    def test_texture_is_valid(self):
        """Texture should validate dimensions."""
        from engine.renderer.texture import Texture

        valid = Texture(width=16, height=16)
        assert valid.is_valid is True

        invalid = Texture(width=0, height=0)
        assert invalid.is_valid is False


class TestTextureFromFile:
    """Test suite for Texture loading from file."""

    def test_texture_load_from_memory(self):
        """Texture should be loadable from memory data."""
        from engine.renderer.texture import Texture

        # Create minimal RGBA data
        data = bytes([255, 128, 64, 255] * 4)
        texture = Texture.from_data(width=2, height=2, data=data)

        assert texture.width == 2
        assert texture.height == 2
        assert texture.get_pixel(0, 0) == (255, 128, 64, 255)


class TestTextureRegion:
    """Test suite for Texture regions (spritesheet support)."""

    def test_texture_region(self):
        """Texture should return region."""
        from engine.renderer.texture import Texture

        data = bytes(range(256))  # 64 pixels of RGBA data
        texture = Texture(width=8, height=8, data=data)

        region = texture.get_region(x=2, y=2, width=4, height=4)

        assert region['x'] == 2
        assert region['y'] == 2
        assert region['width'] == 4
        assert region['height'] == 4
        assert region['texture'] is texture

    def test_texture_uv_coords(self):
        """Texture should return UV coordinates for region."""
        from engine.renderer.texture import Texture

        texture = Texture(width=100, height=100)
        region = texture.get_region(x=25, y=25, width=50, height=50)

        # UV coords should be normalized 0-1
        uvs = texture.get_uv_coords(region)

        assert uvs['u1'] == 0.25
        assert uvs['v1'] == 0.25
        assert uvs['u2'] == 0.75
        assert uvs['v2'] == 0.75


class TestTextureGPU:
    """Test suite for Texture GPU operations."""

    def test_texture_gpu_id(self):
        """Texture should have GPU ID."""
        from engine.renderer.texture import Texture

        texture = Texture(width=16, height=16)

        # GPU ID should be None until uploaded
        assert texture.gpu_id is None

    def test_texture_uploaded_flag(self):
        """Texture should track upload state."""
        from engine.renderer.texture import Texture

        texture = Texture(width=16, height=16)

        assert texture.is_uploaded is False

    def test_texture_mark_uploaded(self):
        """Texture should be markable as uploaded."""
        from engine.renderer.texture import Texture

        texture = Texture(width=16, height=16)
        texture.mark_uploaded(gpu_id=42)

        assert texture.is_uploaded is True
        assert texture.gpu_id == 42


class TestTextureEquality:
    """Test suite for Texture equality and hashing."""

    def test_texture_equality(self):
        """Textures with same data should not be equal (different instances)."""
        from engine.renderer.texture import Texture

        data = bytes([255, 0, 0, 255] * 4)
        t1 = Texture(width=2, height=2, data=data)
        t2 = Texture(width=2, height=2, data=data)

        # Different instances
        assert t1 is not t2

    def test_texture_has_guid(self):
        """Texture should have GUID if it inherits from Object."""
        from engine.renderer.texture import Texture
        from core.guid import GUID

        texture = Texture(width=16, height=16)

        # Check if Texture has guid attribute
        assert hasattr(texture, 'guid')


class TestTextureClone:
    """Test suite for Texture cloning."""

    def test_texture_clone(self):
        """Texture should be cloneable."""
        from engine.renderer.texture import Texture

        data = bytes([255, 0, 0, 255] * 4)
        original = Texture(width=2, height=2, data=data)

        clone = original.clone()

        assert clone.width == original.width
        assert clone.height == original.height
        assert clone.data == original.data
        assert clone is not original
        assert clone.data is not original.data

"""Tests for Texture file loading with Pillow."""

import pytest
import os
import tempfile


class TestTextureFromFile:
    """Test suite for Texture loading from image files."""

    def test_texture_from_file_png(self):
        """Texture should load from PNG file."""
        from engine.renderer.texture import Texture

        # Create a temporary PNG file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            temp_path = f.name

        try:
            # Create a simple PNG using Pillow
            from PIL import Image
            img = Image.new('RGBA', (32, 16), color=(255, 128, 0, 255))
            img.save(temp_path)

            # Load texture from file
            texture = Texture.from_file(temp_path)

            assert texture.width == 32
            assert texture.height == 16
            assert texture.data is not None
            # Check first pixel (orange)
            pixel = texture.get_pixel(0, 0)
            assert pixel[0] == 255  # R
            assert pixel[1] == 128  # G
            assert pixel[2] == 0    # B
            assert pixel[3] == 255  # A
        finally:
            os.unlink(temp_path)

    def test_texture_from_file_jpg(self):
        """Texture should load from JPEG file."""
        from engine.renderer.texture import Texture

        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
            temp_path = f.name

        try:
            from PIL import Image
            img = Image.new('RGB', (64, 64), color=(0, 255, 128))
            img.save(temp_path)

            texture = Texture.from_file(temp_path)

            assert texture.width == 64
            assert texture.height == 64
            assert texture.data is not None
        finally:
            os.unlink(temp_path)

    def test_texture_from_file_not_found(self):
        """Texture should raise error if file not found."""
        from engine.renderer.texture import Texture

        with pytest.raises(FileNotFoundError):
            Texture.from_file('/nonexistent/path/image.png')

    def test_texture_from_bytes(self):
        """Texture should load from bytes data."""
        from engine.renderer.texture import Texture
        from PIL import Image
        import io

        # Create image in memory
        img = Image.new('RGBA', (8, 8), color=(255, 0, 0, 255))
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)

        # Load from bytes
        texture = Texture.from_bytes(buffer.read(), format='PNG')

        assert texture.width == 8
        assert texture.height == 8
        assert texture.data is not None

    def test_texture_from_file_with_transparency(self):
        """Texture should preserve alpha channel from PNG."""
        from engine.renderer.texture import Texture

        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            temp_path = f.name

        try:
            from PIL import Image
            img = Image.new('RGBA', (4, 4), color=(255, 0, 0, 128))  # Semi-transparent red
            img.save(temp_path)

            texture = Texture.from_file(temp_path)

            assert texture.has_transparency is True
            pixel = texture.get_pixel(0, 0)
            assert pixel[3] == 128  # Alpha should be preserved
        finally:
            os.unlink(temp_path)

    def test_texture_from_file_rgba_conversion(self):
        """Texture should convert RGB images to RGBA."""
        from engine.renderer.texture import Texture

        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            temp_path = f.name

        try:
            from PIL import Image
            img = Image.new('RGB', (8, 8), color=(128, 64, 32))
            img.save(temp_path)

            texture = Texture.from_file(temp_path)

            # All pixels should have full alpha
            pixel = texture.get_pixel(0, 0)
            assert pixel[3] == 255  # Alpha should be 255 for RGB images
        finally:
            os.unlink(temp_path)

    def test_texture_save_to_file(self):
        """Texture should save to file."""
        from engine.renderer.texture import Texture

        texture = Texture.from_color(16, 16, (255, 0, 128, 255))

        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            temp_path = f.name

        try:
            texture.save(temp_path)

            # Load it back
            loaded = Texture.from_file(temp_path)
            assert loaded.width == 16
            assert loaded.height == 16
            pixel = loaded.get_pixel(0, 0)
            assert pixel[0] == 255
            assert pixel[1] == 0
            assert pixel[2] == 128
        finally:
            os.unlink(temp_path)


class TestTextureLoader:
    """Test suite for TextureLoader utility class."""

    def test_texture_loader_exists(self):
        """TextureLoader class should exist."""
        from engine.renderer.texture import TextureLoader

        loader = TextureLoader()
        assert loader is not None

    def test_texture_loader_load(self):
        """TextureLoader should load texture from file."""
        from engine.renderer.texture import TextureLoader

        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            temp_path = f.name

        try:
            from PIL import Image
            img = Image.new('RGBA', (32, 32), color=(0, 128, 255, 255))
            img.save(temp_path)

            loader = TextureLoader()
            texture = loader.load(temp_path)

            assert texture.width == 32
            assert texture.height == 32
        finally:
            os.unlink(temp_path)

    def test_texture_loader_cache(self):
        """TextureLoader should cache loaded textures."""
        from engine.renderer.texture import TextureLoader

        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            temp_path = f.name

        try:
            from PIL import Image
            img = Image.new('RGBA', (16, 16), color=(255, 255, 255, 255))
            img.save(temp_path)

            loader = TextureLoader()
            t1 = loader.load(temp_path)
            t2 = loader.load(temp_path)

            # Same instance from cache
            assert t1 is t2
        finally:
            os.unlink(temp_path)

    def test_texture_loader_clear_cache(self):
        """TextureLoader should allow clearing cache."""
        from engine.renderer.texture import TextureLoader

        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            temp_path = f.name

        try:
            from PIL import Image
            img = Image.new('RGBA', (16, 16), color=(255, 255, 255, 255))
            img.save(temp_path)

            loader = TextureLoader()
            t1 = loader.load(temp_path)
            loader.clear_cache()
            t2 = loader.load(temp_path)

            # Different instances after cache clear
            assert t1 is not t2
        finally:
            os.unlink(temp_path)

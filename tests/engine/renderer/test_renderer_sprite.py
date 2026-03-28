"""Tests for Renderer2D sprite drawing functionality."""

import pytest
from engine.renderer.renderer import Renderer2D
from engine.renderer.texture import Texture
from engine.renderer.sprite import Sprite
from hal.headless import HeadlessGPU
from core.vec import Vec2


class TestRendererDrawSprite:
    """Test suite for Renderer2D.draw_sprite method."""

    def test_renderer_has_draw_sprite(self):
        """Renderer should have draw_sprite method."""
        renderer = Renderer2D()
        assert hasattr(renderer, 'draw_sprite')
        assert callable(renderer.draw_sprite)

    def test_draw_sprite_basic(self):
        """Renderer should draw a sprite."""
        renderer = Renderer2D()
        renderer.gpu_device = HeadlessGPU()
        renderer.initialize(None)

        texture = Texture(width=32, height=32)
        texture.fill((255, 0, 0, 255))
        sprite = Sprite(texture=texture)

        # Should not raise
        renderer.draw_sprite(sprite)

    def test_draw_sprite_uploads_texture(self):
        """draw_sprite should upload texture to GPU if needed."""
        renderer = Renderer2D()
        gpu = HeadlessGPU()
        renderer.gpu_device = gpu
        renderer.initialize(None)

        texture = Texture(width=16, height=16)
        sprite = Sprite(texture=texture)

        renderer.draw_sprite(sprite)

        # Texture should be uploaded after draw
        assert texture.is_uploaded is True
        assert texture.gpu_id is not None

    def test_draw_sprite_reuses_uploaded_texture(self):
        """draw_sprite should not re-upload already uploaded textures."""
        renderer = Renderer2D()
        gpu = HeadlessGPU()
        renderer.gpu_device = gpu
        renderer.initialize(None)

        texture = Texture(width=16, height=16)
        texture.mark_uploaded(1)  # Simulate already uploaded

        sprite = Sprite(texture=texture)
        renderer.draw_sprite(sprite)

        # GPU ID should remain the same
        assert texture.gpu_id == 1

    def test_draw_sprite_with_position(self):
        """draw_sprite should respect sprite position."""
        renderer = Renderer2D()
        gpu = HeadlessGPU()
        renderer.gpu_device = gpu
        renderer.initialize(None)

        texture = Texture(width=32, height=32)
        sprite = Sprite(texture=texture, position=(100.0, 200.0))

        # Should not raise
        renderer.draw_sprite(sprite)

    def test_draw_sprite_with_scale(self):
        """draw_sprite should respect sprite scale."""
        renderer = Renderer2D()
        gpu = HeadlessGPU()
        renderer.gpu_device = gpu
        renderer.initialize(None)

        texture = Texture(width=32, height=32)
        sprite = Sprite(texture=texture)
        sprite.scale_x = 2.0
        sprite.scale_y = 0.5

        # Should not raise
        renderer.draw_sprite(sprite)

    def test_draw_sprite_with_rotation(self):
        """draw_sprite should respect sprite rotation."""
        renderer = Renderer2D()
        gpu = HeadlessGPU()
        renderer.gpu_device = gpu
        renderer.initialize(None)

        texture = Texture(width=32, height=32)
        sprite = Sprite(texture=texture, rotation=45.0)

        # Should not raise
        renderer.draw_sprite(sprite)

    def test_draw_sprite_with_color_tint(self):
        """draw_sprite should respect sprite color tint."""
        renderer = Renderer2D()
        gpu = HeadlessGPU()
        renderer.gpu_device = gpu
        renderer.initialize(None)

        texture = Texture(width=32, height=32)
        sprite = Sprite(texture=texture)
        sprite.color = (255, 128, 0, 200)  # Orange with transparency

        # Should not raise
        renderer.draw_sprite(sprite)

    def test_draw_sprite_hidden(self):
        """draw_sprite should skip hidden sprites."""
        renderer = Renderer2D()
        gpu = HeadlessGPU()
        renderer.gpu_device = gpu
        renderer.initialize(None)

        texture = Texture(width=32, height=32)
        sprite = Sprite(texture=texture)
        sprite.visible = False

        # Should not raise and should skip
        renderer.draw_sprite(sprite)

    def test_draw_sprite_without_texture(self):
        """draw_sprite should handle sprites without texture."""
        renderer = Renderer2D()
        gpu = HeadlessGPU()
        renderer.gpu_device = gpu
        renderer.initialize(None)

        sprite = Sprite()  # No texture

        # Should not raise (just skip)
        renderer.draw_sprite(sprite)

    def test_draw_sprite_without_gpu(self):
        """draw_sprite should handle missing GPU device."""
        renderer = Renderer2D()
        renderer.initialize(None)

        texture = Texture(width=32, height=32)
        sprite = Sprite(texture=texture)

        # Should not raise (just skip)
        renderer.draw_sprite(sprite)


class TestRendererDrawTexture:
    """Test suite for Renderer2D.draw_texture method."""

    def test_renderer_has_draw_texture(self):
        """Renderer should have draw_texture method."""
        renderer = Renderer2D()
        assert hasattr(renderer, 'draw_texture')
        assert callable(renderer.draw_texture)

    def test_draw_texture_basic(self):
        """Renderer should draw texture at position."""
        renderer = Renderer2D()
        gpu = HeadlessGPU()
        renderer.gpu_device = gpu
        renderer.initialize(None)

        texture = Texture(width=64, height=32)

        # Should not raise
        renderer.draw_texture(texture, 100.0, 50.0)

    def test_draw_texture_with_size(self):
        """draw_texture should accept optional size."""
        renderer = Renderer2D()
        gpu = HeadlessGPU()
        renderer.gpu_device = gpu
        renderer.initialize(None)

        texture = Texture(width=32, height=32)

        # Should not raise
        renderer.draw_texture(texture, 100.0, 50.0, width=64.0, height=128.0)

    def test_draw_texture_uploads(self):
        """draw_texture should upload texture if needed."""
        renderer = Renderer2D()
        gpu = HeadlessGPU()
        renderer.gpu_device = gpu
        renderer.initialize(None)

        texture = Texture(width=16, height=16)
        renderer.draw_texture(texture, 0.0, 0.0)

        assert texture.is_uploaded is True


class TestRendererDrawCount:
    """Test suite for Renderer draw statistics."""

    def test_renderer_has_draw_count(self):
        """Renderer should track draw count."""
        renderer = Renderer2D()
        assert hasattr(renderer, 'draw_count')

    def test_draw_count_resets_each_frame(self):
        """Draw count should reset each frame."""
        renderer = Renderer2D()
        gpu = HeadlessGPU()
        renderer.gpu_device = gpu
        renderer.initialize(None)

        # Draw some sprites
        texture = Texture(width=16, height=16)
        for i in range(5):
            renderer.draw_sprite(Sprite(texture=texture))

        assert renderer.draw_count == 5

        # Tick resets
        renderer.tick(0.016)
        assert renderer.draw_count == 0

    def test_texture_count(self):
        """Renderer should track texture count."""
        renderer = Renderer2D()
        gpu = HeadlessGPU()
        renderer.gpu_device = gpu
        renderer.initialize(None)

        texture = Texture(width=16, height=16)
        renderer.draw_sprite(Sprite(texture=texture))
        renderer.draw_sprite(Sprite(texture=texture))  # Same texture

        # Both draws, but only one texture upload
        assert renderer.texture_count == 1

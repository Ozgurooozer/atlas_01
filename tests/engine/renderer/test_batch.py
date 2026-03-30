"""Tests for SpriteBatch class."""

import pytest
from engine.renderer.texture import Texture
from engine.renderer.sprite import Sprite
from core.vec import Vec2


class TestSpriteBatch:
    """Test suite for SpriteBatch class."""

    def test_sprite_batch_exists(self):
        """SpriteBatch class should exist."""
        from engine.renderer.batch import SpriteBatch

        batch = SpriteBatch()
        assert batch is not None

    def test_sprite_batch_begin(self):
        """SpriteBatch should have begin method."""
        from engine.renderer.batch import SpriteBatch

        batch = SpriteBatch()
        assert hasattr(batch, 'begin')
        batch.begin()  # Should not raise

    def test_sprite_batch_end(self):
        """SpriteBatch should have end method."""
        from engine.renderer.batch import SpriteBatch

        batch = SpriteBatch()
        assert hasattr(batch, 'end')
        batch.begin()
        batch.end()  # Should not raise

    def test_sprite_batch_draw(self):
        """SpriteBatch should have draw method."""
        from engine.renderer.batch import SpriteBatch

        batch = SpriteBatch()
        texture = Texture(width=32, height=32)
        sprite = Sprite(texture=texture)

        batch.begin()
        batch.draw(sprite)  # Should not raise
        batch.end()

    def test_sprite_batch_draw_multiple(self):
        """SpriteBatch should draw multiple sprites."""
        from engine.renderer.batch import SpriteBatch

        batch = SpriteBatch()
        texture = Texture(width=32, height=32)

        batch.begin()
        for i in range(10):
            sprite = Sprite(texture=texture, position=(i * 40.0, 0.0))
            batch.draw(sprite)
        batch.end()

    def test_sprite_batch_flush_count(self):
        """SpriteBatch should track flush count."""
        from engine.renderer.batch import SpriteBatch

        batch = SpriteBatch()
        texture = Texture(width=32, height=32)

        batch.begin()
        batch.draw(Sprite(texture=texture))
        batch.draw(Sprite(texture=texture))
        batch.end()

        assert batch.flush_count >= 1

    def test_sprite_batch_sort_by_z(self):
        """SpriteBatch should sort sprites by z_index."""
        from engine.renderer.batch import SpriteBatch

        batch = SpriteBatch()
        texture = Texture(width=32, height=32)

        s1 = Sprite(texture=texture)
        s1.z_index = 5
        s2 = Sprite(texture=texture)
        s2.z_index = 1
        s3 = Sprite(texture=texture)
        s3.z_index = 10

        batch.begin()
        batch.draw(s1)
        batch.draw(s2)
        batch.draw(s3)
        batch.end()

        # Sprites should be sorted by z_index
        assert batch.sorted_sprites[0].z_index == 1
        assert batch.sorted_sprites[1].z_index == 5
        assert batch.sorted_sprites[2].z_index == 10

    def test_sprite_batch_texture_batching(self):
        """SpriteBatch should batch sprites with same texture."""
        from engine.renderer.batch import SpriteBatch

        batch = SpriteBatch()
        texture = Texture(width=32, height=32)
        other_texture = Texture(width=16, height=16)

        batch.begin()
        # Same texture sprites
        batch.draw(Sprite(texture=texture))
        batch.draw(Sprite(texture=texture))
        # Different texture
        batch.draw(Sprite(texture=other_texture))
        batch.end()

        # Should batch same textures together
        assert batch.texture_changes == 2  # texture -> other_texture

    def test_sprite_batch_max_sprites(self):
        """SpriteBatch should have configurable max sprites."""
        from engine.renderer.batch import SpriteBatch

        batch = SpriteBatch(max_sprites=100)
        assert batch.max_sprites == 100

    def test_sprite_batch_reset(self):
        """SpriteBatch should reset between begin/end pairs."""
        from engine.renderer.batch import SpriteBatch

        batch = SpriteBatch()
        texture = Texture(width=32, height=32)

        batch.begin()
        batch.draw(Sprite(texture=texture))
        batch.end()

        batch.begin()
        # Should be empty at start of new batch
        assert batch.sprite_count == 0
        batch.end()


class TestSpriteBatchWithRenderer:
    """Test suite for SpriteBatch with Renderer2D."""

    def test_sprite_batch_with_renderer(self):
        """SpriteBatch should work with Renderer2D."""
        from engine.renderer.batch import SpriteBatch
        from engine.renderer.renderer import Renderer2D
        from hal.headless import HeadlessGPU

        renderer = Renderer2D()
        renderer.gpu_device = HeadlessGPU()
        renderer.initialize(None)

        batch = SpriteBatch(renderer=renderer)
        texture = Texture(width=32, height=32)

        batch.begin()
        batch.draw(Sprite(texture=texture))
        batch.end()

        assert batch.renderer is renderer

    def test_sprite_batch_auto_submit(self):
        """SpriteBatch should submit to renderer on end()."""
        from engine.renderer.batch import SpriteBatch
        from engine.renderer.renderer import Renderer2D
        from hal.headless import HeadlessGPU

        renderer = Renderer2D()
        renderer.gpu_device = HeadlessGPU()
        renderer.initialize(None)

        batch = SpriteBatch(renderer=renderer)
        texture = Texture(width=32, height=32)

        batch.begin()
        batch.draw(Sprite(texture=texture))
        batch.draw(Sprite(texture=texture))
        batch.end()

        # Renderer should have received draws
        assert renderer.draw_count == 2

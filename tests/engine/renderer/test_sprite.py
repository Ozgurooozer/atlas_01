"""Tests for Sprite class."""

from core.vec import Vec2


class TestSprite:
    """Test suite for Sprite class."""

    def test_sprite_creation(self):
        """Sprite should be created with texture reference."""
        from engine.renderer.sprite import Sprite
        from engine.renderer.texture import Texture

        texture = Texture(width=64, height=64)
        sprite = Sprite(texture=texture)

        assert sprite.texture is texture

    def test_sprite_position(self):
        """Sprite should have position."""
        from engine.renderer.sprite import Sprite
        from engine.renderer.texture import Texture

        texture = Texture(width=32, height=32)
        sprite = Sprite(texture=texture)

        assert sprite.position.x == 0.0
        assert sprite.position.y == 0.0

    def test_sprite_set_position(self):
        """Sprite should allow setting position."""
        from engine.renderer.sprite import Sprite
        from engine.renderer.texture import Texture

        texture = Texture(width=32, height=32)
        sprite = Sprite(texture=texture)
        sprite.position = Vec2(100.0, 200.0)

        assert sprite.position.x == 100.0
        assert sprite.position.y == 200.0

    def test_sprite_position_tuple(self):
        """Sprite should accept tuple for position."""
        from engine.renderer.sprite import Sprite
        from engine.renderer.texture import Texture

        texture = Texture(width=32, height=32)
        sprite = Sprite(texture=texture, position=(50.0, 75.0))

        assert sprite.position.x == 50.0
        assert sprite.position.y == 75.0

    def test_sprite_scale(self):
        """Sprite should have scale."""
        from engine.renderer.sprite import Sprite
        from engine.renderer.texture import Texture

        texture = Texture(width=32, height=32)
        sprite = Sprite(texture=texture)

        assert sprite.scale_x == 1.0
        assert sprite.scale_y == 1.0

    def test_sprite_set_scale(self):
        """Sprite should allow setting scale."""
        from engine.renderer.sprite import Sprite
        from engine.renderer.texture import Texture

        texture = Texture(width=32, height=32)
        sprite = Sprite(texture=texture)
        sprite.scale_x = 2.0
        sprite.scale_y = 0.5

        assert sprite.scale_x == 2.0
        assert sprite.scale_y == 0.5

    def test_sprite_rotation(self):
        """Sprite should have rotation."""
        from engine.renderer.sprite import Sprite
        from engine.renderer.texture import Texture

        texture = Texture(width=32, height=32)
        sprite = Sprite(texture=texture)

        assert sprite.rotation == 0.0

    def test_sprite_set_rotation(self):
        """Sprite should allow setting rotation."""
        from engine.renderer.sprite import Sprite
        from engine.renderer.texture import Texture

        texture = Texture(width=32, height=32)
        sprite = Sprite(texture=texture)
        sprite.rotation = 45.0

        assert sprite.rotation == 45.0

    def test_sprite_color(self):
        """Sprite should have color tint."""
        from engine.renderer.sprite import Sprite
        from engine.renderer.texture import Texture

        texture = Texture(width=32, height=32)
        sprite = Sprite(texture=texture)

        # Default should be white (no tint)
        assert sprite.color == (255, 255, 255, 255)

    def test_sprite_set_color(self):
        """Sprite should allow setting color tint."""
        from engine.renderer.sprite import Sprite
        from engine.renderer.texture import Texture

        texture = Texture(width=32, height=32)
        sprite = Sprite(texture=texture)
        sprite.color = (255, 128, 0, 255)  # Orange

        assert sprite.color == (255, 128, 0, 255)

    def test_sprite_alpha(self):
        """Sprite should have alpha property."""
        from engine.renderer.sprite import Sprite
        from engine.renderer.texture import Texture

        texture = Texture(width=32, height=32)
        sprite = Sprite(texture=texture)

        assert sprite.alpha == 1.0

    def test_sprite_set_alpha(self):
        """Sprite should allow setting alpha."""
        from engine.renderer.sprite import Sprite
        from engine.renderer.texture import Texture

        texture = Texture(width=32, height=32)
        sprite = Sprite(texture=texture)
        sprite.alpha = 0.5

        # Allow small epsilon due to int conversion
        assert abs(sprite.alpha - 0.5) < 0.01
        assert sprite.color[3] == 127  # 255 * 0.5

    def test_sprite_visible(self):
        """Sprite should have visible flag."""
        from engine.renderer.sprite import Sprite
        from engine.renderer.texture import Texture

        texture = Texture(width=32, height=32)
        sprite = Sprite(texture=texture)

        assert sprite.visible is True

    def test_sprite_set_visible(self):
        """Sprite should allow hiding."""
        from engine.renderer.sprite import Sprite
        from engine.renderer.texture import Texture

        texture = Texture(width=32, height=32)
        sprite = Sprite(texture=texture)
        sprite.visible = False

        assert sprite.visible is False

    def test_sprite_size(self):
        """Sprite should calculate size based on texture and scale."""
        from engine.renderer.sprite import Sprite
        from engine.renderer.texture import Texture

        texture = Texture(width=32, height=64)
        sprite = Sprite(texture=texture)

        assert sprite.width == 32
        assert sprite.height == 64

    def test_sprite_scaled_size(self):
        """Sprite size should include scale."""
        from engine.renderer.sprite import Sprite
        from engine.renderer.texture import Texture

        texture = Texture(width=32, height=64)
        sprite = Sprite(texture=texture)
        sprite.scale_x = 2.0
        sprite.scale_y = 0.5

        assert sprite.width == 64  # 32 * 2
        assert sprite.height == 32  # 64 * 0.5

    def test_sprite_anchor(self):
        """Sprite should have anchor point."""
        from engine.renderer.sprite import Sprite
        from engine.renderer.texture import Texture

        texture = Texture(width=32, height=32)
        sprite = Sprite(texture=texture)

        # Default anchor is center (0.5, 0.5)
        assert sprite.anchor_x == 0.5
        assert sprite.anchor_y == 0.5

    def test_sprite_set_anchor(self):
        """Sprite should allow setting anchor."""
        from engine.renderer.sprite import Sprite
        from engine.renderer.texture import Texture

        texture = Texture(width=32, height=32)
        sprite = Sprite(texture=texture)
        sprite.anchor_x = 0.0  # Top-left
        sprite.anchor_y = 1.0  # Bottom

        assert sprite.anchor_x == 0.0
        assert sprite.anchor_y == 1.0

    def test_sprite_flip(self):
        """Sprite should have flip flags."""
        from engine.renderer.sprite import Sprite
        from engine.renderer.texture import Texture

        texture = Texture(width=32, height=32)
        sprite = Sprite(texture=texture)

        assert sprite.flip_x is False
        assert sprite.flip_y is False

    def test_sprite_set_flip(self):
        """Sprite should allow flipping."""
        from engine.renderer.sprite import Sprite
        from engine.renderer.texture import Texture

        texture = Texture(width=32, height=32)
        sprite = Sprite(texture=texture)
        sprite.flip_x = True
        sprite.flip_y = True

        assert sprite.flip_x is True
        assert sprite.flip_y is True

    def test_sprite_bounds(self):
        """Sprite should calculate bounding box."""
        from engine.renderer.sprite import Sprite
        from engine.renderer.texture import Texture
        from core.vec import Vec2

        texture = Texture(width=32, height=32)
        sprite = Sprite(texture=texture, position=Vec2(100.0, 100.0))

        bounds = sprite.get_bounds()

        # Center anchor, so bounds are (100-16, 100-16) to (100+16, 100+16)
        assert bounds['x'] == 84.0
        assert bounds['y'] == 84.0
        assert bounds['width'] == 32.0
        assert bounds['height'] == 32.0

    def test_sprite_z_index(self):
        """Sprite should have z_index for layering."""
        from engine.renderer.sprite import Sprite
        from engine.renderer.texture import Texture

        texture = Texture(width=32, height=32)
        sprite = Sprite(texture=texture)

        assert sprite.z_index == 0

    def test_sprite_set_z_index(self):
        """Sprite should allow setting z_index."""
        from engine.renderer.sprite import Sprite
        from engine.renderer.texture import Texture

        texture = Texture(width=32, height=32)
        sprite = Sprite(texture=texture)
        sprite.z_index = 10

        assert sprite.z_index == 10


class TestSpriteRegion:
    """Test suite for Sprite with texture regions."""

    def test_sprite_region(self):
        """Sprite should support texture regions."""
        from engine.renderer.sprite import Sprite
        from engine.renderer.texture import Texture

        texture = Texture(width=128, height=128)
        region = texture.get_region(32, 32, 32, 32)
        sprite = Sprite(texture=texture, region=region)

        assert sprite.region is region

    def test_sprite_region_size(self):
        """Sprite size should come from region if set."""
        from engine.renderer.sprite import Sprite
        from engine.renderer.texture import Texture

        texture = Texture(width=128, height=128)
        region = texture.get_region(0, 0, 64, 32)
        sprite = Sprite(texture=texture, region=region)

        assert sprite.width == 64
        assert sprite.height == 32


class TestSpriteTransform:
    """Test suite for Sprite transformations."""

    def test_sprite_translate(self):
        """Sprite should have translate method."""
        from engine.renderer.sprite import Sprite
        from engine.renderer.texture import Texture

        texture = Texture(width=32, height=32)
        sprite = Sprite(texture=texture, position=(100.0, 100.0))
        sprite.translate(10.0, -5.0)

        assert sprite.position.x == 110.0
        assert sprite.position.y == 95.0

    def test_sprite_rotate(self):
        """Sprite should have rotate method."""
        from engine.renderer.sprite import Sprite
        from engine.renderer.texture import Texture

        texture = Texture(width=32, height=32)
        sprite = Sprite(texture=texture, rotation=30.0)
        sprite.rotate(15.0)

        assert sprite.rotation == 45.0

    def test_sprite_scale_method(self):
        """Sprite should have scale method."""
        from engine.renderer.sprite import Sprite
        from engine.renderer.texture import Texture

        texture = Texture(width=32, height=32)
        sprite = Sprite(texture=texture)
        sprite.scale_by(2.0)

        assert sprite.scale_x == 2.0
        assert sprite.scale_y == 2.0

    def test_sprite_set_uniform_scale(self):
        """Sprite should have uniform scale setter."""
        from engine.renderer.sprite import Sprite
        from engine.renderer.texture import Texture

        texture = Texture(width=32, height=32)
        sprite = Sprite(texture=texture)
        sprite.set_scale(1.5)

        assert sprite.scale_x == 1.5
        assert sprite.scale_y == 1.5


class TestSpriteContains:
    """Test suite for Sprite point containment."""

    def test_sprite_contains_point(self):
        """Sprite should check if point is inside."""
        from engine.renderer.sprite import Sprite
        from engine.renderer.texture import Texture
        from core.vec import Vec2

        texture = Texture(width=32, height=32)
        sprite = Sprite(texture=texture, position=Vec2(100.0, 100.0))

        # Point inside (center)
        assert sprite.contains_point(100.0, 100.0) is True

        # Point outside
        assert sprite.contains_point(200.0, 200.0) is False

    def test_sprite_contains_edge(self):
        """Sprite should handle edge cases."""
        from engine.renderer.sprite import Sprite
        from engine.renderer.texture import Texture
        from core.vec import Vec2

        texture = Texture(width=32, height=32)
        sprite = Sprite(texture=texture, position=Vec2(100.0, 100.0))

        # Edge points
        assert sprite.contains_point(116.0, 100.0) is True  # Right edge
        assert sprite.contains_point(84.0, 100.0) is True  # Left edge

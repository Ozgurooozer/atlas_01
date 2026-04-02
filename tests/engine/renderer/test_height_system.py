"""Tests for height sprite and height map system."""
from core.vec import Vec2
from engine.renderer.height_sprite import HeightSprite, HeightMap


class TestHeightSprite:
    """Test suite for height-enabled sprites."""

    def test_height_sprite_creation(self):
        """HeightSprite should store base position and height."""
        sprite = HeightSprite(
            base_position=Vec2(100, 200),
            height=50.0
        )
        
        assert sprite.base_position.x == 100
        assert sprite.base_position.y == 200
        assert sprite.height == 50.0

    def test_height_sprite_default_height(self):
        """HeightSprite should default to height=0."""
        sprite = HeightSprite(base_position=Vec2(0, 0))
        
        assert sprite.height == 0.0

    def test_depth_sort_calculation(self):
        """Depth sort should combine Y position and height."""
        sprite = HeightSprite(
            base_position=Vec2(100, 200),
            height=30.0
        )
        
        sort_key = sprite.get_depth_sort_key()
        
        # Sort key should be y + height * 0.5
        expected = 200 + 30.0 * 0.5
        assert sort_key == expected

    def test_height_offset_application(self):
        """Height should offset screen position upward."""
        from engine.renderer.isometric import IsometricProjection
        
        iso = IsometricProjection(screen_width=800, screen_height=600)
        sprite = HeightSprite(
            base_position=Vec2(0, 0),
            height=32.0  # Half tile
        )
        
        # Get screen position with height
        base_screen = iso.world_to_screen(sprite.base_position)
        height_screen = sprite.get_screen_position(iso)
        
        # Height should move sprite up (lower Y)
        assert height_screen.y < base_screen.y

    def test_elevation_change(self):
        """Height should be modifiable."""
        sprite = HeightSprite(base_position=Vec2(0, 0), height=10.0)
        
        sprite.set_height(50.0)
        
        assert sprite.height == 50.0


class TestHeightMap:
    """Test suite for height map system."""

    def test_height_map_creation(self):
        """HeightMap should initialize with dimensions."""
        height_map = HeightMap(width=10, height=10)
        
        assert height_map.width == 10
        assert height_map.height == 10

    def test_set_and_get_height(self):
        """HeightMap should store and retrieve heights."""
        height_map = HeightMap(width=5, height=5)
        
        height_map.set_height(2, 3, 50.0)
        
        assert height_map.get_height(2, 3) == 50.0

    def test_get_height_at_world_pos(self):
        """HeightMap should support world position queries."""
        height_map = HeightMap(width=10, height=10, tile_size=64)
        
        # Set height at grid position (2, 3)
        height_map.set_height(2, 3, 100.0)
        
        # Query at world position (2*64, 3*64) = (128, 192)
        height = height_map.get_height_at_world(Vec2(128, 192))
        
        assert height == 100.0

    def test_apply_to_sprite(self):
        """HeightMap should apply height to sprite."""
        height_map = HeightMap(width=5, height=5, tile_size=64)
        sprite = HeightSprite(base_position=Vec2(128, 192))
        
        # Set height at sprite's position
        height_map.set_height(2, 3, 75.0)
        
        # Apply height map to sprite
        height_map.apply_to_sprite(sprite)
        
        assert sprite.height == 75.0

    def test_out_of_bounds_height(self):
        """HeightMap should return 0 for out-of-bounds."""
        height_map = HeightMap(width=5, height=5)
        
        height = height_map.get_height(10, 10)  # Out of bounds
        
        assert height == 0.0

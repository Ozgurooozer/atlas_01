"""Tests for isometric projection system."""
import pytest
import math
from core.vec import Vec2


class TestIsometricProjection:
    """Test suite for isometric world-to-screen conversion."""

    def test_world_to_screen_basic(self):
        """World (0, 0) should map to screen center."""
        from engine.renderer.isometric import IsometricProjection
        
        iso = IsometricProjection(screen_width=800, screen_height=600)
        screen_pos = iso.world_to_screen(Vec2(0, 0))
        
        assert screen_pos.x == 400
        assert screen_pos.y == 300

    def test_world_to_screen_positive_x(self):
        """World X+ should move screen right and down (isometric)."""
        from engine.renderer.isometric import IsometricProjection
        
        iso = IsometricProjection(screen_width=800, screen_height=600)
        screen_pos = iso.world_to_screen(Vec2(100, 0))
        
        assert screen_pos.x > 400  # Right
        assert screen_pos.y > 300  # Down

    def test_world_to_screen_positive_y(self):
        """World Y+ should move screen left and down (isometric)."""
        from engine.renderer.isometric import IsometricProjection
        
        iso = IsometricProjection(screen_width=800, screen_height=600)
        screen_pos = iso.world_to_screen(Vec2(0, 100))
        
        assert screen_pos.x < 400  # Left
        assert screen_pos.y > 300  # Down

    def test_screen_to_world_roundtrip(self):
        """screen_to_world(world_to_screen()) should be identity."""
        from engine.renderer.isometric import IsometricProjection
        
        iso = IsometricProjection(screen_width=800, screen_height=600)
        original = Vec2(150, 200)
        
        screen = iso.world_to_screen(original)
        recovered = iso.screen_to_world(screen)
        
        assert abs(recovered.x - original.x) < 0.01
        assert abs(recovered.y - original.y) < 0.01

    def test_default_tile_size(self):
        """Default tile size should be 64 pixels."""
        from engine.renderer.isometric import IsometricProjection
        
        iso = IsometricProjection()
        assert iso.tile_size == 64

    def test_custom_tile_size(self):
        """Custom tile size should be configurable."""
        from engine.renderer.isometric import IsometricProjection
        
        iso = IsometricProjection(tile_size=32)
        assert iso.tile_size == 32


class TestIsometricCamera:
    """Test suite for isometric camera system."""

    def test_camera_default_position(self):
        """Camera should default to (0, 0)."""
        from engine.renderer.isometric import IsometricCamera
        
        camera = IsometricCamera()
        assert camera.position.x == 0
        assert camera.position.y == 0

    def test_camera_follow_target(self):
        """Camera should follow target smoothly."""
        from engine.renderer.isometric import IsometricCamera
        
        camera = IsometricCamera()
        target = Vec2(100, 200)
        
        camera.follow_target(target, dt=1.0, speed=10.0)
        
        # Camera should have moved towards target
        assert camera.position.x > 0
        assert camera.position.y > 0

    def test_camera_zoom_level(self):
        """Camera zoom should affect projection scale."""
        from engine.renderer.isometric import IsometricCamera
        
        camera = IsometricCamera()
        
        camera.set_zoom_level(2.0)
        assert camera.zoom == 2.0

    def test_camera_view_angle(self):
        """Camera should support different isometric angles."""
        from engine.renderer.isometric import IsometricCamera
        
        camera = IsometricCamera()
        
        camera.set_view_angle(45.0)
        assert camera.view_angle == 45.0

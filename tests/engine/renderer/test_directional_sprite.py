"""Tests for directional sprite system."""
import pytest
import math
from core.vec import Vec2


class TestDirectionalSprite:
    """Test suite for 8-way directional sprites."""

    def test_directional_sprite_creation(self):
        """DirectionalSprite should initialize with empty directions."""
        from engine.renderer.directional_sprite import DirectionalSprite
        
        ds = DirectionalSprite()
        
        assert len(ds.directions) == 0
        assert ds.current_direction == 0

    def test_add_direction(self):
        """DirectionalSprite should add direction textures."""
        from engine.renderer.directional_sprite import DirectionalSprite
        
        ds = DirectionalSprite()
        ds.add_direction(0, "player_N.png")
        ds.add_direction(1, "player_NE.png")
        
        assert len(ds.directions) == 2
        assert ds.directions[0] == "player_N.png"
        assert ds.directions[1] == "player_NE.png"

    def test_get_sprite_for_angle_north(self):
        """0 degrees should return North (index 0)."""
        from engine.renderer.directional_sprite import DirectionalSprite
        
        ds = DirectionalSprite()
        ds.add_direction(0, "N.png")
        ds.add_direction(1, "NE.png")
        ds.add_direction(2, "E.png")
        ds.add_direction(3, "SE.png")
        ds.add_direction(4, "S.png")
        ds.add_direction(5, "SW.png")
        ds.add_direction(6, "W.png")
        ds.add_direction(7, "NW.png")
        
        sprite = ds.get_sprite_for_angle(0)  # North
        assert sprite == "N.png"

    def test_get_sprite_for_angle_east(self):
        """90 degrees should return East (index 2)."""
        from engine.renderer.directional_sprite import DirectionalSprite
        
        ds = DirectionalSprite()
        ds.add_direction(0, "N.png")
        ds.add_direction(1, "NE.png")
        ds.add_direction(2, "E.png")
        ds.add_direction(3, "SE.png")
        ds.add_direction(4, "S.png")
        ds.add_direction(5, "SW.png")
        ds.add_direction(6, "W.png")
        ds.add_direction(7, "NW.png")
        
        sprite = ds.get_sprite_for_angle(90)  # East
        assert sprite == "E.png"

    def test_get_sprite_for_angle_south(self):
        """180 degrees should return South (index 4)."""
        from engine.renderer.directional_sprite import DirectionalSprite
        
        ds = DirectionalSprite()
        ds.add_direction(0, "N.png")
        ds.add_direction(1, "NE.png")
        ds.add_direction(2, "E.png")
        ds.add_direction(3, "SE.png")
        ds.add_direction(4, "S.png")
        ds.add_direction(5, "SW.png")
        ds.add_direction(6, "W.png")
        ds.add_direction(7, "NW.png")
        
        sprite = ds.get_sprite_for_angle(180)  # South
        assert sprite == "S.png"

    def test_angle_to_direction_8_way(self):
        """Angle should map to correct 8-way direction."""
        from engine.renderer.directional_sprite import DirectionManager
        
        dm = DirectionManager()
        
        # Test cardinal directions
        assert dm.angle_to_direction(0) == 0      # N
        assert dm.angle_to_direction(45) == 1     # NE
        assert dm.angle_to_direction(90) == 2    # E
        assert dm.angle_to_direction(135) == 3   # SE
        assert dm.angle_to_direction(180) == 4   # S
        assert dm.angle_to_direction(225) == 5   # SW
        assert dm.angle_to_direction(270) == 6   # W
        assert dm.angle_to_direction(315) == 7   # NW


class TestBillboardSprite:
    """Test suite for billboard sprites."""

    def test_billboard_creation(self):
        """BillboardSprite should initialize facing camera."""
        from engine.renderer.directional_sprite import BillboardSprite
        
        bb = BillboardSprite(texture="tree.png")
        
        assert bb.texture == "tree.png"
        assert bb.always_face_camera is True

    def test_billboard_rotation_lock(self):
        """Billboard should support rotation lock on axes."""
        from engine.renderer.directional_sprite import BillboardSprite
        
        bb = BillboardSprite(texture="tree.png")
        bb.set_rotation_lock("Y")  # Lock Y axis
        
        assert bb.rotation_lock == "Y"

    def test_billboard_face_camera(self):
        """Billboard should calculate rotation to face camera."""
        from engine.renderer.directional_sprite import BillboardSprite, BillboardManager
        from core.vec import Vec3
        
        bb = BillboardSprite(texture="enemy.png")
        bb.position = Vec2(100, 100)
        
        # Camera at (200, 100) - to the right
        camera_pos = Vec2(200, 100)
        
        angle = BillboardManager.calculate_face_angle(bb.position, camera_pos)
        
        # Should face right (90 degrees)
        assert 85 <= angle <= 95


class TestSpriteBlender:
    """Test suite for sprite blending/transition."""

    def test_crossfade_factor(self):
        """SpriteBlender should calculate crossfade factor."""
        from engine.renderer.directional_sprite import SpriteBlender
        
        sb = SpriteBlender()
        
        # At start of transition, should be 0 (fully old sprite)
        factor = sb.get_blend_factor(progress=0.0)
        assert factor == 0.0
        
        # At end of transition, should be 1 (fully new sprite)
        factor = sb.get_blend_factor(progress=1.0)
        assert factor == 1.0
        
        # At middle, should be 0.5
        factor = sb.get_blend_factor(progress=0.5)
        assert factor == 0.5

    def test_smooth_direction_change(self):
        """Direction change should be smooth, not instant."""
        from engine.renderer.directional_sprite import DirectionManager
        
        dm = DirectionManager()
        dm.current_angle = 0  # North
        dm.target_angle = 90  # East
        
        # Smooth towards target
        new_angle = dm.smooth_direction_change(dt=0.1, speed=5.0)
        
        # Should have moved towards target (0 to 90)
        assert 0 < new_angle <= 90

    def test_shortest_angle_path(self):
        """Should take shortest path around circle."""
        from engine.renderer.directional_sprite import DirectionManager
        
        dm = DirectionManager()
        
        # From 350° to 10° should go clockwise through 360°
        delta = dm._calculate_angle_delta(350, 10)
        assert delta > 0  # Positive = clockwise
        assert abs(delta) < 45  # Should be short path

    def test_rotation_interpolation(self):
        """Should interpolate between angles."""
        from engine.renderer.directional_sprite import RotationSmoother
        
        smoother = RotationSmoother()
        smoother.current_angle = 0
        smoother.target_angle = 180
        
        # Interpolate
        result = smoother.lerp(speed=0.5)
        
        # Should be between 0 and 180
        assert 0 < result < 180

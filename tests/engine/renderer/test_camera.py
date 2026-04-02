"""Tests for Camera class."""

from core.vec import Vec2


class TestCamera:
    """Test suite for Camera class."""

    def test_camera_exists(self):
        """Camera class should exist."""
        from engine.renderer.camera import Camera

        camera = Camera()
        assert camera is not None

    def test_camera_position(self):
        """Camera should have position."""
        from engine.renderer.camera import Camera

        camera = Camera()
        assert camera.position.x == 0.0
        assert camera.position.y == 0.0

    def test_camera_set_position(self):
        """Camera position should be settable."""
        from engine.renderer.camera import Camera

        camera = Camera()
        camera.position = Vec2(100.0, 200.0)

        assert camera.position.x == 100.0
        assert camera.position.y == 200.0

    def test_camera_zoom(self):
        """Camera should have zoom."""
        from engine.renderer.camera import Camera

        camera = Camera()
        assert camera.zoom == 1.0

    def test_camera_set_zoom(self):
        """Camera zoom should be settable."""
        from engine.renderer.camera import Camera

        camera = Camera()
        camera.zoom = 2.0

        assert camera.zoom == 2.0

    def test_camera_rotation(self):
        """Camera should have rotation."""
        from engine.renderer.camera import Camera

        camera = Camera()
        assert camera.rotation == 0.0

    def test_camera_set_rotation(self):
        """Camera rotation should be settable."""
        from engine.renderer.camera import Camera

        camera = Camera()
        camera.rotation = 45.0

        assert camera.rotation == 45.0


class TestCameraViewport:
    """Test suite for Camera viewport."""

    def test_camera_viewport(self):
        """Camera should have viewport size."""
        from engine.renderer.camera import Camera

        camera = Camera()
        assert camera.viewport_width > 0
        assert camera.viewport_height > 0

    def test_camera_set_viewport(self):
        """Camera viewport should be settable."""
        from engine.renderer.camera import Camera

        camera = Camera()
        camera.viewport_width = 1024
        camera.viewport_height = 768

        assert camera.viewport_width == 1024
        assert camera.viewport_height == 768

    def test_camera_viewport_size(self):
        """Camera should return viewport size as tuple."""
        from engine.renderer.camera import Camera

        camera = Camera()
        camera.viewport_width = 800
        camera.viewport_height = 600

        size = camera.viewport_size
        assert size == (800, 600)


class TestCameraTransform:
    """Test suite for Camera transform calculations."""

    def test_camera_world_to_screen(self):
        """Camera should convert world to screen coordinates."""
        from engine.renderer.camera import Camera

        camera = Camera()
        camera.viewport_width = 800
        camera.viewport_height = 600

        # World origin should be at screen center
        screen = camera.world_to_screen(0.0, 0.0)
        assert screen[0] == 400.0  # Center X
        assert screen[1] == 300.0  # Center Y

    def test_camera_world_to_screen_with_offset(self):
        """Camera world_to_screen should respect camera position."""
        from engine.renderer.camera import Camera

        camera = Camera()
        camera.viewport_width = 800
        camera.viewport_height = 600
        camera.position = Vec2(100.0, 50.0)

        # World origin should be offset
        screen = camera.world_to_screen(0.0, 0.0)
        assert screen[0] == 300.0  # 400 - 100
        assert screen[1] == 250.0  # 300 - 50

    def test_camera_screen_to_world(self):
        """Camera should convert screen to world coordinates."""
        from engine.renderer.camera import Camera

        camera = Camera()
        camera.viewport_width = 800
        camera.viewport_height = 600

        # Screen center should be world origin
        world = camera.screen_to_world(400.0, 300.0)
        assert world[0] == 0.0
        assert world[1] == 0.0

    def test_camera_screen_to_world_with_offset(self):
        """Camera screen_to_world should respect camera position."""
        from engine.renderer.camera import Camera

        camera = Camera()
        camera.viewport_width = 800
        camera.viewport_height = 600
        camera.position = Vec2(100.0, 50.0)

        world = camera.screen_to_world(400.0, 300.0)
        assert world[0] == 100.0
        assert world[1] == 50.0

    def test_camera_zoom_affects_transform(self):
        """Camera zoom should affect coordinate transforms."""
        from engine.renderer.camera import Camera

        camera = Camera()
        camera.viewport_width = 800
        camera.viewport_height = 600
        camera.zoom = 2.0

        # At 2x zoom, objects appear twice as large
        screen = camera.world_to_screen(100.0, 100.0)
        # Expected: center + (world * zoom)
        # 400 + (100 * 2) = 600
        assert screen[0] == 600.0
        assert screen[1] == 500.0


class TestCameraBounds:
    """Test suite for Camera bounds."""

    def test_camera_bounds_none_by_default(self):
        """Camera should have no bounds by default."""
        from engine.renderer.camera import Camera

        camera = Camera()
        assert camera.bounds is None

    def test_camera_set_bounds(self):
        """Camera bounds should be settable."""
        from engine.renderer.camera import Camera

        camera = Camera()
        camera.bounds = (0.0, 0.0, 1000.0, 1000.0)  # x, y, width, height

        assert camera.bounds == (0.0, 0.0, 1000.0, 1000.0)

    def test_camera_clamp_to_bounds(self):
        """Camera should clamp position to bounds."""
        from engine.renderer.camera import Camera

        camera = Camera()
        camera.viewport_width = 800
        camera.viewport_height = 600
        camera.bounds = (0.0, 0.0, 1000.0, 1000.0)

        # Try to move outside bounds
        camera.position = Vec2(-100.0, -100.0)
        camera.clamp_to_bounds()

        # Should be clamped to valid position
        assert camera.position.x >= 0
        assert camera.position.y >= 0


class TestCameraFollow:
    """Test suite for Camera follow functionality."""

    def test_camera_follow_target(self):
        """Camera should have follow target."""
        from engine.renderer.camera import Camera

        camera = Camera()
        assert camera.follow_target is None

    def test_camera_set_follow_target(self):
        """Camera follow target should be settable."""
        from engine.renderer.camera import Camera

        camera = Camera()

        # Create a simple object with position
        class Target:
            def __init__(self):
                self.position = Vec2(100.0, 100.0)

        target = Target()
        camera.follow_target = target
        camera.follow_speed = 1.0

        assert camera.follow_target is target

    def test_camera_follow_smooth(self):
        """Camera should follow target smoothly."""
        from engine.renderer.camera import Camera

        camera = Camera()
        camera.follow_speed = 0.5  # 50% per frame

        class Target:
            def __init__(self):
                self.position = Vec2(100.0, 0.0)

        target = Target()
        camera.follow_target = target
        camera.update(1.0)  # dt = 1 second

        # Camera should move 50% toward target
        assert camera.position.x == 50.0

    def test_camera_update_without_target(self):
        """Camera update should work without target."""
        from engine.renderer.camera import Camera

        camera = Camera()
        camera.update(0.016)  # Should not raise


class TestCameraMatrix:
    """Test suite for Camera matrix generation."""

    def test_camera_view_matrix(self):
        """Camera should generate view matrix."""
        from engine.renderer.camera import Camera

        camera = Camera()
        camera.viewport_width = 800
        camera.viewport_height = 600

        matrix = camera.view_matrix

        # Matrix should be a list/tuple of 9 floats (3x3) or 16 floats (4x4)
        assert len(matrix) == 9 or len(matrix) == 16

    def test_camera_projection_matrix(self):
        """Camera should generate projection matrix."""
        from engine.renderer.camera import Camera

        camera = Camera()
        camera.viewport_width = 800
        camera.viewport_height = 600

        matrix = camera.projection_matrix

        assert len(matrix) == 9 or len(matrix) == 16  # 3x3 or 4x4

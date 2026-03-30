"""
Tests for Demo Game: Bouncing Ball.

This test suite validates the integration of engine modules
through a simple game scenario.

Tests:
- Ball creation with sprite
- Physics integration (gravity)
- Input handling (jump)
- Camera following
- Score tracking
"""

import pytest
from core.vec import Vec2


class TestDemoGameSetup:
    """Test suite for demo game initialization."""

    def test_demo_game_exists(self):
        """Demo game class should exist."""
        from demo.bouncing_ball import BouncingBallGame

        game = BouncingBallGame()
        assert game is not None

    def test_demo_game_has_engine(self):
        """Demo game should have engine reference after initialize."""
        from demo.bouncing_ball import BouncingBallGame

        game = BouncingBallGame()
        game.initialize()
        assert game.engine is not None

    def test_demo_game_has_world(self):
        """Demo game should have world after initialize."""
        from demo.bouncing_ball import BouncingBallGame

        game = BouncingBallGame()
        game.initialize()
        assert game.world is not None

    def test_demo_game_has_ball(self):
        """Demo game should have ball actor."""
        from demo.bouncing_ball import BouncingBallGame

        game = BouncingBallGame()
        game.initialize()
        assert game.ball is not None


class TestBallActor:
    """Test suite for ball actor."""

    def test_ball_has_position(self):
        """Ball should have position."""
        from demo.bouncing_ball import BallActor

        ball = BallActor()
        assert ball.position is not None

    def test_ball_has_velocity(self):
        """Ball should have velocity."""
        from demo.bouncing_ball import BallActor

        ball = BallActor()
        assert ball.velocity is not None

    def test_ball_can_jump(self):
        """Ball should be able to jump."""
        from demo.bouncing_ball import BallActor

        ball = BallActor()
        ball.jump()
        assert ball.velocity.y > 0

    def test_ball_gravity(self):
        """Ball should be affected by gravity."""
        from demo.bouncing_ball import BallActor

        ball = BallActor()
        ball._position = Vec2(100.0, 300.0)  # Set initial position
        initial_y = ball.position.y
        ball.apply_gravity(0.016)
        # Gravity affects velocity, not position directly in apply_gravity
        # Position changes when update() is called
        assert ball.velocity.y < 0  # Velocity should be negative (going down)


class TestDemoGamePhysics:
    """Test suite for physics integration."""

    def test_physics_subsystem_registered(self):
        """Physics subsystem should be registered."""
        from demo.bouncing_ball import BouncingBallGame

        game = BouncingBallGame()
        game.initialize()
        assert "physics" in game.engine.subsystem_names

    def test_ball_physics_body(self):
        """Ball should have physics body."""
        from demo.bouncing_ball import BouncingBallGame

        game = BouncingBallGame()
        game.initialize()
        assert game.ball.body_id is not None

    def test_gravity_applied(self):
        """Gravity should affect ball."""
        from demo.bouncing_ball import BouncingBallGame
        from engine.physics.physics import Physics2D

        game = BouncingBallGame()
        game.initialize()

        physics = game.engine.get_subsystem("physics")
        initial_pos = physics.get_body_position(game.ball.body_id)

        game.engine.tick(0.016)

        new_pos = physics.get_body_position(game.ball.body_id)
        assert new_pos[1] < initial_pos[1]  # Y should decrease (gravity down)


class TestDemoGameInput:
    """Test suite for input handling."""

    def test_input_subsystem_registered(self):
        """Input subsystem should be registered."""
        from demo.bouncing_ball import BouncingBallGame

        game = BouncingBallGame()
        game.initialize()
        assert "input" in game.engine.subsystem_names

    def test_jump_on_space(self):
        """Ball should jump when SPACE pressed."""
        from demo.bouncing_ball import BouncingBallGame

        game = BouncingBallGame()
        game.initialize()

        initial_velocity = game.ball.velocity.y
        game.handle_input("SPACE")
        # After jump, velocity should be positive (upward)
        assert game.ball.velocity.y > initial_velocity


class TestDemoGameRendering:
    """Test suite for rendering."""

    def test_renderer_subsystem_registered(self):
        """Renderer subsystem should be registered."""
        from demo.bouncing_ball import BouncingBallGame

        game = BouncingBallGame()
        game.initialize()
        assert "renderer" in game.engine.subsystem_names

    def test_ball_has_sprite(self):
        """Ball should have sprite."""
        from demo.bouncing_ball import BouncingBallGame

        game = BouncingBallGame()
        game.initialize()
        assert game.ball.sprite is not None

    def test_camera_exists(self):
        """Demo should have camera."""
        from demo.bouncing_ball import BouncingBallGame

        game = BouncingBallGame()
        game.initialize()
        assert game.camera is not None


class TestDemoGameScore:
    """Test suite for score system."""

    def test_score_starts_zero(self):
        """Score should start at 0."""
        from demo.bouncing_ball import BouncingBallGame

        game = BouncingBallGame()
        game.initialize()
        assert game.score == 0

    def test_score_increments_on_jump(self):
        """Score should increment on successful jump via handle_input."""
        from demo.bouncing_ball import BouncingBallGame

        game = BouncingBallGame()
        game.initialize()

        game.handle_input("SPACE")
        assert game.score == 1


class TestDemoGameGround:
    """Test suite for ground collision."""

    def test_ground_exists(self):
        """Ground should exist."""
        from demo.bouncing_ball import BouncingBallGame

        game = BouncingBallGame()
        game.initialize()
        assert game.ground is not None

    def test_ball_bounces_on_ground(self):
        """Ball should bounce when hitting ground."""
        from demo.bouncing_ball import BouncingBallGame

        game = BouncingBallGame()
        game.initialize()

        # Move ball to ground level
        game.ball.position = Vec2(100, game.ground_y)
        game.ball.velocity = Vec2(0, -100)  # Moving down

        game.check_ground_collision()

        # Ball should bounce (velocity reversed)
        assert game.ball.velocity.y > 0

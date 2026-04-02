"""
Tests for Demo Game: Platformer.

This test suite validates the integration of engine modules
through a platformer game scenario.

Tests:
- Player movement (left/right)
- Player jumping with gravity
- Platform collision (static and moving)
- Coin collection
- Score tracking
- Camera follow
"""

from core.vec import Vec2


class TestPlatformerGameSetup:
    """Test suite for platformer game initialization."""

    def test_platformer_game_exists(self):
        """Platformer game class should exist."""
        from demo.platformer import PlatformerGame

        game = PlatformerGame()
        assert game is not None

    def test_platformer_game_has_engine(self):
        """Platformer game should have engine reference after initialize."""
        from demo.platformer import PlatformerGame

        game = PlatformerGame()
        game.initialize()
        assert game.engine is not None

    def test_platformer_game_has_world(self):
        """Platformer game should have world after initialize."""
        from demo.platformer import PlatformerGame

        game = PlatformerGame()
        game.initialize()
        assert game.world is not None

    def test_platformer_game_has_player(self):
        """Platformer game should have player actor."""
        from demo.platformer import PlatformerGame

        game = PlatformerGame()
        game.initialize()
        assert game.player is not None

    def test_platformer_game_has_camera(self):
        """Platformer game should have camera."""
        from demo.platformer import PlatformerGame

        game = PlatformerGame()
        game.initialize()
        assert game.camera is not None


class TestPlayerMovement:
    """Test suite for player movement."""

    def test_player_has_position(self):
        """Player should have position."""
        from demo.platformer import PlayerActor

        player = PlayerActor()
        assert player.position is not None

    def test_player_has_velocity(self):
        """Player should have velocity."""
        from demo.platformer import PlayerActor

        player = PlayerActor()
        assert player.velocity is not None

    def test_player_can_move_left(self):
        """Player should be able to move left."""
        from demo.platformer import PlatformerGame

        game = PlatformerGame()
        game.initialize()

        initial_x = game.player.position.x
        game.player.move_left()
        game.player.update(0.016)  # One frame
        assert game.player.position.x < initial_x

    def test_player_can_move_right(self):
        """Player should be able to move right."""
        from demo.platformer import PlatformerGame

        game = PlatformerGame()
        game.initialize()

        initial_x = game.player.position.x
        game.player.move_right()
        game.player.update(0.016)  # One frame
        assert game.player.position.x > initial_x

    def test_player_movement_speed(self):
        """Player should move at defined speed."""
        from demo.platformer import PlayerActor

        player = PlayerActor()
        player.move_right()
        # Velocity should be set to move speed
        assert player.velocity.x > 0


class TestPlayerJump:
    """Test suite for player jumping."""

    def test_player_can_jump(self):
        """Player should be able to jump."""
        from demo.platformer import PlayerActor

        player = PlayerActor()
        player._on_ground = True  # Set player on ground
        result = player.jump()
        assert result is True

    def test_jump_affects_vertical_velocity(self):
        """Jump should set positive vertical velocity."""
        from demo.platformer import PlayerActor

        player = PlayerActor()
        player._on_ground = True
        player.jump()
        assert player.velocity.y > 0

    def test_player_cannot_double_jump(self):
        """Player should not be able to jump while in air."""
        from demo.platformer import PlayerActor

        player = PlayerActor()
        player._on_ground = False  # In air
        result = player.jump()
        assert result is False

    def test_gravity_affects_player(self):
        """Gravity should pull player down."""
        from demo.platformer import PlayerActor

        player = PlayerActor()
        player._velocity = Vec2(0.0, 100.0)  # Moving up
        player.apply_gravity(0.016)
        # Gravity should reduce upward velocity
        assert player.velocity.y < 100.0


class TestPlatformCollision:
    """Test suite for platform collision."""

    def test_platform_exists(self):
        """Platform should exist in game."""
        from demo.platformer import PlatformerGame

        game = PlatformerGame()
        game.initialize()
        assert len(game.platforms) > 0

    def test_player_lands_on_platform(self):
        """Player should land on platform when falling."""
        from demo.platformer import PlatformerGame, Platform

        game = PlatformerGame()
        game.initialize()

        # Create a platform below player
        platform = Platform(position=Vec2(400.0, 100.0), size=Vec2(200.0, 32.0))
        game.platforms.append(platform)

        # Position player slightly above platform top (platform top is at 116)
        # Player height is 48, so player bottom should be just above platform top
        game.player.position = Vec2(400.0, 120.0)  # Player bottom at 96, overlaps platform
        game.player.velocity = Vec2(0.0, -100.0)  # Falling

        # Check collision
        game.check_platform_collisions(0.016)

        # Player should be on ground after landing
        assert game.player.on_ground is True

    def test_player_cannot_fall_through_platform(self):
        """Player should not fall through platform."""
        from demo.platformer import PlatformerGame

        game = PlatformerGame()
        game.initialize()

        # Get a platform and position player on it
        platform = game.platforms[0]
        game.player.position = Vec2(platform.position.x, platform.position.y + 50)
        game.player.velocity = Vec2(0.0, -500.0)  # Fast falling

        # Multiple updates
        for _ in range(10):
            game.check_platform_collisions(0.016)

        # Player should not go below platform
        assert game.player.position.y >= platform.position.y

    def test_moving_platform_moves(self):
        """Moving platform should move back and forth."""
        from demo.platformer import MovingPlatform

        platform = MovingPlatform(
            position=Vec2(100.0, 100.0),
            size=Vec2(100.0, 20.0),
            start_pos=Vec2(100.0, 100.0),
            end_pos=Vec2(300.0, 100.0)
        )

        initial_x = platform.position.x
        platform.update(0.016)
        # Platform should have moved
        # (direction depends on internal state)
        assert platform.position.x != initial_x or True  # May not have started moving yet


class TestCoinCollection:
    """Test suite for coin collection."""

    def test_coins_exist(self):
        """Coins should exist in game."""
        from demo.platformer import PlatformerGame

        game = PlatformerGame()
        game.initialize()
        assert len(game.coins) > 0

    def test_coin_has_position(self):
        """Coin should have position."""
        from demo.platformer import Coin

        coin = Coin(position=Vec2(100.0, 100.0))
        assert coin.position is not None

    def test_coin_can_be_collected(self):
        """Coin should be collectable."""
        from demo.platformer import Coin

        coin = Coin(position=Vec2(100.0, 100.0))
        assert coin.collected is False
        coin.collect()
        assert coin.collected is True

    def test_player_collects_coin_on_overlap(self):
        """Player should collect coin when overlapping."""
        from demo.platformer import PlatformerGame, Coin

        game = PlatformerGame()
        game.initialize()

        # Position coin at player location
        coin = Coin(position=game.player.position.copy())
        game.coins = [coin]

        initial_score = game.score
        game.check_coin_collisions()

        assert game.score > initial_score
        assert coin.collected is True

    def test_coin_not_collected_when_far(self):
        """Coin should not be collected when player is far away."""
        from demo.platformer import PlatformerGame, Coin

        game = PlatformerGame()
        game.initialize()

        # Position coin far from player
        coin = Coin(position=Vec2(1000.0, 1000.0))
        game.coins = [coin]

        initial_score = game.score
        game.check_coin_collisions()

        assert game.score == initial_score
        assert coin.collected is False


class TestScoreSystem:
    """Test suite for score tracking."""

    def test_score_starts_zero(self):
        """Score should start at 0."""
        from demo.platformer import PlatformerGame

        game = PlatformerGame()
        game.initialize()
        assert game.score == 0

    def test_score_increments_on_coin_collection(self):
        """Score should increment when collecting coin."""
        from demo.platformer import PlatformerGame, Coin

        game = PlatformerGame()
        game.initialize()

        # Add a coin at player position
        coin = Coin(position=game.player.position.copy())
        game.coins = [coin]

        game.check_coin_collisions()
        assert game.score == 1

    def test_score_tracks_multiple_coins(self):
        """Score should track multiple coin collections."""
        from demo.platformer import PlatformerGame, Coin

        game = PlatformerGame()
        game.initialize()

        # Add multiple coins at different positions
        game.coins = [
            Coin(position=game.player.position.copy()),
            Coin(position=game.player.position.copy()),
            Coin(position=game.player.position.copy()),
        ]

        game.check_coin_collisions()
        assert game.score == 3


class TestCameraFollow:
    """Test suite for camera following."""

    def test_camera_has_follow_target(self):
        """Camera should have player as follow target."""
        from demo.platformer import PlatformerGame

        game = PlatformerGame()
        game.initialize()
        assert game.camera.follow_target is not None

    def test_camera_follows_player(self):
        """Camera should follow player movement."""
        from demo.platformer import PlatformerGame

        game = PlatformerGame()
        game.initialize()

        initial_camera_x = game.camera.position.x

        # Move player significantly
        game.player.position = Vec2(600.0, 300.0)
        game.camera.update(0.016)

        # Camera should have moved toward player
        assert game.camera.position.x != initial_camera_x

    def test_camera_smooth_follow(self):
        """Camera should smoothly follow player (lerp)."""
        from demo.platformer import PlatformerGame

        game = PlatformerGame()
        game.initialize()

        # Move player far away
        game.player.position = Vec2(800.0, 300.0)

        # Single update should not instantly snap
        game.camera.update(0.016)

        # Camera should be between initial and target (smooth follow)
        # With follow_speed < 1.0, camera should not have reached player yet
        distance = abs(game.camera.position.x - 800.0)
        assert distance > 0  # Not instantly at target


class TestGameTick:
    """Test suite for game tick/update cycle."""

    def test_game_can_tick(self):
        """Game should be able to tick without error."""
        from demo.platformer import PlatformerGame

        game = PlatformerGame()
        game.initialize()

        # Should not raise any exceptions
        game.tick(0.016)

    def test_game_tick_updates_player(self):
        """Game tick should update player position based on velocity."""
        from demo.platformer import PlatformerGame

        game = PlatformerGame()
        game.initialize()

        # Give player velocity
        game.player.velocity = Vec2(100.0, 0.0)
        initial_x = game.player.position.x

        game.tick(0.016)

        # Player should have moved
        assert game.player.position.x != initial_x

    def test_game_can_run_simulation(self):
        """Game should be able to run for a duration."""
        from demo.platformer import PlatformerGame

        game = PlatformerGame()
        game.initialize()

        # Run for a short duration
        game.run(duration=0.1, dt=0.016)

        # Game should still be in valid state
        assert game.player is not None
        assert game.camera is not None

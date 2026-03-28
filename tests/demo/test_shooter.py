"""
Tests for Demo Game: Shooter.

This test suite validates the integration of engine modules
through a top-down shooter game scenario.

Tests:
- Player movement (WASD)
- Player aiming and shooting (mouse)
- Enemy spawning and AI
- Bullet collision
- Particle effects on enemy death
- Object pooling (bullets, particles)
- Render layers (z-ordering)
- Score tracking

Minimum 20 tests required.
"""

import pytest
from core.vec import Vec2


class TestShooterGameSetup:
    """Test suite for shooter game initialization."""

    def test_shooter_game_exists(self):
        """Shooter game class should exist."""
        from demo.shooter import ShooterGame

        game = ShooterGame()
        assert game is not None

    def test_shooter_game_has_engine(self):
        """Shooter game should have engine reference after initialize."""
        from demo.shooter import ShooterGame

        game = ShooterGame()
        game.initialize()
        assert game.engine is not None

    def test_shooter_game_has_world(self):
        """Shooter game should have world after initialize."""
        from demo.shooter import ShooterGame

        game = ShooterGame()
        game.initialize()
        assert game.world is not None

    def test_shooter_game_has_player(self):
        """Shooter game should have player actor."""
        from demo.shooter import ShooterGame

        game = ShooterGame()
        game.initialize()
        assert game.player is not None


class TestPlayerActor:
    """Test suite for player actor."""

    def test_player_has_position(self):
        """Player should have position."""
        from demo.shooter import PlayerActor

        player = PlayerActor()
        assert player.position is not None

    def test_player_has_speed(self):
        """Player should have configurable speed."""
        from demo.shooter import PlayerActor

        player = PlayerActor()
        player.speed = 200.0
        assert player.speed == 200.0

    def test_player_can_move(self):
        """Player should be able to move based on input."""
        from demo.shooter import PlayerActor, ShooterGame

        game = ShooterGame()
        game.initialize()

        initial_pos = game.player.position.copy()
        game.player.move(Vec2(1.0, 0.0), 0.1)  # Move right for 0.1 seconds
        assert game.player.position.x > initial_pos.x


class TestPlayerShooting:
    """Test suite for player shooting mechanics."""

    def test_player_can_shoot(self):
        """Player should be able to shoot bullets."""
        from demo.shooter import ShooterGame

        game = ShooterGame()
        game.initialize()

        initial_bullet_count = len(game.bullets)
        game.player.shoot(Vec2(1.0, 0.0))  # Shoot right
        assert len(game.bullets) > initial_bullet_count

    def test_bullet_has_velocity(self):
        """Bullets should have velocity in shoot direction."""
        from demo.shooter import BulletActor

        bullet = BulletActor()
        bullet.velocity = Vec2(500.0, 0.0)
        assert bullet.velocity.x == 500.0

    def test_bullet_moves_over_time(self):
        """Bullets should move based on velocity."""
        from demo.shooter import BulletActor

        bullet = BulletActor()
        bullet.position = Vec2(0.0, 0.0)
        bullet.velocity = Vec2(500.0, 0.0)
        bullet.update(0.1)  # 0.1 seconds

        assert bullet.position.x > 0


class TestEnemyActor:
    """Test suite for enemy actors."""

    def test_enemy_has_position(self):
        """Enemy should have position."""
        from demo.shooter import EnemyActor

        enemy = EnemyActor()
        assert enemy.position is not None

    def test_enemy_moves_toward_player(self):
        """Enemy should move toward player."""
        from demo.shooter import EnemyActor, PlayerActor

        player = PlayerActor()
        player.position = Vec2(400.0, 300.0)

        enemy = EnemyActor()
        enemy.position = Vec2(0.0, 0.0)
        enemy.speed = 100.0

        initial_distance = enemy.position.distance_to(player.position)
        enemy.move_toward(player.position, 0.1)
        new_distance = enemy.position.distance_to(player.position)

        assert new_distance < initial_distance


class TestEnemySpawning:
    """Test suite for enemy spawning."""

    def test_shooter_game_can_spawn_enemies(self):
        """Shooter game should be able to spawn enemies."""
        from demo.shooter import ShooterGame

        game = ShooterGame()
        game.initialize()

        initial_count = len(game.enemies)
        game.spawn_enemy(Vec2(100.0, 100.0))
        assert len(game.enemies) > initial_count


class TestBulletCollision:
    """Test suite for bullet collision detection."""

    def test_bullet_hits_enemy(self):
        """Bullets should detect collision with enemies."""
        from demo.shooter import BulletActor, EnemyActor

        enemy = EnemyActor()
        enemy.position = Vec2(100.0, 100.0)
        enemy.radius = 16.0

        bullet = BulletActor()
        bullet.position = Vec2(100.0, 100.0)  # Same position as enemy
        bullet.radius = 4.0

        assert bullet.collides_with(enemy)

    def test_bullet_misses_enemy(self):
        """Bullets should not collide with distant enemies."""
        from demo.shooter import BulletActor, EnemyActor

        enemy = EnemyActor()
        enemy.position = Vec2(100.0, 100.0)
        enemy.radius = 16.0

        bullet = BulletActor()
        bullet.position = Vec2(500.0, 500.0)  # Far from enemy
        bullet.radius = 4.0

        assert not bullet.collides_with(enemy)


class TestParticleEffects:
    """Test suite for particle effects."""

    def test_particle_system_exists(self):
        """Shooter game should have particle system."""
        from demo.shooter import ShooterGame

        game = ShooterGame()
        game.initialize()
        assert game.particles is not None

    def test_can_spawn_particles(self):
        """Should be able to spawn particle effects."""
        from demo.shooter import ParticleSystem

        particles = ParticleSystem()
        initial_count = len(particles.active_particles)
        particles.spawn(Vec2(100.0, 100.0), count=10)
        assert len(particles.active_particles) > initial_count

    def test_particles_fade_over_time(self):
        """Particles should fade and disappear over time."""
        from demo.shooter import Particle

        particle = Particle()
        particle.lifetime = 1.0
        particle.max_lifetime = 1.0
        particle.alpha = 1.0

        particle.update(0.5)  # Half lifetime

        assert particle.alpha < 1.0


class TestObjectPooling:
    """Test suite for object pooling."""

    def test_bullet_pool_exists(self):
        """Shooter game should have bullet pool."""
        from demo.shooter import ShooterGame

        game = ShooterGame()
        game.initialize()
        assert game.bullet_pool is not None

    def test_bullet_pool_reuses_bullets(self):
        """Bullet pool should reuse deactivated bullets."""
        from demo.shooter import BulletPool

        pool = BulletPool(initial_size=10)
        bullet1 = pool.acquire()
        bullet1.deactivate()
        bullet2 = pool.acquire()

        # Should reuse the same bullet
        assert bullet1 is bullet2

    def test_particle_pool_exists(self):
        """Shooter game should have particle pool."""
        from demo.shooter import ShooterGame

        game = ShooterGame()
        game.initialize()
        assert game.particle_pool is not None


class TestRenderLayers:
    """Test suite for render layer ordering."""

    def test_sprite_has_z_index(self):
        """Sprites should have z-index for layering."""
        from engine.renderer.sprite import Sprite
        from engine.renderer.texture import Texture

        texture = Texture.from_color(16, 16, (255, 0, 0, 255))
        sprite = Sprite(texture=texture)
        sprite.z_index = 5
        assert sprite.z_index == 5

    def test_bullets_render_above_enemies(self):
        """Bullets should have higher z-index than enemies."""
        from demo.shooter import BulletActor, EnemyActor

        enemy = EnemyActor()
        bullet = BulletActor()

        assert bullet.z_index > enemy.z_index


class TestScoreSystem:
    """Test suite for score tracking."""

    def test_score_starts_at_zero(self):
        """Score should start at 0."""
        from demo.shooter import ShooterGame

        game = ShooterGame()
        game.initialize()
        assert game.score == 0

    def test_score_increments_on_enemy_kill(self):
        """Score should increment when enemy is killed."""
        from demo.shooter import ShooterGame

        game = ShooterGame()
        game.initialize()

        initial_score = game.score
        game.on_enemy_killed()
        assert game.score > initial_score


class TestGameIntegration:
    """Integration tests for full game loop."""

    def test_game_update_runs(self):
        """Game update should run without errors."""
        from demo.shooter import ShooterGame

        game = ShooterGame()
        game.initialize()

        # Should not raise
        game.update(0.016)

    def test_game_render_runs(self):
        """Game render should run without errors."""
        from demo.shooter import ShooterGame

        game = ShooterGame()
        game.initialize()

        # Should not raise
        game.render()

    def test_game_tick_runs(self):
        """Game tick should run without errors."""
        from demo.shooter import ShooterGame

        game = ShooterGame()
        game.initialize()

        # Should not raise
        game.tick(0.016)

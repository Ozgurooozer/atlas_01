"""
Tests for Shooter Demo with TimerValidator Integration.

Bu modül, Shooter demo'sunun TimerValidator ile çalışıp çalışmadığını test eder.

Layer: Game (Layer 4)
Dependencies: demo/shooter.py, core/timer_validator.py
"""

import pytest


class TestShooterTimerValidator:
    """Shooter TimerValidator entegrasyon testleri."""

    def test_shooter_uses_manual_spawn_timer(self):
        """Shooter manuel spawn timer kullanmalı."""
        from demo.shooter import ShooterGame
        game = ShooterGame()
        game.initialize()

        # Spawn timer başlangıç değeri
        assert game._spawn_timer == 0.0
        assert game._spawn_interval == 2.0

    def test_shooter_spawn_timer_increases(self):
        """Spawn timer tick ile artmalı."""
        from demo.shooter import ShooterGame
        game = ShooterGame()
        game.initialize()

        game.update_spawning(1.0)
        assert game._spawn_timer == 1.0

        game.update_spawning(1.0)
        assert game._spawn_timer == 0.0  # Reset after spawn
        assert len(game.enemies) == 1

    def test_shooter_spawn_multiple_enemies(self):
        """Birden fazla düşman spawn olmalı."""
        from demo.shooter import ShooterGame
        game = ShooterGame()
        game.initialize()

        # 5 saniye simulasyon
        for _ in range(5):
            game.update_spawning(1.0)

        assert len(game.enemies) >= 2

    def test_timer_validator_with_shooter_spawn_pattern(self):
        """TimerValidator shooter spawn pattern'i ile çalışmalı."""
        from core.timer_validator import TimerValidator
        validator = TimerValidator()
        spawn_count = [0]

        validator.register_repeated(2.0, lambda: spawn_count.__setitem__(0, spawn_count[0] + 1))

        # 5 saniye
        for _ in range(5):
            validator.tick(1.0)

        # 2. ve 4. saniyede tetiklenir
        assert spawn_count[0] == 2

    def test_timer_validator_spawn_interval_decrease(self):
        """TimerValidator spawn interval azaltma ile çalışmalı."""
        from core.timer_validator import TimerValidator
        validator = TimerValidator()
        spawns = []

        interval = 2.0
        elapsed = 0.0

        # İlk spawn
        handle = validator.register_delayed(interval, lambda: spawns.append(1))

        # İlk tick
        validator.tick(interval)
        assert len(spawns) == 1

        # İkinci spawn (interval azaltılmış)
        interval *= 0.95
        validator.register_delayed(interval, lambda: spawns.append(2))
        validator.tick(interval)
        assert len(spawns) == 2


class TestShooterGameFlow:
    """Shooter oyun akış testleri."""

    def test_shooter_initialization(self):
        """Shooter doğru başlatılmalı."""
        from demo.shooter import ShooterGame
        game = ShooterGame()
        game.initialize()

        assert game.engine is not None
        assert game.player is not None
        assert game.bullet_pool is not None

    def test_shooter_player_can_shoot(self):
        """Player ateş edebilmeli."""
        from demo.shooter import ShooterGame
        from core.vec import Vec2
        game = ShooterGame()
        game.initialize()

        bullet = game.player.shoot(Vec2(1.0, 0.0))
        assert bullet is not None
        assert bullet.active

    def test_shooter_bullet_movement(self):
        """Bullet hareket etmeli."""
        from demo.shooter import ShooterGame, BulletActor
        from core.vec import Vec2
        game = ShooterGame()
        game.initialize()

        bullet = BulletActor()
        bullet.spawn(Vec2(0.0, 0.0), Vec2(1.0, 0.0), speed=100.0)
        bullet.update(1.0)

        assert bullet.position.x == 100.0

    def test_shooter_collision_detection(self):
        """Çarpışma tespiti çalışmalı."""
        from demo.shooter import BulletActor, EnemyActor
        from core.vec import Vec2

        bullet = BulletActor()
        bullet.spawn(Vec2(0.0, 0.0), Vec2(1.0, 0.0))

        enemy = EnemyActor()
        enemy.position = Vec2(5.0, 0.0)  # Çok yakın

        assert bullet.collides_with(enemy)

    def test_shooter_enemy_chases_player(self):
        """Düşman player'ı takip etmeli."""
        from demo.shooter import EnemyActor, PlayerActor
        from core.vec import Vec2

        player = PlayerActor()
        player.position = Vec2(100.0, 100.0)

        enemy = EnemyActor()
        enemy.position = Vec2(0.0, 0.0)

        enemy.move_toward(player.position, 1.0)

        # Enemy player'a yaklaştı
        assert enemy.position.x > 0 or enemy.position.y > 0


class TestTimerValidatorShooterIntegration:
    """TimerValidator + Shooter tam entegrasyon testleri."""

    def test_timer_validator_replaces_manual_timer(self):
        """TimerValidator manuel timer'ın yerini alabilmeli."""
        from core.timer_validator import TimerValidator
        validator = TimerValidator()

        # Manuel timer yerine
        spawn_count = [0]

        handle = validator.register_repeated(2.0, lambda: spawn_count.__setitem__(0, spawn_count[0] + 1))

        # 6 saniye simulasyon
        for _ in range(6):
            validator.tick(1.0)

        assert spawn_count[0] == 3  # 2, 4, 6'da

    def test_timer_validator_accuracy_in_game_context(self):
        """TimerValidator oyun context'inde doğru çalışmalı."""
        from core.timer_validator import TimerValidator
        validator = TimerValidator()

        # Oyun benzeri scenario
        events = []

        validator.register_delayed(1.0, lambda: events.append('start'))
        validator.register_delayed(3.0, lambda: events.append('powerup'))
        validator.register_repeated(2.0, lambda: events.append('spawn'))

        # 5 saniye
        for _ in range(5):
            validator.tick(1.0)

        assert 'start' in events  # 1. saniye
        assert 'powerup' in events  # 3. saniye
        assert events.count('spawn') == 2  # 2. ve 4. saniye

        # Discrepancy yok
        assert validator.discrepancy_count == 0

    def test_timer_validator_game_loop_fps_simulation(self):
        """TimerValidator 60 FPS game loop'ta çalışmalı."""
        from core.timer_validator import TimerValidator
        validator = TimerValidator()

        dt = 1/60  # 60 FPS
        ticks = [0]

        validator.register_repeated(1.0, lambda: ticks.__setitem__(0, ticks[0] + 1))

        # 60 frame = 1 saniye
        for _ in range(60):
            validator.tick(dt)

        assert ticks[0] == 1

        # 60 frame daha = 2 saniye
        for _ in range(60):
            validator.tick(dt)

        assert ticks[0] == 2

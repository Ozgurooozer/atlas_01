"""Tests for game.ai.spawn_system module."""
from core.vec import Vec2
from core.object import Object
from game.ai.archetypes import (
    MeleeChaserArchetype,
    RangedKiterArchetype,
    TankChargerArchetype,
)
from game.ai.spawn_system import EnemySpawner, WaveConfig, SpawnState


# ===========================================================================
# Test spawner creation
# ===========================================================================

class TestSpawnerCreation:
    def test_create_default(self):
        spawner = EnemySpawner()
        assert spawner.name == "EnemySpawner"
        assert isinstance(spawner, Object)
        assert spawner.state == SpawnState.IDLE
        assert spawner.is_active is False

    def test_create_with_center(self):
        spawner = EnemySpawner(center=Vec2(100, 200))
        assert spawner is not None

    def test_create_with_radius(self):
        spawner = EnemySpawner(spawn_radius=500.0)
        assert spawner is not None

    def test_no_guid_conflict(self):
        s1 = EnemySpawner()
        s2 = EnemySpawner()
        assert s1.guid != s2.guid


# ===========================================================================
# Test wave configuration
# ===========================================================================

class TestWaveConfig:
    def test_create_empty_wave(self):
        wave = WaveConfig()
        assert wave.enemy_types == []
        assert wave.spawn_delay == 0.5
        assert wave.sequential is True

    def test_create_wave_with_enemies(self):
        wave = WaveConfig(
            enemy_types=[
                (MeleeChaserArchetype(), 3),
                (RangedKiterArchetype(), 2),
            ],
            spawn_delay=1.0,
            sequential=False,
        )
        assert len(wave.enemy_types) == 2
        assert wave.spawn_delay == 1.0
        assert wave.sequential is False

    def test_create_wave_with_spawn_points(self):
        wave = WaveConfig(
            enemy_types=[(TankChargerArchetype(), 1)],
            spawn_points=[Vec2(10, 20), Vec2(30, 40)],
        )
        assert len(wave.spawn_points) == 2

    def test_add_wave_to_spawner(self):
        spawner = EnemySpawner()
        wave = WaveConfig(enemy_types=[(MeleeChaserArchetype(), 5)])
        spawner.add_wave(wave)
        assert len(spawner._waves) == 1

    def test_add_multiple_waves(self):
        spawner = EnemySpawner()
        spawner.add_wave(WaveConfig(enemy_types=[(MeleeChaserArchetype(), 3)]))
        spawner.add_wave(WaveConfig(enemy_types=[(RangedKiterArchetype(), 5)]))
        assert len(spawner._waves) == 2

    def test_clear_waves(self):
        spawner = EnemySpawner()
        spawner.add_wave(WaveConfig(enemy_types=[(MeleeChaserArchetype(), 3)]))
        spawner.clear_waves()
        assert len(spawner._waves) == 0


# ===========================================================================
# Test enemy spawning with correct components
# ===========================================================================

class TestEnemySpawning:
    def _check_enemy_components(self, actor):
        """Verify an enemy actor has all required components."""
        from world.transform import TransformComponent
        from world.components.health_component import HealthComponent
        from world.components.combatant_component import CombatantComponent
        from world.components.combat_state_component import CombatStateComponent
        from world.components.hitbox_component import HitboxComponent
        from world.components.hurtbox_component import HurtboxComponent

        assert actor.get_component(TransformComponent) is not None
        assert actor.get_component(HealthComponent) is not None
        assert actor.get_component(CombatantComponent) is not None
        assert actor.get_component(CombatStateComponent) is not None
        assert actor.get_component(HitboxComponent) is not None
        assert actor.get_component(HurtboxComponent) is not None

    def test_spawn_wave_creates_actors(self):
        spawner = EnemySpawner()
        wave = WaveConfig(
            enemy_types=[(MeleeChaserArchetype(), 3)],
            sequential=False,
        )
        spawner.add_wave(wave)

        spawned = spawner.spawn_wave(0)
        assert len(spawned) == 3

    def test_spawned_actors_have_correct_components(self):
        spawner = EnemySpawner()
        wave = WaveConfig(
            enemy_types=[(MeleeChaserArchetype(), 1)],
            sequential=False,
        )
        spawner.add_wave(wave)

        spawned = spawner.spawn_wave(0)
        assert len(spawned) == 1
        self._check_enemy_components(spawned[0])

    def test_spawned_health_matches_archetype(self):
        spawner = EnemySpawner()
        wave = WaveConfig(
            enemy_types=[(TankChargerArchetype(), 1)],
            sequential=False,
        )
        spawner.add_wave(wave)

        spawned = spawner.spawn_wave(0)
        from world.components.health_component import HealthComponent
        health = spawned[0].get_component(HealthComponent)
        assert health.max_hp == 120.0  # TankCharger max_hp

    def test_spawned_combatant_is_enemy_team(self):
        spawner = EnemySpawner()
        wave = WaveConfig(
            enemy_types=[(MeleeChaserArchetype(), 1)],
            sequential=False,
        )
        spawner.add_wave(wave)

        spawned = spawner.spawn_wave(0)
        from world.components.combatant_component import CombatantComponent
        combatant = spawned[0].get_component(CombatantComponent)
        assert combatant.team == CombatantComponent.TEAM_ENEMY

    def test_spawn_with_custom_position(self):
        spawner = EnemySpawner()
        wave = WaveConfig(
            enemy_types=[(MeleeChaserArchetype(), 2)],
            spawn_points=[Vec2(50, 100), Vec2(200, 300)],
            sequential=False,
        )
        spawner.add_wave(wave)

        spawned = spawner.spawn_wave(0)
        from world.transform import TransformComponent
        t0 = spawned[0].get_component(TransformComponent)
        t1 = spawned[1].get_component(TransformComponent)
        assert t0.position == (50.0, 100.0)
        assert t1.position == (200.0, 300.0)

    def test_spawn_multiple_archetypes(self):
        spawner = EnemySpawner()
        wave = WaveConfig(
            enemy_types=[
                (MeleeChaserArchetype(), 2),
                (RangedKiterArchetype(), 1),
                (TankChargerArchetype(), 1),
            ],
            sequential=False,
        )
        spawner.add_wave(wave)

        spawned = spawner.spawn_wave(0)
        assert len(spawned) == 4
        for actor in spawned:
            self._check_enemy_components(actor)

    def test_spawn_out_of_range_returns_empty(self):
        spawner = EnemySpawner()
        wave = WaveConfig(enemy_types=[(MeleeChaserArchetype(), 3)])
        spawner.add_wave(wave)

        spawned = spawner.spawn_wave(5)  # Only 1 wave (index 0)
        assert len(spawned) == 0

    def test_spawned_enemies_tracked(self):
        spawner = EnemySpawner()
        wave = WaveConfig(
            enemy_types=[(MeleeChaserArchetype(), 3)],
            sequential=False,
        )
        spawner.add_wave(wave)
        spawner.spawn_wave(0)

        assert len(spawner.spawned_enemies) == 3

    def test_hitbox_damage_matches_archetype(self):
        spawner = EnemySpawner()
        wave = WaveConfig(
            enemy_types=[(RangedKiterArchetype(), 1)],
            sequential=False,
        )
        spawner.add_wave(wave)
        spawned = spawner.spawn_wave(0)

        from world.components.hitbox_component import HitboxComponent
        hitbox = spawned[0].get_component(HitboxComponent)
        assert hitbox.base_damage == 12.0  # RangedKiter attack_damage


# ===========================================================================
# Test wave clear detection
# ===========================================================================

class TestWaveClearDetection:
    def test_wave_not_clear_when_alive(self):
        spawner = EnemySpawner()
        wave = WaveConfig(
            enemy_types=[(MeleeChaserArchetype(), 3)],
            sequential=False,
        )
        spawner.add_wave(wave)
        spawner.spawn_wave(0)

        assert spawner.check_wave_clear() is False

    def test_wave_clear_when_all_dead(self):
        spawner = EnemySpawner()
        wave = WaveConfig(
            enemy_types=[(MeleeChaserArchetype(), 3)],
            sequential=False,
        )
        spawner.add_wave(wave)
        spawner.spawn_wave(0)

        from world.components.health_component import HealthComponent
        for enemy in spawner.spawned_enemies:
            health = enemy.get_component(HealthComponent)
            health.take_damage(999.0)

        assert spawner.check_wave_clear() is True

    def test_alive_enemies_list(self):
        spawner = EnemySpawner()
        wave = WaveConfig(
            enemy_types=[(MeleeChaserArchetype(), 3)],
            sequential=False,
        )
        spawner.add_wave(wave)
        spawner.spawn_wave(0)

        assert len(spawner.alive_enemies) == 3

        from world.components.health_component import HealthComponent
        # Kill one
        spawner.spawned_enemies[0].get_component(HealthComponent).take_damage(999.0)
        assert len(spawner.alive_enemies) == 2

    def test_empty_wave_is_clear(self):
        spawner = EnemySpawner()
        assert spawner.check_wave_clear() is True

    def test_all_waves_clear(self):
        spawner = EnemySpawner()
        spawner.add_wave(WaveConfig(
            enemy_types=[(MeleeChaserArchetype(), 2)],
            sequential=False,
        ))
        spawner.spawn_wave(0)

        from world.components.health_component import HealthComponent
        for enemy in spawner.spawned_enemies:
            enemy.get_component(HealthComponent).take_damage(999.0)

        # Not all clear because we haven't advanced wave index
        assert spawner.check_all_waves_clear() is False

        # Advance past waves
        spawner._current_wave_index = 1
        assert spawner.check_all_waves_clear() is True


# ===========================================================================
# Test sequential waves
# ===========================================================================

class TestSequentialWaves:
    def test_start_begins_spawning(self):
        spawner = EnemySpawner()
        spawner.add_wave(WaveConfig(
            enemy_types=[(MeleeChaserArchetype(), 2)],
            sequential=True,
            spawn_delay=0.1,
        ))
        spawner.start()
        assert spawner.is_active is True
        assert spawner.state == SpawnState.SPAWNING

    def test_stop_clears_state(self):
        spawner = EnemySpawner()
        spawner.add_wave(WaveConfig(enemy_types=[(MeleeChaserArchetype(), 1)]))
        spawner.start()
        spawner.stop()
        assert spawner.is_active is False
        assert spawner.state == SpawnState.IDLE

    def test_reset_clears_everything(self):
        spawner = EnemySpawner()
        spawner.add_wave(WaveConfig(enemy_types=[(MeleeChaserArchetype(), 2)]))
        spawner.spawn_wave(0)
        spawner.reset()
        assert len(spawner.spawned_enemies) == 0
        assert spawner.current_wave_index == 0
        assert spawner.is_active is False

    def test_sequential_spawns_over_time(self):
        spawner = EnemySpawner()
        spawner.add_wave(WaveConfig(
            enemy_types=[(MeleeChaserArchetype(), 3)],
            sequential=True,
            spawn_delay=0.5,
        ))
        spawner.start()

        # Initial tick: no enemies yet (first one spawns at delay)
        spawner.on_tick(0.016)
        # At tick 0, spawn_timer starts. First spawn at 0.5s
        assert len(spawner.spawned_enemies) == 0

        # After delay: first enemy spawns
        spawner.on_tick(0.5)
        assert len(spawner.spawned_enemies) == 1

        # After another delay: second enemy spawns
        spawner.on_tick(0.5)
        assert len(spawner.spawned_enemies) == 2

        # After another delay: third enemy spawns
        spawner.on_tick(0.5)
        assert len(spawner.spawned_enemies) == 3

    def test_non_sequential_spawns_all_at_once(self):
        spawner = EnemySpawner()
        spawner.add_wave(WaveConfig(
            enemy_types=[(MeleeChaserArchetype(), 3)],
            sequential=False,
        ))
        spawner.start()

        spawner.on_tick(0.016)
        assert len(spawner.spawned_enemies) == 3

    def test_wave_clear_triggers_next_wave(self):
        spawner = EnemySpawner()
        spawner._wave_delay = 0.0  # No delay for testing
        spawner.add_wave(WaveConfig(
            enemy_types=[(MeleeChaserArchetype(), 1)],
            sequential=False,
        ))
        spawner.add_wave(WaveConfig(
            enemy_types=[(RangedKiterArchetype(), 1)],
            sequential=False,
        ))
        spawner.start()

        # First wave spawns immediately
        spawner.on_tick(0.016)
        assert len(spawner.spawned_enemies) == 1

        # Kill the first enemy
        from world.components.health_component import HealthComponent
        spawner.spawned_enemies[0].get_component(HealthComponent).take_damage(999.0)

        # Tick to detect wave clear
        spawner.on_tick(0.016)
        assert spawner.state == SpawnState.WAVE_CLEAR

        # Tick past wave delay
        spawner.on_tick(0.016)
        # Should advance to next wave
        assert spawner.current_wave_index == 1

    def test_all_clear_after_final_wave(self):
        spawner = EnemySpawner()
        spawner._wave_delay = 0.0
        spawner.add_wave(WaveConfig(
            enemy_types=[(MeleeChaserArchetype(), 1)],
            sequential=False,
        ))
        spawner.start()

        spawner.on_tick(0.016)
        from world.components.health_component import HealthComponent
        spawner.spawned_enemies[0].get_component(HealthComponent).take_damage(999.0)

        spawner.on_tick(0.016)  # Wave clear
        spawner.on_tick(0.016)  # Advance past waves

        assert spawner.state == SpawnState.ALL_CLEAR

    def test_start_with_no_waves_does_nothing(self):
        spawner = EnemySpawner()
        spawner.start()
        assert spawner.is_active is False


# ===========================================================================
# Test callbacks
# ===========================================================================

class TestCallbacks:
    def test_wave_clear_callback(self):
        spawner = EnemySpawner()
        spawner._wave_delay = 0.0
        results = []
        spawner.on_wave_clear(lambda idx: results.append(idx))

        spawner.add_wave(WaveConfig(
            enemy_types=[(MeleeChaserArchetype(), 1)],
            sequential=False,
        ))
        spawner.start()
        spawner.on_tick(0.016)

        from world.components.health_component import HealthComponent
        spawner.spawned_enemies[0].get_component(HealthComponent).take_damage(999.0)

        spawner.on_tick(0.016)
        assert len(results) == 1
        assert results[0] == 0

    def test_all_clear_callback(self):
        spawner = EnemySpawner()
        spawner._wave_delay = 0.0
        results = []
        spawner.on_all_clear(lambda: results.append("all_clear"))

        spawner.add_wave(WaveConfig(
            enemy_types=[(MeleeChaserArchetype(), 1)],
            sequential=False,
        ))
        spawner.start()
        spawner.on_tick(0.016)

        from world.components.health_component import HealthComponent
        spawner.spawned_enemies[0].get_component(HealthComponent).take_damage(999.0)

        spawner.on_tick(0.016)  # Wave clear
        spawner.on_tick(0.016)  # All clear

        assert len(results) == 1
        assert results[0] == "all_clear"

    def test_enemy_spawned_callback(self):
        spawner = EnemySpawner()
        spawned_list = []
        spawner.on_enemy_spawned(lambda e: spawned_list.append(e))

        wave = WaveConfig(
            enemy_types=[(MeleeChaserArchetype(), 2)],
            sequential=False,
        )
        spawner.add_wave(wave)
        spawner.spawn_wave(0)

        assert len(spawned_list) == 2

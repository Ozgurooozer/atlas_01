"""
Enemy Spawn System.

Manages wave-based enemy spawning for rooms/dungeons.
Creates actors with proper combat components and tracks wave state.

Layer: 4 (Game/AI)
Dependencies: core.object, world.actor, game.ai.archetypes, game.ai.enemy_ai
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional, TYPE_CHECKING

from core.object import Object
from core.vec import Vec2
from game.ai.archetypes import (
    AIArchetype,
)

if TYPE_CHECKING:
    from world.actor import Actor


class SpawnState(Enum):
    """Spawner state machine states."""
    IDLE = auto()
    SPAWNING = auto()
    WAITING = auto()
    WAVE_CLEAR = auto()
    ALL_CLEAR = auto()


@dataclass
class WaveConfig:
    """Configuration for a single enemy wave.

    Attributes:
        enemy_types: List of (AIArchetype, count) pairs.
        spawn_delay: Seconds between individual enemy spawns within the wave.
        spawn_points: Optional list of Vec2 positions to spawn at.
                     If empty, random positions are used around a center.
        sequential: If True, spawn enemies one at a time with delay.
                    If False, spawn all at once.
    """
    enemy_types: List[tuple] = field(default_factory=list)
    spawn_delay: float = 0.5
    spawn_points: List[Vec2] = field(default_factory=list)
    sequential: bool = True


class EnemySpawner(Object):
    """
    Manages enemy spawning in waves for a room/dungeon area.

    Creates Actor instances with all required combat components
    (HealthComponent, CombatantComponent, CombatStateComponent,
    HitboxComponent, HurtboxComponent, TransformComponent, ScriptComponent)
    and tracks wave completion state.

    Example::

        from game.ai.archetypes import MeleeChaserArchetype
        spawner = EnemySpawner()
        wave = WaveConfig(
            enemy_types=[(MeleeChaserArchetype(), 3)],
            spawn_delay=1.0,
        )
        spawner.add_wave(wave)
        spawner.start()
    """

    def __init__(
        self,
        center: Vec2 | None = None,
        spawn_radius: float = 200.0,
    ):
        super().__init__(name="EnemySpawner")
        self._waves: List[WaveConfig] = []
        self._current_wave_index: int = 0
        self._spawned_enemies: List[Actor] = []
        self._spawn_queue: List[tuple] = []  # (archetype, spawn_point)

        self._center = center or Vec2(0, 0)
        self._spawn_radius = spawn_radius

        # Timing
        self._spawn_timer: float = 0.0
        self._wave_delay: float = 2.0  # Delay between waves
        self._wave_clear_timer: float = 0.0

        # State
        self._state: SpawnState = SpawnState.IDLE
        self._is_active: bool = False

        # Callbacks
        self._on_wave_clear_callbacks: list = []
        self._on_all_clear_callbacks: list = []
        self._on_enemy_spawned_callbacks: list = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def state(self) -> SpawnState:
        return self._state

    @property
    def is_active(self) -> bool:
        return self._is_active

    @property
    def current_wave_index(self) -> int:
        return self._current_wave_index

    @property
    def spawned_enemies(self) -> List["Actor"]:
        return list(self._spawned_enemies)

    @property
    def alive_enemies(self) -> List["Actor"]:
        """Get enemies that are still alive."""
        from world.components.health_component import HealthComponent
        alive = []
        for enemy in self._spawned_enemies:
            health = enemy.get_component(HealthComponent)
            if health is not None and not health.is_dead:
                alive.append(enemy)
        return alive

    def add_wave(self, wave: WaveConfig) -> None:
        """Add a wave configuration."""
        self._waves.append(wave)

    def clear_waves(self) -> None:
        """Remove all wave configurations."""
        self._waves.clear()
        self._current_wave_index = 0

    def start(self) -> None:
        """Begin the spawning sequence."""
        if not self._waves:
            return
        self._is_active = True
        self._state = SpawnState.SPAWNING
        self._current_wave_index = 0
        self._spawned_enemies.clear()
        self._prepare_wave()

    def stop(self) -> None:
        """Stop spawning."""
        self._is_active = False
        self._state = SpawnState.IDLE
        self._spawn_queue.clear()

    def reset(self) -> None:
        """Reset the spawner to initial state."""
        self.stop()
        self._current_wave_index = 0
        self._spawned_enemies.clear()
        self._spawn_queue.clear()
        self._spawn_timer = 0.0
        self._wave_clear_timer = 0.0

    def spawn_wave(self, wave_index: int | None = None) -> List["Actor"]:
        """
        Immediately spawn all enemies in a wave.

        Args:
            wave_index: Wave to spawn. Defaults to current wave.

        Returns:
            List of spawned Actor instances.
        """
        if wave_index is None:
            wave_index = self._current_wave_index

        if wave_index >= len(self._waves):
            return []

        wave = self._waves[wave_index]
        spawned = []

        point_index = 0
        for archetype, count in wave.enemy_types:
            for i in range(count):
                if wave.spawn_points:
                    pos = wave.spawn_points[point_index % len(wave.spawn_points)]
                    point_index += 1
                else:
                    pos = self._random_spawn_point()
                actor = self._create_enemy(archetype, pos)
                spawned.append(actor)
                self._spawned_enemies.append(actor)
                self._notify_enemy_spawned(actor)

        return spawned

    def check_wave_clear(self) -> bool:
        """
        Check if all enemies in the current wave are dead.

        Returns:
            True if all enemies in the current wave are dead or no enemies remain.
        """
        from world.components.health_component import HealthComponent
        for enemy in self._spawned_enemies:
            health = enemy.get_component(HealthComponent)
            if health is not None and not health.is_dead:
                return False
        return True

    def check_all_waves_clear(self) -> bool:
        """Check if all waves have been spawned and cleared."""
        if self._current_wave_index < len(self._waves):
            return False
        return self.check_wave_clear()

    def on_wave_clear(self, callback) -> None:
        """Register callback for when a wave is cleared."""
        self._on_wave_clear_callbacks.append(callback)

    def on_all_clear(self, callback) -> None:
        """Register callback for when all waves are cleared."""
        self._on_all_clear_callbacks.append(callback)

    def on_enemy_spawned(self, callback) -> None:
        """Register callback for when an enemy is spawned."""
        self._on_enemy_spawned_callbacks.append(callback)

    # ------------------------------------------------------------------
    # Tick (for timed/sequential spawning)
    # ------------------------------------------------------------------

    def on_tick(self, dt: float) -> None:
        """Update the spawner each frame."""
        if not self._is_active:
            return

        if self._state == SpawnState.SPAWNING:
            self._tick_spawning(dt)
        elif self._state == SpawnState.WAITING:
            self._tick_waiting(dt)
        elif self._state == SpawnState.WAVE_CLEAR:
            self._tick_wave_clear(dt)

    # ------------------------------------------------------------------
    # Internal: Wave preparation
    # ------------------------------------------------------------------

    def _prepare_wave(self) -> None:
        """Build the spawn queue for the current wave."""
        if self._current_wave_index >= len(self._waves):
            self._state = SpawnState.ALL_CLEAR
            self._notify_all_clear()
            return

        wave = self._waves[self._current_wave_index]
        self._spawn_queue.clear()

        point_index = 0
        for archetype, count in wave.enemy_types:
            for i in range(count):
                if wave.spawn_points:
                    pos = wave.spawn_points[point_index % len(wave.spawn_points)]
                    point_index += 1
                else:
                    pos = self._random_spawn_point()
                self._spawn_queue.append((archetype, pos))

        self._spawn_timer = 0.0

        if not wave.sequential:
            # Spawn all immediately
            self._spawn_all_queued()
        else:
            self._state = SpawnState.SPAWNING

    def _random_spawn_point(self) -> Vec2:
        """Generate a random spawn point around the center."""
        angle = math.radians(len(self._spawned_enemies) * 137.5)  # golden angle
        radius = self._spawn_radius * (0.5 + 0.5 * ((len(self._spawned_enemies) * 7 + 3) % 10) / 10.0)
        x = self._center.x + math.cos(angle) * radius
        y = self._center.y + math.sin(angle) * radius
        return Vec2(x, y)

    # ------------------------------------------------------------------
    # Internal: Spawning
    # ------------------------------------------------------------------

    def _create_enemy(self, archetype: AIArchetype, position: Vec2 | None = None) -> "Actor":
        """
        Create a fully-equipped enemy actor.

        Attaches: TransformComponent, HealthComponent, CombatantComponent,
                  CombatStateComponent, HitboxComponent, HurtboxComponent.
        """
        from world.actor import Actor
        from world.transform import TransformComponent
        from world.components.health_component import HealthComponent
        from world.components.combatant_component import CombatantComponent
        from world.components.combat_state_component import CombatStateComponent
        from world.components.hitbox_component import HitboxComponent
        from world.components.hurtbox_component import HurtboxComponent

        enemy = Actor(name=f"Enemy_{archetype.name}")

        # Transform
        transform = TransformComponent()
        if position is not None:
            transform.position = (position.x, position.y)
        enemy.add_component(transform)

        # Health
        enemy.add_component(HealthComponent(max_hp=archetype.max_hp))

        # Combatant
        enemy.add_component(CombatantComponent(team=CombatantComponent.TEAM_ENEMY))

        # Combat state
        enemy.add_component(CombatStateComponent())

        # Hitbox
        enemy.add_component(HitboxComponent(
            width=40.0,
            height=40.0,
            damage=archetype.attack_damage,
        ))

        # Hurtbox
        enemy.add_component(HurtboxComponent(
            width=30.0,
            height=50.0,
        ))

        return enemy

    def _spawn_next(self) -> Optional["Actor"]:
        """Spawn the next enemy in the queue."""
        if not self._spawn_queue:
            return None

        archetype, pos = self._spawn_queue.pop(0)
        enemy = self._create_enemy(archetype, pos)
        self._spawned_enemies.append(enemy)
        self._notify_enemy_spawned(enemy)
        return enemy

    def _spawn_all_queued(self) -> None:
        """Spawn all enemies in the queue immediately."""
        while self._spawn_queue:
            self._spawn_next()

        self._state = SpawnState.WAITING
        self._wave_clear_timer = 0.0

    # ------------------------------------------------------------------
    # Internal: Tick handlers
    # ------------------------------------------------------------------

    def _tick_spawning(self, dt: float) -> None:
        """Handle sequential spawning."""
        if self._current_wave_index >= len(self._waves):
            self._prepare_wave()  # Will set ALL_CLEAR
            return

        wave = self._waves[self._current_wave_index]

        if not self._spawn_queue:
            # All enemies in this wave spawned
            self._state = SpawnState.WAITING
            self._wave_clear_timer = 0.0
            return

        self._spawn_timer += dt
        if self._spawn_timer >= wave.spawn_delay:
            self._spawn_timer = 0.0
            self._spawn_next()

    def _tick_waiting(self, dt: float) -> None:
        """Wait for the current wave to be cleared."""
        if self.check_wave_clear():
            self._state = SpawnState.WAVE_CLEAR
            self._wave_clear_timer = 0.0
            self._notify_wave_clear()
        else:
            self._wave_clear_timer += dt

    def _tick_wave_clear(self, dt: float) -> None:
        """Handle wave clear delay before next wave."""
        self._wave_clear_timer += dt
        if self._wave_clear_timer >= self._wave_delay:
            self._current_wave_index += 1
            if self._current_wave_index >= len(self._waves):
                self._state = SpawnState.ALL_CLEAR
                self._notify_all_clear()
            else:
                self._state = SpawnState.SPAWNING
                self._prepare_wave()

    # ------------------------------------------------------------------
    # Internal: Notifications
    # ------------------------------------------------------------------

    def _notify_wave_clear(self) -> None:
        for cb in self._on_wave_clear_callbacks:
            try:
                cb(self._current_wave_index)
            except Exception:
                pass

    def _notify_all_clear(self) -> None:
        for cb in self._on_all_clear_callbacks:
            try:
                cb()
            except Exception:
                pass

    def _notify_enemy_spawned(self, enemy: "Actor") -> None:
        for cb in self._on_enemy_spawned_callbacks:
            try:
                cb(enemy)
            except Exception:
                pass


__all__ = [
    "SpawnState",
    "WaveConfig",
    "EnemySpawner",
]

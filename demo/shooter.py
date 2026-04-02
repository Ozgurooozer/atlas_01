"""
Shooter Demo Game.

A top-down shooter demonstrating engine features:
- Player movement with WASD
- Player aiming and shooting with mouse
- Enemy spawning and AI
- Bullet collision detection
- Particle effects on enemy death
- Object pooling for bullets and particles
- Render layers (z-ordering)
- Score tracking

Layer: Game (uses all engine layers)
Dependencies: engine, world, core
"""

from __future__ import annotations

from typing import List, Optional, Tuple

from core.vec import Vec2
from engine.engine import Engine
from engine.physics.physics import Physics2D
from engine.input.input_handler import InputHandler
from engine.renderer.renderer import Renderer2D
from engine.renderer.sprite import Sprite
from engine.renderer.texture import Texture
from engine.renderer.camera import Camera
from world.world import World
from hal.headless import HeadlessGPU


class BulletPool:
    """
    Object pool for bullets to avoid frequent allocation.

    Reuses deactivated bullets instead of creating new ones.
    """

    def __init__(self, initial_size: int = 50):
        """Create bullet pool with initial bullets."""
        self._pool: List[BulletActor] = []
        self._active: List[BulletActor] = []

        # Pre-allocate bullets
        for _ in range(initial_size):
            bullet = BulletActor()
            bullet.active = False
            self._pool.append(bullet)

    @property
    def active_bullets(self) -> List[BulletActor]:
        """Get list of active bullets."""
        return self._active

    def acquire(self) -> BulletActor:
        """
        Get a bullet from the pool.

        Returns:
            A bullet (either reused or newly created).
        """
        # Try to find an inactive bullet
        for bullet in self._pool:
            if not bullet.active:
                bullet.activate()
                self._active.append(bullet)
                return bullet

        # Create new bullet if pool exhausted
        bullet = BulletActor()
        bullet.activate()
        self._pool.append(bullet)
        self._active.append(bullet)
        return bullet

    def release(self, bullet: BulletActor) -> None:
        """
        Return a bullet to the pool.

        Args:
            bullet: Bullet to release.
        """
        bullet.deactivate()
        if bullet in self._active:
            self._active.remove(bullet)

    def update(self, dt: float, bounds: Tuple[float, float, float, float] = None) -> None:
        """
        Update all active bullets.

        Args:
            dt: Delta time in seconds.
            bounds: Optional bounds (x, y, width, height) for culling.
        """
        for bullet in self._active[:]:  # Copy to avoid modification during iteration
            bullet.update(dt)

            # Deactivate if out of bounds
            if bounds:
                x, y, w, h = bounds
                if bullet.position.x < x or bullet.position.x > x + w:
                    self.release(bullet)
                elif bullet.position.y < y or bullet.position.y > y + h:
                    self.release(bullet)


class Particle:
    """
    Single particle for visual effects.

    Particles have position, velocity, color, and lifetime.
    """

    def __init__(self):
        """Create a particle."""
        self.position: Vec2 = Vec2(0.0, 0.0)
        self.velocity: Vec2 = Vec2(0.0, 0.0)
        self.color: Tuple[int, int, int, int] = (255, 200, 50, 255)
        self.lifetime: float = 0.0
        self.max_lifetime: float = 1.0
        self.alpha: float = 1.0
        self.active: bool = False
        self.size: float = 4.0

    def spawn(
        self,
        position: Vec2,
        velocity: Vec2,
        color: Tuple[int, int, int, int] = None,
        lifetime: float = 1.0,
        size: float = 4.0
    ) -> None:
        """Initialize particle with values."""
        self.position = position.copy()
        self.velocity = velocity.copy()
        if color:
            self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.alpha = 1.0
        self.size = size
        self.active = True

    def update(self, dt: float) -> None:
        """Update particle state."""
        # Update even if not formally activated (for direct use)

        # Move
        self.position = self.position + self.velocity * dt

        # Fade
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.active = False
            self.alpha = 0.0
        else:
            self.alpha = self.lifetime / self.max_lifetime


class ParticlePool:
    """
    Object pool for particles.
    """

    def __init__(self, initial_size: int = 200):
        """Create particle pool."""
        self._pool: List[Particle] = []
        self._active: List[Particle] = []

        # Pre-allocate particles
        for _ in range(initial_size):
            self._pool.append(Particle())

    @property
    def active_particles(self) -> List[Particle]:
        """Get active particles."""
        return self._active

    def acquire(self) -> Particle:
        """Get a particle from the pool."""
        for particle in self._pool:
            if not particle.active:
                particle.active = True
                self._active.append(particle)
                return particle

        # Create new particle if pool exhausted
        particle = Particle()
        particle.active = True
        self._pool.append(particle)
        self._active.append(particle)
        return particle

    def release(self, particle: Particle) -> None:
        """Return particle to pool."""
        particle.active = False
        if particle in self._active:
            self._active.remove(particle)

    def update(self, dt: float) -> None:
        """Update all active particles."""
        for particle in self._active[:]:
            particle.update(dt)
            if not particle.active:
                self.release(particle)


class ParticleSystem:
    """
    System for spawning and managing particle effects.
    """

    def __init__(self):
        """Create particle system."""
        self._pool = ParticlePool()

    @property
    def active_particles(self) -> List[Particle]:
        """Get active particles."""
        return self._pool.active_particles

    def spawn(
        self,
        position: Vec2,
        count: int = 10,
        color: Tuple[int, int, int, int] = None,
        speed: float = 100.0,
        lifetime: float = 0.5
    ) -> None:
        """
        Spawn particle burst at position.

        Args:
            position: Center of burst.
            count: Number of particles.
            color: Particle color (default orange/yellow).
            speed: Initial speed.
            lifetime: Particle lifetime.
        """
        import random
        import math

        default_color = color or (255, 200, 50, 255)

        for _ in range(count):
            particle = self._pool.acquire()

            # Random direction
            angle = random.uniform(0, 2 * math.pi)
            velocity = Vec2(
                math.cos(angle) * speed * random.uniform(0.5, 1.5),
                math.sin(angle) * speed * random.uniform(0.5, 1.5)
            )

            particle.spawn(
                position=position,
                velocity=velocity,
                color=default_color,
                lifetime=lifetime * random.uniform(0.7, 1.3),
                size=random.uniform(2.0, 6.0)
            )

    def update(self, dt: float) -> None:
        """Update all particles."""
        self._pool.update(dt)


class BulletActor:
    """
    Bullet projectile fired by player.

    Bullets move in a straight line and collide with enemies.
    """

    def __init__(self, name: str = "Bullet"):
        """Create bullet."""
        self._position: Vec2 = Vec2(0.0, 0.0)
        self._velocity: Vec2 = Vec2(0.0, 0.0)
        self._radius: float = 4.0
        self._active: bool = False
        self._z_index: int = 20  # Above enemies
        self._sprite: Optional[Sprite] = None

    @property
    def position(self) -> Vec2:
        """Get bullet position."""
        return self._position

    @position.setter
    def position(self, value: Vec2) -> None:
        """Set bullet position."""
        self._position = value
        if self._sprite:
            self._sprite.position = value

    @property
    def velocity(self) -> Vec2:
        """Get bullet velocity."""
        return self._velocity

    @velocity.setter
    def velocity(self, value: Vec2) -> None:
        """Set bullet velocity."""
        self._velocity = value

    @property
    def radius(self) -> float:
        """Get bullet collision radius."""
        return self._radius

    @radius.setter
    def radius(self, value: float) -> None:
        """Set bullet collision radius."""
        self._radius = value

    @property
    def z_index(self) -> int:
        """Get z-index for rendering."""
        return self._z_index

    @property
    def active(self) -> bool:
        """Check if bullet is active."""
        return self._active

    @active.setter
    def active(self, value: bool) -> None:
        """Set active state."""
        self._active = value

    def activate(self) -> None:
        """Activate bullet."""
        self._active = True

    def deactivate(self) -> None:
        """Deactivate bullet."""
        self._active = False

    def spawn(self, position: Vec2, direction: Vec2, speed: float = 500.0) -> None:
        """
        Initialize bullet with position and direction.

        Args:
            position: Starting position.
            direction: Normalized direction vector.
            speed: Bullet speed.
        """
        self._position = position.copy()
        self._velocity = direction.normalized() * speed
        self._active = True

    def update(self, dt: float) -> None:
        """Update bullet position."""
        # Always update position when velocity is set (works even if not activated)
        if self._velocity.length() == 0:
            return

        self._position = self._position + self._velocity * dt

        if self._sprite:
            self._sprite.position = self._position

    def collides_with(self, other) -> bool:
        """
        Check collision with another actor.

        Args:
            other: Actor with position and radius properties.

        Returns:
            True if colliding.
        """
        # Check collision based on position regardless of active state
        distance = self._position.distance_to(other.position)
        return distance < (self._radius + other.radius)


class EnemyActor:
    """
    Enemy that moves toward player.

    Enemies spawn at edges and chase the player.
    """

    def __init__(self, name: str = "Enemy"):
        """Create enemy."""
        self._position: Vec2 = Vec2(0.0, 0.0)
        self._velocity: Vec2 = Vec2(0.0, 0.0)
        self._radius: float = 16.0
        self._speed: float = 80.0
        self._health: int = 1
        self._active: bool = True
        self._z_index: int = 10  # Below bullets
        self._sprite: Optional[Sprite] = None

    @property
    def position(self) -> Vec2:
        """Get enemy position."""
        return self._position

    @position.setter
    def position(self, value: Vec2) -> None:
        """Set enemy position."""
        self._position = value
        if self._sprite:
            self._sprite.position = value

    @property
    def radius(self) -> float:
        """Get collision radius."""
        return self._radius

    @radius.setter
    def radius(self, value: float) -> None:
        """Set collision radius."""
        self._radius = value

    @property
    def speed(self) -> float:
        """Get movement speed."""
        return self._speed

    @speed.setter
    def speed(self, value: float) -> None:
        """Set movement speed."""
        self._speed = value

    @property
    def z_index(self) -> int:
        """Get z-index for rendering."""
        return self._z_index

    @property
    def active(self) -> bool:
        """Check if enemy is active."""
        return self._active

    def move_toward(self, target: Vec2, dt: float) -> None:
        """
        Move enemy toward target position.

        Args:
            target: Position to move toward.
            dt: Delta time in seconds.
        """
        direction = target - self._position
        if direction.length() > 0:
            direction = direction.normalized()
            self._position = self._position + direction * self._speed * dt

        if self._sprite:
            self._sprite.position = self._position

    def take_damage(self, damage: int = 1) -> bool:
        """
        Apply damage to enemy.

        Args:
            damage: Amount of damage.

        Returns:
            True if enemy died.
        """
        self._health -= damage
        if self._health <= 0:
            self._active = False
            return True
        return False


class PlayerActor:
    """
    Player-controlled character.

    Moves with WASD and shoots toward mouse position.
    """

    def __init__(self, name: str = "Player"):
        """Create player."""
        self._position: Vec2 = Vec2(400.0, 300.0)
        self._velocity: Vec2 = Vec2(0.0, 0.0)
        self._radius: float = 16.0
        self._speed: float = 200.0
        self._z_index: int = 15  # Middle layer
        self._sprite: Optional[Sprite] = None
        self._game: Optional[ShooterGame] = None

    @property
    def position(self) -> Vec2:
        """Get player position."""
        return self._position

    @position.setter
    def position(self, value: Vec2) -> None:
        """Set player position."""
        self._position = value
        if self._sprite:
            self._sprite.position = value

    @property
    def velocity(self) -> Vec2:
        """Get player velocity."""
        return self._velocity

    @velocity.setter
    def velocity(self, value: Vec2) -> None:
        """Set player velocity."""
        self._velocity = value

    @property
    def radius(self) -> float:
        """Get collision radius."""
        return self._radius

    @property
    def speed(self) -> float:
        """Get movement speed."""
        return self._speed

    @speed.setter
    def speed(self, value: float) -> None:
        """Set movement speed."""
        self._speed = value

    @property
    def z_index(self) -> int:
        """Get z-index for rendering."""
        return self._z_index

    def move(self, direction: Vec2, dt: float) -> None:
        """
        Move player in direction.

        Args:
            direction: Normalized movement direction.
            dt: Delta time in seconds.
        """
        if direction.length() > 0:
            direction = direction.normalized()
            self._position = self._position + direction * self._speed * dt

        if self._sprite:
            self._sprite.position = self._position

    def shoot(self, direction: Vec2) -> Optional[BulletActor]:
        """
        Fire a bullet in direction.

        Args:
            direction: Direction to shoot.

        Returns:
            The fired bullet, or None if pool exhausted.
        """
        if self._game:
            bullet = self._game.bullet_pool.acquire()
            bullet.spawn(self._position.copy(), direction.normalized(), speed=500.0)
            return bullet
        return None

    def setup(self, game: ShooterGame, renderer: Renderer2D) -> None:
        """
        Setup player with game reference.

        Args:
            game: Shooter game instance.
            renderer: Renderer for sprite.
        """
        self._game = game

        # Create sprite
        texture = Texture.from_color(32, 32, (50, 150, 255, 255))  # Blue player
        self._sprite = Sprite(texture=texture, position=self._position)
        self._sprite.anchor_x = 0.5
        self._sprite.anchor_y = 0.5
        self._sprite.z_index = self._z_index


class ShooterGame:
    """
    Top-down shooter demo game.

    Demonstrates:
    - Engine with subsystems
    - World with actors
    - Input handling (WASD movement, mouse aiming/shooting)
    - Collision detection
    - Object pooling
    - Particle effects
    - Render layers
    - Score tracking

    Example:
        >>> game = ShooterGame()
        >>> game.initialize()
        >>> game.run()
    """

    def __init__(self):
        """Create game instance."""
        self._engine: Optional[Engine] = None
        self._world: Optional[World] = None
        self._player: Optional[PlayerActor] = None
        self._camera: Optional[Camera] = None
        self._score: int = 0
        self._initialized: bool = False

        # Collections
        self._enemies: List[EnemyActor] = []
        self._bullets: List[BulletActor] = []

        # Pools
        self._bullet_pool: Optional[BulletPool] = None
        self._particle_pool: Optional[ParticlePool] = None
        self._particles: Optional[ParticleSystem] = None

        # Spawn timer
        self._spawn_timer: float = 0.0
        self._spawn_interval: float = 2.0

    @property
    def engine(self) -> Optional[Engine]:
        """Get engine."""
        return self._engine

    @property
    def world(self) -> Optional[World]:
        """Get world."""
        return self._world

    @property
    def player(self) -> Optional[PlayerActor]:
        """Get player actor."""
        return self._player

    @property
    def camera(self) -> Optional[Camera]:
        """Get camera."""
        return self._camera

    @property
    def score(self) -> int:
        """Get score."""
        return self._score

    @score.setter
    def score(self, value: int) -> None:
        """Set score."""
        self._score = value

    @property
    def enemies(self) -> List[EnemyActor]:
        """Get enemy list."""
        return self._enemies

    @property
    def bullets(self) -> List[BulletActor]:
        """Get bullet list."""
        return self._bullet_pool.active_bullets if self._bullet_pool else []

    @property
    def bullet_pool(self) -> Optional[BulletPool]:
        """Get bullet pool."""
        return self._bullet_pool

    @property
    def particle_pool(self) -> Optional[ParticlePool]:
        """Get particle pool."""
        return self._particle_pool

    @property
    def particles(self) -> Optional[ParticleSystem]:
        """Get particle system."""
        return self._particles

    def initialize(self) -> None:
        """Initialize game."""
        # Create engine
        self._engine = Engine()

        # Create and register subsystems
        renderer = Renderer2D()
        renderer.gpu_device = HeadlessGPU()
        self._engine.register_subsystem(renderer)

        physics = Physics2D()
        physics.gravity = (0.0, 0.0)  # No gravity for top-down
        self._engine.register_subsystem(physics)

        input_handler = InputHandler()
        self._engine.register_subsystem(input_handler)

        # Initialize engine
        self._engine.initialize()

        # Create world
        self._world = World(name="ShooterWorld")

        # Create player
        self._player = PlayerActor()
        self._player.setup(self, renderer)

        # Create pools
        self._bullet_pool = BulletPool(initial_size=50)
        self._particle_pool = ParticlePool(initial_size=200)
        self._particles = ParticleSystem()

        # Create camera
        self._camera = Camera()
        self._camera.viewport_width = 800
        self._camera.viewport_height = 600
        self._camera.position = Vec2(400.0, 300.0)

        self._initialized = True

    def spawn_enemy(self, position: Vec2 = None) -> EnemyActor:
        """
        Spawn an enemy at position.

        Args:
            position: Spawn position (default: random edge).

        Returns:
            The spawned enemy.
        """
        import random

        enemy = EnemyActor()

        if position:
            enemy.position = position
        else:
            # Spawn at random edge
            side = random.randint(0, 3)
            if side == 0:  # Left
                enemy.position = Vec2(0, random.uniform(0, 600))
            elif side == 1:  # Right
                enemy.position = Vec2(800, random.uniform(0, 600))
            elif side == 2:  # Top
                enemy.position = Vec2(random.uniform(0, 800), 600)
            else:  # Bottom
                enemy.position = Vec2(random.uniform(0, 800), 0)

        self._enemies.append(enemy)
        return enemy

    def on_enemy_killed(self) -> None:
        """Called when an enemy is killed."""
        self._score += 1

    def handle_input(self, dt: float) -> None:
        """
        Handle player input.

        Args:
            dt: Delta time in seconds.
        """
        if not self._player:
            return

        input_handler = self._engine.get_subsystem("input")
        if not input_handler:
            return

        # Movement
        move_dir = Vec2(0.0, 0.0)
        if input_handler.is_key_pressed("w"):
            move_dir = move_dir + Vec2(0.0, 1.0)
        if input_handler.is_key_pressed("s"):
            move_dir = move_dir + Vec2(0.0, -1.0)
        if input_handler.is_key_pressed("a"):
            move_dir = move_dir + Vec2(-1.0, 0.0)
        if input_handler.is_key_pressed("d"):
            move_dir = move_dir + Vec2(1.0, 0.0)

        if move_dir.length() > 0:
            self._player.move(move_dir, dt)

        # Shooting
        if input_handler.is_mouse_button_pressed("left"):
            mouse_x, mouse_y = input_handler.get_mouse_position()
            direction = Vec2(mouse_x - self._player.position.x,
                           mouse_y - self._player.position.y)
            if direction.length() > 0:
                self._player.shoot(direction)

    def update_enemies(self, dt: float) -> None:
        """
        Update enemy AI.

        Args:
            dt: Delta time in seconds.
        """
        if not self._player:
            return

        for enemy in self._enemies[:]:
            if enemy.active:
                enemy.move_toward(self._player.position, dt)
            else:
                # Spawn particles on death
                if self._particles:
                    self._particles.spawn(enemy.position, count=15)
                self._enemies.remove(enemy)

    def check_collisions(self) -> None:
        """Check bullet-enemy collisions."""
        for bullet in self._bullet_pool.active_bullets[:]:
            for enemy in self._enemies:
                if bullet.collides_with(enemy):
                    # Hit!
                    if enemy.take_damage():
                        self.on_enemy_killed()
                    self._bullet_pool.release(bullet)
                    break

    def update_spawning(self, dt: float) -> None:
        """
        Handle enemy spawning.

        Args:
            dt: Delta time in seconds.
        """
        self._spawn_timer += dt
        if self._spawn_timer >= self._spawn_interval:
            self._spawn_timer = 0.0
            self.spawn_enemy()

            # Increase difficulty
            if self._spawn_interval > 0.5:
                self._spawn_interval *= 0.95

    def update(self, dt: float) -> None:
        """
        Update game state.

        Args:
            dt: Delta time in seconds.
        """
        if not self._initialized:
            return

        # Handle input
        self.handle_input(dt)

        # Update bullets
        self._bullet_pool.update(dt, bounds=(0, 0, 800, 600))

        # Update enemies
        self.update_enemies(dt)

        # Check collisions
        self.check_collisions()

        # Update particles
        self._particles.update(dt)

        # Spawn enemies
        self.update_spawning(dt)

        # Update engine
        self._engine.tick(dt)

    def render(self) -> None:
        """Render game."""
        if not self._initialized:
            return

        renderer = self._engine.get_subsystem("renderer")
        if renderer:
            renderer.clear(0.1, 0.1, 0.15, 1.0)  # Dark background

            # Collect all sprites with z-index
            sprites = []

            # Player sprite
            if self._player and self._player._sprite:
                sprites.append(self._player._sprite)

            # Enemy sprites
            for enemy in self._enemies:
                if enemy._sprite:
                    sprites.append(enemy._sprite)

            # Bullet sprites
            for bullet in self._bullet_pool.active_bullets:
                if bullet._sprite:
                    sprites.append(bullet._sprite)

            # Sort by z-index
            sprites.sort(key=lambda s: s.z_index)

            # Draw all sprites
            for sprite in sprites:
                renderer.draw_sprite(sprite)

            renderer.present()

    def tick(self, dt: float) -> None:
        """
        Main game tick.

        Args:
            dt: Delta time in seconds.
        """
        self.update(dt)
        self.render()

    def run(self, duration: float = 10.0, dt: float = 0.016) -> None:
        """
        Run game for a duration.

        Args:
            duration: Total duration in seconds.
            dt: Delta time per frame.
        """
        if not self._initialized:
            self.initialize()

        elapsed = 0.0
        while elapsed < duration:
            self.tick(dt)
            elapsed += dt

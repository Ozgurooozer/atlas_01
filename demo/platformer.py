"""
Platformer Demo Game.

A platformer game demonstrating engine features:
- Player movement (walk left/right, jump)
- Platform collision (static and moving)
- Camera follow
- Collectible coins
- Score tracking

Layer: Game (uses all engine layers)
Dependencies: engine, world, core
"""

from __future__ import annotations

from typing import List, Optional

from core.vec import Vec2
from engine.engine import Engine
from engine.physics.physics import Physics2D
from engine.input.input_handler import InputHandler
from engine.renderer.renderer import Renderer2D
from engine.renderer.sprite import Sprite
from engine.renderer.texture import Texture
from engine.renderer.camera import Camera
from world.world import World
from world.actor import Actor
from world.component import Component
from hal.headless import HeadlessGPU, HeadlessWindow


class PlayerActor(Actor):
    """
    Player actor with movement, jumping, and physics.

    Demonstrates:
    - Actor-Component pattern
    - Movement mechanics
    - Jump with gravity
    - Collision with platforms
    """

    # Movement constants
    MOVE_SPEED = 200.0  # pixels per second
    JUMP_FORCE = 400.0  # initial jump velocity
    GRAVITY = -900.0    # gravity acceleration

    def __init__(self, name: str = "Player"):
        """Create player actor."""
        super().__init__(name)
        self._position: Vec2 = Vec2(400.0, 300.0)
        self._velocity: Vec2 = Vec2(0.0, 0.0)
        self._sprite: Optional[Sprite] = None
        self._body_id: Optional[int] = None
        self._physics: Optional[Physics2D] = None
        self._on_ground: bool = False
        self._width: float = 32.0
        self._height: float = 48.0

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
    def sprite(self) -> Optional[Sprite]:
        """Get player sprite."""
        return self._sprite

    @property
    def body_id(self) -> Optional[int]:
        """Get physics body ID."""
        return self._body_id

    @property
    def on_ground(self) -> bool:
        """Check if player is on ground."""
        return self._on_ground

    @on_ground.setter
    def on_ground(self, value: bool) -> None:
        """Set on ground state."""
        self._on_ground = value

    @property
    def bounds(self) -> tuple:
        """Get player bounding box (left, bottom, right, top)."""
        half_w = self._width / 2
        half_h = self._height / 2
        return (
            self._position.x - half_w,
            self._position.y - half_h,
            self._position.x + half_w,
            self._position.y + half_h
        )

    def setup(
        self,
        physics: Physics2D,
        renderer: Renderer2D,
        position: Vec2 = None
    ) -> None:
        """
        Setup player with physics and renderer.

        Args:
            physics: Physics subsystem.
            renderer: Renderer subsystem.
            position: Initial position.
        """
        self._physics = physics
        self._position = position or Vec2(400.0, 300.0)

        # Create physics body
        self._body_id = physics.create_body(mass=1.0, moment=100.0)
        physics.set_body_position(self._body_id, self._position.x, self._position.y)
        physics.set_body_velocity(self._body_id, 0.0, 0.0)

        # Create sprite (solid color texture - blue player)
        texture = Texture.from_color(32, 48, (100, 150, 255, 255))
        self._sprite = Sprite(texture=texture, position=self._position)
        self._sprite.anchor_x = 0.5
        self._sprite.anchor_y = 0.5

    def move_left(self) -> None:
        """Start moving left."""
        self._velocity = Vec2(-self.MOVE_SPEED, self._velocity.y)

    def move_right(self) -> None:
        """Start moving right."""
        self._velocity = Vec2(self.MOVE_SPEED, self._velocity.y)

    def stop_horizontal(self) -> None:
        """Stop horizontal movement."""
        self._velocity = Vec2(0.0, self._velocity.y)

    def jump(self) -> bool:
        """
        Make player jump.

        Returns:
            True if jump was successful.
        """
        if self._on_ground:
            self._velocity = Vec2(self._velocity.x, self.JUMP_FORCE)
            self._on_ground = False
            return True
        return False

    def apply_gravity(self, dt: float) -> None:
        """
        Apply gravity to player.

        Args:
            dt: Delta time in seconds.
        """
        self._velocity = Vec2(
            self._velocity.x,
            self._velocity.y + self.GRAVITY * dt
        )

    def update(self, dt: float) -> None:
        """
        Update player position.

        Args:
            dt: Delta time in seconds.
        """
        # Update position from velocity
        self._position = Vec2(
            self._position.x + self._velocity.x * dt,
            self._position.y + self._velocity.y * dt
        )

        # Update sprite position
        if self._sprite:
            self._sprite.position = self._position

        # Sync physics body
        if self._physics and self._body_id:
            self._physics.set_body_position(
                self._body_id,
                self._position.x,
                self._position.y
            )
            self._physics.set_body_velocity(
                self._body_id,
                self._velocity.x,
                self._velocity.y
            )


class Platform(Actor):
    """
    Static platform actor.

    Demonstrates static collision geometry.
    """

    def __init__(
        self,
        name: str = "Platform",
        position: Vec2 = None,
        size: Vec2 = None
    ):
        """Create platform actor."""
        super().__init__(name)
        self._position = position or Vec2(400.0, 100.0)
        self._size = size or Vec2(200.0, 32.0)
        self._sprite: Optional[Sprite] = None

    @property
    def position(self) -> Vec2:
        """Get platform position (center)."""
        return self._position

    @position.setter
    def position(self, value: Vec2) -> None:
        """Set platform position."""
        self._position = value
        if self._sprite:
            self._sprite.position = value

    @property
    def size(self) -> Vec2:
        """Get platform size."""
        return self._size

    @property
    def bounds(self) -> tuple:
        """Get platform bounding box (left, bottom, right, top)."""
        half_w = self._size.x / 2
        half_h = self._size.y / 2
        return (
            self._position.x - half_w,
            self._position.y - half_h,
            self._position.x + half_w,
            self._position.y + half_h
        )

    def setup(self, renderer: Renderer2D) -> None:
        """
        Setup platform with renderer.

        Args:
            renderer: Renderer subsystem.
        """
        # Create platform sprite (green/brown color)
        texture = Texture.from_color(
            int(self._size.x),
            int(self._size.y),
            (100, 80, 60, 255)  # Brown color
        )
        self._sprite = Sprite(texture=texture, position=self._position)
        self._sprite.anchor_x = 0.5
        self._sprite.anchor_y = 0.5

    def update(self, dt: float) -> None:
        """
        Update platform (static, so no-op).

        Args:
            dt: Delta time in seconds.
        """
        pass


class MovingPlatform(Platform):
    """
    Moving platform actor.

    Demonstrates moving collision geometry.
    Moves back and forth between two points.
    """

    def __init__(
        self,
        name: str = "MovingPlatform",
        position: Vec2 = None,
        size: Vec2 = None,
        start_pos: Vec2 = None,
        end_pos: Vec2 = None,
        speed: float = 100.0
    ):
        """Create moving platform actor."""
        super().__init__(name, position, size)
        self._start_pos = start_pos or (position or Vec2(100.0, 100.0))
        self._end_pos = end_pos or Vec2(300.0, 100.0)
        self._speed = speed
        self._direction = 1  # 1 = toward end, -1 = toward start
        self._progress = 0.0  # 0 = at start, 1 = at end

    @property
    def start_pos(self) -> Vec2:
        """Get start position."""
        return self._start_pos

    @property
    def end_pos(self) -> Vec2:
        """Get end position."""
        return self._end_pos

    def update(self, dt: float) -> None:
        """
        Update moving platform position.

        Args:
            dt: Delta time in seconds.
        """
        # Calculate movement
        distance = self._start_pos.distance_to(self._end_pos)
        if distance > 0:
            move_amount = (self._speed * dt) / distance
            self._progress += move_amount * self._direction

            # Reverse direction at endpoints
            if self._progress >= 1.0:
                self._progress = 1.0
                self._direction = -1
            elif self._progress <= 0.0:
                self._progress = 0.0
                self._direction = 1

            # Interpolate position
            self._position = self._start_pos.lerp(self._end_pos, self._progress)

            # Update sprite
            if self._sprite:
                self._sprite.position = self._position


class Coin(Actor):
    """
    Collectible coin actor.

    Demonstrates collectible items.
    """

    def __init__(
        self,
        name: str = "Coin",
        position: Vec2 = None
    ):
        """Create coin actor."""
        super().__init__(name)
        self._position = position or Vec2(100.0, 100.0)
        self._sprite: Optional[Sprite] = None
        self._collected: bool = False
        self._radius: float = 12.0

    @property
    def position(self) -> Vec2:
        """Get coin position."""
        return self._position

    @position.setter
    def position(self, value: Vec2) -> None:
        """Set coin position."""
        self._position = value
        if self._sprite:
            self._sprite.position = value

    @property
    def collected(self) -> bool:
        """Check if coin is collected."""
        return self._collected

    @property
    def radius(self) -> float:
        """Get coin collision radius."""
        return self._radius

    def setup(self, renderer: Renderer2D) -> None:
        """
        Setup coin with renderer.

        Args:
            renderer: Renderer subsystem.
        """
        # Create coin sprite (yellow/gold color)
        texture = Texture.from_color(24, 24, (255, 215, 0, 255))  # Gold
        self._sprite = Sprite(texture=texture, position=self._position)
        self._sprite.anchor_x = 0.5
        self._sprite.anchor_y = 0.5

    def collect(self) -> bool:
        """
        Collect this coin.

        Returns:
            True if coin was collected (first time).
        """
        if not self._collected:
            self._collected = True
            if self._sprite:
                self._sprite.visible = False
            return True
        return False

    def overlaps_point(self, point: Vec2) -> bool:
        """
        Check if point is within coin radius.

        Args:
            point: Point to check.

        Returns:
            True if point overlaps coin.
        """
        distance = self._position.distance_to(point)
        return distance < self._radius


class PlatformerGame:
    """
    Platformer demo game.

    Demonstrates full engine integration:
    - Engine with subsystems
    - World with actors
    - Physics simulation
    - Input handling
    - Sprite rendering
    - Camera system
    - Collision detection
    - Collectibles and scoring

    Example:
        >>> game = PlatformerGame()
        >>> game.initialize()
        >>> game.run()
    """

    def __init__(self):
        """Create game instance."""
        self._engine: Optional[Engine] = None
        self._world: Optional[World] = None
        self._player: Optional[PlayerActor] = None
        self._platforms: List[Platform] = []
        self._coins: List[Coin] = []
        self._camera: Optional[Camera] = None
        self._score: int = 0
        self._initialized: bool = False

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
    def platforms(self) -> List[Platform]:
        """Get platforms list."""
        return self._platforms

    @property
    def coins(self) -> List[Coin]:
        """Get coins list."""
        return self._coins

    @coins.setter
    def coins(self, value: List[Coin]) -> None:
        """Set coins list."""
        self._coins = value

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

    def initialize(self) -> None:
        """Initialize game."""
        # Create engine
        self._engine = Engine()

        # Create and register subsystems
        renderer = Renderer2D()
        renderer.gpu_device = HeadlessGPU()
        self._engine.register_subsystem(renderer)

        physics = Physics2D()
        physics.gravity = (0.0, -900.0)
        self._engine.register_subsystem(physics)

        input_handler = InputHandler()
        self._engine.register_subsystem(input_handler)

        # Initialize engine
        self._engine.initialize()

        # Create world
        self._world = World(name="PlatformerWorld")

        # Create player
        self._player = PlayerActor()
        self._player.setup(physics, renderer, Vec2(400.0, 300.0))
        self._world.spawn_actor(self._player)

        # Create platforms
        self._create_platforms(renderer)

        # Create coins
        self._create_coins(renderer)

        # Create camera
        self._camera = Camera()
        self._camera.viewport_width = 800
        self._camera.viewport_height = 600
        self._camera.position = Vec2(400.0, 300.0)
        self._camera.follow_target = self._player
        self._camera.follow_speed = 0.1  # Smooth follow

        self._initialized = True

    def _create_platforms(self, renderer: Renderer2D) -> None:
        """Create level platforms."""
        # Ground platform
        ground = Platform(
            name="Ground",
            position=Vec2(400.0, 50.0),
            size=Vec2(800.0, 32.0)
        )
        ground.setup(renderer)
        self._platforms.append(ground)
        self._world.spawn_actor(ground)

        # Static platforms
        platforms_data = [
            (Vec2(200.0, 150.0), Vec2(150.0, 24.0)),
            (Vec2(500.0, 200.0), Vec2(150.0, 24.0)),
            (Vec2(350.0, 280.0), Vec2(200.0, 24.0)),
            (Vec2(150.0, 350.0), Vec2(120.0, 24.0)),
            (Vec2(600.0, 350.0), Vec2(120.0, 24.0)),
        ]

        for i, (pos, size) in enumerate(platforms_data):
            platform = Platform(name=f"Platform{i}", position=pos, size=size)
            platform.setup(renderer)
            self._platforms.append(platform)
            self._world.spawn_actor(platform)

        # Moving platform
        moving = MovingPlatform(
            name="MovingPlatform",
            position=Vec2(300.0, 420.0),
            size=Vec2(100.0, 20.0),
            start_pos=Vec2(200.0, 420.0),
            end_pos=Vec2(500.0, 420.0),
            speed=80.0
        )
        moving.setup(renderer)
        self._platforms.append(moving)
        self._world.spawn_actor(moving)

    def _create_coins(self, renderer: Renderer2D) -> None:
        """Create collectible coins."""
        coins_data = [
            Vec2(200.0, 200.0),
            Vec2(500.0, 250.0),
            Vec2(350.0, 330.0),
            Vec2(150.0, 400.0),
            Vec2(600.0, 400.0),
        ]

        for i, pos in enumerate(coins_data):
            coin = Coin(name=f"Coin{i}", position=pos)
            coin.setup(renderer)
            self._coins.append(coin)
            self._world.spawn_actor(coin)

    def handle_input(self, key: str) -> None:
        """
        Handle input.

        Args:
            key: Key pressed.
        """
        if key == "SPACE" or key == "UP":
            self._player.jump()
        elif key == "LEFT":
            self._player.move_left()
        elif key == "RIGHT":
            self._player.move_right()

    def check_platform_collisions(self, dt: float) -> None:
        """
        Check and handle platform collisions.

        Args:
            dt: Delta time in seconds.
        """
        if self._player is None:
            return

        player_bounds = self._player.bounds
        player_left, player_bottom, player_right, player_top = player_bounds

        # Reset ground state - only reset if player is falling
        # (not when they have upward velocity from jumping)
        if self._player.velocity.y <= 0:
            self._player.on_ground = False

        for platform in self._platforms:
            plat_bounds = platform.bounds
            plat_left, plat_bottom, plat_right, plat_top = plat_bounds

            # Check AABB overlap
            if (player_left < plat_right and
                player_right > plat_left and
                player_bottom < plat_top and
                player_top > plat_bottom):

                # Determine collision side
                # Calculate overlap on each axis
                overlap_left = player_right - plat_left
                overlap_right = plat_right - player_left
                overlap_bottom = player_top - plat_bottom
                overlap_top = plat_top - player_bottom

                # Find minimum overlap
                min_overlap_x = min(overlap_left, overlap_right)
                min_overlap_y = min(overlap_bottom, overlap_top)

                if min_overlap_y < min_overlap_x:
                    # Vertical collision
                    if overlap_top < overlap_bottom:
                        # Player landing on platform
                        self._player.position = Vec2(
                            self._player.position.x,
                            plat_top + self._player._height / 2
                        )
                        self._player.velocity = Vec2(
                            self._player.velocity.x,
                            max(0, self._player.velocity.y)  # Stop falling
                        )
                        self._player.on_ground = True
                    else:
                        # Player hitting platform from below
                        self._player.position = Vec2(
                            self._player.position.x,
                            plat_bottom - self._player._height / 2
                        )
                        self._player.velocity = Vec2(
                            self._player.velocity.x,
                            min(0, self._player.velocity.y)
                        )
                else:
                    # Horizontal collision
                    if overlap_left < overlap_right:
                        self._player.position = Vec2(
                            plat_left - self._player._width / 2,
                            self._player.position.y
                        )
                    else:
                        self._player.position = Vec2(
                            plat_right + self._player._width / 2,
                            self._player.position.y
                        )

    def check_coin_collisions(self) -> None:
        """Check and handle coin collisions."""
        if self._player is None:
            return

        player_pos = self._player.position

        for coin in self._coins:
            if not coin.collected:
                if coin.overlaps_point(player_pos):
                    if coin.collect():
                        self._score += 1

    def update(self, dt: float) -> None:
        """
        Update game state.

        Args:
            dt: Delta time in seconds.
        """
        if not self._initialized:
            return

        # Apply gravity
        self._player.apply_gravity(dt)

        # Update player
        self._player.update(dt)

        # Update platforms
        for platform in self._platforms:
            platform.update(dt)

        # Check collisions
        self.check_platform_collisions(dt)
        self.check_coin_collisions()

        # Update camera
        self._camera.update(dt)

        # Update world
        self._world.tick(dt)

    def render(self) -> None:
        """Render game."""
        if not self._initialized:
            return

        renderer = self._engine.get_subsystem("renderer")
        if renderer:
            renderer.clear(0.2, 0.3, 0.5, 1.0)  # Blue sky background

            # Draw platforms
            for platform in self._platforms:
                if platform._sprite:
                    renderer.draw_sprite(platform._sprite)

            # Draw coins
            for coin in self._coins:
                if coin._sprite and not coin.collected:
                    renderer.draw_sprite(coin._sprite)

            # Draw player
            if self._player and self._player._sprite:
                renderer.draw_sprite(self._player._sprite)

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
        import time

        if not self._initialized:
            self.initialize()

        elapsed = 0.0
        while elapsed < duration:
            self.tick(dt)
            elapsed += dt

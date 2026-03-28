"""
Bouncing Ball Demo Game.

A simple game demonstrating engine integration:
- Sprite rendering
- Physics simulation
- Input handling
- Camera system

Layer: Game (uses all engine layers)
Dependencies: engine, world, core
"""

from __future__ import annotations

from typing import Optional

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


class BallActor(Actor):
    """
    Ball actor with physics and sprite.

    Demonstrates:
    - Actor-Component pattern
    - Physics integration
    - Sprite rendering
    """

    def __init__(self, name: str = "Ball"):
        """Create ball actor."""
        super().__init__(name)
        self._velocity: Vec2 = Vec2(0.0, 0.0)
        self._sprite: Optional[Sprite] = None
        self._body_id: Optional[int] = None
        self._physics: Optional[Physics2D] = None
        self._on_ground: bool = False

    @property
    def position(self) -> Vec2:
        """Get ball position."""
        return self._position if hasattr(self, '_position') else Vec2(0.0, 0.0)

    @position.setter
    def position(self, value: Vec2) -> None:
        """Set ball position."""
        self._position = value
        if self._sprite:
            self._sprite.position = value

    @property
    def velocity(self) -> Vec2:
        """Get ball velocity."""
        return self._velocity

    @velocity.setter
    def velocity(self, value: Vec2) -> None:
        """Set ball velocity."""
        self._velocity = value

    @property
    def sprite(self) -> Optional[Sprite]:
        """Get ball sprite."""
        return self._sprite

    @property
    def body_id(self) -> Optional[int]:
        """Get physics body ID."""
        return self._body_id

    @property
    def on_ground(self) -> bool:
        """Check if ball is on ground."""
        return self._on_ground

    def setup(
        self,
        physics: Physics2D,
        renderer: Renderer2D,
        position: Vec2 = None
    ) -> None:
        """
        Setup ball with physics and renderer.

        Args:
            physics: Physics subsystem.
            renderer: Renderer subsystem.
            position: Initial position.
        """
        self._physics = physics
        self._position = position or Vec2(100.0, 300.0)

        # Create physics body
        self._body_id = physics.create_body(mass=1.0, moment=100.0)
        physics.set_body_position(self._body_id, self._position.x, self._position.y)
        physics.set_body_velocity(self._body_id, 0.0, 0.0)

        # Create sprite (solid color texture)
        texture = Texture.from_color(32, 32, (255, 100, 100, 255))  # Red ball
        self._sprite = Sprite(texture=texture, position=self._position)
        self._sprite.anchor_x = 0.5
        self._sprite.anchor_y = 0.5

    def jump(self) -> bool:
        """
        Make ball jump.

        Returns:
            True if jump was successful.
        """
        if self._on_ground or self._velocity.y >= 0:
            self._velocity = Vec2(self._velocity.x, 300.0)  # Jump force
            self._on_ground = False
            return True
        return False

    def apply_gravity(self, dt: float) -> None:
        """
        Apply gravity to ball.

        Args:
            dt: Delta time in seconds.
        """
        gravity = -500.0  # Gravity force
        self._velocity = Vec2(
            self._velocity.x,
            self._velocity.y + gravity * dt
        )

    def update(self, dt: float) -> None:
        """
        Update ball position.

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


class GroundActor(Actor):
    """
    Ground actor for collision.

    Demonstrates static collision geometry.
    """

    def __init__(self, name: str = "Ground"):
        """Create ground actor."""
        super().__init__(name)
        self._y: float = 50.0  # Ground Y position
        self._sprite: Optional[Sprite] = None

    @property
    def y(self) -> float:
        """Get ground Y position."""
        return self._y

    def setup(self, renderer: Renderer2D, width: int = 800) -> None:
        """
        Setup ground with renderer.

        Args:
            renderer: Renderer subsystem.
            width: Screen width.
        """
        # Create ground sprite (green rectangle)
        texture = Texture.from_color(width, 50, (50, 150, 50, 255))  # Green ground
        self._sprite = Sprite(texture=texture, position=Vec2(width / 2, 25))
        self._sprite.anchor_x = 0.5
        self._sprite.anchor_y = 0.5


class BouncingBallGame:
    """
    Bouncing Ball demo game.

    Demonstrates full engine integration:
    - Engine with subsystems
    - World with actors
    - Physics simulation
    - Input handling
    - Sprite rendering
    - Camera system

    Example:
        >>> game = BouncingBallGame()
        >>> game.initialize()
        >>> game.run()
    """

    def __init__(self):
        """Create game instance."""
        self._engine: Optional[Engine] = None
        self._world: Optional[World] = None
        self._ball: Optional[BallActor] = None
        self._ground: Optional[GroundActor] = None
        self._camera: Optional[Camera] = None
        self._score: int = 0
        self._ground_y: float = 50.0
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
    def ball(self) -> Optional[BallActor]:
        """Get ball actor."""
        return self._ball

    @property
    def ground(self) -> Optional[GroundActor]:
        """Get ground actor."""
        return self._ground

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
    def ground_y(self) -> float:
        """Get ground Y position."""
        return self._ground_y

    def initialize(self) -> None:
        """Initialize game."""
        # Create engine
        self._engine = Engine()

        # Create and register subsystems
        renderer = Renderer2D()
        renderer.gpu_device = HeadlessGPU()
        self._engine.register_subsystem(renderer)

        physics = Physics2D()
        physics.gravity = (0.0, -500.0)
        self._engine.register_subsystem(physics)

        input_handler = InputHandler()
        self._engine.register_subsystem(input_handler)

        # Initialize engine
        self._engine.initialize()

        # Create world
        self._world = World(name="GameWorld")

        # Create ball
        self._ball = BallActor()
        self._ball.setup(physics, renderer, Vec2(400.0, 300.0))
        self._world.spawn_actor(self._ball)

        # Create ground
        self._ground = GroundActor()
        self._ground.setup(renderer, width=800)
        self._world.spawn_actor(self._ground)

        # Create camera
        self._camera = Camera()
        self._camera.viewport_width = 800
        self._camera.viewport_height = 600
        self._camera.position = Vec2(400.0, 300.0)

        self._initialized = True

    def handle_input(self, key: str) -> None:
        """
        Handle input.

        Args:
            key: Key pressed.
        """
        if key == "SPACE":
            if self._ball.jump():
                self._score += 1

    def check_ground_collision(self) -> None:
        """Check and handle ground collision."""
        if self._ball is None:
            return

        ball_radius = 16.0  # Half of 32

        # Check if ball hits ground
        if self._ball.position.y - ball_radius <= self._ground_y:
            # Place ball on ground
            self._ball._position = Vec2(
                self._ball.position.x,
                self._ground_y + ball_radius
            )

            # Bounce (reverse velocity with some energy loss)
            if self._ball.velocity.y < 0:
                bounce_factor = 0.7  # Energy loss on bounce
                self._ball.velocity = Vec2(
                    self._ball.velocity.x,
                    -self._ball.velocity.y * bounce_factor
                )

            self._ball._on_ground = True
        else:
            self._ball._on_ground = False

    def update(self, dt: float) -> None:
        """
        Update game state.

        Args:
            dt: Delta time in seconds.
        """
        if not self._initialized:
            return

        # Update ball physics
        self._ball.apply_gravity(dt)
        self._ball.update(dt)

        # Check collisions
        self.check_ground_collision()

        # Update world
        self._world.tick(dt)

    def render(self) -> None:
        """Render game."""
        if not self._initialized:
            return

        renderer = self._engine.get_subsystem("renderer")
        if renderer:
            renderer.clear(0.1, 0.1, 0.2, 1.0)  # Dark blue background

            # Draw ground
            if self._ground and self._ground._sprite:
                renderer.draw_sprite(self._ground._sprite)

            # Draw ball
            if self._ball and self._ball._sprite:
                renderer.draw_sprite(self._ball._sprite)

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

"""
Physics Subsystem.

Provides 2D physics simulation using Pymunk (in production)
or headless implementation (for testing).

Layer: 2 (Engine)
Dependencies: engine.subsystem
"""

from __future__ import annotations
from abc import abstractmethod
from typing import Optional, Tuple, Dict, TYPE_CHECKING

from engine.subsystem import ISubsystem

if TYPE_CHECKING:
    from engine.engine import Engine


class IPhysics(ISubsystem):
    """
    Interface for physics subsystems.

    Extends ISubsystem with physics-specific methods.
    """

    @abstractmethod
    def create_body(self, mass: float = 1.0, moment: float = 100.0) -> int:
        """
        Create a physics body.

        Args:
            mass: Body mass
            moment: Moment of inertia

        Returns:
            Body ID
        """
        pass

    @abstractmethod
    def remove_body(self, body_id: int) -> None:
        """
        Remove a physics body.

        Args:
            body_id: Body ID to remove
        """
        pass

    @abstractmethod
    def set_body_position(self, body_id: int, x: float, y: float) -> None:
        """Set body position."""
        pass

    @abstractmethod
    def get_body_position(self, body_id: int) -> Tuple[float, float]:
        """Get body position."""
        pass

    @abstractmethod
    def set_body_velocity(self, body_id: int, vx: float, vy: float) -> None:
        """Set body velocity."""
        pass

    @abstractmethod
    def get_body_velocity(self, body_id: int) -> Tuple[float, float]:
        """Get body velocity."""
        pass


class Physics2D(IPhysics):
    """
    2D Physics implementation.

    Provides basic 2D physics simulation:
    - Body creation and removal
    - Gravity
    - Position and velocity management

    Uses simple physics simulation (can be replaced with Pymunk).

    Example:
        >>> physics = Physics2D()
        >>> physics.initialize(engine)
        >>> body_id = physics.create_body(mass=1.0, moment=100.0)
        >>> physics.set_body_position(body_id, 100, 200)
        >>> physics.tick(0.016)

    Attributes:
        gravity: Gravity vector (gx, gy)
        enabled: Whether physics is active
        body_count: Number of active bodies
    """

    def __init__(self):
        """Create a new Physics2D."""
        self._gravity: Tuple[float, float] = (0.0, -900.0)
        self._enabled: bool = True
        self._bodies: Dict[int, Dict] = {}
        self._next_body_id: int = 1

    @property
    def name(self) -> str:
        """Get subsystem name."""
        return "physics"

    @property
    def gravity(self) -> Tuple[float, float]:
        """Get gravity vector."""
        return self._gravity

    @gravity.setter
    def gravity(self, value: Tuple[float, float]) -> None:
        """Set gravity vector."""
        self._gravity = value

    @property
    def enabled(self) -> bool:
        """Get whether physics is enabled."""
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """Set whether physics is enabled."""
        self._enabled = value

    @property
    def body_count(self) -> int:
        """Get number of bodies."""
        return len(self._bodies)

    def initialize(self, engine: "Engine") -> None:
        """
        Initialize the physics subsystem.

        Args:
            engine: Reference to the Engine instance
        """
        pass

    def tick(self, dt: float) -> None:
        """
        Step the physics simulation.

        Args:
            dt: Delta time in seconds
        """
        if not self._enabled:
            return

        gx, gy = self._gravity

        for body_id, body in self._bodies.items():
            # Apply gravity to velocity
            vx, vy = body["velocity"]
            vx += gx * dt
            vy += gy * dt
            body["velocity"] = (vx, vy)

            # Apply velocity to position
            x, y = body["position"]
            x += vx * dt
            y += vy * dt
            body["position"] = (x, y)

    def shutdown(self) -> None:
        """Clean up physics resources."""
        self._bodies.clear()
        self._next_body_id = 1

    def create_body(self, mass: float = 1.0, moment: float = 100.0) -> int:
        """
        Create a physics body.

        Args:
            mass: Body mass
            moment: Moment of inertia

        Returns:
            Body ID
        """
        body_id = self._next_body_id
        self._next_body_id += 1

        self._bodies[body_id] = {
            "mass": mass,
            "moment": moment,
            "position": (0.0, 0.0),
            "velocity": (0.0, 0.0),
        }

        return body_id

    def remove_body(self, body_id: int) -> None:
        """
        Remove a physics body.

        Args:
            body_id: Body ID to remove
        """
        if body_id in self._bodies:
            del self._bodies[body_id]

    def set_body_position(self, body_id: int, x: float, y: float) -> None:
        """Set body position."""
        if body_id in self._bodies:
            self._bodies[body_id]["position"] = (x, y)

    def get_body_position(self, body_id: int) -> Tuple[float, float]:
        """Get body position.

        Raises:
            KeyError: If body_id does not exist
        """
        if body_id not in self._bodies:
            raise KeyError(f"Body ID {body_id} does not exist")
        return self._bodies[body_id]["position"]

    def set_body_velocity(self, body_id: int, vx: float, vy: float) -> None:
        """Set body velocity."""
        if body_id in self._bodies:
            self._bodies[body_id]["velocity"] = (vx, vy)

    def get_body_velocity(self, body_id: int) -> Tuple[float, float]:
        """Get body velocity.

        Raises:
            KeyError: If body_id does not exist
        """
        if body_id not in self._bodies:
            raise KeyError(f"Body ID {body_id} does not exist")
        return self._bodies[body_id]["velocity"]

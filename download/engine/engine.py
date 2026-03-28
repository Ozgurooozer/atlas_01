"""
Engine - Main Subsystem Manager.

The Engine class manages lifecycle of all subsystems.
It registers, initializes, ticks, and shuts down subsystems.
Also provides a Scheduler for time-based callbacks.

Layer: 2 (Engine)
Dependencies: engine.subsystem, core.scheduler
"""

from __future__ import annotations
from typing import Dict, Optional, TYPE_CHECKING

from core.scheduler import Scheduler

if TYPE_CHECKING:
    from engine.subsystem import ISubsystem


class Engine:
    """
    Main engine class that manages all subsystems.

    The Engine is the central hub of the game engine. It:
    - Registers subsystems (Renderer, Physics, Audio, etc.)
    - Initializes all subsystems at startup
    - Ticks all subsystems every frame
    - Provides a Scheduler for delayed/repeated callbacks
    - Shuts down all subsystems at exit

    Example:
        >>> engine = Engine()
        >>> engine.register_subsystem(Renderer())
        >>> engine.register_subsystem(Physics())
        >>> engine.initialize()
        >>> while running:
        ...     engine.tick(dt)
        >>> engine.shutdown()
    """

    def __init__(self):
        """Initialize empty engine with scheduler."""
        self._subsystems: Dict[str, "ISubsystem"] = {}
        self._scheduler = Scheduler()
        self._initialized = False

    def register_subsystem(self, subsystem: "ISubsystem") -> None:
        """
        Register a subsystem with the engine.

        Args:
            subsystem: Subsystem instance to register

        Raises:
            ValueError: If subsystem with same name already registered
        """
        name = subsystem.name
        if name in self._subsystems:
            raise ValueError(f"Subsystem '{name}' already registered")
        self._subsystems[name] = subsystem

    def unregister_subsystem(self, name: str) -> Optional["ISubsystem"]:
        """
        Unregister a subsystem from the engine.

        Args:
            name: Name of subsystem to unregister

        Returns:
            The removed subsystem, or None if not found
        """
        return self._subsystems.pop(name, None)

    def get_subsystem(self, name: str) -> Optional["ISubsystem"]:
        """
        Get a registered subsystem by name.

        Args:
            name: Name of the subsystem

        Returns:
            Subsystem instance, or None if not found
        """
        return self._subsystems.get(name)

    def initialize(self) -> None:
        """
        Initialize all registered subsystems.

        Calls initialize() on each subsystem in registration order.
        """
        for subsystem in self._subsystems.values():
            subsystem.initialize(self)
        self._initialized = True

    def tick(self, dt: float) -> None:
        """
        Update all subsystems for one frame.

        Also processes scheduled callbacks via the scheduler.

        Args:
            dt: Delta time in seconds since last frame
        """
        # Process scheduled callbacks first
        self._scheduler.tick(dt)

        # Then tick subsystems
        for subsystem in self._subsystems.values():
            subsystem.tick(dt)

    def shutdown(self) -> None:
        """
        Shut down all registered subsystems.

        Calls shutdown() on each subsystem in reverse registration order.
        """
        # Shutdown in reverse order
        for subsystem in reversed(list(self._subsystems.values())):
            subsystem.shutdown()
        self._initialized = False

    @property
    def is_initialized(self) -> bool:
        """Check if engine has been initialized."""
        return self._initialized

    @property
    def subsystem_names(self) -> list:
        """Get list of registered subsystem names."""
        return list(self._subsystems.keys())

    @property
    def scheduler(self) -> Scheduler:
        """
        Get the engine's scheduler for time-based callbacks.

        Use for delayed and repeated callbacks:
        - scheduler.call_later(delay, callback)
        - scheduler.call_every(interval, callback)

        Returns:
            The Scheduler instance.
        """
        return self._scheduler

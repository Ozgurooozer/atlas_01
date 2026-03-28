"""
ISubsystem Interface.

All engine subsystems (Renderer, Physics, Audio, Input, Asset) 
must implement this interface.

Layer: 2 (Engine)
Dependencies: None
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.engine import Engine


class ISubsystem(ABC):
    """
    Interface for all engine subsystems.

    A subsystem is a major engine component that:
    - Has a unique name
    - Can be initialized with engine context
    - Ticks every frame
    - Can be shut down cleanly

    Example subsystems: Renderer, Physics, Audio, Input, AssetManager.

    Example:
        >>> class Renderer(ISubsystem):
        ...     @property
        ...     def name(self) -> str:
        ...         return "renderer"
        ...
        ...     def initialize(self, engine: "Engine") -> None:
        ...         self._ctx = moderngl.create_context()
        ...
        ...     def tick(self, dt: float) -> None:
        ...         self.render_all_objects()
        ...
        ...     def shutdown(self) -> None:
        ...         self._ctx.release()
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Get the subsystem name.

        Used for identification and logging.

        Returns:
            Unique name string (e.g., "renderer", "physics")
        """
        pass

    @abstractmethod
    def initialize(self, engine: "Engine") -> None:
        """
        Initialize the subsystem.

        Called once when engine starts.
        Use this to set up resources, register handlers, etc.

        Args:
            engine: Reference to the Engine instance
        """
        pass

    @abstractmethod
    def tick(self, dt: float) -> None:
        """
        Update the subsystem for one frame.

        Called every frame with delta time.

        Args:
            dt: Delta time in seconds since last frame
        """
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """
        Clean up the subsystem.

        Called once when engine stops.
        Release all resources here.
        """
        pass

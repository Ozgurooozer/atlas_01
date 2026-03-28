"""
GameMode Base Class.

GameMode defines the rules and state of the game.
It manages game flow, player interaction, and win/lose conditions.

Layer: 4 (Game)
Dependencies: core.object
"""

from __future__ import annotations
from typing import Any, Dict, Optional, TYPE_CHECKING

from core.object import Object

if TYPE_CHECKING:
    from world.world import World


class GameMode(Object):
    """
    Base class for game modes.

    A GameMode defines the rules and state of the game. It:
    - Manages game lifecycle (start, tick, end)
    - References the World
    - Provides hooks for game-specific logic

    Example:
        >>> class Deathmatch(GameMode):
        ...     def on_start(self):
        ...         self.score = { "player1": 0, "player2": 0 }
        ...
        ...     def on_tick(self, delta_time: float):
        ...         if self.score["player1"] >= 10:
        ...             self.end()
        ...
        ...     def on_end(self):
        ...         print("Game Over!")

    Attributes:
        world: Reference to the game World
        is_running: Whether the game is currently running
    """

    def __init__(self, name: str | None = None):
        """
        Create a new GameMode.

        Args:
            name: Optional name. Defaults to class name.
        """
        super().__init__(name)
        self._world: Optional["World"] = None
        self._is_running: bool = False

    @property
    def world(self) -> Optional["World"]:
        """Get the World this GameMode is associated with."""
        return self._world

    @world.setter
    def world(self, value: Optional["World"]) -> None:
        """Set the World this GameMode is associated with."""
        self._world = value

    @property
    def is_running(self) -> bool:
        """Get whether the game is running."""
        return self._is_running

    def start(self) -> None:
        """
        Start the game.

        Sets is_running to True and calls on_start.
        """
        if self._is_running:
            return

        self._is_running = True
        self.on_start()

    def end(self) -> None:
        """
        End the game.

        Sets is_running to False and calls on_end.
        """
        if not self._is_running:
            return

        self._is_running = False
        self.on_end()

    def tick(self, delta_time: float) -> None:
        """
        Update the game for one frame.

        Calls on_tick if the game is running.

        Args:
            delta_time: Time elapsed since last frame in seconds
        """
        if not self._is_running:
            return

        self.on_tick(delta_time)

    def on_start(self) -> None:
        """
        Called when the game starts.

        Override in subclasses to perform initialization.
        """
        pass

    def on_tick(self, delta_time: float) -> None:
        """
        Called each frame while the game is running.

        Override in subclasses to implement game logic.

        Args:
            delta_time: Time elapsed since last frame in seconds
        """
        pass

    def on_end(self) -> None:
        """
        Called when the game ends.

        Override in subclasses to perform cleanup.
        """
        pass

    def serialize(self) -> Dict[str, Any]:
        """
        Serialize this GameMode to a dictionary.

        Returns:
            Dictionary containing gamemode data
        """
        data = super().serialize()
        data["is_running"] = self._is_running
        return data

    def deserialize(self, data: Dict[str, Any]) -> None:
        """
        Deserialize this GameMode from a dictionary.

        Args:
            data: Dictionary containing gamemode data
        """
        super().deserialize(data)
        if "is_running" in data:
            self._is_running = data["is_running"]

    def __repr__(self) -> str:
        """Return string representation for debugging."""
        return f"{self.__class__.__name__}(name={self._name!r}, is_running={self._is_running})"

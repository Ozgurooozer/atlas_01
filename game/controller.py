"""
Controller Classes.

Controllers handle input and control Actors (pawns).
They provide the link between input and game behavior.

Layer: 4 (Game)
Dependencies: core.object
"""

from __future__ import annotations
from typing import Any, Dict, Optional, TYPE_CHECKING

from core.object import Object

if TYPE_CHECKING:
    from world.actor import Actor


class Controller(Object):
    """
    Base class for all controllers.

    A Controller is responsible for controlling an Actor (pawn).
    It can possess and unpossess actors, and tick each frame.

    Example:
        >>> ctrl = Controller()
        >>> actor = Actor(name="Player")
        >>> ctrl.possess(actor)
        >>> ctrl.tick(0.016)
        >>> ctrl.unpossess()

    Attributes:
        pawn: The Actor this Controller is controlling
        enabled: Whether this Controller is active
    """

    def __init__(self, name: str | None = None):
        """
        Create a new Controller.

        Args:
            name: Optional name. Defaults to class name.
        """
        super().__init__(name)
        self._pawn: Optional["Actor"] = None
        self._enabled: bool = True

    @property
    def pawn(self) -> Optional["Actor"]:
        """Get the controlled Actor."""
        return self._pawn

    @pawn.setter
    def pawn(self, value: Optional["Actor"]) -> None:
        """Set the controlled Actor."""
        self._pawn = value

    @property
    def enabled(self) -> bool:
        """Get whether this Controller is enabled."""
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """Set whether this Controller is enabled."""
        self._enabled = value

    def possess(self, pawn: "Actor") -> None:
        """
        Take control of an Actor.

        Calls on_possess hook.

        Args:
            pawn: The Actor to control
        """
        if self._pawn is pawn:
            return

        # Unpossess current pawn first
        if self._pawn is not None:
            self.unpossess()

        self._pawn = pawn
        self.on_possess(pawn)

    def unpossess(self) -> None:
        """
        Release control of the current Actor.

        Calls on_unpossess hook.
        """
        if self._pawn is None:
            return

        self.on_unpossess()
        self._pawn = None

    def on_possess(self, pawn: "Actor") -> None:
        """
        Called when possessing an Actor.

        Override in subclasses to perform setup.

        Args:
            pawn: The Actor being possessed
        """
        pass

    def on_unpossess(self) -> None:
        """
        Called when unpossessing an Actor.

        Override in subclasses to perform cleanup.
        """
        pass

    def tick(self, delta_time: float) -> None:
        """
        Update this Controller for one frame.

        Calls on_tick if enabled.

        Args:
            delta_time: Time elapsed since last frame in seconds
        """
        if not self._enabled:
            return

        self.on_tick(delta_time)

    def on_tick(self, delta_time: float) -> None:
        """
        Called each frame while enabled.

        Override in subclasses to implement per-frame logic.

        Args:
            delta_time: Time elapsed since last frame in seconds
        """
        pass

    def serialize(self) -> Dict[str, Any]:
        """
        Serialize this Controller to a dictionary.

        Returns:
            Dictionary containing controller data
        """
        data = super().serialize()
        data["enabled"] = self._enabled
        return data

    def deserialize(self, data: Dict[str, Any]) -> None:
        """
        Deserialize this Controller from a dictionary.

        Args:
            data: Dictionary containing controller data
        """
        super().deserialize(data)
        if "enabled" in data:
            self._enabled = data["enabled"]

    def __repr__(self) -> str:
        """Return string representation for debugging."""
        pawn_name = self._pawn.name if self._pawn else "None"
        return f"{self.__class__.__name__}(name={self._name!r}, pawn={pawn_name}, enabled={self._enabled})"


class PlayerController(Controller):
    """
    Controller for player input.

    PlayerController handles keyboard/mouse input and
    translates it into Actor behavior.

    Example:
        >>> pc = PlayerController()
        >>> pc.possess(player_actor)
        >>> pc.on_input("jump", True)  # Player pressed jump
        >>> pc.on_input("jump", False)  # Player released jump

    Attributes:
        Inherits all attributes from Controller
    """

    def __init__(self, name: str | None = None):
        """
        Create a new PlayerController.

        Args:
            name: Optional name. Defaults to class name.
        """
        super().__init__(name)

    def on_input(self, action: str, pressed: bool) -> None:
        """
        Handle an input action.

        Override in subclasses to implement input handling.

        Args:
            action: Name of the input action (e.g., "jump", "move_left")
            pressed: True if pressed, False if released
        """
        pass

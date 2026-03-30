"""
Component Base Class.

Components are modular behaviors attached to Actors.
Each Component provides specific functionality (physics, rendering, AI, etc.).

Components:
- Inherit from Object (unique ID, name, serialization)
- Have an owner reference (the Actor they belong to)
- Have enabled/disabled state
- Provide lifecycle hooks (on_attach, on_detach, on_tick)

Layer: 3 (World)
Dependencies: core.object, core.guid
"""

from __future__ import annotations
from typing import Any, Dict, Optional, TYPE_CHECKING

from core.object import Object

if TYPE_CHECKING:
    from world.actor import Actor


class Component(Object):
    """
    Base class for all components.

    Components are attached to Actors and provide modular functionality.
    A single Actor can have multiple Components of different types.

    Lifecycle:
        1. Component is created
        2. on_attach(owner) called when attached to Actor
        3. on_tick(delta_time) called each frame if enabled
        4. on_detach() called when removed from Actor

    Example:
        >>> class HealthComponent(Component):
        ...     def __init__(self, name: str | None = None):
        ...         super().__init__(name)
        ...         self._health = 100.0
        ...
        ...     @reflect("float", min=0, max=100)
        ...     def health(self) -> float:
        ...         return self._health
        ...
        ...     @health.setter
        ...     def health(self, value: float):
        ...         self._health = value

    Attributes:
        owner: The Actor this Component is attached to (or None)
        enabled: Whether this Component is active
    """

    def __init__(self, name: str | None = None):
        """
        Create a new Component.

        Args:
            name: Optional name. Defaults to class name.
        """
        super().__init__(name)
        self._owner: Optional["Actor"] = None
        self._enabled: bool = True

    @property
    def owner(self) -> Optional["Actor"]:
        """Get the Actor this Component is attached to."""
        return self._owner

    @owner.setter
    def owner(self, value: Optional["Actor"]) -> None:
        """Set the owner Actor."""
        self._owner = value

    @property
    def enabled(self) -> bool:
        """Get whether this Component is enabled."""
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """Set whether this Component is enabled."""
        self._enabled = value

    def on_attach(self, owner: "Actor") -> None:
        """
        Called when this Component is attached to an Actor.

        Override in subclasses to perform initialization that
        requires access to the owner Actor.

        Args:
            owner: The Actor this Component is being attached to
        """
        pass

    def on_detach(self) -> None:
        """
        Called when this Component is detached from its Actor.

        Override in subclasses to perform cleanup.
        """
        pass

    def on_tick(self, delta_time: float) -> None:
        """
        Called each frame if the Component is enabled.

        Override in subclasses to implement per-frame logic.

        Args:
            delta_time: Time elapsed since last frame in seconds
        """
        pass

    def serialize(self) -> Dict[str, Any]:
        """
        Serialize this Component to a dictionary.

        Returns:
            Dictionary containing component data
        """
        data = super().serialize()
        data["enabled"] = self._enabled
        # Note: owner is not serialized (set on attach)
        return data

    def deserialize(self, data: Dict[str, Any]) -> None:
        """
        Deserialize this Component from a dictionary.

        Args:
            data: Dictionary containing component data
        """
        super().deserialize(data)
        if "enabled" in data:
            self._enabled = data["enabled"]

    def __repr__(self) -> str:
        """Return string representation for debugging."""
        owner_name = self._owner.name if self._owner else "None"
        return f"{self.__class__.__name__}(name={self._name!r}, owner={owner_name}, enabled={self._enabled})"

"""
Actor Class.

Actors are objects that exist in the game world.
They contain Components that define their behavior.

Actors:
- Inherit from Object (unique ID, name, serialization)
- Contain a list of Components
- Propagate tick to enabled components
- Belong to a World (optional reference)

Layer: 3 (World)
Dependencies: core.object, world.component
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Type, TYPE_CHECKING

from core.object import Object
from world.component import Component

if TYPE_CHECKING:
    from world.world import World


class Actor(Object):
    """
    Base class for all actors in the game world.

    An Actor is an object that can exist in the world. It serves as a
    container for Components, which provide specific behaviors.

    Actors can have any number of Components attached. Each frame,
    the Actor's tick() method propagates to all enabled Components.

    Example:
        >>> player = Actor(name="Player")
        >>> player.add_component(TransformComponent())
        >>> player.add_component(SpriteComponent("player.png"))
        >>> player.tick(0.016)  # Update all components

    Attributes:
        components: List of Components attached to this Actor
        world: Reference to the World this Actor belongs to
        enabled: Whether this Actor is active
    """

    def __init__(self, name: str | None = None):
        """
        Create a new Actor.

        Args:
            name: Optional name. Defaults to class name.
        """
        super().__init__(name)
        self._components: List[Component] = []
        self._world: Optional["World"] = None
        self._enabled: bool = True

    @property
    def components(self) -> List[Component]:
        """Get the list of Components attached to this Actor."""
        return self._components

    @property
    def world(self) -> Optional["World"]:
        """Get the World this Actor belongs to."""
        return self._world

    @world.setter
    def world(self, value: Optional["World"]) -> None:
        """Set the World this Actor belongs to."""
        self._world = value

    @property
    def enabled(self) -> bool:
        """Get whether this Actor is enabled."""
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """Set whether this Actor is enabled."""
        self._enabled = value

    def add_component(self, component: Component) -> None:
        """
        Add a Component to this Actor.

        Sets the component's owner and calls on_attach.

        Args:
            component: The Component to add
        """
        self._components.append(component)
        component.owner = self
        component.on_attach(self)

    def remove_component(self, component: Component) -> None:
        """
        Remove a Component from this Actor.

        Calls on_detach and clears the component's owner.

        Args:
            component: The Component to remove
        """
        if component in self._components:
            component.on_detach()
            component.owner = None
            self._components.remove(component)

    def get_component(self, component_type: Type[Component]) -> Optional[Component]:
        """
        Get a Component by type.

        Args:
            component_type: The type of Component to find

        Returns:
            The first Component of the given type, or None if not found
        """
        for component in self._components:
            if isinstance(component, component_type):
                return component
        return None

    def tick(self, delta_time: float) -> None:
        """
        Update this Actor for one frame.

        Propagates tick to all enabled Components.

        Args:
            delta_time: Time elapsed since last frame in seconds
        """
        if not self._enabled:
            return

        for component in self._components:
            if component.enabled:
                component.on_tick(delta_time)

    def on_destroyed(self) -> None:
        """
        Called when this Actor is destroyed.

        Removes all Components.
        """
        # Remove all components
        for component in self._components[:]:  # Copy to avoid modification during iteration
            self.remove_component(component)

    def serialize(self) -> Dict[str, Any]:
        """
        Serialize this Actor to a dictionary.

        Returns:
            Dictionary containing actor data
        """
        data = super().serialize()
        data["enabled"] = self._enabled
        # Note: components and world are handled separately
        return data

    def deserialize(self, data: Dict[str, Any]) -> None:
        """
        Deserialize this Actor from a dictionary.

        Args:
            data: Dictionary containing actor data
        """
        super().deserialize(data)
        if "enabled" in data:
            self._enabled = data["enabled"]

    def __repr__(self) -> str:
        """Return string representation for debugging."""
        return f"{self.__class__.__name__}(name={self._name!r}, components={len(self._components)}, enabled={self._enabled})"

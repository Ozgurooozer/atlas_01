"""
World Class.

World is the container for all Actors in the game.
It manages actor lifecycle and provides queries.

Features:
- Actor spawning and destruction
- Actor queries (by name, by type)
- World tick propagation
- Clear all actors

Layer: 3 (World)
Dependencies: core.object, world.actor
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Type

from core.object import Object
from world.actor import Actor


class World(Object):
    """
    Container for all Actors in the game.

    The World manages the lifecycle of Actors and provides
    methods to query and manipulate them.

    Example:
        >>> world = World(name="Level1")
        >>> player = Actor(name="Player")
        >>> world.spawn_actor(player)
        >>> world.tick(0.016)  # Update all actors
        >>> world.destroy_actor(player)

    Attributes:
        actors: List of all Actors in this World
        enabled: Whether this World is active
        actor_count: Number of actors in this World
    """

    def __init__(self, name: str | None = None):
        """
        Create a new World.

        Args:
            name: Optional name. Defaults to class name.
        """
        super().__init__(name)
        self._actors: List[Actor] = []
        self._enabled: bool = True

    @property
    def actors(self) -> List[Actor]:
        """Get the list of all Actors in this World."""
        return self._actors

    @property
    def enabled(self) -> bool:
        """Get whether this World is enabled."""
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """Set whether this World is enabled."""
        self._enabled = value

    @property
    def actor_count(self) -> int:
        """Get the number of actors in this World."""
        return len(self._actors)

    def spawn_actor(self, actor: Actor) -> None:
        """
        Spawn an Actor into this World.

        Sets the actor's world reference and calls on_created.

        Args:
            actor: The Actor to spawn

        Raises:
            ValueError: If actor is already in this world
        """
        if actor in self._actors:
            raise ValueError(f"Actor '{actor.name}' is already spawned in this world")
        self._actors.append(actor)
        actor.world = self
        actor.on_created()

    def destroy_actor(self, actor: Actor) -> None:
        """
        Remove an Actor from this World.

        Calls on_destroyed and clears the world reference.

        Args:
            actor: The Actor to destroy

        Raises:
            ValueError: If actor is not in this world
        """
        if actor not in self._actors:
            raise ValueError(f"Actor '{actor.name}' is not in this world")
        actor.on_destroyed()
        actor.world = None
        self._actors.remove(actor)

    def get_actor_by_name(self, name: str) -> Optional[Actor]:
        """
        Find an Actor by name.

        Args:
            name: The name to search for

        Returns:
            The first Actor with the given name, or None if not found
        """
        for actor in self._actors:
            if actor.name == name:
                return actor
        return None

    def get_actors_by_type(self, actor_type: Type[Actor]) -> List[Actor]:
        """
        Find all Actors of a specific type.

        Args:
            actor_type: The type of Actor to find

        Returns:
            List of all Actors of the given type
        """
        return [actor for actor in self._actors if isinstance(actor, actor_type)]

    def get_all_actors(self) -> List[Actor]:
        """
        Get all Actors in this World.

        Returns:
            List of all Actors
        """
        return self._actors.copy()

    def tick(self, delta_time: float) -> None:
        """
        Update this World for one frame.

        Propagates tick to all enabled Actors.

        Args:
            delta_time: Time elapsed since last frame in seconds
        """
        if not self._enabled:
            return

        for actor in self._actors:
            if actor.enabled:
                actor.tick(delta_time)

    def clear(self) -> None:
        """
        Remove all Actors from this World.

        Calls destroy_actor for each actor.
        """
        for actor in self._actors[:]:  # Copy to avoid modification during iteration
            self.destroy_actor(actor)

    def serialize(self) -> Dict[str, Any]:
        """
        Serialize this World to a dictionary.

        Returns:
            Dictionary containing world data
        """
        data = super().serialize()
        data["enabled"] = self._enabled
        # Note: actors are serialized separately
        return data

    def deserialize(self, data: Dict[str, Any]) -> None:
        """
        Deserialize this World from a dictionary.

        Args:
            data: Dictionary containing world data
        """
        super().deserialize(data)
        if "enabled" in data:
            self._enabled = data["enabled"]

    def __repr__(self) -> str:
        """Return string representation for debugging."""
        return f"{self.__class__.__name__}(name={self._name!r}, actors={len(self._actors)}, enabled={self._enabled})"

"""
Object Base Class.

The foundation of everything in the engine.
Every class (Actor, Component, Widget, Asset) inherits from Object.

Provides:
- Unique identification (GUID)
- Name management
- Serialization
- Lifecycle hooks
- Flags

Layer: 1 (Core)
Dependencies: core.guid
"""

from __future__ import annotations
from typing import Any, Dict

from core.guid import GUID


class Object:
    """
    Base class for all engine objects.

    Object provides the foundation for:
    - Unique identification via GUID
    - Named objects for debugging
    - Serialization to/from dict
    - Lifecycle hooks (on_created, on_destroyed)
    - Flags for state management

    Example:
        >>> obj = Object(name="MyObject")
        >>> obj.name
        'MyObject'
        >>> str(obj.guid)  # UUID string
        '550e8400-e29b-41d4-a716-446655440000'
        >>> data = obj.serialize()
        >>> new_obj = Object()
        >>> new_obj.deserialize(data)
    """

    def __init__(self, name: str | None = None):
        """
        Create a new Object.

        Args:
            name: Optional name. Defaults to class name.
        """
        self._guid = GUID()
        self._name = name if name is not None else self.__class__.__name__
        self._flags = 0

    @property
    def guid(self) -> GUID:
        """Get the unique identifier for this object."""
        return self._guid

    @property
    def name(self) -> str:
        """Get the name of this object."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """Set the name of this object."""
        self._name = value

    @property
    def flags(self) -> int:
        """Get the flags for this object."""
        return self._flags

    @flags.setter
    def flags(self, value: int) -> None:
        """Set the flags for this object."""
        self._flags = value

    def serialize(self) -> Dict[str, Any]:
        """
        Serialize this object to a dictionary.

        Returns:
            Dictionary containing object data
        """
        return {
            "__class__": self.__class__.__name__,
            "guid": str(self._guid),
            "name": self._name,
            "flags": self._flags,
        }

    def deserialize(self, data: Dict[str, Any]) -> None:
        """
        Deserialize this object from a dictionary.

        Args:
            data: Dictionary containing object data
        """
        if "guid" in data:
            self._guid = GUID(data["guid"])
        if "name" in data:
            self._name = data["name"]
        if "flags" in data:
            self._flags = data["flags"]

    def on_created(self) -> None:
        """
        Called after object is created.

        Override in subclasses to perform initialization.
        """
        pass

    def on_destroyed(self) -> None:
        """
        Called before object is destroyed.

        Override in subclasses to perform cleanup.
        """
        pass

    def __repr__(self) -> str:
        """Return string representation for debugging."""
        return f"{self.__class__.__name__}(name={self._name!r}, guid={self._guid!r})"

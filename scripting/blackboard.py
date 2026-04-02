"""
Blackboard - AI Shared State.

Provides a key-value store for AI systems to share data.
Supports change listeners and scoped keys (dot notation).

Layer: 5 (Scripting)
Dependencies: core.object
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Tuple

from core.object import Object


class Blackboard(Object):
    """
    Shared state for AI systems.

    A key-value store that allows AI components to share data.
    Supports change listeners for reactive updates and scoped
    keys using dot notation (e.g., "enemy.health").

    Example:
        >>> bb = Blackboard()
        >>> bb.set("target", "player")
        >>> bb.get("target")
        'player'
        >>> bb.set("enemy.health", 100)
        >>> bb.get_scope("enemy")
        {'health': 100}

    Attributes:
        data: The key-value store dictionary.
    """

    def __init__(self) -> None:
        """Create a new Blackboard."""
        super().__init__(name="Blackboard")
        self._data: Dict[str, Any] = {}
        self._listeners: List[Callable[[str, Any], None]] = []

    @property
    def data(self) -> Dict[str, Any]:
        """Get the data dictionary."""
        return self._data

    def set(self, key: str, value: Any) -> None:
        """
        Set a value.

        Notifies all listeners after setting.

        Args:
            key: The key to set.
            value: The value to store.
        """
        self._data[key] = value
        self._notify_listeners(key, value)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a value.

        Args:
            key: The key to retrieve.
            default: Default value if key not found.

        Returns:
            The stored value or default.
        """
        return self._data.get(key, default)

    def has(self, key: str) -> bool:
        """
        Check if key exists.

        Args:
            key: The key to check.

        Returns:
            True if key exists, False otherwise.
        """
        return key in self._data

    def remove(self, key: str) -> None:
        """
        Remove a key.

        Does nothing if key doesn't exist.

        Args:
            key: The key to remove.
        """
        if key in self._data:
            del self._data[key]

    def clear(self) -> None:
        """Remove all keys."""
        self._data.clear()

    def keys(self) -> List[str]:
        """
        Get all keys.

        Returns:
            List of all keys.
        """
        return list(self._data.keys())

    def values(self) -> List[Any]:
        """
        Get all values.

        Returns:
            List of all values.
        """
        return list(self._data.values())

    def items(self) -> List[Tuple[str, Any]]:
        """
        Get all key-value pairs.

        Returns:
            List of (key, value) tuples.
        """
        return list(self._data.items())

    def on_change(self, listener: Callable[[str, Any], None]) -> None:
        """
        Register a change listener.

        Listener is called with (key, value) after each set.

        Args:
            listener: Callback function(key, value).
        """
        self._listeners.append(listener)

    def _notify_listeners(self, key: str, value: Any) -> None:
        """Notify all listeners of a change."""
        for listener in self._listeners:
            try:
                listener(key, value)
            except Exception:
                pass

    def get_scope(self, scope: str) -> Dict[str, Any]:
        """
        Get all keys in a scope.

        Scope is the prefix before the dot in scoped keys.
        E.g., for "enemy.health", scope is "enemy".

        Args:
            scope: The scope prefix.

        Returns:
            Dictionary of keys (without scope prefix) and values.
        """
        prefix = f"{scope}."
        result: Dict[str, Any] = {}

        for key, value in self._data.items():
            if key.startswith(prefix):
                # Remove scope prefix
                scoped_key = key[len(prefix):]
                result[scoped_key] = value

        return result

    def serialize(self) -> Dict[str, Any]:
        """
        Serialize blackboard data.

        Returns:
            Dictionary with data key.
        """
        data = super().serialize()
        data["data"] = self._data.copy()
        return data

    def deserialize(self, data: Dict[str, Any]) -> None:
        """
        Deserialize blackboard data.

        Args:
            data: Dictionary with data key.
        """
        super().deserialize(data)
        if "data" in data:
            self._data = data["data"].copy()

    def __repr__(self) -> str:
        """Return string representation."""
        return f"Blackboard(keys={len(self._data)})"


__all__ = ['Blackboard']

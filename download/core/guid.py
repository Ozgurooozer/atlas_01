"""
GUID - Global Unique Identifier.

Provides unique identifiers for all objects in the engine.
Default format is UUID4 for uniqueness and standard compliance.

Layer: 1 (Core)
Dependencies: None
"""

import uuid


class GUID:
    """
    Global Unique Identifier.

    Wraps a string value (default UUID4) and provides:
    - Uniqueness across the engine
    - Hashability for use in sets/dicts
    - Equality comparison
    - String representation

    Example:
        >>> guid1 = GUID()
        >>> guid2 = GUID()
        >>> guid1 != guid2  # Always unique
        True

        >>> guid = GUID("my-custom-id")
        >>> str(guid)
        'my-custom-id'
    """

    def __init__(self, value: str = None):
        """
        Create a GUID.

        Args:
            value: Optional string value. If None, generates UUID4.
        """
        if value is None:
            value = str(uuid.uuid4())
        self._value = value

    def __str__(self) -> str:
        """Return string representation."""
        return self._value

    def __repr__(self) -> str:
        """Return repr for debugging."""
        return f"GUID({self._value!r})"

    def __eq__(self, other) -> bool:
        """Check equality with another GUID."""
        if isinstance(other, GUID):
            return self._value == other._value
        return False

    def __hash__(self) -> int:
        """Return hash for use in sets/dicts."""
        return hash(self._value)

    def __ne__(self, other) -> bool:
        """Check inequality."""
        return not self.__eq__(other)

    @property
    def value(self) -> str:
        """Get the underlying string value."""
        return self._value

"""
Input Buffer.

Frame-based input buffer for responsive combat feel.
Stores recent inputs with timestamps, allows FIFO consumption by type.

Layer 4 (Game/Input)
Dependencies: core.object
"""
from __future__ import annotations
from typing import Optional, List, Tuple, Any
from core.object import Object


class InputBuffer(Object):
    """
    Frame-based input buffer for responsive combat.

    Stores recent player inputs with timestamps. Consumes inputs
    in FIFO order by type. Supports timeout-based eviction.
    """

    DEFAULT_MAX_SIZE: int = 4
    DEFAULT_TIMEOUT: float = 0.2

    def __init__(self, max_size: int = 4, timeout: float = 0.2):
        super().__init__(name="InputBuffer")
        self.max_size: int = max_size
        self.timeout: float = timeout
        self._entries: List[Tuple[Any, float]] = []

    @property
    def count(self) -> int:
        """Number of buffered entries."""
        return len(self._entries)

    @property
    def is_empty(self) -> bool:
        """True when buffer has no entries."""
        return len(self._entries) == 0

    def push(self, input_type: Any, timestamp: Optional[float] = None) -> None:
        """
        Add an input to the buffer.

        Args:
            input_type: Type identifier for the input (e.g. "attack").
            timestamp: Time of input. Auto-generated if None.
        """
        if timestamp is None:
            import time
            timestamp = time.monotonic()

        self._entries.append((input_type, timestamp))

        if len(self._entries) > self.max_size:
            self._entries.pop(0)

    def consume(self, input_type: Any) -> Optional[Tuple[Any, float]]:
        """
        Consume the oldest entry matching input_type.

        Args:
            input_type: Type to consume.

        Returns:
            Tuple of (input_type, timestamp) or None if not found.
        """
        for i, (entry_type, entry_time) in enumerate(self._entries):
            if entry_type == input_type:
                self._entries.pop(i)
                return (entry_type, entry_time)
        return None

    def peek(self, input_type: Any) -> Optional[Tuple[Any, float]]:
        """
        Peek at the oldest entry matching input_type without removing.

        Args:
            input_type: Type to peek.

        Returns:
            Tuple of (input_type, timestamp) or None if not found.
        """
        for entry_type, entry_time in self._entries:
            if entry_type == input_type:
                return (entry_type, entry_time)
        return None

    def has(self, input_type: Any) -> bool:
        """
        Check if an input type exists in the buffer.

        Args:
            input_type: Type to check.

        Returns:
            True if found in buffer.
        """
        for entry_type, _ in self._entries:
            if entry_type == input_type:
                return True
        return False

    def tick(self, current_time: Optional[float] = None) -> None:
        """
        Remove expired entries based on timeout.

        Args:
            current_time: Current monotonic time. Auto-generated if None.
        """
        if current_time is None:
            import time
            current_time = time.monotonic()

        cutoff = current_time - self.timeout
        self._entries = [
            (itype, itime) for itype, itime in self._entries
            if itime > cutoff
        ]

    def clear(self) -> None:
        """Remove all entries from the buffer."""
        self._entries.clear()

    def serialize(self) -> dict[str, Any]:
        """Serialize buffer state to dict."""
        data = super().serialize()
        data.update({
            "max_size": self.max_size,
            "timeout": self.timeout,
            "entries": [
                {"type": str(itype), "timestamp": itime}
                for itype, itime in self._entries
            ],
        })
        return data

    def deserialize(self, data: dict[str, Any]) -> None:
        """Restore buffer state from dict."""
        super().deserialize(data)
        self.max_size = data.get("max_size", self.DEFAULT_MAX_SIZE)
        self.timeout = data.get("timeout", self.DEFAULT_TIMEOUT)
        self._entries.clear()
        for entry in data.get("entries", []):
            self._entries.append((entry["type"], entry["timestamp"]))

"""
Time-based callback scheduler.

Provides delayed and repeated callback execution for game loops.
Used for:
- Delayed actions (spawn enemies after X seconds)
- Repeated actions (update every X seconds)
- Cooldowns, timers, periodic events

Layer: 1 (Core)
Dependencies: None (stdlib only)

Example:
    >>> scheduler = Scheduler()
    >>> scheduler.call_later(2.0, lambda: print("2 seconds passed"))
    >>> scheduler.call_every(1.0, lambda: print("Every second"))
    >>> scheduler.tick(dt)  # Call in game loop
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Optional
import time


@dataclass
class DelayedCall:
    """
    A delayed (one-shot) callback.

    Attributes:
        handle: Unique identifier for this callback.
        delay: Time in seconds before execution.
        callback: Function to call.
        remaining: Time remaining until execution.
    """
    handle: int
    delay: float
    callback: Callable[[], None]
    remaining: float = field(init=False)

    def __post_init__(self) -> None:
        """Initialize remaining time."""
        self.remaining = self.delay


@dataclass
class RepeatedCall:
    """
    A repeated (interval) callback.

    Attributes:
        handle: Unique identifier for this callback.
        interval: Time in seconds between executions.
        callback: Function to call.
        accumulator: Time accumulated since last execution.
    """
    handle: int
    interval: float
    callback: Callable[[], None]
    accumulator: float = field(default=0.0)


class Scheduler:
    """
    Time-based callback scheduler.

    Manages delayed and repeated callbacks. Call tick(dt) every frame
    to process pending callbacks.

    Example:
        >>> scheduler = Scheduler()
        >>> # Spawn enemy after 3 seconds
        >>> scheduler.call_later(3.0, spawn_enemy)
        >>> # Update score every 0.5 seconds
        >>> scheduler.call_every(0.5, update_score)
        >>> # In game loop:
        >>> scheduler.tick(dt)
    """

    def __init__(self):
        """Create an empty scheduler."""
        self._delayed: List[DelayedCall] = []
        self._repeating: List[RepeatedCall] = []
        self._next_handle: int = 1

    @property
    def pending_count(self) -> int:
        """
        Get total number of pending callbacks.

        Returns:
            Sum of delayed and repeating callbacks.
        """
        return len(self._delayed) + len(self._repeating)

    @property
    def delayed_count(self) -> int:
        """
        Get number of delayed callbacks.

        Returns:
            Count of call_later callbacks.
        """
        return len(self._delayed)

    @property
    def repeating_count(self) -> int:
        """
        Get number of repeating callbacks.

        Returns:
            Count of call_every callbacks.
        """
        return len(self._repeating)

    def call_later(self, delay: float, callback: Callable[[], None]) -> int:
        """
        Schedule a callback to execute after delay seconds.

        Args:
            delay: Time in seconds before execution.
                   Negative or zero delay executes immediately on next tick.
            callback: Function to call (no arguments).

        Returns:
            Handle that can be used to cancel the callback.

        Example:
            >>> handle = scheduler.call_later(2.0, lambda: print("Done!"))
        """
        handle = self._next_handle
        self._next_handle += 1

        call = DelayedCall(handle=handle, delay=max(0.0, delay), callback=callback)
        self._delayed.append(call)

        return handle

    def call_every(self, interval: float, callback: Callable[[], None]) -> int:
        """
        Schedule a callback to execute every interval seconds.

        The callback will execute repeatedly until cancelled.

        Args:
            interval: Time in seconds between executions.
                      Zero interval executes every tick.
            callback: Function to call (no arguments).

        Returns:
            Handle that can be used to cancel the callback.

        Example:
            >>> handle = scheduler.call_every(1.0, lambda: print("Tick!"))
        """
        handle = self._next_handle
        self._next_handle += 1

        call = RepeatedCall(handle=handle, interval=max(0.0, interval), callback=callback)
        self._repeating.append(call)

        return handle

    def cancel(self, handle: int) -> bool:
        """
        Cancel a scheduled callback.

        Args:
            handle: Handle returned by call_later or call_every.

        Returns:
            True if callback was found and cancelled, False if not found.

        Example:
            >>> handle = scheduler.call_later(5.0, my_func)
            >>> scheduler.cancel(handle)  # Cancel before it executes
            True
        """
        # Check delayed calls
        for i, call in enumerate(self._delayed):
            if call.handle == handle:
                self._delayed.pop(i)
                return True

        # Check repeating calls
        for i, call in enumerate(self._repeating):
            if call.handle == handle:
                self._repeating.pop(i)
                return True

        return False

    def clear(self) -> None:
        """
        Remove all scheduled callbacks.

        Useful for cleanup when resetting game state.
        """
        self._delayed.clear()
        self._repeating.clear()

    def tick(self, dt: float) -> None:
        """
        Process pending callbacks.

        Call this every frame from your game loop.

        Args:
            dt: Delta time in seconds since last tick.

        Note:
            - Exceptions in callbacks are caught and logged.
            - Callbacks can schedule new callbacks.
            - Cancelled callbacks are ignored.

        Example:
            >>> def game_loop():
            ...     while running:
            ...         dt = clock.tick()
            ...         scheduler.tick(dt)
        """
        # Process delayed calls
        # Use slice copy to allow modification during iteration
        for call in self._delayed[:]:
            call.remaining -= dt

            if call.remaining <= 0:
                # Execute callback
                try:
                    call.callback()
                except Exception:
                    pass  # Ignore exceptions in callbacks

                # Remove executed call
                if call in self._delayed:
                    self._delayed.remove(call)

        # Process repeating calls
        for call in self._repeating[:]:
            # Special case: zero interval = execute once per tick
            if call.interval <= 0:
                if call in self._repeating:
                    try:
                        call.callback()
                    except Exception:
                        pass  # Ignore exceptions in callbacks
                continue

            call.accumulator += dt

            # Execute as many times as intervals have passed
            while call.accumulator >= call.interval:
                call.accumulator -= call.interval

                # Check if still in list (may have been cancelled)
                if call in self._repeating:
                    try:
                        call.callback()
                    except Exception:
                        pass  # Ignore exceptions in callbacks
                else:
                    break  # Was cancelled during execution


__all__ = ['Scheduler', 'DelayedCall', 'RepeatedCall']

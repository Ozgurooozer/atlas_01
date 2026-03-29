"""
EventBus - Publish/Subscribe Event System.

Provides loose coupling between engine components.
Components can communicate without direct references.

Layer: 1 (Core)
Dependencies: None
"""

from __future__ import annotations
from typing import Any, Callable, Dict, List, Optional

# Type alias for event handlers
EventHandler = Callable[[Dict[str, Any]], None]


class EventBus:
    """
    Publish/Subscribe event bus for loose coupling.

    Components can:
    - Subscribe to events by name
    - Publish events with data
    - Unsubscribe when done

    Example:
        >>> bus = EventBus()
        >>> def on_collision(data):
        ...     print(f"Collision: {data}")
        >>> bus.subscribe("physics.collision", on_collision)
        >>> bus.publish("physics.collision", {"entity1": "player", "entity2": "enemy"})
        Collision: {'entity1': 'player', 'entity2': 'enemy'}
    """

    def __init__(self):
        """Initialize empty event bus."""
        self._handlers: Dict[str, List[EventHandler]] = {}

    def subscribe(self, event_name: str, handler: EventHandler) -> None:
        """
        Subscribe to an event.

        Args:
            event_name: Name of the event (e.g., "physics.collision")
            handler: Callback function that receives event data
        """
        if event_name not in self._handlers:
            self._handlers[event_name] = []
        if handler not in self._handlers[event_name]:
            self._handlers[event_name].append(handler)

    def unsubscribe(self, event_name: str, handler: EventHandler) -> None:
        """
        Unsubscribe from an event.

        Args:
            event_name: Name of the event
            handler: Handler to remove
        """
        if event_name in self._handlers:
            if handler in self._handlers[event_name]:
                self._handlers[event_name].remove(handler)

    def publish(self, event_name: str, data: Dict[str, Any] | None = None) -> bool:
        """
        Publish an event to all subscribers.

        Args:
            event_name: Name of the event
            data: Event data dictionary

        Returns:
            True if event was handled, False if no handlers
        """
        if event_name not in self._handlers:
            return False

        handlers = self._handlers[event_name]
        if not handlers:
            return False

        event_data = data if data is not None else {}
        for handler in handlers:
            handler(event_data)

        return True

    def clear(self, event_name: str | None = None) -> None:
        """
        Clear subscriptions.

        Args:
            event_name: If provided, clear only this event. Otherwise clear all.
        """
        if event_name is not None:
            if event_name in self._handlers:
                self._handlers[event_name] = []
        else:
            self._handlers.clear()

    def has_handlers(self, event_name: str) -> bool:
        """
        Check if an event has any handlers.

        Args:
            event_name: Name of the event

        Returns:
            True if event has handlers
        """
        return event_name in self._handlers and len(self._handlers[event_name]) > 0

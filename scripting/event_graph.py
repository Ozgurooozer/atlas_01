"""
Event Graph - Visual scripting node system.

Provides a node-based event graph for scripting game logic
without code. Nodes connect via pins and execute in sequence.

Layer: 5 (Scripting)
Dependencies: core.object
"""
from __future__ import annotations
from typing import Any, Callable, Dict, Optional
from core.object import Object


class Pin:
    """A connection point on a node (input or output)."""

    def __init__(self, name: str, pin_type: str = "any", is_input: bool = True) -> None:
        self.name = name
        self.pin_type = pin_type
        self.is_input = is_input
        self._value: Any = None
        self._connected_to: Optional["Pin"] = None

    @property
    def value(self) -> Any:
        if self._connected_to is not None:
            return self._connected_to._value
        return self._value

    @value.setter
    def value(self, v: Any) -> None:
        self._value = v

    def connect(self, other: "Pin") -> bool:
        if self.is_input == other.is_input:
            return False
        self._connected_to = other
        return True

    def disconnect(self) -> None:
        self._connected_to = None

    @property
    def is_connected(self) -> bool:
        return self._connected_to is not None


class GraphNode(Object):
    """
    A node in the event graph.

    Nodes have input/output pins and an execute method.
    """

    def __init__(self, name: str = "Node") -> None:
        super().__init__(name=name)
        self._inputs: Dict[str, Pin] = {}
        self._outputs: Dict[str, Pin] = {}
        self._next: Optional["GraphNode"] = None

    def add_input(self, name: str, pin_type: str = "any") -> Pin:
        pin = Pin(name, pin_type, is_input=True)
        self._inputs[name] = pin
        return pin

    def add_output(self, name: str, pin_type: str = "any") -> Pin:
        pin = Pin(name, pin_type, is_input=False)
        self._outputs[name] = pin
        return pin

    def get_input(self, name: str) -> Optional[Pin]:
        return self._inputs.get(name)

    def get_output(self, name: str) -> Optional[Pin]:
        return self._outputs.get(name)

    def set_next(self, node: Optional["GraphNode"]) -> None:
        self._next = node

    @property
    def next_node(self) -> Optional["GraphNode"]:
        return self._next

    def execute(self, context: Any = None) -> Optional["GraphNode"]:
        """Execute this node and return the next node to execute."""
        self._on_execute(context)
        return self._next

    def _on_execute(self, context: Any = None) -> None:
        """Override in subclasses to implement node logic."""
        pass


class EventNode(GraphNode):
    """Entry point node triggered by an event."""

    def __init__(self, event_name: str) -> None:
        super().__init__(name=f"Event_{event_name}")
        self.event_name = event_name


class ActionGraphNode(GraphNode):
    """Node that executes a callable action."""

    def __init__(self, name: str, action: Callable) -> None:
        super().__init__(name=name)
        self._action = action

    def _on_execute(self, context: Any = None) -> None:
        try:
            self._action(context) if context is not None else self._action()
        except Exception:
            pass


class BranchNode(GraphNode):
    """
    Conditional branch node.

    Routes execution to true_node or false_node based on condition.
    """

    def __init__(self, name: str, condition: Callable[[], bool]) -> None:
        super().__init__(name=name)
        self._condition = condition
        self._true_node: Optional[GraphNode] = None
        self._false_node: Optional[GraphNode] = None

    def set_true_node(self, node: GraphNode) -> None:
        self._true_node = node

    def set_false_node(self, node: GraphNode) -> None:
        self._false_node = node

    def execute(self, context: Any = None) -> Optional[GraphNode]:
        try:
            result = self._condition()
        except Exception:
            result = False
        return self._true_node if result else self._false_node


class EventGraph(Object):
    """
    Event graph that connects nodes and executes them.

    Example:
        >>> graph = EventGraph()
        >>> entry = EventNode("on_start")
        >>> action = ActionGraphNode("print", lambda: print("Hello"))
        >>> entry.set_next(action)
        >>> graph.register_event("on_start", entry)
        >>> graph.trigger("on_start")
    """

    def __init__(self, name: str = "EventGraph") -> None:
        super().__init__(name=name)
        self._events: Dict[str, EventNode] = {}
        self._max_steps = 1000  # Prevent infinite loops

    def register_event(self, event_name: str, node: EventNode) -> None:
        self._events[event_name] = node

    def trigger(self, event_name: str, context: Any = None) -> bool:
        entry = self._events.get(event_name)
        if entry is None:
            return False

        current: Optional[GraphNode] = entry
        steps = 0

        while current is not None and steps < self._max_steps:
            current = current.execute(context)
            steps += 1

        return True

    def has_event(self, event_name: str) -> bool:
        return event_name in self._events


__all__ = [
    "Pin", "GraphNode", "EventNode", "ActionGraphNode",
    "BranchNode", "EventGraph"
]

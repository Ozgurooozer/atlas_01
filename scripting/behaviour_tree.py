"""
Behaviour Tree - AI decision making system.

Provides composite, decorator, and leaf nodes for building
AI behaviour trees.

Layer: 5 (Scripting)
Dependencies: core.object
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, List, Optional
from core.object import Object


class NodeStatus(Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    RUNNING = "running"


class BTNode(Object, ABC):
    """Base class for all behaviour tree nodes."""

    def __init__(self, name: str = "BTNode") -> None:
        super().__init__(name=name)

    @abstractmethod
    def tick(self, context: Any = None) -> NodeStatus:
        """Execute this node. Returns SUCCESS, FAILURE, or RUNNING."""
        pass

    def reset(self) -> None:
        """Reset node state."""
        pass


# --- Composite Nodes ---

class Sequence(BTNode):
    """
    Runs children left-to-right. Fails on first failure.
    Succeeds only if all children succeed.
    """

    def __init__(self, name: str = "Sequence") -> None:
        super().__init__(name=name)
        self._children: List[BTNode] = []
        self._current: int = 0

    def add_child(self, node: BTNode) -> None:
        self._children.append(node)

    def tick(self, context: Any = None) -> NodeStatus:
        while self._current < len(self._children):
            status = self._children[self._current].tick(context)
            if status == NodeStatus.FAILURE:
                self._current = 0
                return NodeStatus.FAILURE
            if status == NodeStatus.RUNNING:
                return NodeStatus.RUNNING
            self._current += 1
        self._current = 0
        return NodeStatus.SUCCESS

    def reset(self) -> None:
        self._current = 0
        for child in self._children:
            child.reset()


class Selector(BTNode):
    """
    Runs children left-to-right. Succeeds on first success.
    Fails only if all children fail.
    """

    def __init__(self, name: str = "Selector") -> None:
        super().__init__(name=name)
        self._children: List[BTNode] = []
        self._current: int = 0

    def add_child(self, node: BTNode) -> None:
        self._children.append(node)

    def tick(self, context: Any = None) -> NodeStatus:
        while self._current < len(self._children):
            status = self._children[self._current].tick(context)
            if status == NodeStatus.SUCCESS:
                self._current = 0
                return NodeStatus.SUCCESS
            if status == NodeStatus.RUNNING:
                return NodeStatus.RUNNING
            self._current += 1
        self._current = 0
        return NodeStatus.FAILURE

    def reset(self) -> None:
        self._current = 0
        for child in self._children:
            child.reset()


class Parallel(BTNode):
    """
    Runs all children simultaneously.
    Succeeds if >= success_threshold children succeed.
    """

    def __init__(self, name: str = "Parallel", success_threshold: int = 1) -> None:
        super().__init__(name=name)
        self._children: List[BTNode] = []
        self._success_threshold = success_threshold

    def add_child(self, node: BTNode) -> None:
        self._children.append(node)

    def tick(self, context: Any = None) -> NodeStatus:
        if not self._children:
            return NodeStatus.FAILURE

        successes = 0
        failures = 0
        for child in self._children:
            status = child.tick(context)
            if status == NodeStatus.SUCCESS:
                successes += 1
            elif status == NodeStatus.FAILURE:
                failures += 1

        if successes >= self._success_threshold:
            return NodeStatus.SUCCESS
        if failures > len(self._children) - self._success_threshold:
            return NodeStatus.FAILURE
        return NodeStatus.RUNNING


# --- Decorator Nodes ---

class Inverter(BTNode):
    """Inverts child's result: SUCCESS↔FAILURE, RUNNING unchanged."""

    def __init__(self, child: BTNode, name: str = "Inverter") -> None:
        super().__init__(name=name)
        self._child = child

    def tick(self, context: Any = None) -> NodeStatus:
        status = self._child.tick(context)
        if status == NodeStatus.SUCCESS:
            return NodeStatus.FAILURE
        if status == NodeStatus.FAILURE:
            return NodeStatus.SUCCESS
        return NodeStatus.RUNNING

    def reset(self) -> None:
        self._child.reset()


class Repeater(BTNode):
    """Repeats child N times (or infinitely if times=0)."""

    def __init__(self, child: BTNode, times: int = 0, name: str = "Repeater") -> None:
        super().__init__(name=name)
        self._child = child
        self._times = times
        self._count = 0

    def tick(self, context: Any = None) -> NodeStatus:
        while self._times == 0 or self._count < self._times:
            status = self._child.tick(context)
            if status == NodeStatus.RUNNING:
                return NodeStatus.RUNNING
            if status == NodeStatus.FAILURE:
                self._count = 0
                return NodeStatus.FAILURE
            self._child.reset()
            self._count += 1
            if self._times > 0 and self._count >= self._times:
                self._count = 0
                return NodeStatus.SUCCESS
        return NodeStatus.SUCCESS

    def reset(self) -> None:
        self._count = 0
        self._child.reset()


# --- Leaf Nodes ---

class ActionNode(BTNode):
    """Leaf node that executes a callable action."""

    def __init__(self, action, name: str = "Action") -> None:
        super().__init__(name=name)
        self._action = action

    def tick(self, context: Any = None) -> NodeStatus:
        try:
            result = self._action(context) if context is not None else self._action()
            if result is False:
                return NodeStatus.FAILURE
            return NodeStatus.SUCCESS
        except Exception:
            return NodeStatus.FAILURE


class ConditionNode(BTNode):
    """Leaf node that checks a condition."""

    def __init__(self, condition, name: str = "Condition") -> None:
        super().__init__(name=name)
        self._condition = condition

    def tick(self, context: Any = None) -> NodeStatus:
        try:
            result = self._condition(context) if context is not None else self._condition()
            return NodeStatus.SUCCESS if result else NodeStatus.FAILURE
        except Exception:
            return NodeStatus.FAILURE


class BehaviourTree(Object):
    """
    Behaviour tree runner.

    Example:
        >>> tree = BehaviourTree()
        >>> root = Selector()
        >>> root.add_child(ConditionNode(lambda: False))
        >>> root.add_child(ActionNode(lambda: True))
        >>> tree.set_root(root)
        >>> tree.tick()
        <NodeStatus.SUCCESS: 'success'>
    """

    def __init__(self, name: str = "BehaviourTree") -> None:
        super().__init__(name=name)
        self._root: Optional[BTNode] = None

    def set_root(self, node: BTNode) -> None:
        self._root = node

    def tick(self, context: Any = None) -> Optional[NodeStatus]:
        if self._root is None:
            return None
        return self._root.tick(context)

    def reset(self) -> None:
        if self._root:
            self._root.reset()


__all__ = [
    "NodeStatus", "BTNode", "Sequence", "Selector", "Parallel",
    "Inverter", "Repeater", "ActionNode", "ConditionNode", "BehaviourTree"
]

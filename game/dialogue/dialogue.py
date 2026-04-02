"""
Dialogue system.

Layer: 4 (Game)
Dependencies: core.object
"""
from __future__ import annotations
from typing import Callable, Dict, List, Optional
from core.object import Object


class DialogueChoice:
    """A player choice in a dialogue node."""

    def __init__(self, text: str, next_node: str = "") -> None:
        self.text = text
        self.next_node = next_node
        self.condition: Optional[Callable[[], bool]] = None

    def is_available(self) -> bool:
        if self.condition is None:
            return True
        try:
            return self.condition()
        except Exception:
            return False


class DialogueNode:
    """
    A single node in a dialogue tree.

    Contains speaker, text, choices, and optional callback.
    """

    def __init__(
        self,
        node_id: str,
        speaker: str = "",
        text: str = "",
    ) -> None:
        self.node_id = node_id
        self.speaker = speaker
        self.text = text
        self.choices: List[DialogueChoice] = []
        self.on_enter: Optional[Callable] = None
        self.auto_next: str = ""  # Auto-advance to this node if no choices

    def add_choice(self, choice: DialogueChoice) -> None:
        self.choices.append(choice)

    def get_available_choices(self) -> List[DialogueChoice]:
        return [c for c in self.choices if c.is_available()]

    def __repr__(self) -> str:
        return f"DialogueNode({self.node_id!r}, speaker={self.speaker!r})"


class DialogueTree(Object):
    """
    A complete dialogue tree with nodes and navigation.

    Example:
        >>> tree = DialogueTree(name="Merchant")
        >>> node = DialogueNode("start", "Merchant", "Hello traveler!")
        >>> tree.add_node(node)
        >>> tree.start("start")
        >>> tree.current_node.text
        'Hello traveler!'
    """

    def __init__(self, name: str = "Dialogue") -> None:
        super().__init__(name=name)
        self._nodes: Dict[str, DialogueNode] = {}
        self._current: Optional[DialogueNode] = None
        self._active = False
        self._on_end: Optional[Callable] = None

    @property
    def current_node(self) -> Optional[DialogueNode]:
        return self._current

    @property
    def is_active(self) -> bool:
        return self._active

    def add_node(self, node: DialogueNode) -> None:
        self._nodes[node.node_id] = node

    def start(self, start_node_id: str) -> bool:
        node = self._nodes.get(start_node_id)
        if node is None:
            return False
        self._active = True
        self._go_to(node)
        return True

    def _go_to(self, node: DialogueNode) -> None:
        self._current = node
        if node.on_enter:
            try:
                node.on_enter()
            except Exception:
                pass

    def choose(self, choice_index: int) -> bool:
        """
        Select a choice from current node.

        Returns:
            True if advanced, False if invalid.
        """
        if not self._active or self._current is None:
            return False

        choices = self._current.get_available_choices()
        if choice_index < 0 or choice_index >= len(choices):
            return False

        choice = choices[choice_index]
        if not choice.next_node:
            self.end()
            return True

        next_node = self._nodes.get(choice.next_node)
        if next_node is None:
            self.end()
            return True

        self._go_to(next_node)
        return True

    def advance(self) -> bool:
        """Auto-advance if current node has no choices."""
        if not self._active or self._current is None:
            return False

        choices = self._current.get_available_choices()
        if choices:
            return False  # Has choices, use choose()

        if self._current.auto_next:
            next_node = self._nodes.get(self._current.auto_next)
            if next_node:
                self._go_to(next_node)
                return True

        self.end()
        return True

    def end(self) -> None:
        self._active = False
        self._current = None
        if self._on_end:
            try:
                self._on_end()
            except Exception:
                pass

    def on_end(self, callback: Callable) -> None:
        self._on_end = callback

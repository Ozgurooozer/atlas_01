"""
Quest system.

Layer: 4 (Game)
Dependencies: core.object
"""
from __future__ import annotations
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from core.object import Object


class QuestStatus(Enum):
    INACTIVE = "inactive"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"


class QuestObjective:
    """A single objective within a quest."""

    def __init__(self, description: str, required: int = 1) -> None:
        self.description = description
        self.required = required
        self.current = 0
        self.completed = False

    def progress(self, amount: int = 1) -> None:
        self.current = min(self.current + amount, self.required)
        if self.current >= self.required:
            self.completed = True

    @property
    def is_complete(self) -> bool:
        return self.completed

    def __repr__(self) -> str:
        return f"Objective({self.description!r} {self.current}/{self.required})"


class Quest(Object):
    """
    A quest with objectives, rewards, and lifecycle callbacks.

    Example:
        >>> q = Quest(name="Kill Wolves")
        >>> obj = QuestObjective("Kill 5 wolves", required=5)
        >>> q.add_objective(obj)
        >>> q.start()
        >>> obj.progress(3)
        >>> q.is_complete
        False
    """

    def __init__(self, name: str = "Quest", description: str = "") -> None:
        super().__init__(name=name)
        self.description = description
        self._status = QuestStatus.INACTIVE
        self._objectives: List[QuestObjective] = []
        self._on_complete: Optional[Callable] = None
        self._on_fail: Optional[Callable] = None

    @property
    def status(self) -> QuestStatus:
        return self._status

    @property
    def is_active(self) -> bool:
        return self._status == QuestStatus.ACTIVE

    @property
    def is_complete(self) -> bool:
        return self._status == QuestStatus.COMPLETED

    @property
    def objectives(self) -> List[QuestObjective]:
        return self._objectives

    def add_objective(self, objective: QuestObjective) -> None:
        self._objectives.append(objective)

    def start(self) -> None:
        if self._status == QuestStatus.INACTIVE:
            self._status = QuestStatus.ACTIVE

    def fail(self) -> None:
        if self._status == QuestStatus.ACTIVE:
            self._status = QuestStatus.FAILED
            if self._on_fail:
                self._on_fail()

    def check_completion(self) -> bool:
        """Check if all objectives are complete and mark quest done."""
        if self._status != QuestStatus.ACTIVE:
            return False
        if not self._objectives:
            return False
        if all(o.is_complete for o in self._objectives):
            self._status = QuestStatus.COMPLETED
            if self._on_complete:
                self._on_complete()
            return True
        return False

    def on_complete(self, callback: Callable) -> None:
        self._on_complete = callback

    def on_fail(self, callback: Callable) -> None:
        self._on_fail = callback

    def serialize(self) -> Dict[str, Any]:
        data = super().serialize()
        data["description"] = self.description
        data["status"] = self._status.value
        return data

    def deserialize(self, data: Dict[str, Any]) -> None:
        super().deserialize(data)
        if "description" in data:
            self.description = data["description"]
        if "status" in data:
            self._status = QuestStatus(data["status"])


class QuestManager(Object):
    """Manages all quests in the game."""

    def __init__(self) -> None:
        super().__init__(name="QuestManager")
        self._quests: Dict[str, Quest] = {}

    def register(self, quest: Quest) -> None:
        self._quests[quest.name] = quest

    def get(self, name: str) -> Optional[Quest]:
        return self._quests.get(name)

    def start(self, name: str) -> bool:
        quest = self.get(name)
        if quest:
            quest.start()
            return True
        return False

    def get_active(self) -> List[Quest]:
        return [q for q in self._quests.values() if q.is_active]

    def get_completed(self) -> List[Quest]:
        return [q for q in self._quests.values() if q.is_complete]

    def tick(self) -> None:
        """Check completion for all active quests."""
        for quest in self.get_active():
            quest.check_completion()

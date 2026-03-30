"""
Meta Progression.

Persistent progression between runs: unlocks, currency, and stats.

Layer: 4 (Game/Progression)
Dependencies: core.object
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional, Callable
from core.object import Object


class Unlockable(Object):
    """Represents an unlockable item/upgrade."""

    def __init__(
        self,
        unlock_id: str,
        name: str = "",
        cost: int = 0,
    ):
        super().__init__(name=name or unlock_id)
        self.unlock_id: str = unlock_id
        self.cost: int = cost
        self._is_unlocked: bool = False
        self._on_unlock_callbacks: List[Callable] = []

    @property
    def is_unlocked(self) -> bool:
        return self._is_unlocked

    def unlock(self) -> bool:
        """Attempt to unlock this item. Returns True if newly unlocked."""
        if self._is_unlocked:
            return False
        self._is_unlocked = True
        for cb in self._on_unlock_callbacks:
            cb(self)
        return True

    def on_unlock(self, callback: Callable) -> None:
        """Register a callback for when this item is unlocked."""
        self._on_unlock_callbacks.append(callback)

    def serialize(self) -> Dict[str, Any]:
        data = super().serialize()
        data.update({
            "unlock_id": self.unlock_id,
            "name": self.name,
            "cost": self.cost,
            "is_unlocked": self._is_unlocked,
        })
        return data

    def deserialize(self, data: Dict[str, Any]) -> None:
        super().deserialize(data)
        self.unlock_id = data.get("unlock_id", self.unlock_id)
        self.name = data.get("name", self.name)
        self.cost = data.get("cost", self.cost)
        self._is_unlocked = data.get("is_unlocked", False)


class MetaProgression(Object):
    """
    Tracks persistent meta-progression across all runs.

    Manages currency, unlockables, and aggregate run statistics.
    """

    def __init__(self):
        super().__init__(name="MetaProgression")
        self.currency: int = 0
        self._total_runs: int = 0
        self._best_run_room: int = 0
        self._total_kills: int = 0
        self._unlockables: Dict[str, Unlockable] = {}

    @property
    def total_runs(self) -> int:
        return self._total_runs

    @property
    def best_run_room(self) -> int:
        return self._best_run_room

    @property
    def total_kills(self) -> int:
        return self._total_kills

    def add_currency(self, amount: int) -> None:
        self.currency += amount

    def spend_currency(self, amount: int) -> bool:
        """Attempt to spend currency. Returns True if successful."""
        if amount > self.currency:
            return False
        self.currency -= amount
        return True

    def register_unlockable(self, unlockable: Unlockable) -> None:
        self._unlockables[unlockable.unlock_id] = unlockable

    def get_unlockable(self, unlock_id: str) -> Optional[Unlockable]:
        return self._unlockables.get(unlock_id)

    def try_unlock(self, unlock_id: str) -> bool:
        """Attempt to purchase and unlock an item. Returns True if successful."""
        unlockable = self._unlockables.get(unlock_id)
        if unlockable is None:
            return False
        if not self.spend_currency(unlockable.cost):
            return False
        return unlockable.unlock()

    def update_run_stats(self, rooms_reached: int = 0, kills: int = 0) -> None:
        self._total_runs += 1
        self._best_run_room = max(self._best_run_room, rooms_reached)
        self._total_kills += kills

    def serialize(self) -> Dict[str, Any]:
        data = super().serialize()
        data.update({
            "currency": self.currency,
            "total_runs": self._total_runs,
            "best_run_room": self._best_run_room,
            "total_kills": self._total_kills,
            "unlockables": {
                uid: u.serialize() for uid, u in self._unlockables.items()
            },
        })
        return data

    def deserialize(self, data: Dict[str, Any]) -> None:
        super().deserialize(data)
        self.currency = data.get("currency", 0)
        self._total_runs = data.get("total_runs", 0)
        self._best_run_room = data.get("best_run_room", 0)
        self._total_kills = data.get("total_kills", 0)
        for uid, udata in data.get("unlockables", {}).items():
            unlockable = self._unlockables.get(uid)
            if unlockable:
                unlockable.deserialize(udata)

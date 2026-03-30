"""
Inventory system.

Layer: 4 (Game)
Dependencies: core.object, game.inventory.item
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from core.object import Object
from game.inventory.item import Item


class InventorySlot:
    """A single slot in an inventory."""

    def __init__(self) -> None:
        self.item: Optional[Item] = None
        self.quantity: int = 0

    @property
    def is_empty(self) -> bool:
        return self.item is None

    def clear(self) -> None:
        self.item = None
        self.quantity = 0

    def __repr__(self) -> str:
        if self.is_empty:
            return "InventorySlot(empty)"
        return f"InventorySlot({self.item.name} x{self.quantity})"


class Inventory(Object):
    """
    Fixed-size inventory with slot-based storage.

    Supports adding, removing, and querying items.
    Stackable items auto-stack into existing slots.

    Example:
        >>> inv = Inventory(capacity=20)
        >>> sword = Item(name="Sword", item_type=ItemType.WEAPON)
        >>> inv.add_item(sword)
        True
    """

    def __init__(self, name: str = "Inventory", capacity: int = 20) -> None:
        super().__init__(name=name)
        self._capacity = capacity
        self._slots: List[InventorySlot] = [InventorySlot() for _ in range(capacity)]

    @property
    def capacity(self) -> int:
        return self._capacity

    @property
    def used_slots(self) -> int:
        return sum(1 for s in self._slots if not s.is_empty)

    @property
    def free_slots(self) -> int:
        return self._capacity - self.used_slots

    @property
    def is_full(self) -> bool:
        return self.free_slots == 0

    def add_item(self, item: Item, quantity: int = 1) -> bool:
        """
        Add item to inventory.

        Returns:
            True if added successfully, False if no space.
        """
        if quantity <= 0:
            return False

        # Non-stackable items: each unit needs its own slot
        if not item.stackable and quantity > 1:
            if self.free_slots < quantity:
                return False

        # Try stacking into existing slot
        if item.stackable:
            for slot in self._slots:
                if slot.item and slot.item.name == item.name:
                    space = item.max_stack - slot.quantity
                    if space > 0:
                        add = min(quantity, space)
                        slot.quantity += add
                        quantity -= add
                        if quantity <= 0:
                            return True

        # Place in empty slot
        while quantity > 0:
            empty = next((s for s in self._slots if s.is_empty), None)
            if empty is None:
                return False
            stack = min(quantity, item.max_stack)
            empty.item = item
            empty.quantity = stack
            quantity -= stack

        return True

    def remove_item(self, item_name: str, quantity: int = 1) -> bool:
        """
        Remove item by name.

        Returns:
            True if removed, False if not enough quantity.
        """
        total = self.get_quantity(item_name)
        if total < quantity:
            return False

        remaining = quantity
        for slot in self._slots:
            if slot.item and slot.item.name == item_name:
                take = min(remaining, slot.quantity)
                slot.quantity -= take
                remaining -= take
                if slot.quantity <= 0:
                    slot.clear()
                if remaining <= 0:
                    break
        return True

    def has_item(self, item_name: str) -> bool:
        return self.get_quantity(item_name) > 0

    def get_quantity(self, item_name: str) -> int:
        return sum(s.quantity for s in self._slots if s.item and s.item.name == item_name)

    def get_all_items(self) -> List[Item]:
        return [s.item for s in self._slots if not s.is_empty]

    def clear(self) -> None:
        for slot in self._slots:
            slot.clear()

    def serialize(self) -> Dict[str, Any]:
        data = super().serialize()
        data["capacity"] = self._capacity
        data["slots"] = [
            {"item": s.item.serialize() if s.item else None, "quantity": s.quantity}
            for s in self._slots
        ]
        return data

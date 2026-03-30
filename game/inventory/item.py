"""
Item definition for inventory system.

Layer: 4 (Game)
Dependencies: core.object
"""
from __future__ import annotations
from enum import Enum
from typing import Any, Dict
from core.object import Object


class ItemType(Enum):
    WEAPON = "weapon"
    ARMOR = "armor"
    CONSUMABLE = "consumable"
    QUEST = "quest"
    MISC = "misc"


class Item(Object):
    """
    Base class for all inventory items.

    Attributes:
        item_type: Category of the item.
        description: Human-readable description.
        stackable: Whether multiple can occupy one slot.
        max_stack: Maximum stack size (if stackable).
        weight: Item weight.
        value: Item monetary value.
    """

    def __init__(
        self,
        name: str = "Item",
        item_type: ItemType = ItemType.MISC,
        description: str = "",
        stackable: bool = False,
        max_stack: int = 1,
        weight: float = 0.0,
        value: int = 0,
    ) -> None:
        super().__init__(name=name)
        self.item_type = item_type
        self.description = description
        self.stackable = stackable
        self.max_stack = max_stack if stackable else 1
        self.weight = weight
        self.value = value

    def serialize(self) -> Dict[str, Any]:
        data = super().serialize()
        data["item_type"] = self.item_type.value
        data["description"] = self.description
        data["stackable"] = self.stackable
        data["max_stack"] = self.max_stack
        data["weight"] = self.weight
        data["value"] = self.value
        return data

    def deserialize(self, data: Dict[str, Any]) -> None:
        super().deserialize(data)
        if "item_type" in data:
            self.item_type = ItemType(data["item_type"])
        if "description" in data:
            self.description = data["description"]
        if "stackable" in data:
            self.stackable = data["stackable"]
        if "max_stack" in data:
            self.max_stack = data["max_stack"]
        if "weight" in data:
            self.weight = data["weight"]
        if "value" in data:
            self.value = data["value"]

    def __repr__(self) -> str:
        return f"Item(name={self.name!r}, type={self.item_type.value})"

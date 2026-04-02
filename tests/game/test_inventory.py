"""Tests for inventory system."""
from game.inventory.item import Item, ItemType
from game.inventory.inventory import Inventory


class TestItem:
    def test_item_creation(self):
        item = Item(name="Sword", item_type=ItemType.WEAPON)
        assert item.name == "Sword"
        assert item.item_type == ItemType.WEAPON

    def test_item_defaults(self):
        item = Item()
        assert item.stackable is False
        assert item.max_stack == 1
        assert item.weight == 0.0
        assert item.value == 0

    def test_stackable_item(self):
        item = Item(name="Arrow", stackable=True, max_stack=99)
        assert item.stackable is True
        assert item.max_stack == 99

    def test_non_stackable_max_stack_forced_to_1(self):
        item = Item(name="Sword", stackable=False, max_stack=10)
        assert item.max_stack == 1

    def test_item_serialize(self):
        item = Item(name="Potion", item_type=ItemType.CONSUMABLE, value=50)
        data = item.serialize()
        assert data["item_type"] == "consumable"
        assert data["value"] == 50


class TestInventory:
    def test_inventory_creation(self):
        inv = Inventory(capacity=10)
        assert inv.capacity == 10
        assert inv.used_slots == 0
        assert inv.free_slots == 10

    def test_add_item(self):
        inv = Inventory(capacity=5)
        item = Item(name="Sword")
        assert inv.add_item(item) is True
        assert inv.used_slots == 1

    def test_has_item(self):
        inv = Inventory(capacity=5)
        item = Item(name="Sword")
        inv.add_item(item)
        assert inv.has_item("Sword") is True
        assert inv.has_item("Shield") is False

    def test_remove_item(self):
        inv = Inventory(capacity=5)
        item = Item(name="Sword")
        inv.add_item(item)
        assert inv.remove_item("Sword") is True
        assert inv.has_item("Sword") is False

    def test_stackable_items(self):
        inv = Inventory(capacity=5)
        arrow = Item(name="Arrow", stackable=True, max_stack=99)
        inv.add_item(arrow, quantity=50)
        inv.add_item(arrow, quantity=30)
        assert inv.get_quantity("Arrow") == 80
        assert inv.used_slots == 1

    def test_inventory_full(self):
        inv = Inventory(capacity=2)
        inv.add_item(Item(name="A"))
        inv.add_item(Item(name="B"))
        assert inv.is_full is True
        assert inv.add_item(Item(name="C")) is False

    def test_remove_more_than_available(self):
        inv = Inventory(capacity=5)
        inv.add_item(Item(name="Sword"))
        assert inv.remove_item("Sword", quantity=5) is False

    def test_clear(self):
        inv = Inventory(capacity=5)
        inv.add_item(Item(name="Sword"))
        inv.clear()
        assert inv.used_slots == 0

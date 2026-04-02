"""
Tests for Blackboard - AI Shared State.

Blackboard provides a key-value store for AI systems
to share data and communicate.

Layer: 5 (Scripting)
Dependencies: core.object
"""

from scripting.blackboard import Blackboard


class TestBlackboardBasics:
    """Test Blackboard basic functionality."""

    def test_blackboard_creation(self):
        """Blackboard should be creatable."""
        bb = Blackboard()
        assert bb is not None

    def test_blackboard_has_data(self):
        """Blackboard should have data dictionary."""
        bb = Blackboard()
        assert hasattr(bb, 'data')

    def test_blackboard_empty_initially(self):
        """Blackboard should be empty initially."""
        bb = Blackboard()
        assert len(bb.data) == 0


class TestBlackboardGetSet:
    """Test Blackboard get/set operations."""

    def test_set_value(self):
        """Blackboard should store values."""
        bb = Blackboard()
        bb.set("target", "player")
        assert bb.data["target"] == "player"

    def test_get_value(self):
        """Blackboard should retrieve values."""
        bb = Blackboard()
        bb.set("target", "player")
        assert bb.get("target") == "player"

    def test_get_missing_returns_none(self):
        """Getting missing key should return None."""
        bb = Blackboard()
        assert bb.get("missing") is None

    def test_get_with_default(self):
        """Getting missing key should return default."""
        bb = Blackboard()
        assert bb.get("missing", default="default") == "default"

    def test_set_overwrites(self):
        """Setting same key should overwrite."""
        bb = Blackboard()
        bb.set("count", 1)
        bb.set("count", 2)
        assert bb.get("count") == 2

    def test_set_none_value(self):
        """Should be able to set None as value."""
        bb = Blackboard()
        bb.set("empty", None)
        assert bb.get("empty") is None


class TestBlackboardHasKey:
    """Test Blackboard has operation."""

    def test_has_key_true(self):
        """has should return True for existing key."""
        bb = Blackboard()
        bb.set("target", "player")
        assert bb.has("target") is True

    def test_has_key_false(self):
        """has should return False for missing key."""
        bb = Blackboard()
        assert bb.has("missing") is False

    def test_has_none_value_true(self):
        """has should return True even for None value."""
        bb = Blackboard()
        bb.set("empty", None)
        assert bb.has("empty") is True


class TestBlackboardDelete:
    """Test Blackboard delete operations."""

    def test_remove_key(self):
        """remove should delete key."""
        bb = Blackboard()
        bb.set("target", "player")
        bb.remove("target")
        assert not bb.has("target")

    def test_remove_missing_no_error(self):
        """remove missing key should not raise."""
        bb = Blackboard()
        bb.remove("missing")  # Should not raise

    def test_clear(self):
        """clear should remove all keys."""
        bb = Blackboard()
        bb.set("a", 1)
        bb.set("b", 2)
        bb.set("c", 3)
        bb.clear()
        assert len(bb.data) == 0


class TestBlackboardListeners:
    """Test Blackboard change notification."""

    def test_on_change_listener(self):
        """Listener should be called on set."""
        bb = Blackboard()
        changes = []

        def on_change(key, value):
            changes.append((key, value))

        bb.on_change(on_change)
        bb.set("target", "player")

        assert len(changes) == 1
        assert changes[0] == ("target", "player")

    def test_multiple_listeners(self):
        """Multiple listeners should all be called."""
        bb = Blackboard()
        changes1 = []
        changes2 = []

        bb.on_change(lambda k, v: changes1.append((k, v)))
        bb.on_change(lambda k, v: changes2.append((k, v)))

        bb.set("target", "player")

        assert len(changes1) == 1
        assert len(changes2) == 1

    def test_listener_not_called_on_remove(self):
        """Listener should not be called on remove."""
        bb = Blackboard()
        changes = []

        bb.on_change(lambda k, v: changes.append((k, v)))
        bb.set("target", "player")
        bb.remove("target")

        # Only called once (for set, not remove)
        assert len(changes) == 1


class TestBlackboardKeys:
    """Test Blackboard key operations."""

    def test_keys_method(self):
        """keys should return all keys."""
        bb = Blackboard()
        bb.set("a", 1)
        bb.set("b", 2)

        keys = bb.keys()
        assert "a" in keys
        assert "b" in keys
        assert len(keys) == 2

    def test_values_method(self):
        """values should return all values."""
        bb = Blackboard()
        bb.set("a", 1)
        bb.set("b", 2)

        values = bb.values()
        assert 1 in values
        assert 2 in values

    def test_items_method(self):
        """items should return key-value pairs."""
        bb = Blackboard()
        bb.set("a", 1)
        bb.set("b", 2)

        items = dict(bb.items())
        assert items["a"] == 1
        assert items["b"] == 2


class TestBlackboardNestedValues:
    """Test Blackboard with nested values."""

    def test_dict_value(self):
        """Should store dict values."""
        bb = Blackboard()
        bb.set("config", {"speed": 10, "health": 100})
        config = bb.get("config")
        assert config["speed"] == 10

    def test_list_value(self):
        """Should store list values."""
        bb = Blackboard()
        bb.set("targets", ["player1", "player2"])
        targets = bb.get("targets")
        assert len(targets) == 2

    def test_update_nested_value(self):
        """Should be able to update nested values."""
        bb = Blackboard()
        bb.set("config", {"speed": 10})
        config = bb.get("config")
        config["speed"] = 20
        bb.set("config", config)
        assert bb.get("config")["speed"] == 20


class TestBlackboardSerialization:
    """Test Blackboard serialization."""

    def test_serialize(self):
        """Blackboard should serialize data."""
        bb = Blackboard()
        bb.set("target", "player")
        bb.set("count", 5)

        data = bb.serialize()
        assert data["data"]["target"] == "player"
        assert data["data"]["count"] == 5

    def test_deserialize(self):
        """Blackboard should deserialize data."""
        bb = Blackboard()
        bb.deserialize({
            "data": {
                "target": "enemy",
                "count": 10
            }
        })

        assert bb.get("target") == "enemy"
        assert bb.get("count") == 10


class TestBlackboardScope:
    """Test Blackboard scoped keys."""

    def test_get_with_scope(self):
        """Should support scoped keys with dot notation."""
        bb = Blackboard()
        bb.set("enemy.health", 100)
        bb.set("enemy.speed", 5)

        assert bb.get("enemy.health") == 100
        assert bb.get("enemy.speed") == 5

    def test_get_scope_dict(self):
        """get_scope should return all keys in scope."""
        bb = Blackboard()
        bb.set("enemy.health", 100)
        bb.set("enemy.speed", 5)
        bb.set("player.health", 50)

        enemy = bb.get_scope("enemy")
        assert enemy == {"health": 100, "speed": 5}

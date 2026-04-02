"""Tests for game.progression module."""
from game.progression.meta import MetaProgression, Unlockable


class TestUnlockable:
    def test_create(self):
        u = Unlockable(unlock_id="sword_1", name="Iron Sword", cost=100)
        assert u.is_unlocked is False
        assert u.cost == 100

    def test_unlock(self):
        u = Unlockable(unlock_id="sword_1", name="Iron Sword")
        result = u.unlock()
        assert result is True
        assert u.is_unlocked is True

    def test_double_unlock(self):
        u = Unlockable(unlock_id="sword_1", name="Iron Sword")
        u.unlock()
        result = u.unlock()
        assert result is False

    def test_on_unlock_callback(self):
        u = Unlockable(unlock_id="sword_1", name="Iron Sword")
        unlocked = []
        u.on_unlock(lambda x: unlocked.append(x))
        u.unlock()
        assert len(unlocked) == 1

    def test_serialize(self):
        u = Unlockable(unlock_id="test", name="Test", cost=50)
        data = u.serialize()
        assert data["unlock_id"] == "test"
        assert data["cost"] == 50


class TestMetaProgression:
    def test_create(self):
        mp = MetaProgression()
        assert mp.currency == 0
        assert mp.total_runs == 0

    def test_add_currency(self):
        mp = MetaProgression()
        mp.add_currency(100)
        assert mp.currency == 100

    def test_spend_currency(self):
        mp = MetaProgression()
        mp.add_currency(100)
        result = mp.spend_currency(50)
        assert result is True
        assert mp.currency == 50

    def test_spend_insufficient(self):
        mp = MetaProgression()
        result = mp.spend_currency(50)
        assert result is False
        assert mp.currency == 0

    def test_register_unlockable(self):
        mp = MetaProgression()
        u = Unlockable(unlock_id="u1", name="Item1", cost=100)
        mp.register_unlockable(u)
        assert mp.get_unlockable("u1") is u

    def test_try_unlock(self):
        mp = MetaProgression()
        mp.add_currency(200)
        u = Unlockable(unlock_id="u1", name="Item1", cost=100)
        mp.register_unlockable(u)
        result = mp.try_unlock("u1")
        assert result is True
        assert u.is_unlocked is True
        assert mp.currency == 100

    def test_try_unlock_insufficient(self):
        mp = MetaProgression()
        mp.add_currency(50)
        u = Unlockable(unlock_id="u1", name="Item1", cost=100)
        mp.register_unlockable(u)
        result = mp.try_unlock("u1")
        assert result is False

    def test_update_run_stats(self):
        mp = MetaProgression()
        mp.update_run_stats(rooms_reached=5, kills=20)
        assert mp.total_runs == 1
        assert mp.best_run_room == 5
        assert mp.total_kills == 20

    def test_best_run_room(self):
        mp = MetaProgression()
        mp.update_run_stats(3, 10)
        mp.update_run_stats(7, 20)
        assert mp.best_run_room == 7

    def test_serialize_deserialize(self):
        mp = MetaProgression()
        mp.add_currency(500)
        u = Unlockable(unlock_id="u1", name="Item1", cost=100)
        mp.register_unlockable(u)
        mp.try_unlock("u1")
        data = mp.serialize()
        mp2 = MetaProgression()
        u2 = Unlockable(unlock_id="u1", name="Item1", cost=100)
        mp2.register_unlockable(u2)
        mp2.deserialize(data)
        assert mp2.currency == 400
        assert mp2.total_runs == 0

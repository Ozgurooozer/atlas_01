"""Tests for save system."""
import pytest
from game.save.save import SaveSystem, SaveData
from hal.headless import MemoryFilesystem


class TestSaveData:
    def test_save_data_creation(self):
        sd = SaveData(slot=0)
        assert sd.slot == 0
        assert sd.data == {}

    def test_set_get(self):
        sd = SaveData()
        sd.set("level", 5)
        assert sd.get("level") == 5

    def test_get_default(self):
        sd = SaveData()
        assert sd.get("missing", 42) == 42

    def test_to_dict(self):
        sd = SaveData(slot=1)
        sd.set("hp", 100)
        d = sd.to_dict()
        assert d["slot"] == 1
        assert d["data"]["hp"] == 100

    def test_from_dict(self):
        d = {"slot": 2, "version": 1, "timestamp": "", "data": {"score": 999}}
        sd = SaveData.from_dict(d)
        assert sd.slot == 2
        assert sd.get("score") == 999


class TestSaveSystem:
    def test_save_and_load(self):
        fs = MemoryFilesystem()
        save = SaveSystem(filesystem=fs)
        assert save.save(slot=0, data={"level": 3}) is True
        loaded = save.load(slot=0)
        assert loaded is not None
        assert loaded.get("level") == 3

    def test_slot_not_exists(self):
        fs = MemoryFilesystem()
        save = SaveSystem(filesystem=fs)
        assert save.slot_exists(0) is False

    def test_slot_exists_after_save(self):
        fs = MemoryFilesystem()
        save = SaveSystem(filesystem=fs)
        save.save(slot=0, data={})
        assert save.slot_exists(0) is True

    def test_load_nonexistent(self):
        fs = MemoryFilesystem()
        save = SaveSystem(filesystem=fs)
        assert save.load(slot=99) is None

    def test_no_filesystem(self):
        save = SaveSystem()
        assert save.save(slot=0, data={}) is False
        assert save.load(slot=0) is None

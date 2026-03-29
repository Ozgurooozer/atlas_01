"""
Save/Load system.

Layer: 4 (Game)
Dependencies: core.object, core.serializer, hal.interfaces
"""
from __future__ import annotations
from typing import Any, Dict, Optional, TYPE_CHECKING
from core.object import Object
from core.serializer import Serializer

if TYPE_CHECKING:
    from hal.interfaces import IFilesystem


class SaveData:
    """Container for a single save slot's data."""

    def __init__(self, slot: int = 0) -> None:
        self.slot = slot
        self.data: Dict[str, Any] = {}
        self.timestamp: str = ""
        self.version: int = 1

    def set(self, key: str, value: Any) -> None:
        self.data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "slot": self.slot,
            "version": self.version,
            "timestamp": self.timestamp,
            "data": self.data,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "SaveData":
        sd = cls(slot=d.get("slot", 0))
        sd.version = d.get("version", 1)
        sd.timestamp = d.get("timestamp", "")
        sd.data = d.get("data", {})
        return sd


class SaveSystem(Object):
    """
    Save/Load system with slot support.

    Example:
        >>> save = SaveSystem(filesystem=fs)
        >>> save.save(slot=0, data={"level": 1, "hp": 100})
        >>> loaded = save.load(slot=0)
        >>> loaded.get("level")
        1
    """

    def __init__(
        self,
        filesystem: Optional["IFilesystem"] = None,
        save_dir: str = "saves",
    ) -> None:
        super().__init__(name="SaveSystem")
        self._filesystem = filesystem
        self._save_dir = save_dir
        self._serializer = Serializer()
        self._cache: Dict[int, SaveData] = {}

    @property
    def filesystem(self) -> Optional["IFilesystem"]:
        return self._filesystem

    @filesystem.setter
    def filesystem(self, value: Optional["IFilesystem"]) -> None:
        self._filesystem = value

    def _slot_path(self, slot: int) -> str:
        return f"{self._save_dir}/save_{slot:02d}.json"

    def save(self, slot: int, data: Dict[str, Any]) -> bool:
        """
        Save data to slot.

        Returns:
            True if saved successfully.
        """
        if self._filesystem is None:
            return False

        sd = SaveData(slot=slot)
        sd.data = data
        self._cache[slot] = sd

        try:
            json_str = self._serializer.serialize(sd.to_dict())
            self._filesystem.write_file(self._slot_path(slot), json_str.encode())
            return True
        except Exception:
            return False

    def load(self, slot: int) -> Optional[SaveData]:
        """
        Load data from slot.

        Returns:
            SaveData or None if slot doesn't exist.
        """
        if slot in self._cache:
            return self._cache[slot]

        if self._filesystem is None:
            return None

        path = self._slot_path(slot)
        if not self._filesystem.file_exists(path):
            return None

        try:
            raw = self._filesystem.read_file(path)
            d = self._serializer.deserialize(raw.decode())
            sd = SaveData.from_dict(d)
            self._cache[slot] = sd
            return sd
        except Exception:
            return None

    def delete(self, slot: int) -> bool:
        """Delete a save slot."""
        self._cache.pop(slot, None)
        if self._filesystem is None:
            return False
        path = self._slot_path(slot)
        if self._filesystem.file_exists(path):
            try:
                self._filesystem.delete_file(path)
                return True
            except Exception:
                return False
        return False

    def slot_exists(self, slot: int) -> bool:
        if slot in self._cache:
            return True
        if self._filesystem is None:
            return False
        return self._filesystem.file_exists(self._slot_path(slot))

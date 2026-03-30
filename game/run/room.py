"""
Room System.

Represents a single room in the run (combat, reward, boss, start, shop, etc.).

Layer: 4 (Game/Run)
Dependencies: core.object
"""
from __future__ import annotations
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Callable
from core.object import Object


class RoomType(Enum):
    START = auto()
    COMBAT = auto()
    REWARD = auto()
    SHOP = auto()
    BOSS = auto()
    TREASURE = auto()
    REST = auto()


class Room(Object):
    """Represents a single room in a run."""

    def __init__(
        self,
        room_type: RoomType = RoomType.COMBAT,
        room_id: int = 0,
        seed: int = 0,
    ):
        super().__init__(name=f"Room_{room_type.name}_{room_id}")
        self.room_type: RoomType = room_type
        self.room_id: int = room_id
        self.seed: int = seed
        self.is_cleared: bool = False
        self.is_visited: bool = False
        self.template_name: str = ""
        self.template_width: int = 0
        self.template_height: int = 0
        self._enemies: list = []
        self._rewards: list = []
        self._next_rooms: List[Room] = []
        self._on_enter_callbacks: List[Callable] = []
        self._on_clear_callbacks: List[Callable] = []

    @property
    def enemies(self) -> list:
        return list(self._enemies)

    @property
    def rewards(self) -> list:
        return list(self._rewards)

    @property
    def next_rooms(self) -> List[Room]:
        return list(self._next_rooms)

    @property
    def has_next(self) -> bool:
        return len(self._next_rooms) > 0

    def add_enemy(self, enemy) -> None:
        self._enemies.append(enemy)

    def add_reward(self, reward) -> None:
        self._rewards.append(reward)

    def add_next_room(self, room: Room) -> None:
        self._next_rooms.append(room)

    def clear_room(self) -> None:
        self.is_cleared = True
        for cb in self._on_clear_callbacks:
            cb(self)

    def visit(self) -> None:
        self.is_visited = True
        for cb in self._on_enter_callbacks:
            cb(self)

    def on_enter(self, callback: Callable) -> None:
        self._on_enter_callbacks.append(callback)

    def on_clear(self, callback: Callable) -> None:
        self._on_clear_callbacks.append(callback)

    def serialize(self) -> Dict[str, Any]:
        data = super().serialize()
        data.update({
            "room_type": self.room_type.name,
            "room_id": self.room_id,
            "seed": self.seed,
            "is_cleared": self.is_cleared,
            "is_visited": self.is_visited,
            "template_name": self.template_name,
            "template_width": self.template_width,
            "template_height": self.template_height,
        })
        return data

    def deserialize(self, data: Dict[str, Any]) -> None:
        super().deserialize(data)
        self.room_type = RoomType[data.get("room_type", "COMBAT")]
        self.room_id = data.get("room_id", 0)
        self.seed = data.get("seed", 0)
        self.is_cleared = data.get("is_cleared", False)
        self.is_visited = data.get("is_visited", False)
        self.template_name = data.get("template_name", "")
        self.template_width = data.get("template_width", 0)
        self.template_height = data.get("template_height", 0)


class RoomGraph(Object):
    """Generates and manages room graphs for runs."""

    def __init__(self, seed: int = 0):
        super().__init__(name="RoomGraph")
        self.seed: int = seed
        self.rooms: List[Room] = []
        self._current_index: int = -1

    @property
    def current_room(self) -> Optional[Room]:
        if 0 <= self._current_index < len(self.rooms):
            return self.rooms[self._current_index]
        return None

    @property
    def current_index(self) -> int:
        return self._current_index

    @property
    def is_finished(self) -> bool:
        if self._current_index < 0:
            return False  # Not started yet
        if self.current_room is None:
            return True
        return self.current_room.room_type == RoomType.BOSS and self.current_room.is_cleared

    def generate(self, room_count: int = 10) -> RoomGraph:
        """Generate a room graph with the given count."""
        import random
        rng = random.Random(self.seed)
        self.rooms.clear()
        self._current_index = -1

        for i in range(room_count):
            if i == 0:
                rtype = RoomType.START
            elif i == room_count - 1:
                rtype = RoomType.BOSS
            elif room_count >= 4 and i == room_count - 3:
                rtype = RoomType.REWARD
            elif i % 4 == 2:
                rtype = rng.choice([RoomType.SHOP, RoomType.REST, RoomType.TREASURE])
            else:
                rtype = RoomType.COMBAT

            room = Room(room_type=rtype, room_id=i, seed=rng.randint(0, 999999))
            self.rooms.append(room)

        # Link rooms
        for i in range(len(self.rooms) - 1):
            self.rooms[i].add_next_room(self.rooms[i + 1])

        return self

    def generate_game_rng(self, room_count: int = 10) -> RoomGraph:
        """Generate room graph using GameRNG (no global random)."""
        from game.run.game_rng import GameRNG
        rng = GameRNG(seed=self.seed)
        non_combat = [RoomType.SHOP, RoomType.REST, RoomType.TREASURE]

        self.rooms.clear()
        self._current_index = -1

        for i in range(room_count):
            if i == 0:
                rtype = RoomType.START
            elif i == room_count - 1:
                rtype = RoomType.BOSS
            elif room_count >= 4 and i == room_count - 3:
                rtype = RoomType.REWARD
            elif i % 4 == 2:
                rtype = rng.choice(non_combat)
            else:
                rtype = RoomType.COMBAT

            room_seed = GameRNG.room_seed(self.seed, i)
            room = Room(room_type=rtype, room_id=i, seed=room_seed)
            self.rooms.append(room)

        for i in range(len(self.rooms) - 1):
            self.rooms[i].add_next_room(self.rooms[i + 1])

        return self

    def advance(self) -> Optional[Room]:
        """Advance to next room. Returns the new room or None if finished."""
        if self.is_finished:
            return None
        self._current_index += 1
        room = self.current_room
        if room:
            room.visit()
        return room

    def reset(self) -> None:
        self._current_index = -1
        for room in self.rooms:
            room.is_cleared = False
            room.is_visited = False

    def serialize(self) -> Dict[str, Any]:
        data = super().serialize()
        data.update({
            "seed": self.seed,
            "current_index": self._current_index,
            "rooms": [r.serialize() for r in self.rooms],
        })
        return data

    def deserialize(self, data: Dict[str, Any]) -> None:
        super().deserialize(data)
        self.seed = data.get("seed", 0)
        self._current_index = data.get("current_index", -1)
        self.rooms.clear()
        for room_data in data.get("rooms", []):
            room = Room()
            room.deserialize(room_data)
            self.rooms.append(room)

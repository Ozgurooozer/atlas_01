"""
Run Controller.

Manages the run lifecycle: start, tick, death, reward, next-room, end.

Layer: 4 (Game/Run)
Dependencies: core.object, game.run.room
"""
from __future__ import annotations
from enum import Enum, auto
from typing import Optional, Callable, Dict, Any, List
from core.object import Object
from game.run.room import RoomGraph, Room, RoomType


class RunPhase(Enum):
    IDLE = auto()
    RUNNING = auto()
    DEATH = auto()
    REWARD = auto()
    VICTORY = auto()
    PAUSED = auto()


class RunController(Object):
    """
    Controls the run lifecycle.

    Single game loop contract:
    start_run -> (tick -> combat_clear -> reward_select -> next_room)* -> boss_clear -> victory
    Any death -> death_screen -> restart_run
    """

    def __init__(self, seed: int = 42):
        super().__init__(name="RunController")
        self.seed: int = seed
        self.phase: RunPhase = RunPhase.IDLE
        self.room_graph: Optional[RoomGraph] = None
        self.run_number: int = 0
        self._run_time: float = 0.0
        self._room_clear_time: float = 0.0
        self._death_count: int = 0
        self._kill_count: int = 0
        self._on_phase_change: List[Callable] = []
        self._on_room_enter: List[Callable] = []
        self._on_room_clear: List[Callable] = []
        self._on_death: List[Callable] = []
        self._on_reward: List[Callable] = []
        self._on_victory: List[Callable] = []
        self._pending_rewards: list = []

    @property
    def current_room(self) -> Optional[Room]:
        if self.room_graph:
            return self.room_graph.current_room
        return None

    @property
    def stats(self) -> Dict[str, Any]:
        return {
            "run_number": self.run_number,
            "run_time": self._run_time,
            "death_count": self._death_count,
            "kill_count": self._kill_count,
            "room_index": self.room_graph.current_index if self.room_graph else -1,
            "total_rooms": len(self.room_graph.rooms) if self.room_graph else 0,
        }

    def start_run(self, seed: int | None = None) -> Room:
        """Start a new run."""
        if seed is not None:
            self.seed = seed
        self.run_number += 1
        self._run_time = 0.0
        self._death_count = 0
        self._kill_count = 0
        self._pending_rewards.clear()

        self.room_graph = RoomGraph(seed=self.seed).generate()
        self._set_phase(RunPhase.RUNNING)

        room = self.room_graph.advance()
        if room:
            self._notify_room_enter(room)
        return room

    def restart_run(self) -> Room:
        """Restart after death."""
        self._death_count += 1
        return self.start_run()

    def tick(self, dt: float) -> None:
        """Tick the run controller."""
        if self.phase == RunPhase.RUNNING:
            self._run_time += dt

    def on_enemy_killed(self) -> None:
        self._kill_count += 1

    def on_room_cleared(self) -> None:
        """Called when current room is cleared."""
        room = self.current_room
        if room:
            room.clear_room()
            self._room_clear_time = self._run_time
            self._notify_room_clear(room)

            # Check if boss room
            if room.room_type == RoomType.BOSS:
                self._set_phase(RunPhase.VICTORY)
                return

            # Check for rewards
            if room.room_type == RoomType.REWARD or room.rewards:
                self._pending_rewards = list(room.rewards)
                self._set_phase(RunPhase.REWARD)
                return

            # Auto-advance for non-combat rooms
            if room.room_type in (RoomType.START, RoomType.REST, RoomType.SHOP, RoomType.TREASURE):
                self.advance_room()

    def on_death(self) -> None:
        self._set_phase(RunPhase.DEATH)
        for cb in self._on_death:
            cb()

    def select_reward(self, reward) -> None:
        """Player selects a reward. Advances to next room."""
        self._pending_rewards.clear()
        self._set_phase(RunPhase.RUNNING)
        self.advance_room()

    def skip_reward(self) -> None:
        """Skip reward selection."""
        self._pending_rewards.clear()
        self._set_phase(RunPhase.RUNNING)
        self.advance_room()

    def advance_room(self) -> Optional[Room]:
        """Manually advance to next room."""
        if not self.room_graph:
            return None
        room = self.room_graph.advance()
        if room is None:
            self._set_phase(RunPhase.VICTORY)
        else:
            self._notify_room_enter(room)
        return room

    def pause(self) -> None:
        if self.phase == RunPhase.RUNNING:
            self._set_phase(RunPhase.PAUSED)

    def resume(self) -> None:
        if self.phase == RunPhase.PAUSED:
            self._set_phase(RunPhase.RUNNING)

    def _set_phase(self, phase: RunPhase) -> None:
        old = self.phase
        self.phase = phase
        for cb in self._on_phase_change:
            cb(old, phase)

    def _notify_room_enter(self, room: Room) -> None:
        for cb in self._on_room_enter:
            cb(room)

    def _notify_room_clear(self, room: Room) -> None:
        for cb in self._on_room_clear:
            cb(room)

    # Callback registration
    def on_phase_change(self, callback: Callable) -> None:
        self._on_phase_change.append(callback)

    def on_room_enter(self, callback: Callable) -> None:
        self._on_room_enter.append(callback)

    def on_room_clear(self, callback: Callable) -> None:
        self._on_room_clear.append(callback)

    def register_on_death(self, callback: Callable) -> None:
        self._on_death.append(callback)

    def on_reward(self, callback: Callable) -> None:
        self._on_reward.append(callback)

    def on_victory(self, callback: Callable) -> None:
        self._on_victory.append(callback)

    def serialize(self) -> Dict[str, Any]:
        data = super().serialize()
        data.update({
            "seed": self.seed,
            "phase": self.phase.name,
            "run_number": self.run_number,
            "run_time": self._run_time,
            "death_count": self._death_count,
            "kill_count": self._kill_count,
        })
        if self.room_graph:
            data["room_graph"] = self.room_graph.serialize()
        return data

"""
Room Transition Manager.

Manages fade transitions between rooms with state machine and callbacks.
States: IDLE -> FADING_OUT -> FADING_IN -> IDLE

Layer: 4 (Game/Run)
Dependencies: core.object
"""
from __future__ import annotations
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional

from core.object import Object


class TransitionState(Enum):
    """States for room transitions."""
    IDLE = auto()
    FADING_OUT = auto()
    FADING_IN = auto()


class RoomTransitionManager(Object):
    """Manages room-to-room transitions with fade effects."""

    def __init__(self, name: str | None = None):
        """Create a new RoomTransitionManager."""
        super().__init__(name=name or "RoomTransitionManager")
        self._state: TransitionState = TransitionState.IDLE
        self._progress: float = 0.0
        self._fade_duration: float = 0.5
        self._target_room: str = ""
        self._direction: str = "right"
        self._on_start_cbs: List[Callable] = []
        self._on_complete_cbs: List[Callable] = []

    @property
    def state(self) -> TransitionState:
        """Get the current transition state."""
        return self._state

    @property
    def is_transitioning(self) -> bool:
        """Check if a transition is in progress."""
        return self._state != TransitionState.IDLE

    @property
    def transition_progress(self) -> float:
        """Get the current transition progress (0.0 to 1.0)."""
        return self._progress

    @property
    def fade_duration(self) -> float:
        """Get the fade duration in seconds."""
        return self._fade_duration

    @fade_duration.setter
    def fade_duration(self, value: float) -> None:
        """Set the fade duration in seconds."""
        self._fade_duration = value

    @property
    def target_room(self) -> str:
        """Get the target room name."""
        return self._target_room

    @property
    def direction(self) -> str:
        """Get the transition direction."""
        return self._direction

    @staticmethod
    def get_idle_state() -> TransitionState:
        """Return the IDLE state constant."""
        return TransitionState.IDLE

    def transition_to(self, room_name: str, direction: str = "right") -> None:
        """Start a transition to the given room.

        Args:
            room_name: Name of the target room.
            direction: Direction of the transition ('right', 'left', 'up', 'down').

        Raises:
            RuntimeError: If already transitioning.
        """
        if self._state != TransitionState.IDLE:
            raise RuntimeError("Cannot start transition while one is active")
        self._target_room = room_name
        self._direction = direction
        self._state = TransitionState.FADING_OUT
        self._progress = 0.0
        self._fire_start(room_name)

    def tick(self, dt: float) -> None:
        """Update transition progress by dt seconds.

        Args:
            dt: Time delta in seconds.
        """
        if self._state == TransitionState.IDLE:
            return
        if self._fade_duration <= 0:
            self._complete_transition()
            return
        step = dt / self._fade_duration
        if self._state == TransitionState.FADING_OUT:
            self._progress += step
            if self._progress >= 1.0:
                self._progress = 1.0
                self._state = TransitionState.FADING_IN
        elif self._state == TransitionState.FADING_IN:
            self._progress -= step
            if self._progress <= 0.0:
                self._complete_transition()

    def cancel(self) -> None:
        """Cancel the active transition without firing complete."""
        if self._state == TransitionState.IDLE:
            return
        self._state = TransitionState.IDLE
        self._progress = 0.0

    def on_transition_start(self, callback: Callable) -> None:
        """Register a callback for when a transition starts.

        Args:
            callback: Function receiving room_name (str).
        """
        self._on_start_cbs.append(callback)

    def on_transition_complete(self, callback: Callable) -> None:
        """Register a callback for when a transition completes.

        Args:
            callback: Function receiving room_name (str).
        """
        self._on_complete_cbs.append(callback)

    def _fire_start(self, room_name: str) -> None:
        """Fire all start callbacks."""
        for cb in self._on_start_cbs:
            cb(room_name)

    def _fire_complete(self, room_name: str) -> None:
        """Fire all complete callbacks."""
        for cb in self._on_complete_cbs:
            cb(room_name)

    def _complete_transition(self) -> None:
        """Finish the transition and return to IDLE."""
        room_name = self._target_room
        self._state = TransitionState.IDLE
        self._progress = 0.0
        self._fire_complete(room_name)

    def serialize(self) -> Dict[str, Any]:
        """Serialize the manager to a dictionary."""
        data = super().serialize()
        data.update({
            "state": self._state.name,
            "progress": self._progress,
            "fade_duration": self._fade_duration,
            "target_room": self._target_room,
            "direction": self._direction,
        })
        return data

    def deserialize(self, data: Dict[str, Any]) -> None:
        """Restore the manager from a dictionary.

        Args:
            data: Dictionary containing manager state.
        """
        super().deserialize(data)
        state_name = data.get("state", "IDLE")
        self._state = TransitionState[state_name]
        self._progress = data.get("progress", 0.0)
        self._fade_duration = data.get("fade_duration", 0.5)
        self._target_room = data.get("target_room", "")
        self._direction = data.get("direction", "right")

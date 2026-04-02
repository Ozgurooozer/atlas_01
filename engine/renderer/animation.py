"""
Engine Layer (Layer 2) - Animation

Frame-based sprite animation system.

Animation:   a named sequence of UV frames + durations
AnimationPlayer: drives a Sprite's UV region over time

Layer: 2 (Engine)
Dependencies: engine.renderer.texture
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional, Callable

from engine.renderer.texture import UVRegion


@dataclass
class AnimationFrame:
    """Single frame: UV region + display duration."""
    uv: UVRegion
    duration: float = 1.0 / 12.0  # 12 fps default

    def __post_init__(self) -> None:
        if self.duration <= 0:
            raise ValueError("Frame duration must be positive")


class Animation:
    """
    Named sequence of UV frames.

    Supports looping, ping-pong, one-shot.
    Can attach event callbacks at specific frames.
    """

    LOOP = "loop"
    ONE_SHOT = "one_shot"
    PING_PONG = "ping_pong"

    def __init__(
        self,
        name: str,
        frames: List[AnimationFrame],
        mode: str = "loop",
    ) -> None:
        if not frames:
            raise ValueError("Animation must have at least one frame")
        self._name = name
        self._frames = list(frames)
        self._mode = mode
        self._events: Dict[int, List[Callable]] = {}

    @property
    def name(self) -> str:
        return self._name

    @property
    def frames(self) -> List[AnimationFrame]:
        return self._frames

    @property
    def frame_count(self) -> int:
        return len(self._frames)

    @property
    def mode(self) -> str:
        return self._mode

    @property
    def total_duration(self) -> float:
        return sum(f.duration for f in self._frames)

    def add_event(self, frame_index: int, callback: Callable) -> None:
        """Register a callback to fire when a frame is entered."""
        self._events.setdefault(frame_index, []).append(callback)

    def get_events(self, frame_index: int) -> List[Callable]:
        return self._events.get(frame_index, [])

    def __repr__(self) -> str:
        return f"Animation({self._name!r}, {self.frame_count} frames, {self._mode})"


class AnimationPlayer:
    """
    Drives animation playback on a Sprite or UV consumer.

    Usage:
        player = AnimationPlayer()
        player.play(animation)
        player.update(dt)
        sprite.uv = player.current_uv
    """

    def __init__(self) -> None:
        self._animation: Optional[Animation] = None
        self._time: float = 0.0
        self._frame_index: int = 0
        self._direction: int = 1  # 1 = forward, -1 = backward
        self._playing: bool = False
        self._finished: bool = False
        self._speed: float = 1.0
        self._on_finish: Optional[Callable] = None
        self._on_frame_change: Optional[Callable[[int], None]] = None

    def play(self, animation: Animation, reset: bool = True) -> None:
        """Start or resume animation playback."""
        if animation is self._animation and not reset:
            self._playing = True
            return
        self._animation = animation
        self._playing = True
        self._finished = False
        self._direction = 1
        if reset:
            self._time = 0.0
            self._frame_index = 0

    def pause(self) -> None:
        self._playing = False

    def resume(self) -> None:
        self._playing = True

    def stop(self) -> None:
        self._playing = False
        self._time = 0.0
        self._frame_index = 0
        self._finished = False

    def set_frame(self, index: int) -> None:
        """Jump to a specific frame index."""
        if self._animation is None:
            return
        self._frame_index = index % self._animation.frame_count
        self._time = 0.0

    @property
    def is_playing(self) -> bool:
        return self._playing

    @property
    def is_finished(self) -> bool:
        return self._finished

    @property
    def current_frame_index(self) -> int:
        return self._frame_index

    @property
    def speed(self) -> float:
        return self._speed

    @speed.setter
    def speed(self, value: float) -> None:
        self._speed = max(0.0, value)

    @property
    def current_uv(self) -> Optional[UVRegion]:
        if self._animation is None:
            return None
        return self._animation.frames[self._frame_index].uv

    def on_finish(self, callback: Callable) -> None:
        self._on_finish = callback

    def on_frame_change(self, callback: Callable[[int], None]) -> None:
        self._on_frame_change = callback

    def update(self, dt: float) -> None:
        """Advance animation by dt seconds."""
        if not self._playing or self._animation is None or self._finished:
            return

        self._time += dt * self._speed
        anim = self._animation
        current_frame = anim.frames[self._frame_index]

        if self._time >= current_frame.duration:
            self._time -= current_frame.duration
            self._advance_frame()

    def _advance_frame(self) -> None:
        anim = self._animation
        prev_index = self._frame_index
        mode = anim.mode

        if mode == Animation.LOOP:
            self._frame_index = (self._frame_index + 1) % anim.frame_count

        elif mode == Animation.ONE_SHOT:
            if self._frame_index < anim.frame_count - 1:
                self._frame_index += 1
            else:
                self._playing = False
                self._finished = True
                if self._on_finish:
                    self._on_finish()
                return

        elif mode == Animation.PING_PONG:
            next_index = self._frame_index + self._direction
            if next_index >= anim.frame_count:
                self._direction = -1
                next_index = anim.frame_count - 2
            elif next_index < 0:
                self._direction = 1
                next_index = 1
            self._frame_index = max(0, min(anim.frame_count - 1, next_index))

        # Fire frame events
        for event in anim.get_events(self._frame_index):
            event()

        if self._on_frame_change and self._frame_index != prev_index:
            self._on_frame_change(self._frame_index)

    def __repr__(self) -> str:
        anim_name = self._animation.name if self._animation else "None"
        return f"AnimationPlayer(anim={anim_name!r}, frame={self._frame_index}, playing={self._playing})"

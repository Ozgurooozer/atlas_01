"""
Timeline / Director system.

Provides time-sequenced events for cutscenes and scripted sequences.

Layer: 5 (Scripting)
Dependencies: core.object
"""
from __future__ import annotations
from typing import Callable, List, Optional
from core.object import Object


class TimelineEvent:
    """A single event at a specific time in the timeline."""

    def __init__(self, time: float, callback: Callable, name: str = "") -> None:
        self.time = time
        self.callback = callback
        self.name = name
        self.fired = False

    def try_fire(self, current_time: float) -> bool:
        """Fire if time has been reached and not already fired."""
        if not self.fired and current_time >= self.time:
            try:
                self.callback()
            except Exception:
                pass
            self.fired = True
            return True
        return False

    def reset(self) -> None:
        self.fired = False


class Timeline(Object):
    """
    Time-sequenced event runner for cutscenes and scripted sequences.

    Example:
        >>> tl = Timeline(duration=5.0)
        >>> tl.add_event(1.0, lambda: print("1 second"))
        >>> tl.add_event(3.0, lambda: print("3 seconds"))
        >>> tl.play()
        >>> tl.tick(1.0)  # fires "1 second"
    """

    def __init__(self, name: str = "Timeline", duration: float = 0.0) -> None:
        super().__init__(name=name)
        self._events: List[TimelineEvent] = []
        self._duration = duration
        self._time = 0.0
        self._playing = False
        self._loop = False
        self._on_end: Optional[Callable] = None

    @property
    def current_time(self) -> float:
        return self._time

    @property
    def duration(self) -> float:
        return self._duration

    @property
    def is_playing(self) -> bool:
        return self._playing

    @property
    def progress(self) -> float:
        if self._duration <= 0:
            return 0.0
        return min(1.0, self._time / self._duration)

    def add_event(self, time: float, callback: Callable, name: str = "") -> None:
        event = TimelineEvent(time, callback, name)
        self._events.append(event)
        self._events.sort(key=lambda e: e.time)

    def play(self) -> None:
        self._playing = True

    def pause(self) -> None:
        self._playing = False

    def stop(self) -> None:
        self._playing = False
        self._time = 0.0
        for event in self._events:
            event.reset()

    def seek(self, time: float) -> None:
        self._time = max(0.0, min(time, self._duration))

    def set_loop(self, loop: bool) -> None:
        self._loop = loop

    def on_end(self, callback: Callable) -> None:
        self._on_end = callback

    def tick(self, dt: float) -> None:
        if not self._playing:
            return

        self._time += dt

        # Fire events
        for event in self._events:
            event.try_fire(self._time)

        # Check end
        if self._duration > 0 and self._time >= self._duration:
            if self._loop:
                self.stop()
                self.play()
            else:
                self._playing = False
                if self._on_end:
                    try:
                        self._on_end()
                    except Exception:
                        pass


__all__ = ["Timeline", "TimelineEvent"]

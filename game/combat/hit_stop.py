"""
Hit-Stop Controller.

Freeze frame system for combat impact feedback.
Pauses game logic for N frames on hit to emphasize impact.

Layer 4 (Game/Combat)
Dependencies: core.object
"""
from __future__ import annotations
from typing import Any, Dict
from core.object import Object


class HitStopController(Object):
    """
    Freeze frame controller for combat feel.

    On hit, game logic pauses for N frames while rendering continues.
    This single technique does more for combat impact than particles.

    Presets:
      light=1 frame, heavy=3 frames, critical=4 frames, kill=6 frames
    """

    PRESET_LIGHT: int = 1
    PRESET_HEAVY: int = 3
    PRESET_CRITICAL: int = 4
    PRESET_KILL: int = 6
    DEFAULT_MAX: int = 10

    def __init__(self, max_frames: int = 10):
        super().__init__(name="HitStopController")
        self.max_frames: int = max_frames
        self.remaining_frames: int = 0

    @property
    def is_active(self) -> bool:
        """True when freeze is active."""
        return self.remaining_frames > 0

    def request(self, frames: int) -> None:
        """
        Request a freeze for N frames.

        Args:
            frames: Number of frames to freeze. Clamped to max.
        """
        if frames <= 0:
            return
        self.remaining_frames = min(frames, self.max_frames)

    def request_light(self) -> None:
        """Request light hit freeze (1 frame)."""
        self.request(self.PRESET_LIGHT)

    def request_heavy(self) -> None:
        """Request heavy hit freeze (3 frames)."""
        self.request(self.PRESET_HEAVY)

    def request_critical(self) -> None:
        """Request critical hit freeze (4 frames)."""
        self.request(self.PRESET_CRITICAL)

    def request_kill(self) -> None:
        """Request kill freeze (6 frames)."""
        self.request(self.PRESET_KILL)

    def tick(self) -> bool:
        """
        Decrement freeze counter by 1 frame.

        Returns:
            True if still active after tick, False if just deactivated.
        """
        if not self.is_active:
            return False
        self.remaining_frames -= 1
        return self.is_active

    def cancel(self) -> None:
        """Immediately cancel active freeze."""
        self.remaining_frames = 0

    def serialize(self) -> Dict[str, Any]:
        """Serialize state to dict."""
        data = super().serialize()
        data.update({
            "max_frames": self.max_frames,
            "remaining_frames": self.remaining_frames,
        })
        return data

    def deserialize(self, data: Dict[str, Any]) -> None:
        """Restore state from dict."""
        super().deserialize(data)
        self.max_frames = data.get("max_frames", self.DEFAULT_MAX)
        self.remaining_frames = data.get("remaining_frames", 0)

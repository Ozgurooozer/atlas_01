"""
Screen Shake.

Camera shake system for combat impact feedback.
Uses deterministic pseudo-random offset based on time for consistent feel.

Layer 4 (Game/Camera)
Dependencies: core.object, core.vec
"""
from __future__ import annotations
import math
from typing import Any, Dict, Optional
from core.object import Object
from core.vec import Vec2


def _deterministic_noise(t: float, seed: float) -> float:
    """Simple deterministic noise function based on sin mixing."""
    return math.sin(t * 12.9898 + seed * 78.233) * 43758.5453 % 1.0 - 0.5


class ScreenShake(Object):
    """
    Camera shake controller.

    Generates pseudo-random camera offset that decays over time.
    Used for combat hit feedback, explosions, and impact emphasis.

    Presets:
      hit: amplitude=3, duration=0.1
      heavy: amplitude=6, duration=0.2
      explosion: amplitude=10, duration=0.4
    """

    PRESET_HIT_AMP: float = 3.0
    PRESET_HIT_DUR: float = 0.1
    PRESET_HEAVY_AMP: float = 6.0
    PRESET_HEAVY_DUR: float = 0.2
    PRESET_EXPLOSION_AMP: float = 10.0
    PRESET_EXPLOSION_DUR: float = 0.4

    def __init__(self):
        super().__init__(name="ScreenShake")
        self._amplitude: float = 0.0
        self._frequency: float = 25.0
        self._duration: float = 0.0
        self._elapsed: float = 0.0
        self._seed: float = 0.0
        self._direction: Optional[Vec2] = None

    @property
    def is_active(self) -> bool:
        """True when shake is in progress."""
        return self._elapsed < self._duration and self._duration > 0

    @property
    def offset(self) -> Vec2:
        """
        Current shake offset to add to camera position.

        Returns:
            Vec2 offset. Zero when inactive.
        """
        if not self.is_active:
            return Vec2(0, 0)

        progress = self._elapsed / self._duration
        decay = 1.0 - progress
        current_amp = self._amplitude * decay

        nx = _deterministic_noise(self._elapsed * self._frequency, self._seed)
        ny = _deterministic_noise(self._elapsed * self._frequency, self._seed + 100.0)

        if self._direction is not None:
            dx = self._direction.x * nx * current_amp
            dy = self._direction.y * ny * current_amp
        else:
            dx = nx * current_amp
            dy = ny * current_amp

        return Vec2(dx, dy)

    def trigger(
        self,
        amplitude: float,
        duration: float,
        frequency: float = 25.0,
        direction: Optional[Vec2] = None,
    ) -> None:
        """
        Start a new camera shake.

        Args:
            amplitude: Maximum shake displacement in pixels.
            duration: Shake duration in seconds.
            frequency: Shake speed (noise frequency).
            direction: Optional directional bias (e.g. knockback direction).
        """
        self._amplitude = amplitude
        self._frequency = frequency
        self._duration = duration
        self._elapsed = 0.0
        self._direction = direction

        import random
        self._seed = random.random() * 1000.0

    def trigger_hit(self, direction: Optional[Vec2] = None) -> None:
        """Trigger light hit shake."""
        self.trigger(
            self.PRESET_HIT_AMP, self.PRESET_HIT_DUR, direction=direction
        )

    def trigger_heavy(self, direction: Optional[Vec2] = None) -> None:
        """Trigger heavy hit shake."""
        self.trigger(
            self.PRESET_HEAVY_AMP, self.PRESET_HEAVY_DUR, direction=direction
        )

    def trigger_explosion(self, direction: Optional[Vec2] = None) -> None:
        """Trigger explosion shake."""
        self.trigger(
            self.PRESET_EXPLOSION_AMP, self.PRESET_EXPLOSION_DUR,
            direction=direction
        )

    def tick(self, dt: float) -> None:
        """
        Update shake timer.

        Args:
            dt: Delta time in seconds.
        """
        if self.is_active:
            self._elapsed += dt

    def cancel(self) -> None:
        """Immediately stop shake."""
        self._duration = 0.0
        self._elapsed = 0.0
        self._amplitude = 0.0

    def serialize(self) -> Dict[str, Any]:
        """Serialize state to dict."""
        data = super().serialize()
        data.update({
            "amplitude": self._amplitude,
            "frequency": self._frequency,
            "duration": self._duration,
            "elapsed": self._elapsed,
            "seed": self._seed,
            "direction": (
                [self._direction.x, self._direction.y]
                if self._direction else None
            ),
        })
        return data

    def deserialize(self, data: Dict[str, Any]) -> None:
        """Restore state from dict."""
        super().deserialize(data)
        self._amplitude = data.get("amplitude", 0.0)
        self._frequency = data.get("frequency", 25.0)
        self._duration = data.get("duration", 0.0)
        self._elapsed = data.get("elapsed", 0.0)
        self._seed = data.get("seed", 0.0)
        dir_data = data.get("direction")
        self._direction = Vec2(dir_data[0], dir_data[1]) if dir_data else None

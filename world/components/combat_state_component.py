"""
Combat State Component.

Tracks combat-specific states: stun, knockback, cooldowns, i-frames, status effects.

Layer: 3 (World/Components)
Dependencies: core.object
"""
from __future__ import annotations
from typing import Any, Dict, Callable
from world.component import Component


class CombatStateComponent(Component):
    """
    Manages combat-specific transient states.

    Handles stun timers, knockback vectors, action cooldowns,
    and timed status effects. All timers are updated via on_tick.

    Attributes:
        is_stunned: Whether the entity is currently stunned.
        stun_timer: Remaining stun duration in seconds.
        knockback_x: Current knockback velocity on X axis.
        knockback_y: Current knockback velocity on Y axis.
        knockback_decay: Rate at which knockback decays per second.
    """

    def __init__(self):
        """Initialize the CombatStateComponent."""
        super().__init__()
        self.is_stunned: bool = False
        self.stun_timer: float = 0.0
        self.knockback_x: float = 0.0
        self.knockback_y: float = 0.0
        self.knockback_decay: float = 5.0
        # Cooldowns dict: action_name -> remaining_time
        self._cooldowns: Dict[str, float] = {}
        self._cooldown_durations: Dict[str, float] = {}
        # Status effects: effect_name -> remaining_duration
        self._status_effects: Dict[str, float] = {}
        self._max_status_stacks: Dict[str, int] = {}

    def set_cooldown(self, action: str, duration: float) -> None:
        """
        Set or refresh a cooldown for an action.

        Args:
            action: Name of the action (e.g. 'attack', 'dash').
            duration: Cooldown duration in seconds.
        """
        self._cooldowns[action] = duration
        self._cooldown_durations[action] = duration

    def is_on_cooldown(self, action: str) -> bool:
        """
        Check if an action is currently on cooldown.

        Args:
            action: Name of the action.

        Returns:
            True if the action is on cooldown.
        """
        return self._cooldowns.get(action, 0.0) > 0

    def get_cooldown_ratio(self, action: str) -> float:
        """
        Get cooldown progress as a ratio.

        Args:
            action: Name of the action.

        Returns:
            0.0 (ready) to 1.0 (just started cooldown).
        """
        if action not in self._cooldowns:
            return 0.0
        remaining = self._cooldowns[action]
        if remaining <= 0:
            return 0.0
        original = self._cooldown_durations.get(action, remaining)
        if original <= 0:
            return 0.0
        return remaining / original

    def apply_stun(self, duration: float) -> None:
        """
        Apply or extend a stun effect.

        Args:
            duration: Stun duration in seconds.
        """
        self.is_stunned = True
        self.stun_timer = max(self.stun_timer, duration)

    def apply_knockback(self, kx: float, ky: float) -> None:
        """
        Apply knockback velocity.

        Args:
            kx: Knockback force on X axis.
            ky: Knockback force on Y axis.
        """
        self.knockback_x += kx
        self.knockback_y += ky

    def apply_status(self, effect: str, duration: float) -> None:
        """
        Apply or refresh a status effect.

        Args:
            effect: Name of the status effect.
            duration: Duration in seconds.
        """
        current = self._status_effects.get(effect, 0.0)
        self._status_effects[effect] = max(current, duration)

    def has_status(self, effect: str) -> bool:
        """
        Check if a status effect is currently active.

        Args:
            effect: Name of the status effect.

        Returns:
            True if the effect is active.
        """
        return self._status_effects.get(effect, 0.0) > 0

    def get_status_duration(self, effect: str) -> float:
        """
        Get remaining duration of a status effect.

        Args:
            effect: Name of the status effect.

        Returns:
            Remaining duration in seconds (0.0 if not active).
        """
        return self._status_effects.get(effect, 0.0)

    def remove_status(self, effect: str) -> None:
        """
        Remove a status effect immediately.

        Args:
            effect: Name of the status effect.
        """
        self._status_effects.pop(effect, None)

    def on_tick(self, dt: float) -> None:
        """
        Update all timers each frame.

        Ticks down cooldowns, stun, status effects, and decays knockback.

        Args:
            dt: Delta time in seconds.
        """
        # Update cooldowns
        for action in self._cooldowns:
            self._cooldowns[action] -= dt
            if self._cooldowns[action] < 0:
                self._cooldowns[action] = 0.0

        # Update stun
        if self.is_stunned:
            self.stun_timer -= dt
            if self.stun_timer <= 0:
                self.is_stunned = False
                self.stun_timer = 0.0

        # Update status effects
        expired_effects = []
        for effect, remaining in self._status_effects.items():
            self._status_effects[effect] = remaining - dt
            if self._status_effects[effect] <= 0:
                expired_effects.append(effect)
        for effect in expired_effects:
            del self._status_effects[effect]

        # Decay knockback
        if abs(self.knockback_x) > 0.01 or abs(self.knockback_y) > 0.01:
            decay = self.knockback_decay * dt
            if abs(self.knockback_x) > decay:
                self.knockback_x -= decay * (1 if self.knockback_x > 0 else -1)
            else:
                self.knockback_x = 0.0
            if abs(self.knockback_y) > decay:
                self.knockback_y -= decay * (1 if self.knockback_y > 0 else -1)
            else:
                self.knockback_y = 0.0

    def serialize(self) -> Dict[str, Any]:
        """Serialize the component."""
        data = super().serialize()
        data.update({
            "is_stunned": self.is_stunned,
            "stun_timer": self.stun_timer,
            "knockback_x": self.knockback_x,
            "knockback_y": self.knockback_y,
            "status_effects": dict(self._status_effects),
        })
        return data

    def deserialize(self, data: Dict[str, Any]) -> None:
        """Deserialize the component."""
        super().deserialize(data)
        self.is_stunned = data.get("is_stunned", False)
        self.stun_timer = data.get("stun_timer", 0.0)
        self.knockback_x = data.get("knockback_x", 0.0)
        self.knockback_y = data.get("knockback_y", 0.0)
        self._status_effects = data.get("status_effects", {})

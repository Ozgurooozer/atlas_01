"""
Health Component.

Tracks HP, max HP, death state, and invincibility frames.

Layer: 3 (World/Components)
Dependencies: core.object
"""
from __future__ import annotations
from typing import Any, Dict, Optional, Callable
from world.component import Component


class HealthComponent(Component):
    """
    Manages hit points and death state for an Actor.

    Attributes:
        max_hp: Maximum hit points.
        hp: Current hit points.
        is_dead: Whether the entity is dead.
        invincible_duration: Duration of invincibility frames.
    """

    def __init__(
        self,
        max_hp: float = 100.0,
        hp: float | None = None,
        invincible_duration: float = 0.0,
    ):
        """
        Initialize the HealthComponent.

        Args:
            max_hp: Maximum hit points.
            hp: Current hit points. Defaults to max_hp.
            invincible_duration: Default invincibility duration on damage.
        """
        super().__init__()
        self.max_hp: float = max_hp
        self.hp: float = hp if hp is not None else max_hp
        self.is_dead: bool = False
        self._invincible_timer: float = 0.0
        self.invincible_duration: float = invincible_duration
        self._on_death_callbacks: list[Callable] = []
        self._on_damage_callbacks: list[Callable] = []
        self._on_heal_callbacks: list[Callable] = []

    @property
    def hp_ratio(self) -> float:
        """Current HP as a ratio of max HP (0.0 to 1.0)."""
        return self.hp / self.max_hp if self.max_hp > 0 else 0.0

    @property
    def is_invincible(self) -> bool:
        """Whether the entity is currently invincible."""
        return self._invincible_timer > 0

    def take_damage(self, amount: float) -> float:
        """
        Apply damage. Returns actual damage dealt.

        Args:
            amount: Amount of damage to apply.

        Returns:
            Actual damage dealt (0.0 if invincible or dead).
        """
        if self.is_dead or self.is_invincible or amount <= 0:
            return 0.0
        self.hp = max(0.0, self.hp - amount)
        for cb in self._on_damage_callbacks:
            cb(amount)
        if self.hp <= 0:
            self.is_dead = True
            for cb in self._on_death_callbacks:
                cb()
        return amount

    def heal(self, amount: float) -> float:
        """
        Heal HP. Returns actual amount healed.

        Args:
            amount: Amount of HP to heal.

        Returns:
            Actual amount healed (0.0 if dead or invalid).
        """
        if self.is_dead or amount <= 0:
            return 0.0
        actual = min(amount, self.max_hp - self.hp)
        self.hp += actual
        for cb in self._on_heal_callbacks:
            cb(actual)
        return actual

    def set_invincible(self, duration: float) -> None:
        """
        Activate invincibility for the given duration.

        Args:
            duration: Duration in seconds.
        """
        self._invincible_timer = max(self._invincible_timer, duration)

    def on_tick(self, dt: float) -> None:
        """
        Update invincibility timer each frame.

        Args:
            dt: Delta time in seconds.
        """
        if self._invincible_timer > 0:
            self._invincible_timer = max(0.0, self._invincible_timer - dt)

    def on_death(self, callback: Callable) -> None:
        """
        Register a callback for when this entity dies.

        Args:
            callback: Function to call on death.
        """
        self._on_death_callbacks.append(callback)

    def on_damage(self, callback: Callable) -> None:
        """
        Register a callback for when this entity takes damage.

        Args:
            callback: Function called with damage amount.
        """
        self._on_damage_callbacks.append(callback)

    def on_heal(self, callback: Callable) -> None:
        """
        Register a callback for when this entity is healed.

        Args:
            callback: Function called with heal amount.
        """
        self._on_heal_callbacks.append(callback)

    def reset(self) -> None:
        """Reset HP to max and clear death/invincibility state."""
        self.hp = self.max_hp
        self.is_dead = False
        self._invincible_timer = 0.0

    def serialize(self) -> Dict[str, Any]:
        """Serialize the component."""
        data = super().serialize()
        data.update({
            "max_hp": self.max_hp,
            "hp": self.hp,
            "is_dead": self.is_dead,
            "invincible_duration": self.invincible_duration,
        })
        return data

    def deserialize(self, data: Dict[str, Any]) -> None:
        """Deserialize the component."""
        super().deserialize(data)
        self.max_hp = data.get("max_hp", 100.0)
        self.hp = data.get("hp", self.max_hp)
        self.is_dead = data.get("is_dead", False)
        self.invincible_duration = data.get("invincible_duration", 0.0)

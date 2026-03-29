"""
Combat Stats Component.

Defines offensive and defensive stats: attack, defense, speed, crit, etc.

Layer: 3 (World/Components)
Dependencies: core.object
"""
from __future__ import annotations
from typing import Any, Dict
from world.component import Component


class CombatStatsComponent(Component):
    """
    Combat statistics for an Actor.

    Supports base stats with flat bonus and multiplier modifiers
    from items, relics, or buffs.

    Attributes:
        base_attack: Base attack power.
        base_defense: Base defense value.
        base_speed: Base movement speed.
        base_crit_chance: Base critical hit chance (0.0 to 1.0).
        base_crit_multiplier: Base critical hit damage multiplier.
        base_attack_speed: Base attacks per second.
    """

    def __init__(
        self,
        attack: float = 10.0,
        defense: float = 5.0,
        speed: float = 200.0,
        crit_chance: float = 0.05,
        crit_multiplier: float = 2.0,
        attack_speed: float = 1.0,
    ):
        """
        Initialize the CombatStatsComponent.

        Args:
            attack: Base attack power.
            defense: Base defense value.
            speed: Base movement speed.
            crit_chance: Base critical hit chance (0.0 to 1.0).
            crit_multiplier: Base critical hit damage multiplier.
            attack_speed: Base attacks per second.
        """
        super().__init__()
        self.base_attack: float = attack
        self.base_defense: float = defense
        self.base_speed: float = speed
        self.base_crit_chance: float = crit_chance
        self.base_crit_multiplier: float = crit_multiplier
        self.base_attack_speed: float = attack_speed
        # Flat modifiers (from items/relics)
        self._bonus_attack: float = 0.0
        self._bonus_defense: float = 0.0
        self._bonus_speed: float = 0.0
        self._bonus_crit_chance: float = 0.0
        self._bonus_crit_multiplier: float = 0.0
        self._bonus_attack_speed: float = 0.0
        # Multiplier modifiers
        self._mult_attack: float = 1.0
        self._mult_defense: float = 1.0
        self._mult_speed: float = 1.0

    @property
    def attack(self) -> float:
        """Effective attack (base + bonus) * multiplier."""
        return (self.base_attack + self._bonus_attack) * self._mult_attack

    @property
    def defense(self) -> float:
        """Effective defense (base + bonus) * multiplier."""
        return (self.base_defense + self._bonus_defense) * self._mult_defense

    @property
    def speed(self) -> float:
        """Effective speed (base + bonus) * multiplier."""
        return (self.base_speed + self._bonus_speed) * self._mult_speed

    @property
    def crit_chance(self) -> float:
        """Effective crit chance, capped at 1.0."""
        return min(1.0, self.base_crit_chance + self._bonus_crit_chance)

    @property
    def crit_multiplier(self) -> float:
        """Effective crit multiplier (base + bonus)."""
        return self.base_crit_multiplier + self._bonus_crit_multiplier

    @property
    def attack_speed(self) -> float:
        """Effective attack speed (base + bonus)."""
        return self.base_attack_speed + self._bonus_attack_speed

    def add_bonus(self, stat: str, value: float) -> None:
        """
        Add a flat bonus to a stat.

        Args:
            stat: Stat name (e.g. 'attack', 'defense', 'speed').
            value: Flat bonus amount to add.
        """
        attr = f"_bonus_{stat}"
        if hasattr(self, attr):
            setattr(self, attr, getattr(self, attr) + value)

    def add_multiplier(self, stat: str, value: float) -> None:
        """
        Multiply a stat's multiplier.

        Args:
            stat: Stat name (e.g. 'attack', 'defense', 'speed').
            value: Multiplicative factor to apply.
        """
        attr = f"_mult_{stat}"
        if hasattr(self, attr):
            setattr(self, attr, getattr(self, attr) * value)

    def remove_all_modifiers(self) -> None:
        """Remove all bonus and multiplier modifiers, restoring base values."""
        self._bonus_attack = 0.0
        self._bonus_defense = 0.0
        self._bonus_speed = 0.0
        self._bonus_crit_chance = 0.0
        self._bonus_crit_multiplier = 0.0
        self._bonus_attack_speed = 0.0
        self._mult_attack = 1.0
        self._mult_defense = 1.0
        self._mult_speed = 1.0

    def calculate_damage(self, is_crit: bool = False) -> float:
        """
        Calculate raw damage from attack stat.

        Args:
            is_crit: Whether this attack is a critical hit.

        Returns:
            Calculated damage value.
        """
        dmg = self.attack
        if is_crit:
            dmg *= self.crit_multiplier
        return dmg

    def roll_crit(self) -> bool:
        """
        Roll for a critical hit based on crit_chance.

        Returns:
            True if the roll is a critical hit.
        """
        import random
        return random.random() < self.crit_chance

    def serialize(self) -> Dict[str, Any]:
        """Serialize the component."""
        data = super().serialize()
        data.update({
            "base_attack": self.base_attack,
            "base_defense": self.base_defense,
            "base_speed": self.base_speed,
            "base_crit_chance": self.base_crit_chance,
            "base_crit_multiplier": self.base_crit_multiplier,
            "base_attack_speed": self.base_attack_speed,
        })
        return data

    def deserialize(self, data: Dict[str, Any]) -> None:
        """Deserialize the component."""
        super().deserialize(data)
        self.base_attack = data.get("base_attack", 10.0)
        self.base_defense = data.get("base_defense", 5.0)
        self.base_speed = data.get("base_speed", 200.0)
        self.base_crit_chance = data.get("base_crit_chance", 0.05)
        self.base_crit_multiplier = data.get("base_crit_multiplier", 2.0)
        self.base_attack_speed = data.get("base_attack_speed", 1.0)

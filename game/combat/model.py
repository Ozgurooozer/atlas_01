"""
Combat Data Model.

Defines combat events, damage types, and data transfer objects.

Layer: 4 (Game/Combat)
Dependencies: core.object, core.vec
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional, TYPE_CHECKING
from core.vec import Vec2

if TYPE_CHECKING:
    from world.actor import Actor


class DamageType(Enum):
    PHYSICAL = auto()
    MAGICAL = auto()
    FIRE = auto()
    POISON = auto()
    ICE = auto()
    TRUE = auto()


class CombatEventType(Enum):
    DAMAGE_DEALT = "damage_dealt"
    DAMAGE_RECEIVED = "damage_received"
    HEAL = "heal"
    DEATH = "death"
    CRITICAL_HIT = "critical_hit"
    DODGE = "dodge"
    STATUS_APPLIED = "status_applied"
    STATUS_REMOVED = "status_removed"
    COMBAT_START = "combat_start"
    COMBAT_END = "combat_end"


class StatusEffectType(Enum):
    POISON = auto()
    BURN = auto()
    STUN = auto()
    SLOW = auto()
    BLEED = auto()
    FREEZE = auto()
    SHIELD = auto()
    BUFF_ATTACK = auto()
    BUFF_DEFENSE = auto()


@dataclass
class DamageData:
    """Data transfer object for damage calculations."""
    amount: float = 0.0
    damage_type: DamageType = DamageType.PHYSICAL
    is_crit: bool = False
    source: Optional[Actor] = None
    target: Optional[Actor] = None
    knockback: Vec2 = field(default_factory=lambda: Vec2(0, 0))
    status_effect: Optional[StatusEffectType] = None
    status_duration: float = 0.0
    position: Vec2 = field(default_factory=lambda: Vec2(0, 0))

    @property
    def final_damage(self) -> float:
        return self.amount if self.amount > 0 else 0.0


@dataclass
class CombatResult:
    """Result of a damage calculation."""
    raw_damage: float = 0.0
    defense_reduction: float = 0.0
    final_damage: float = 0.0
    was_crit: bool = False
    was_dodged: bool = False
    target_died: bool = False
    overkill: float = 0.0

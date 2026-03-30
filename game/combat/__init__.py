"""
Combat Module.

Provides combat data models, damage processing, and status effect systems.

Layer: 4 (Game/Combat)
"""

from game.combat.model import DamageData, StatusEffectType
from game.combat.system import CombatSystem

__all__ = [
    "DamageData",
    "CombatSystem",
    "StatusEffectType",
]

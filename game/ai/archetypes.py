"""
AI Archetypes.

Defines enemy AI behavior archetypes: melee chaser, ranged kiter, tank charger.
These configure BehaviourTree and StateMachine parameters.

Layer: 4 (Game/AI)
Dependencies: core.object
"""
from __future__ import annotations
from typing import Any, Dict
from core.object import Object


class AIArchetype(Object):
    """Base class for enemy AI archetypes."""
    
    def __init__(self, name: str = "AIArchetype"):
        super().__init__(name=name)
        self.chase_speed: float = 100.0
        self.detection_range: float = 300.0
        self.attack_range: float = 50.0
        self.attack_cooldown: float = 1.0
        self.max_hp: float = 50.0
        self.attack_damage: float = 10.0
        self.prefers_ranged: bool = False
        self.projectile_speed: float = 0.0
    
    def get_config(self) -> Dict[str, Any]:
        return {
            "chase_speed": self.chase_speed,
            "detection_range": self.detection_range,
            "attack_range": self.attack_range,
            "attack_cooldown": self.attack_cooldown,
            "max_hp": self.max_hp,
            "attack_damage": self.attack_damage,
        }


class MeleeChaserArchetype(AIArchetype):
    """Melee enemy that chases the player aggressively."""
    
    def __init__(self):
        super().__init__(name="MeleeChaser")
        self.chase_speed = 150.0
        self.detection_range = 250.0
        self.attack_range = 40.0
        self.attack_cooldown = 0.8
        self.max_hp = 40.0
        self.attack_damage = 8.0


class RangedKiterArchetype(AIArchetype):
    """Ranged enemy that keeps distance and shoots."""
    
    def __init__(self):
        super().__init__(name="RangedKiter")
        self.chase_speed = 80.0
        self.detection_range = 400.0
        self.attack_range = 250.0
        self.attack_cooldown = 1.5
        self.max_hp = 30.0
        self.attack_damage = 12.0
        self.prefers_ranged = True
        self.projectile_speed = 300.0


class TankChargerArchetype(AIArchetype):
    """Tank enemy that charges and has high HP."""
    
    def __init__(self):
        super().__init__(name="TankCharger")
        self.chase_speed = 60.0
        self.detection_range = 200.0
        self.attack_range = 60.0
        self.attack_cooldown = 2.0
        self.max_hp = 120.0
        self.attack_damage = 20.0

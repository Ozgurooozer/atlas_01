"""
Combat System.

Central system that processes damage, manages hitbox/hurtbox interactions,
and publishes combat events via EventBus.

Layer: 4 (Game/Combat)
Dependencies: game.combat.model, core.eventbus
"""
from __future__ import annotations
from typing import Optional, Dict, List, TYPE_CHECKING
from core.object import Object
from core.eventbus import EventBus

from game.combat.model import (
    DamageData, DamageType, CombatResult, CombatEventType, StatusEffectType
)

if TYPE_CHECKING:
    from world.actor import Actor
    from world.components.health_component import HealthComponent
    from world.components.combat_stats_component import CombatStatsComponent
    from world.components.combatant_component import CombatantComponent
    from world.components.hitbox_component import HitboxComponent
    from world.components.hurtbox_component import HurtboxComponent
    from world.components.combat_state_component import CombatStateComponent


class CombatSystem(Object):
    """
    Central combat system.

    Processes hitbox/hurtbox overlaps, calculates damage, applies results,
    and publishes events via EventBus.
    """

    def __init__(self, event_bus: Optional[EventBus] = None):
        super().__init__(name="CombatSystem")
        self._event_bus = event_bus or EventBus()
        self._is_active = False

    @property
    def event_bus(self) -> EventBus:
        return self._event_bus

    @property
    def is_active(self) -> bool:
        return self._is_active

    def start_combat(self) -> None:
        self._is_active = True
        self._event_bus.publish(CombatEventType.COMBAT_START, {})

    def end_combat(self) -> None:
        self._is_active = False
        self._event_bus.publish(CombatEventType.COMBAT_END, {})

    def calculate_damage(
        self,
        raw_damage: float,
        attacker_stats: Optional[CombatStatsComponent] = None,
        defender_stats: Optional[CombatStatsComponent] = None,
        is_crit: bool = False,
    ) -> CombatResult:
        """Calculate damage with defense reduction and crit."""
        if attacker_stats and is_crit:
            raw_damage = attacker_stats.calculate_damage(is_crit=True)

        defense = 0.0
        if defender_stats:
            defense = defender_stats.defense

        defense_reduction = min(defense, raw_damage * 0.8)  # Cap at 80% reduction
        final = max(1.0, raw_damage - defense_reduction) if raw_damage > 0 else 0.0

        return CombatResult(
            raw_damage=raw_damage,
            defense_reduction=defense_reduction,
            final_damage=final,
            was_crit=is_crit,
        )

    def apply_damage(
        self,
        damage_data: DamageData,
        target_health: HealthComponent,
        target_state: Optional[CombatStateComponent] = None,
    ) -> CombatResult:
        """Apply damage to a target."""
        if target_health.is_dead:
            return CombatResult(was_dodged=True)

        if target_state and target_state.is_stunned:
            pass  # Stunned targets can't dodge, proceed with damage

        result = CombatResult(
            raw_damage=damage_data.amount,
            was_crit=damage_data.is_crit,
        )

        hp_before = target_health.hp
        actual = target_health.take_damage(damage_data.final_damage)
        result.final_damage = actual
        result.target_died = target_health.is_dead

        if result.target_died:
            result.overkill = max(0.0, actual - hp_before)

        # Publish events
        self._event_bus.publish(CombatEventType.DAMAGE_RECEIVED, {
            "target": damage_data.target,
            "amount": actual,
            "is_crit": damage_data.is_crit,
            "damage_type": damage_data.damage_type,
            "position": damage_data.position,
        })

        if damage_data.source:
            self._event_bus.publish(CombatEventType.DAMAGE_DEALT, {
                "source": damage_data.source,
                "amount": actual,
                "is_crit": damage_data.is_crit,
                "damage_type": damage_data.damage_type,
            })

        if damage_data.is_crit:
            self._event_bus.publish(CombatEventType.CRITICAL_HIT, {
                "source": damage_data.source,
                "target": damage_data.target,
                "amount": actual,
                "position": damage_data.position,
            })

        if result.target_died:
            self._event_bus.publish(CombatEventType.DEATH, {
                "target": damage_data.target,
                "killer": damage_data.source,
            })

        # Apply knockback
        if damage_data.knockback and target_state:
            target_state.apply_knockback(
                damage_data.knockback.x,
                damage_data.knockback.y,
            )

        # Apply status effect
        if damage_data.status_effect and target_state:
            target_state.apply_status(
                damage_data.status_effect.name,
                damage_data.status_duration,
            )
            self._event_bus.publish(CombatEventType.STATUS_APPLIED, {
                "target": damage_data.target,
                "effect": damage_data.status_effect,
                "duration": damage_data.status_duration,
            })

        return result

    def apply_heal(
        self,
        amount: float,
        target_health: HealthComponent,
        source: Optional[Actor] = None,
    ) -> float:
        actual = target_health.heal(amount)
        self._event_bus.publish(CombatEventType.HEAL, {
            "target": None,  # target_health.owner
            "amount": actual,
            "source": source,
        })
        return actual

    def process_hitbox_hit(
        self,
        attacker: Actor,
        target: Actor,
        hitbox: HitboxComponent,
        hurtbox: HurtboxComponent,
    ) -> Optional[CombatResult]:
        """Process a hitbox hitting a hurtbox."""
        if not hitbox.can_hit:
            return None
        if not hurtbox.is_enabled:
            return None

        # Check team
        attacker_comb = attacker.get_component(CombatantComponent)
        target_comb = target.get_component(CombatantComponent)
        if attacker_comb and target_comb:
            if not attacker_comb.is_hostile_to(target_comb.team):
                return None

        # Prevent multi-hit
        target_id = id(target)
        if not hitbox.register_hit(target_id):
            return None

        # Gather components
        attacker_stats = attacker.get_component(CombatStatsComponent)
        target_health = target.get_component(HealthComponent)
        target_state = target.get_component(CombatStateComponent)

        if target_health is None:
            return None

        is_crit = False
        if attacker_stats:
            is_crit = attacker_stats.roll_crit()

        damage_data = DamageData(
            amount=hitbox.base_damage,
            damage_type=DamageType.PHYSICAL,
            is_crit=is_crit,
            source=attacker,
            target=target,
            knockback=__import__('core.vec', fromlist=['Vec2']).Vec2(
                hitbox.knockback, 0
            ),
        )

        # Get position from attacker transform
        from world.components.transform_component import TransformComponent
        transform = attacker.get_component(TransformComponent)
        if transform:
            damage_data.position = transform.position

        result = self.calculate_damage(
            damage_data.amount, attacker_stats,
            target.get_component(CombatStatsComponent),
            is_crit,
        )
        damage_data.amount = result.final_damage
        damage_data.is_crit = result.was_crit

        return self.apply_damage(damage_data, target_health, target_state)

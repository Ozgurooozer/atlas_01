"""
Combat Status Effects.

Process status effects (poison, burn, stun, etc.) each tick.

Layer: 4 (Game/Combat)
Dependencies: game.combat.model, core.eventbus
"""
from __future__ import annotations
from typing import Dict, TYPE_CHECKING
from core.object import Object
from game.combat.model import StatusEffectType

if TYPE_CHECKING:
    from world.actor import Actor
    from world.components.health_component import HealthComponent
    from world.components.combat_state_component import CombatStateComponent


# Damage-per-tick values for DoT effects
DOT_DAMAGE: Dict[StatusEffectType, float] = {
    StatusEffectType.POISON: 3.0,
    StatusEffectType.BURN: 5.0,
    StatusEffectType.BLEED: 2.0,
}

TICK_INTERVAL: float = 0.5  # seconds between DoT ticks


class StatusEffectProcessor(Object):
    """Processes active status effects on combatants each tick."""

    def __init__(self):
        super().__init__(name="StatusEffectProcessor")
        self._tick_accumulators: Dict[int, float] = {}  # actor_id -> accumulator

    def process(
        self,
        actor: Actor,
        health: HealthComponent,
        state: CombatStateComponent,
        dt: float,
    ) -> None:
        """Process all active status effects on an actor."""
        if health.is_dead:
            return

        actor_id = id(actor)

        # Initialize accumulator
        if actor_id not in self._tick_accumulators:
            self._tick_accumulators[actor_id] = 0.0

        self._tick_accumulators[actor_id] += dt

        # Only process DoT on tick intervals
        if self._tick_accumulators[actor_id] < TICK_INTERVAL:
            # Still process non-DoT effects
            self._process_instant_effects(actor, health, state, dt)
            return

        self._tick_accumulators[actor_id] -= TICK_INTERVAL

        # Process DoT effects
        for effect_type in DOT_DAMAGE:
            if state.has_status(effect_type.name):
                damage = DOT_DAMAGE[effect_type]
                health.take_damage(damage)

        # Process other effects
        self._process_instant_effects(actor, health, state, dt)

        # Clean up if actor is removed
        if health.is_dead:
            self._tick_accumulators.pop(actor_id, None)

    def _process_instant_effects(
        self,
        actor: Actor,
        health: HealthComponent,
        state: CombatStateComponent,
        dt: float,
    ) -> None:
        """Process non-DoT status effects."""
        if state.has_status(StatusEffectType.FREEZE.name):
            state.apply_stun(dt)  # Freeze acts as continuous stun

        if state.has_status(StatusEffectType.SLOW.name):
            # Slow is handled via stat modifier, just check duration
            pass

    def cleanup(self, actor_id: int) -> None:
        self._tick_accumulators.pop(actor_id, None)

"""
Enemy AI System.

Combines BehaviourTree for decision-making with StateMachine for execution.
Supports three archetypes: MeleeChaser, RangedKiter, TankCharger.

Layer: 4 (Game/AI)
Dependencies: core.object, core.vec, scripting.*, game.ai.archetypes
"""
from __future__ import annotations

import math
from enum import Enum
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from core.object import Object
from core.vec import Vec2
from scripting.blackboard import Blackboard
from scripting.behaviour_tree import (
    BehaviourTree,
    NodeStatus,
    Sequence,
    Selector,
    ActionNode,
    ConditionNode,
)
from scripting.statemachine import State, StateMachine
from game.ai.archetypes import (
    AIArchetype,
    MeleeChaserArchetype,
    RangedKiterArchetype,
    TankChargerArchetype,
)

if TYPE_CHECKING:
    from world.actor import Actor


class AIState(Enum):
    """Enemy AI state identifiers."""
    IDLE = "IDLE"
    PATROL = "PATROL"
    CHASE = "CHASE"
    ATTACK = "ATTACK"
    RETREAT = "RETREAT"
    STUNNED = "STUNNED"
    DEAD = "DEAD"


# ---------------------------------------------------------------------------
# State implementations – each receives a back-reference to the owning EnemyAI
# ---------------------------------------------------------------------------

class _AIState(State):
    """Base state class with back-reference to the EnemyAI controller."""

    def __init__(self, name: str, ai: "EnemyAI"):
        super().__init__(name=name)
        self._ai = ai


class _IdleState(_AIState):
    def tick(self, dt: float) -> None:
        # Nothing to do while idle
        pass


class _PatrolState(_AIState):
    def on_enter(self, context: Any = None) -> None:
        self._ai._patrol_wait_timer = 0.0

    def tick(self, dt: float) -> None:
        ai = self._ai
        if not ai._patrol_points:
            return

        target_point = ai._patrol_points[ai._patrol_index % len(ai._patrol_points)]
        my_pos = ai._get_position()
        distance = my_pos.distance_to(target_point)

        if distance < 5.0:
            # Reached patrol point, wait then move to next
            ai._patrol_wait_timer += dt
            if ai._patrol_wait_timer >= 1.0:
                ai._patrol_index = (ai._patrol_index + 1) % len(ai._patrol_points)
                ai._patrol_wait_timer = 0.0
        else:
            ai._move_toward(target_point, ai._archetype.chase_speed * 0.5, dt)


class _ChaseState(_AIState):
    def tick(self, dt: float) -> None:
        ai = self._ai
        target = ai._get_target_actor()
        if target is None:
            return

        target_pos = ai._get_actor_position(target)
        if target_pos is None:
            return

        speed = ai._archetype.chase_speed
        ai._move_toward(target_pos, speed, dt)


class _AttackState(_AIState):
    def on_enter(self, context: Any = None) -> None:
        ai = self._ai
        ai._attack_timer = ai._get_attack_duration()
        ai._set_attack_cooldown()

    def tick(self, dt: float) -> None:
        ai = self._ai
        ai._attack_timer -= dt

        if ai._attack_timer <= 0:
            ai._execute_attack()

            # Transition to retreat after attack
            if isinstance(ai._archetype, (MeleeChaserArchetype,)):
                ai._do_transition(AIState.RETREAT.value)
            elif isinstance(ai._archetype, (RangedKiterArchetype, TankChargerArchetype)):
                ai._do_transition(AIState.IDLE.value)
            else:
                ai._do_transition(AIState.CHASE.value)


class _RetreatState(_AIState):
    def on_enter(self, context: Any = None) -> None:
        ai = self._ai
        ai._retreat_timer = ai._get_retreat_duration()
        # Cache retreat target position so movement continues even if target is lost
        target = ai._get_target_actor()
        if target is not None:
            target_pos = ai._get_actor_position(target)
            if target_pos is not None:
                ai._blackboard.set("_retreat_from_pos", target_pos)
            else:
                ai._blackboard.set("_retreat_from_pos", None)
        else:
            ai._blackboard.set("_retreat_from_pos", None)

    def tick(self, dt: float) -> None:
        ai = self._ai
        ai._retreat_timer -= dt

        # Move away from cached target position
        retreat_pos = ai._blackboard.get("_retreat_from_pos")
        if retreat_pos is not None:
            ai._move_away_from(retreat_pos, ai._archetype.chase_speed * 0.8, dt)

        if ai._retreat_timer <= 0:
            target = ai._get_target_actor()
            if target is not None:
                ai._do_transition(AIState.CHASE.value)
            else:
                ai._do_transition(AIState.IDLE.value)


class _StunnedState(_AIState):
    def on_enter(self, context: Any = None) -> None:
        ai = self._ai
        ai._stun_timer = ai._blackboard.get("stun_duration", 1.0)

    def tick(self, dt: float) -> None:
        ai = self._ai
        ai._stun_timer -= dt
        if ai._stun_timer <= 0:
            ai._do_transition(AIState.IDLE.value)


class _DeadState(_AIState):
    def on_enter(self, context: Any = None) -> None:
        ai = self._ai
        if ai._actor is not None:
            ai._actor.enabled = False


# ---------------------------------------------------------------------------
# EnemyAI – main controller
# ---------------------------------------------------------------------------

class EnemyAI(Object):
    """
    Enemy AI controller using BehaviourTree + StateMachine.

    Supports three archetypes via AIArchetype configuration:
    - MeleeChaserArchetype: chase → attack → retreat
    - RangedKiterArchetype: keep distance → shoot → reposition
    - TankChargerArchetype: patrol → detect → charge → stun recovery

    Usable as a standalone script or via ScriptComponent.
    Lifecycle: ``on_attach(actor)`` → ``on_tick(dt)`` → ``on_detach()``

    Example::

        from game.ai.archetypes import MeleeChaserArchetype
        ai = EnemyAI(MeleeChaserArchetype())
        ai.on_attach(enemy_actor)
        ai.on_tick(0.016)
    """

    def __init__(self, archetype: AIArchetype):
        super().__init__(name=f"EnemyAI_{archetype.name}")
        self._archetype = archetype
        self._blackboard = Blackboard()
        self._actor: Optional[Actor] = None

        # ScriptComponent compatibility attributes
        self.actor: Optional[Actor] = None
        self.blackboard: Dict[str, Any] = {}

        # Subsystems
        self._tree = BehaviourTree(name=f"BT_{archetype.name}")
        self._sm: Optional[StateMachine] = None

        # Internal timers
        self._attack_timer: float = 0.0
        self._retreat_timer: float = 0.0
        self._stun_timer: float = 0.0
        self._patrol_wait_timer: float = 0.0

        # Patrol
        self._patrol_points: List[Vec2] = []
        self._patrol_index: int = 0

        # Build AI
        self._build_states()
        self._build_tree()

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def on_attach(self, actor: "Actor") -> None:
        """Attach this AI to an actor."""
        self._actor = actor
        self.actor = actor

    def on_start(self) -> None:
        """Called by ScriptComponent after actor injection."""
        if self.actor is not None and self._actor is None:
            self._actor = self.actor

    def on_tick(self, dt: float) -> None:
        """Main update loop called each frame."""
        if self._actor is None:
            return
        if not self._actor.enabled:
            return
        if self._sm and self._sm.current_state.name == AIState.DEAD.value:
            return

        self._update_blackboard()
        self._update_timers(dt)
        self._tree.tick(self._blackboard)
        if self._sm:
            self._sm.tick(dt)

    def on_detach(self) -> None:
        """Detach this AI from its actor."""
        self._actor = None

    def on_destroy(self) -> None:
        """Called by ScriptComponent on cleanup."""
        self.on_detach()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def archetype(self) -> AIArchetype:
        """Get the archetype configuration."""
        return self._archetype

    @property
    def bb(self) -> Blackboard:
        """Get the internal Blackboard for BT shared state."""
        return self._blackboard

    @property
    def state_machine(self) -> Optional[StateMachine]:
        """Get the internal StateMachine."""
        return self._sm

    @property
    def current_state(self) -> str:
        """Get the current state name."""
        if self._sm:
            return self._sm.current_state.name
        return "NONE"

    def set_patrol_points(self, points: List[Vec2]) -> None:
        """Set patrol waypoints (primarily for TankCharger)."""
        self._patrol_points = list(points)
        self._patrol_index = 0

    def set_target(self, target: Optional["Actor"]) -> None:
        """Manually set the AI target."""
        self._blackboard.set("target", target)

    def force_state(self, state_name: str) -> None:
        """Force a state transition (for testing)."""
        if self._sm and state_name in self._sm.states:
            self._sm.transition(state_name)

    # ------------------------------------------------------------------
    # Internal: Tree construction
    # ------------------------------------------------------------------

    def _build_tree(self) -> None:
        root = Selector(name="Root")

        # --- Priority 1: Dead ---
        dead_seq = Sequence(name="DeadCheck")
        dead_seq.add_child(ConditionNode(
            lambda ctx: ctx.get("is_dead", False), "IsDead"
        ))
        dead_seq.add_child(ActionNode(
            lambda ctx: self._do_transition(AIState.DEAD.value), "GoDead"
        ))
        root.add_child(dead_seq)

        # --- Priority 2: Stunned ---
        stun_seq = Sequence(name="StunCheck")
        stun_seq.add_child(ConditionNode(
            lambda ctx: ctx.get("is_stunned", False), "IsStunned"
        ))
        stun_seq.add_child(ActionNode(
            lambda ctx: self._do_transition(AIState.STUNNED.value), "GoStunned"
        ))
        root.add_child(stun_seq)

        # --- Archetype-specific branches ---
        if isinstance(self._archetype, MeleeChaserArchetype):
            self._build_melee_tree(root)
        elif isinstance(self._archetype, RangedKiterArchetype):
            self._build_ranged_tree(root)
        elif isinstance(self._archetype, TankChargerArchetype):
            self._build_tank_tree(root)
        else:
            self._build_default_tree(root)

        self._tree.set_root(root)

    def _build_melee_tree(self, root: Selector) -> None:
        # Attack
        attack_seq = Sequence(name="MeleeAttack")
        attack_seq.add_child(ConditionNode(
            lambda ctx: ctx.get("target_in_attack_range", False), "InRange"
        ))
        attack_seq.add_child(ConditionNode(
            lambda ctx: not ctx.get("attack_on_cooldown", True), "CanAttack"
        ))
        attack_seq.add_child(ActionNode(
            lambda ctx: self._do_transition(AIState.ATTACK.value), "GoAttack"
        ))
        root.add_child(attack_seq)

        # Retreat
        retreat_seq = Sequence(name="MeleeRetreat")
        retreat_seq.add_child(ConditionNode(
            lambda ctx: ctx.get("should_retreat", False), "ShouldRetreat"
        ))
        retreat_seq.add_child(ActionNode(
            lambda ctx: self._do_transition(AIState.RETREAT.value), "GoRetreat"
        ))
        root.add_child(retreat_seq)

        # Chase
        chase_seq = Sequence(name="MeleeChase")
        chase_seq.add_child(ConditionNode(
            lambda ctx: ctx.get("target_detected", False), "HasTarget"
        ))
        chase_seq.add_child(ActionNode(
            lambda ctx: self._do_transition(AIState.CHASE.value), "GoChase"
        ))
        root.add_child(chase_seq)

        root.add_child(ActionNode(
            lambda ctx: self._do_transition(AIState.IDLE.value), "GoIdle"
        ))

    def _build_ranged_tree(self, root: Selector) -> None:
        # Attack at preferred distance
        attack_seq = Sequence(name="RangedAttack")
        attack_seq.add_child(ConditionNode(
            lambda ctx: ctx.get("target_in_attack_range", False), "InRange"
        ))
        attack_seq.add_child(ConditionNode(
            lambda ctx: not ctx.get("attack_on_cooldown", True), "CanAttack"
        ))
        attack_seq.add_child(ConditionNode(
            lambda ctx: ctx.get("at_preferred_distance", True), "AtPrefDist"
        ))
        attack_seq.add_child(ActionNode(
            lambda ctx: self._do_transition(AIState.ATTACK.value), "GoAttack"
        ))
        root.add_child(attack_seq)

        # Too close → retreat
        too_close = Sequence(name="TooClose")
        too_close.add_child(ConditionNode(
            lambda ctx: ctx.get("target_detected", False), "HasTarget"
        ))
        too_close.add_child(ConditionNode(
            lambda ctx: ctx.get("target_too_close", False), "TooClose"
        ))
        too_close.add_child(ActionNode(
            lambda ctx: self._do_transition(AIState.RETREAT.value), "GoRetreat"
        ))
        root.add_child(too_close)

        # Chase to preferred distance
        chase_seq = Sequence(name="RangedChase")
        chase_seq.add_child(ConditionNode(
            lambda ctx: ctx.get("target_detected", False), "HasTarget"
        ))
        chase_seq.add_child(ConditionNode(
            lambda ctx: not ctx.get("at_preferred_distance", False), "NotPrefDist"
        ))
        chase_seq.add_child(ActionNode(
            lambda ctx: self._do_transition(AIState.CHASE.value), "GoChase"
        ))
        root.add_child(chase_seq)

        # Hold position (target detected, at preferred distance, on cooldown)
        hold_seq = Sequence(name="HoldPosition")
        hold_seq.add_child(ConditionNode(
            lambda ctx: ctx.get("target_detected", False), "HasTarget"
        ))
        hold_seq.add_child(ActionNode(
            lambda ctx: self._do_transition(AIState.IDLE.value), "GoIdle"
        ))
        root.add_child(hold_seq)

        root.add_child(ActionNode(
            lambda ctx: self._do_transition(AIState.IDLE.value), "GoIdle"
        ))

    def _build_tank_tree(self, root: Selector) -> None:
        # Attack
        attack_seq = Sequence(name="TankAttack")
        attack_seq.add_child(ConditionNode(
            lambda ctx: ctx.get("target_in_attack_range", False), "InRange"
        ))
        attack_seq.add_child(ConditionNode(
            lambda ctx: not ctx.get("attack_on_cooldown", True), "CanAttack"
        ))
        attack_seq.add_child(ActionNode(
            lambda ctx: self._do_transition(AIState.ATTACK.value), "GoAttack"
        ))
        root.add_child(attack_seq)

        # Chase
        chase_seq = Sequence(name="TankChase")
        chase_seq.add_child(ConditionNode(
            lambda ctx: ctx.get("target_detected", False), "HasTarget"
        ))
        chase_seq.add_child(ActionNode(
            lambda ctx: self._do_transition(AIState.CHASE.value), "GoChase"
        ))
        root.add_child(chase_seq)

        # Patrol (default)
        root.add_child(ActionNode(
            lambda ctx: self._do_transition(AIState.PATROL.value), "GoPatrol"
        ))

    def _build_default_tree(self, root: Selector) -> None:
        attack_seq = Sequence(name="DefaultAttack")
        attack_seq.add_child(ConditionNode(
            lambda ctx: ctx.get("target_in_attack_range", False), "InRange"
        ))
        attack_seq.add_child(ConditionNode(
            lambda ctx: not ctx.get("attack_on_cooldown", True), "CanAttack"
        ))
        attack_seq.add_child(ActionNode(
            lambda ctx: self._do_transition(AIState.ATTACK.value), "GoAttack"
        ))
        root.add_child(attack_seq)

        chase_seq = Sequence(name="DefaultChase")
        chase_seq.add_child(ConditionNode(
            lambda ctx: ctx.get("target_detected", False), "HasTarget"
        ))
        chase_seq.add_child(ActionNode(
            lambda ctx: self._do_transition(AIState.CHASE.value), "GoChase"
        ))
        root.add_child(chase_seq)

        root.add_child(ActionNode(
            lambda ctx: self._do_transition(AIState.IDLE.value), "GoIdle"
        ))

    # ------------------------------------------------------------------
    # Internal: State construction
    # ------------------------------------------------------------------

    def _build_states(self) -> None:
        idle = _IdleState(name=AIState.IDLE.value, ai=self)
        patrol = _PatrolState(name=AIState.PATROL.value, ai=self)
        chase = _ChaseState(name=AIState.CHASE.value, ai=self)
        attack = _AttackState(name=AIState.ATTACK.value, ai=self)
        retreat = _RetreatState(name=AIState.RETREAT.value, ai=self)
        stunned = _StunnedState(name=AIState.STUNNED.value, ai=self)
        dead = _DeadState(name=AIState.DEAD.value, ai=self)

        self._sm = StateMachine(initial_state=idle)
        for state in [patrol, chase, attack, retreat, stunned, dead]:
            self._sm.add_state(state)

    # ------------------------------------------------------------------
    # Internal: Blackboard refresh
    # ------------------------------------------------------------------

    def _update_blackboard(self) -> None:
        if self._actor is None:
            return

        from world.components.health_component import HealthComponent
        from world.components.combat_state_component import CombatStateComponent
        from world.components.combatant_component import CombatantComponent

        bb = self._blackboard

        # --- Health / death ---
        health_comp = self._actor.get_component(HealthComponent)
        is_dead = False
        if health_comp is not None:
            is_dead = health_comp.is_dead
            bb.set("hp", health_comp.hp)
            bb.set("max_hp", health_comp.max_hp)
        bb.set("is_dead", is_dead)

        # --- Combat state (stun) ---
        combat_state = self._actor.get_component(CombatStateComponent)
        is_stunned = False
        if combat_state is not None:
            is_stunned = combat_state.is_stunned
            attack_on_cd = combat_state.is_on_cooldown("attack")
            bb.set("attack_on_cooldown", attack_on_cd)
            bb.set("stun_duration", combat_state.stun_timer)
        else:
            attack_on_cd = bb.get("attack_on_cooldown", False)
            bb.set("attack_on_cooldown", attack_on_cd)
        bb.set("is_stunned", is_stunned)

        # --- Position & targeting ---
        my_pos = self._get_position()
        bb.set("self_position", my_pos)

        # Get target from CombatantComponent or blackboard
        combatant = self._actor.get_component(CombatantComponent)
        target: Optional[Actor] = bb.get("target")
        if target is None and combatant is not None:
            target = combatant.current_target
            bb.set("target", target)

        if target is not None and target.enabled:
            target_pos = self._get_actor_position(target)
            if target_pos is not None:
                dist = my_pos.distance_to(target_pos)
                bb.set("distance_to_target", dist)
                bb.set("target_detected", dist <= self._archetype.detection_range)
                bb.set("target_in_attack_range", dist <= self._archetype.attack_range)

                # Archetype-specific distance thresholds
                preferred = self._archetype.attack_range * 0.7
                too_close = self._archetype.attack_range * 0.3
                bb.set("at_preferred_distance",
                       abs(dist - preferred) < 30.0)
                bb.set("target_too_close", dist < too_close)

                bb.set("target_position", target_pos)
            else:
                bb.set("distance_to_target", float("inf"))
                bb.set("target_detected", False)
                bb.set("target_in_attack_range", False)
        else:
            bb.set("target", None)
            bb.set("distance_to_target", float("inf"))
            bb.set("target_detected", False)
            bb.set("target_in_attack_range", False)
            bb.set("at_preferred_distance", False)
            bb.set("target_too_close", False)

        # Retreat flag (set externally or after attack)
        should_retreat = bb.get("should_retreat", False)
        bb.set("should_retreat", should_retreat)

    # ------------------------------------------------------------------
    # Internal: Timers
    # ------------------------------------------------------------------

    def _update_timers(self, dt: float) -> None:
        """Tick any timers managed outside of states."""
        # Internal cooldown tracking (supplements CombatStateComponent)
        current_cd = self._blackboard.get("_internal_attack_cd", 0.0)
        if current_cd > 0:
            current_cd -= dt
            self._blackboard.set("_internal_attack_cd", max(0.0, current_cd))
            if current_cd <= 0:
                self._blackboard.set("attack_on_cooldown", False)

    # ------------------------------------------------------------------
    # Internal: Movement helpers
    # ------------------------------------------------------------------

    def _get_position(self) -> Vec2:
        """Get this AI actor's position."""
        if self._actor is None:
            return Vec2(0, 0)
        from world.transform import TransformComponent
        transform = self._actor.get_component(TransformComponent)
        if transform is not None:
            return Vec2(transform.x, transform.y)
        return Vec2(0, 0)

    def _get_actor_position(self, actor: "Actor") -> Optional[Vec2]:
        """Get another actor's position."""
        from world.transform import TransformComponent
        transform = actor.get_component(TransformComponent)
        if transform is not None:
            return Vec2(transform.x, transform.y)
        return None

    def _get_target_actor(self) -> Optional["Actor"]:
        """Get the current target actor."""
        target = self._blackboard.get("target")
        if target is not None and hasattr(target, "enabled") and target.enabled:
            return target
        return None

    def _move_toward(self, target_pos: Vec2, speed: float, dt: float) -> None:
        """Move this AI toward a world position."""
        if self._actor is None:
            return
        from world.transform import TransformComponent
        transform = self._actor.get_component(TransformComponent)
        if transform is None:
            return

        my_pos = Vec2(transform.x, transform.y)
        diff = target_pos - my_pos
        dist = diff.length()
        if dist < 1.0:
            return

        direction = diff.normalized()
        step = direction * speed * dt
        transform.translate(step.x, step.y)

    def _move_away_from(self, target_pos: Vec2, speed: float, dt: float) -> None:
        """Move this AI away from a world position."""
        if self._actor is None:
            return
        from world.transform import TransformComponent
        transform = self._actor.get_component(TransformComponent)
        if transform is None:
            return

        my_pos = Vec2(transform.x, transform.y)
        diff = my_pos - target_pos
        dist = diff.length()
        if dist < 1.0:
            # Just push away in an arbitrary direction
            diff = Vec2(1, 0)

        direction = diff.normalized()
        step = direction * speed * dt
        transform.translate(step.x, step.y)

    # ------------------------------------------------------------------
    # Internal: Attack helpers
    # ------------------------------------------------------------------

    def _get_attack_duration(self) -> float:
        """Get attack windup duration based on archetype."""
        if isinstance(self._archetype, TankChargerArchetype):
            return 1.0
        if isinstance(self._archetype, RangedKiterArchetype):
            return 0.5
        return 0.3  # MeleeChaser / default

    def _get_retreat_duration(self) -> float:
        """Get retreat duration based on archetype."""
        if isinstance(self._archetype, TankChargerArchetype):
            return 1.5
        if isinstance(self._archetype, RangedKiterArchetype):
            return 0.8
        return 0.5  # MeleeChaser / default

    def _set_attack_cooldown(self) -> None:
        """Set attack cooldown on both CombatStateComponent and internal."""
        from world.components.combat_state_component import CombatStateComponent
        duration = self._archetype.attack_cooldown

        combat_state = self._actor.get_component(CombatStateComponent) if self._actor else None
        if combat_state is not None:
            combat_state.set_cooldown("attack", duration)

        self._blackboard.set("attack_on_cooldown", True)
        self._blackboard.set("_internal_attack_cd", duration)

    def _execute_attack(self) -> None:
        """Execute the attack action."""
        if self._actor is None:
            return
        from world.components.hitbox_component import HitboxComponent

        hitbox = self._actor.get_component(HitboxComponent)
        if hitbox is not None:
            hitbox.activate()
            # Hitbox stays active for combat system to process overlap.
            # Will be deactivated when exiting ATTACK state via _do_transition.

        # Fire projectile for ranged archetypes
        if isinstance(self._archetype, RangedKiterArchetype) and self._archetype.projectile_speed > 0:
            self._blackboard.set("fire_projectile", True)
            self._blackboard.set("projectile_speed", self._archetype.projectile_speed)
            self._blackboard.set("projectile_damage", self._archetype.attack_damage)

        # Clear retreat flag (melee sets it after attacking)
        self._blackboard.set("should_retreat", False)

        # Melee chaser: flag retreat for next tick
        if isinstance(self._archetype, MeleeChaserArchetype):
            self._blackboard.set("should_retreat", True)

    # ------------------------------------------------------------------
    # Internal: Transition helper
    # ------------------------------------------------------------------

    def _do_transition(self, state_name: str) -> bool:
        """Attempt a state machine transition. Returns True on success."""
        if self._sm is None:
            return False
        if self._sm.is_in_state(state_name):
            return True  # Already there
        if state_name in self._sm.states:
            # Deactivate hitbox when leaving ATTACK state
            if self._sm.current_state == "ATTACK" and self._actor:
                from world.components.hitbox_component import HitboxComponent
                hitbox = self._actor.get_component(HitboxComponent)
                if hitbox is not None:
                    hitbox.deactivate()
            self._sm.transition(state_name)
            return True
        return False


__all__ = [
    "AIState",
    "EnemyAI",
]

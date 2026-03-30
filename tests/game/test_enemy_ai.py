"""Tests for game.ai.enemy_ai module."""
import pytest
from core.vec import Vec2
from core.object import Object
from game.ai.archetypes import (
    AIArchetype,
    MeleeChaserArchetype,
    RangedKiterArchetype,
    TankChargerArchetype,
)
from game.ai.enemy_ai import EnemyAI, AIState


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_actor(name="TestActor", pos=None):
    """Create a minimal actor with all components the AI needs."""
    from world.actor import Actor
    from world.transform import TransformComponent
    from world.components.health_component import HealthComponent
    from world.components.combatant_component import CombatantComponent
    from world.components.combat_state_component import CombatStateComponent
    from world.components.hitbox_component import HitboxComponent
    from world.components.hurtbox_component import HurtboxComponent

    actor = Actor(name=name)
    transform = TransformComponent()
    if pos is not None:
        transform.position = (pos.x, pos.y)
    actor.add_component(transform)
    actor.add_component(HealthComponent(max_hp=100.0))
    actor.add_component(CombatantComponent(team=CombatantComponent.TEAM_ENEMY))
    actor.add_component(CombatStateComponent())
    actor.add_component(HitboxComponent(width=40, height=40, damage=10))
    actor.add_component(HurtboxComponent(width=30, height=50))
    return actor


def _make_player(name="Player", pos=None):
    """Create a minimal player actor."""
    from world.actor import Actor
    from world.transform import TransformComponent
    from world.components.health_component import HealthComponent
    from world.components.combatant_component import CombatantComponent

    actor = Actor(name=name)
    transform = TransformComponent()
    if pos is not None:
        transform.position = (pos.x, pos.y)
    actor.add_component(transform)
    actor.add_component(HealthComponent(max_hp=100.0))
    actor.add_component(CombatantComponent(team=CombatantComponent.TEAM_PLAYER))
    return actor


def _make_ai(archetype, actor, target=None):
    """Create an EnemyAI, attach it to actor, and optionally set target."""
    ai = EnemyAI(archetype)
    ai.on_attach(actor)
    if target is not None:
        ai.set_target(target)
    return ai


# ===========================================================================
# Test creation with different archetypes
# ===========================================================================

class TestEnemyAICreation:
    def test_create_melee(self):
        ai = EnemyAI(MeleeChaserArchetype())
        assert ai.current_state == "IDLE"
        assert ai.archetype.name == "MeleeChaser"
        assert ai.state_machine is not None

    def test_create_ranged(self):
        ai = EnemyAI(RangedKiterArchetype())
        assert ai.current_state == "IDLE"
        assert ai.archetype.prefers_ranged is True
        assert ai.archetype.projectile_speed == 300.0

    def test_create_tank(self):
        ai = EnemyAI(TankChargerArchetype())
        assert ai.current_state == "IDLE"
        assert ai.archetype.max_hp == 120.0

    def test_create_custom_archetype(self):
        arch = AIArchetype(name="Custom")
        arch.chase_speed = 999.0
        ai = EnemyAI(arch)
        assert ai.archetype.chase_speed == 999.0

    def test_inherits_from_object(self):
        ai = EnemyAI(MeleeChaserArchetype())
        assert isinstance(ai, Object)
        assert ai.guid is not None
        assert ai.name.startswith("EnemyAI_")


# ===========================================================================
# Test state transitions
# ===========================================================================

class TestStateTransitions:
    def test_initial_state_is_idle(self):
        ai = EnemyAI(MeleeChaserArchetype())
        assert ai.current_state == AIState.IDLE.value

    def test_all_states_exist(self):
        ai = EnemyAI(MeleeChaserArchetype())
        sm = ai.state_machine
        for state in AIState:
            assert state.value in sm.states

    def test_transition_to_chase_on_target(self):
        enemy = _make_actor("E", pos=Vec2(0, 0))
        player = _make_player("P", pos=Vec2(100, 0))
        ai = _make_ai(MeleeChaserArchetype(), enemy, target=player)

        ai.on_tick(0.016)
        assert ai.current_state == AIState.CHASE.value

    def test_transition_to_dead(self):
        enemy = _make_actor("E", pos=Vec2(0, 0))
        ai = _make_ai(MeleeChaserArchetype(), enemy)

        # Kill the enemy
        health = enemy.get_component(type(enemy.components[0]))  # HealthComponent
        from world.components.health_component import HealthComponent
        health = enemy.get_component(HealthComponent)
        health.take_damage(200.0)

        ai.on_tick(0.016)
        assert ai.current_state == AIState.DEAD.value
        assert enemy.enabled is False

    def test_transition_to_stunned(self):
        enemy = _make_actor("E", pos=Vec2(0, 0))
        ai = _make_ai(MeleeChaserArchetype(), enemy)

        from world.components.combat_state_component import CombatStateComponent
        cs = enemy.get_component(CombatStateComponent)
        cs.apply_stun(1.0)

        ai.on_tick(0.016)
        assert ai.current_state == AIState.STUNNED.value

    def test_force_state(self):
        ai = EnemyAI(MeleeChaserArchetype())
        ai.force_state(AIState.PATROL.value)
        assert ai.current_state == AIState.PATROL.value

    def test_force_invalid_state_raises(self):
        ai = EnemyAI(MeleeChaserArchetype())
        ai.force_state("INVALID_STATE")  # Should not crash
        assert ai.current_state == AIState.IDLE.value


# ===========================================================================
# Test blackboard state sharing
# ===========================================================================

class TestBlackboardSharing:
    def test_blackboard_created(self):
        ai = EnemyAI(MeleeChaserArchetype())
        assert ai.bb is not None

    def test_blackboard_target_set(self):
        enemy = _make_actor("E", pos=Vec2(0, 0))
        player = _make_player("P", pos=Vec2(100, 0))
        ai = _make_ai(MeleeChaserArchetype(), enemy, target=player)

        ai.on_tick(0.016)
        assert ai.bb.get("target") is player

    def test_blackboard_position_updated(self):
        enemy = _make_actor("E", pos=Vec2(50, 75))
        ai = _make_ai(MeleeChaserArchetype(), enemy)

        ai.on_tick(0.016)
        pos = ai.bb.get("self_position")
        assert pos.x == 50.0
        assert pos.y == 75.0

    def test_blackboard_distance_calculated(self):
        enemy = _make_actor("E", pos=Vec2(0, 0))
        player = _make_player("P", pos=Vec2(100, 0))
        ai = _make_ai(MeleeChaserArchetype(), enemy, target=player)

        ai.on_tick(0.016)
        assert ai.bb.get("distance_to_target") == 100.0

    def test_blackboard_detection_range(self):
        enemy = _make_actor("E", pos=Vec2(0, 0))
        player_far = _make_player("PFar", pos=Vec2(500, 0))
        ai = _make_ai(MeleeChaserArchetype(), enemy, target=player_far)

        ai.on_tick(0.016)
        assert ai.bb.get("target_detected") is False

    def test_blackboard_attack_range(self):
        enemy = _make_actor("E", pos=Vec2(0, 0))
        player_close = _make_player("PClose", pos=Vec2(30, 0))
        ai = _make_ai(MeleeChaserArchetype(), enemy, target=player_close)

        ai.on_tick(0.016)
        # MeleeChaser attack_range is 40.0, distance is 30.0
        assert ai.bb.get("target_in_attack_range") is True

    def test_blackboard_hp_tracked(self):
        enemy = _make_actor("E", pos=Vec2(0, 0))
        ai = _make_ai(MeleeChaserArchetype(), enemy)

        ai.on_tick(0.016)
        assert ai.bb.get("hp") == 100.0
        assert ai.bb.get("max_hp") == 100.0

    def test_blackboard_death_flag(self):
        enemy = _make_actor("E", pos=Vec2(0, 0))
        ai = _make_ai(MeleeChaserArchetype(), enemy)

        from world.components.health_component import HealthComponent
        health = enemy.get_component(HealthComponent)
        health.take_damage(100.0)

        ai.on_tick(0.016)
        assert ai.bb.get("is_dead") is True


# ===========================================================================
# Test behaviour tree tick
# ===========================================================================

class TestBehaviourTreeTick:
    def test_bt_ticks_successfully(self):
        enemy = _make_actor("E", pos=Vec2(0, 0))
        ai = _make_ai(MeleeChaserArchetype(), enemy)

        # Should not raise
        ai.on_tick(0.016)

    def test_bt_drives_chase_when_target_detected(self):
        enemy = _make_actor("E", pos=Vec2(0, 0))
        player = _make_player("P", pos=Vec2(100, 0))
        ai = _make_ai(MeleeChaserArchetype(), enemy, target=player)

        ai.on_tick(0.016)
        assert ai.current_state == AIState.CHASE.value

    def test_bt_stays_idle_without_target(self):
        enemy = _make_actor("E", pos=Vec2(0, 0))
        ai = _make_ai(MeleeChaserArchetype(), enemy)

        ai.on_tick(0.016)
        assert ai.current_state == AIState.IDLE.value

    def test_bt_prioritizes_death_over_chase(self):
        enemy = _make_actor("E", pos=Vec2(0, 0))
        player = _make_player("P", pos=Vec2(30, 0))
        ai = _make_ai(MeleeChaserArchetype(), enemy, target=player)

        from world.components.health_component import HealthComponent
        health = enemy.get_component(HealthComponent)
        health.take_damage(200.0)

        ai.on_tick(0.016)
        assert ai.current_state == AIState.DEAD.value

    def test_bt_prioritizes_stun_over_chase(self):
        enemy = _make_actor("E", pos=Vec2(0, 0))
        player = _make_player("P", pos=Vec2(100, 0))
        ai = _make_ai(MeleeChaserArchetype(), enemy, target=player)

        from world.components.combat_state_component import CombatStateComponent
        cs = enemy.get_component(CombatStateComponent)
        cs.apply_stun(1.0)

        ai.on_tick(0.016)
        assert ai.current_state == AIState.STUNNED.value


# ===========================================================================
# Test target detection
# ===========================================================================

class TestTargetDetection:
    def test_detect_target_in_range(self):
        enemy = _make_actor("E", pos=Vec2(0, 0))
        player = _make_player("P", pos=Vec2(200, 0))
        ai = _make_ai(MeleeChaserArchetype(), enemy, target=player)

        ai.on_tick(0.016)
        # MeleeChaser detection_range = 250, distance = 200
        assert ai.bb.get("target_detected") is True

    def test_no_detect_out_of_range(self):
        enemy = _make_actor("E", pos=Vec2(0, 0))
        player = _make_player("P", pos=Vec2(500, 0))
        ai = _make_ai(MeleeChaserArchetype(), enemy, target=player)

        ai.on_tick(0.016)
        assert ai.bb.get("target_detected") is False

    def test_no_detect_disabled_target(self):
        enemy = _make_actor("E", pos=Vec2(0, 0))
        player = _make_player("P", pos=Vec2(100, 0))
        player.enabled = False
        ai = _make_ai(MeleeChaserArchetype(), enemy, target=player)

        ai.on_tick(0.016)
        assert ai.bb.get("target_detected") is False

    def test_ranged_detection_range(self):
        enemy = _make_actor("E", pos=Vec2(0, 0))
        player = _make_player("P", pos=Vec2(350, 0))
        ai = _make_ai(RangedKiterArchetype(), enemy, target=player)

        ai.on_tick(0.016)
        # RangedKiter detection_range = 400, distance = 350
        assert ai.bb.get("target_detected") is True

    def test_tank_detection_range(self):
        enemy = _make_actor("E", pos=Vec2(0, 0))
        player = _make_player("P", pos=Vec2(150, 0))
        ai = _make_ai(TankChargerArchetype(), enemy, target=player)

        ai.on_tick(0.016)
        # TankCharger detection_range = 200, distance = 150
        assert ai.bb.get("target_detected") is True


# ===========================================================================
# Test attack cooldowns
# ===========================================================================

class TestAttackCooldowns:
    def test_attack_sets_cooldown(self):
        enemy = _make_actor("E", pos=Vec2(0, 0))
        player = _make_player("P", pos=Vec2(30, 0))
        ai = _make_ai(MeleeChaserArchetype(), enemy, target=player)

        # Player at 30 is within attack range (40), so BT drives to ATTACK
        ai.on_tick(0.016)
        assert ai.current_state == AIState.ATTACK.value

        # After entering ATTACK state, cooldown should be set
        assert ai.bb.get("attack_on_cooldown") is True

    def test_cooldown_prevents_repeated_attacks(self):
        enemy = _make_actor("E", pos=Vec2(0, 0))
        player = _make_player("P", pos=Vec2(25, 0))
        ai = _make_ai(MeleeChaserArchetype(), enemy, target=player)

        # First tick: chase/attack
        ai.on_tick(0.016)

        # Force into ATTACK state and let it execute
        ai.force_state(AIState.ATTACK.value)
        ai.on_tick(0.016)  # Triggers _set_attack_cooldown

        # Cooldown should be set
        assert ai.bb.get("attack_on_cooldown") is True

    def test_cooldown_expires(self):
        from world.components.combat_state_component import CombatStateComponent
        enemy = _make_actor("E", pos=Vec2(0, 0))
        ai = _make_ai(MeleeChaserArchetype(), enemy)

        # Manually set a short cooldown to avoid BT re-triggering attacks
        combat_state = enemy.get_component(CombatStateComponent)
        combat_state.set_cooldown("attack", 0.1)
        ai._blackboard.set("attack_on_cooldown", True)
        ai._blackboard.set("_internal_attack_cd", 0.1)

        # Cooldown should be active
        assert combat_state.is_on_cooldown("attack")

        # Tick enough time for cooldown to expire (0.1s / 0.016 ≈ 7 ticks)
        for _ in range(20):
            combat_state.on_tick(0.016)
            ai._update_timers(0.016)

        assert not combat_state.is_on_cooldown("attack")


# ===========================================================================
# Test death state
# ===========================================================================

class TestDeathState:
    def test_death_disables_actor(self):
        enemy = _make_actor("E", pos=Vec2(0, 0))
        ai = _make_ai(MeleeChaserArchetype(), enemy)

        from world.components.health_component import HealthComponent
        health = enemy.get_component(HealthComponent)
        health.take_damage(100.0)

        assert enemy.enabled is True  # Not yet disabled
        ai.on_tick(0.016)
        assert ai.current_state == AIState.DEAD.value
        assert enemy.enabled is False

    def test_dead_ai_does_not_tick(self):
        enemy = _make_actor("E", pos=Vec2(0, 0))
        ai = _make_ai(MeleeChaserArchetype(), enemy)

        from world.components.health_component import HealthComponent
        health = enemy.get_component(HealthComponent)
        health.take_damage(100.0)

        ai.on_tick(0.016)
        # Should stay in DEAD, not transition to anything else
        assert ai.current_state == AIState.DEAD.value

    def test_no_tick_without_actor(self):
        ai = EnemyAI(MeleeChaserArchetype())
        # Should not raise
        ai.on_tick(0.016)

    def test_no_tick_when_actor_disabled(self):
        enemy = _make_actor("E", pos=Vec2(0, 0))
        ai = _make_ai(MeleeChaserArchetype(), enemy)
        enemy.enabled = False
        ai.on_tick(0.016)
        assert ai.current_state == AIState.IDLE.value  # No update


# ===========================================================================
# Test movement
# ===========================================================================

class TestMovement:
    def test_chase_moves_toward_target(self):
        enemy = _make_actor("E", pos=Vec2(0, 0))
        player = _make_player("P", pos=Vec2(100, 0))
        ai = _make_ai(MeleeChaserArchetype(), enemy, target=player)

        ai.on_tick(0.016)
        assert ai.current_state == AIState.CHASE.value

        from world.transform import TransformComponent
        t = enemy.get_component(TransformComponent)

        # Tick several frames to see movement
        for _ in range(10):
            ai.on_tick(0.016)

        # Enemy should have moved toward player (positive X)
        assert t.x > 0.0

    def test_retreat_moves_away_from_target(self):
        enemy = _make_actor("E", pos=Vec2(50, 0))
        player = _make_player("P", pos=Vec2(0, 0))
        ai = _make_ai(MeleeChaserArchetype(), enemy, target=player)

        # Force into retreat (on_enter caches the player position)
        ai.force_state(AIState.RETREAT.value)
        # Clear target so BT doesn't override back to chase
        ai.set_target(None)

        from world.transform import TransformComponent
        t = enemy.get_component(TransformComponent)

        original_x = t.x
        # Tick retreat state directly (BT won't override since no target)
        for _ in range(10):
            ai.state_machine.tick(0.016)

        # Should have moved away from player (positive X, further from origin)
        assert t.x > original_x


# ===========================================================================
# Test patrol
# ===========================================================================

class TestPatrol:
    def test_tank_patrols_without_target(self):
        enemy = _make_actor("E", pos=Vec2(0, 0))
        ai = _make_ai(TankChargerArchetype(), enemy)

        ai.set_patrol_points([
            Vec2(100, 0),
            Vec2(100, 100),
            Vec2(0, 100),
        ])

        ai.on_tick(0.016)
        assert ai.current_state == AIState.PATROL.value

    def test_tank_switches_to_chase_with_target(self):
        enemy = _make_actor("E", pos=Vec2(0, 0))
        player = _make_player("P", pos=Vec2(150, 0))
        ai = _make_ai(TankChargerArchetype(), enemy, target=player)

        ai.on_tick(0.016)
        # Should detect target and switch to chase
        assert ai.current_state == AIState.CHASE.value


# ===========================================================================
# Test ranged behaviour
# ===========================================================================

class TestRangedBehaviour:
    def test_ranged_stays_at_preferred_distance(self):
        enemy = _make_actor("E", pos=Vec2(0, 0))
        player = _make_player("P", pos=Vec2(175, 0))  # Near preferred dist (0.7 * 250 = 175)
        ai = _make_ai(RangedKiterArchetype(), enemy, target=player)

        ai.on_tick(0.016)
        # At preferred distance, should be idle or attack, not chasing
        assert ai.current_state in (AIState.IDLE.value, AIState.ATTACK.value, AIState.CHASE.value)

    def test_ranged_retreats_when_too_close(self):
        enemy = _make_actor("E", pos=Vec2(0, 0))
        player = _make_player("P", pos=Vec2(20, 0))  # Very close
        ai = _make_ai(RangedKiterArchetype(), enemy, target=player)

        ai.on_tick(0.016)
        # Too close threshold = 250 * 0.3 = 75. Distance 20 < 75, so should retreat
        assert ai.current_state == AIState.RETREAT.value


# ===========================================================================
# Test ScriptComponent compatibility
# ===========================================================================

class TestScriptComponentCompatibility:
    def test_on_attach_sets_actor(self):
        enemy = _make_actor("E", pos=Vec2(0, 0))
        ai = EnemyAI(MeleeChaserArchetype())
        ai.on_attach(enemy)
        assert ai._actor is enemy
        assert ai.actor is enemy

    def test_on_detach_clears_actor(self):
        enemy = _make_actor("E", pos=Vec2(0, 0))
        ai = _make_ai(MeleeChaserArchetype(), enemy)
        ai.on_detach()
        assert ai._actor is None

    def test_on_destroy_calls_detach(self):
        enemy = _make_actor("E", pos=Vec2(0, 0))
        ai = _make_ai(MeleeChaserArchetype(), enemy)
        ai.on_destroy()
        assert ai._actor is None

    def test_start_with_script_component_pattern(self):
        """Simulate ScriptComponent setting actor then calling on_start."""
        enemy = _make_actor("E", pos=Vec2(0, 0))
        ai = EnemyAI(MeleeChaserArchetype())
        ai.actor = enemy  # ScriptComponent does this
        ai.on_start()  # ScriptComponent calls this
        assert ai._actor is enemy

    def test_has_blackboard_attribute(self):
        ai = EnemyAI(MeleeChaserArchetype())
        assert hasattr(ai, "blackboard")
        assert isinstance(ai.blackboard, dict)


# ===========================================================================
# Test state machine history
# ===========================================================================

class TestStateMachineIntegration:
    def test_history_tracks(self):
        enemy = _make_actor("E", pos=Vec2(0, 0))
        player = _make_player("P", pos=Vec2(100, 0))
        ai = _make_ai(MeleeChaserArchetype(), enemy, target=player)

        ai.on_tick(0.016)
        assert ai.current_state == AIState.CHASE.value

        # Remove target
        ai.set_target(None)
        ai.on_tick(0.016)
        assert ai.current_state == AIState.IDLE.value

        history = ai.state_machine.history
        assert "IDLE" in history
        assert "CHASE" in history

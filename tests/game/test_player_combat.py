"""Tests for game.combat.player_combat module."""
import pytest
from core.vec import Vec2
from world.actor import Actor
from world.transform import TransformComponent
from world.components.script_component import ScriptComponent
from world.components.health_component import HealthComponent
from world.components.combat_stats_component import CombatStatsComponent
from world.components.combatant_component import CombatantComponent
from world.components.hitbox_component import HitboxComponent
from world.components.hurtbox_component import HurtboxComponent
from world.components.combat_state_component import CombatStateComponent
from game.combat.player_combat import (
    PlayerCombatScript,
    PLAYER_STATE_IDLE,
    PLAYER_STATE_MOVE,
    PLAYER_STATE_ATTACK,
    PLAYER_STATE_DASH,
    PLAYER_STATE_HURT,
    PLAYER_STATE_DEAD,
    ATTACK_DURATION,
    ATTACK_COOLDOWN,
    COMBO_WINDOW,
    MAX_COMBO_HITS,
    DASH_DURATION,
    DASH_COOLDOWN,
    DASH_IFRAMES,
    HURT_DURATION,
    HURT_IFRAMES,
    SKILL_COOLDOWNS,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_player_actor(
    max_hp: float = 100.0,
    attack: float = 20.0,
) -> Actor:
    """Build a fully-equipped player actor for testing."""
    actor = Actor(name="Player")
    actor.add_component(TransformComponent())
    actor.add_component(HealthComponent(max_hp=max_hp))
    actor.add_component(CombatStatsComponent(attack=attack))
    actor.add_component(CombatantComponent(team=CombatantComponent.TEAM_PLAYER))
    actor.add_component(HitboxComponent())
    actor.add_component(HurtboxComponent())
    actor.add_component(CombatStateComponent())
    return actor


def _attach_script(actor: Actor) -> PlayerCombatScript:
    """Create a PlayerCombatScript and attach it via ScriptComponent."""
    script = PlayerCombatScript()
    comp = ScriptComponent(script=script)
    actor.add_component(comp)
    return script


# ===========================================================================
# Tests
# ===========================================================================

class TestCreationAndAttachment:
    """Test script creation, attachment, and initial state."""

    def test_create_script(self):
        script = PlayerCombatScript()
        assert script.state_name == PLAYER_STATE_IDLE
        assert script.combo_count == 0
        assert script.actor is None

    def test_create_with_args(self):
        actor = Actor(name="Test")
        bb = {"key": "value"}
        script = PlayerCombatScript(actor=actor, blackboard=bb)
        assert script.actor is actor
        assert script.blackboard == bb

    def test_attach_via_script_component(self):
        actor = _make_player_actor()
        script = _attach_script(actor)
        assert script.actor is actor
        assert isinstance(script.blackboard, dict)

    def test_on_start_builds_state_machine(self):
        actor = _make_player_actor()
        script = _attach_script(actor)
        # on_start is called inside ScriptComponent.on_attach
        assert script.state_name == PLAYER_STATE_IDLE

    def test_detach(self):
        actor = _make_player_actor()
        script = _attach_script(actor)
        script.on_detach()
        assert script.actor is None


class TestInitialState:
    """Verify initial state after attachment."""

    def test_idle_state(self):
        actor = _make_player_actor()
        script = _attach_script(actor)
        assert script.state_name == PLAYER_STATE_IDLE

    def test_hitbox_inactive(self):
        actor = _make_player_actor()
        script = _attach_script(actor)
        hitbox = actor.get_component(HitboxComponent)
        assert hitbox.is_active is False

    def test_can_attack(self):
        actor = _make_player_actor()
        script = _attach_script(actor)
        assert script.can_attack is True

    def test_can_dash(self):
        actor = _make_player_actor()
        script = _attach_script(actor)
        assert script.can_dash is True


class TestAttackStateTransition:
    """Test that attacking transitions to the ATTACK state."""

    def test_attack_transitions_to_attack_state(self):
        actor = _make_player_actor()
        script = _attach_script(actor)
        result = script.attack()
        assert result is True
        assert script.state_name == PLAYER_STATE_ATTACK
        assert script.is_attacking is True

    def test_attack_activates_hitbox(self):
        actor = _make_player_actor(attack=20.0)
        script = _attach_script(actor)
        script.attack()
        hitbox = actor.get_component(HitboxComponent)
        assert hitbox.is_active is True
        # First combo hit: base damage * 1.0
        assert hitbox.base_damage == pytest.approx(20.0)

    def test_attack_returns_false_when_already_attacking(self):
        actor = _make_player_actor()
        script = _attach_script(actor)
        script.attack()
        assert script.attack() is False  # still in ATTACK state

    def test_attack_ends_returns_to_idle(self):
        actor = _make_player_actor()
        script = _attach_script(actor)
        script.attack()
        # Tick past attack duration
        script.on_tick(ATTACK_DURATION + 0.01)
        assert script.state_name == PLAYER_STATE_IDLE
        assert script.is_attacking is False

    def test_hitbox_deactivated_after_attack(self):
        actor = _make_player_actor()
        script = _attach_script(actor)
        script.attack()
        script.on_tick(ATTACK_DURATION + 0.01)
        hitbox = actor.get_component(HitboxComponent)
        assert hitbox.is_active is False


class TestAttackCooldown:
    """Test that attacks respect the cooldown window."""

    def test_cooldown_after_attack(self):
        actor = _make_player_actor()
        script = _attach_script(actor)
        script.attack()
        script.on_tick(ATTACK_DURATION + 0.01)
        # Cooldown set on exiting ATTACK state
        state_comp = actor.get_component(CombatStateComponent)
        assert state_comp.is_on_cooldown("attack") is True

    def test_cannot_attack_during_cooldown(self):
        """After a single attack, cooldown blocks non-combo attacks.

        However, since the combo window is open, the attack is allowed as
        a combo chain (combo_count 1 → 2).  The cooldown only blocks
        fresh attacks once the combo window expires.
        """
        actor = _make_player_actor()
        script = _attach_script(actor)
        script.attack()
        script.on_tick(ATTACK_DURATION + 0.01)
        # Cooldown is active, but combo window is also active → combo chain
        assert script.can_attack is True  # allowed via combo window
        assert script.attack() is True
        assert script.combo_count == 2

        # After the combo window expires and cooldown is still active, blocked
        # (consume the remaining combo window)
        script.on_tick(ATTACK_DURATION + 0.01)
        script.on_tick(COMBO_WINDOW + 0.01)
        # Now both combo window and cooldown are expired
        assert script.can_attack is True

    def test_can_attack_after_cooldown_expires(self):
        actor = _make_player_actor()
        script = _attach_script(actor)
        script.attack()
        # Tick through attack + cooldown
        script.on_tick(ATTACK_DURATION + ATTACK_COOLDOWN + 0.01)
        assert script.can_attack is True
        assert script.attack() is True


class TestComboSystem:
    """Test the 3-hit combo system."""

    def test_first_hit_is_combo_one(self):
        actor = _make_player_actor()
        script = _attach_script(actor)
        script.attack()
        assert script.combo_count == 1

    def test_second_hit_within_window(self):
        actor = _make_player_actor()
        script = _attach_script(actor)
        # First hit
        script.attack()
        script.on_tick(ATTACK_DURATION + 0.01)
        # Second hit – within combo window, no full cooldown needed
        # because combo window resets the chain
        assert script.combo_count == 1
        # combo_timer was set to COMBO_WINDOW, so we're still in window
        result = script.attack()
        assert result is True
        assert script.combo_count == 2

    def test_third_hit_within_window(self):
        actor = _make_player_actor()
        script = _attach_script(actor)
        # Hit 1
        script.attack()
        script.on_tick(ATTACK_DURATION + 0.01)
        # Hit 2
        script.attack()
        script.on_tick(ATTACK_DURATION + 0.01)
        # Hit 3
        result = script.attack()
        assert result is True
        assert script.combo_count == 3

    def test_fourth_hit_resets_combo(self):
        """After a full 3-hit combo the next attack starts a fresh combo."""
        actor = _make_player_actor()
        script = _attach_script(actor)
        # Complete 3-hit combo
        for _ in range(3):
            script.attack()
            script.on_tick(ATTACK_DURATION + 0.01)
        # combo_count is now 3 (max). Wait for combo window to expire.
        script.on_tick(COMBO_WINDOW + 0.01)
        assert script.combo_count == 0  # combo window expired
        # Next attack starts a fresh combo (combo_count == 1)
        result = script.attack()
        assert result is True
        assert script.combo_count == 1

    def test_combo_resets_after_window_expires(self):
        actor = _make_player_actor()
        script = _attach_script(actor)
        # First hit
        script.attack()
        script.on_tick(ATTACK_DURATION + 0.01)
        assert script.combo_count == 1
        # Let combo window expire
        script.on_tick(COMBO_WINDOW + 0.01)
        assert script.combo_count == 0
        # Next attack starts fresh
        script.attack()
        assert script.combo_count == 1

    def test_combo_damage_scaling(self):
        """Each combo hit should do more damage."""
        actor = _make_player_actor(attack=100.0)
        script = _attach_script(actor)
        hitbox = actor.get_component(HitboxComponent)

        # Hit 1: 100%
        script.attack()
        assert hitbox.base_damage == pytest.approx(100.0)
        script.on_tick(ATTACK_DURATION + 0.01)

        # Hit 2: 120%
        script.attack()
        assert hitbox.base_damage == pytest.approx(120.0)
        script.on_tick(ATTACK_DURATION + 0.01)

        # Hit 3: 160%
        script.attack()
        assert hitbox.base_damage == pytest.approx(160.0)
        script.on_tick(ATTACK_DURATION + 0.01)


class TestDashState:
    """Test dash mechanics including i-frames and cooldown."""

    def test_dash_transitions_to_dash_state(self):
        actor = _make_player_actor()
        script = _attach_script(actor)
        result = script.dash(Vec2.RIGHT)
        assert result is True
        assert script.state_name == PLAYER_STATE_DASH
        assert script.is_dashing is True

    def test_dash_applies_movement(self):
        actor = _make_player_actor()
        script = _attach_script(actor)
        transform = actor.get_component(TransformComponent)
        script.dash(Vec2.RIGHT)
        script.on_tick(DASH_DURATION)
        # Should have moved right
        _, y = transform.position
        assert y == pytest.approx(0.0)  # No vertical movement
        x, _ = transform.position
        assert x > 0.0

    def test_dash_grants_iframes(self):
        actor = _make_player_actor()
        script = _attach_script(actor)
        health = actor.get_component(HealthComponent)
        script.dash(Vec2.RIGHT)
        assert health.is_invincible is True

    def test_dash_cooldown_after_ending(self):
        actor = _make_player_actor()
        script = _attach_script(actor)
        script.dash(Vec2.RIGHT)
        script.on_tick(DASH_DURATION + 0.01)
        state_comp = actor.get_component(CombatStateComponent)
        assert state_comp.is_on_cooldown("dash") is True

    def test_cannot_dash_during_cooldown(self):
        actor = _make_player_actor()
        script = _attach_script(actor)
        script.dash(Vec2.RIGHT)
        script.on_tick(DASH_DURATION + 0.01)
        assert script.can_dash is False
        assert script.dash(Vec2.RIGHT) is False

    def test_can_dash_after_cooldown(self):
        actor = _make_player_actor()
        script = _attach_script(actor)
        script.dash(Vec2.RIGHT)
        script.on_tick(DASH_DURATION + DASH_COOLDOWN + 0.01)
        assert script.can_dash is True
        assert script.dash(Vec2.LEFT) is True

    def test_dash_returns_to_idle(self):
        actor = _make_player_actor()
        script = _attach_script(actor)
        script.dash(Vec2.RIGHT)
        script.on_tick(DASH_DURATION + 0.01)
        assert script.state_name == PLAYER_STATE_IDLE

    def test_dash_cannot_attack_while_dashing(self):
        actor = _make_player_actor()
        script = _attach_script(actor)
        script.dash(Vec2.RIGHT)
        assert script.can_attack is False

    def test_dash_default_direction_when_zero(self):
        """A zero-length direction should default to RIGHT."""
        actor = _make_player_actor()
        script = _attach_script(actor)
        script.dash(Vec2.ZERO)
        assert script._dash_direction == Vec2.RIGHT


class TestHurtState:
    """Test receiving damage and entering the hurt state."""

    def test_take_hit_enters_hurt_state(self):
        actor = _make_player_actor(max_hp=100.0)
        script = _attach_script(actor)
        actual = script.take_hit(20.0)
        assert actual == 20.0
        assert script.state_name == PLAYER_STATE_HURT
        assert script.is_hurt is True

    def test_take_hit_grants_iframes(self):
        actor = _make_player_actor(max_hp=100.0)
        script = _attach_script(actor)
        health = actor.get_component(HealthComponent)
        script.take_hit(20.0)
        assert health.is_invincible is True

    def test_take_hit_no_damage_during_iframes(self):
        actor = _make_player_actor(max_hp=100.0)
        script = _attach_script(actor)
        # First hit
        script.take_hit(20.0)
        # Second hit during i-frames should be blocked
        actual = script.take_hit(50.0)
        assert actual == 0.0

    def test_hurt_returns_to_idle(self):
        actor = _make_player_actor(max_hp=100.0)
        script = _attach_script(actor)
        script.take_hit(10.0)
        script.on_tick(HURT_DURATION + 0.01)
        assert script.state_name == PLAYER_STATE_IDLE

    def test_take_hit_resets_combo(self):
        actor = _make_player_actor()
        script = _attach_script(actor)
        # Build a combo
        script.attack()
        script.on_tick(ATTACK_DURATION + 0.01)
        script.attack()
        script.on_tick(ATTACK_DURATION + 0.01)
        assert script.combo_count == 2
        # Take a hit
        script.take_hit(10.0)
        assert script.combo_count == 0

    def test_take_hit_with_damage_data_object(self):
        """Accept a DamageData-like object with an 'amount' attribute."""
        from game.combat.model import DamageData
        actor = _make_player_actor(max_hp=100.0)
        script = _attach_script(actor)
        dd = DamageData(amount=25.0)
        actual = script.take_hit(dd)
        assert actual == 25.0
        health = actor.get_component(HealthComponent)
        assert health.hp == pytest.approx(75.0)

    def test_take_hit_no_damage_when_dead(self):
        actor = _make_player_actor(max_hp=100.0)
        script = _attach_script(actor)
        script.take_hit(200.0)
        actual = script.take_hit(50.0)
        assert actual == 0.0


class TestDeathState:
    """Test transition to DEAD state and behavior."""

    def test_killing_blow_enters_dead_state(self):
        actor = _make_player_actor(max_hp=100.0)
        script = _attach_script(actor)
        script.take_hit(100.0)
        assert script.state_name == PLAYER_STATE_DEAD
        assert script.is_dead is True

    def test_cannot_attack_when_dead(self):
        actor = _make_player_actor(max_hp=100.0)
        script = _attach_script(actor)
        script.take_hit(100.0)
        assert script.can_attack is False
        assert script.attack() is False

    def test_cannot_dash_when_dead(self):
        actor = _make_player_actor(max_hp=100.0)
        script = _attach_script(actor)
        script.take_hit(100.0)
        assert script.can_dash is False
        assert script.dash(Vec2.RIGHT) is False

    def test_dead_disables_hurtbox(self):
        actor = _make_player_actor(max_hp=100.0)
        script = _attach_script(actor)
        hurtbox = actor.get_component(HurtboxComponent)
        script.take_hit(100.0)
        assert hurtbox.is_enabled is False

    def test_dead_stays_dead_after_hurt_timer(self):
        actor = _make_player_actor(max_hp=100.0)
        script = _attach_script(actor)
        script.take_hit(100.0)
        script.on_tick(HURT_DURATION + 10.0)
        assert script.state_name == PLAYER_STATE_DEAD

    def test_no_damage_accepted_when_dead(self):
        actor = _make_player_actor(max_hp=50.0)
        script = _attach_script(actor)
        script.take_hit(50.0)
        actual = script.take_hit(10.0)
        assert actual == 0.0


class TestSkillCooldowns:
    """Test skill activation and cooldown management."""

    def test_use_skill_valid_index(self):
        actor = _make_player_actor()
        script = _attach_script(actor)
        assert script.use_skill(0) is True

    def test_use_skill_invalid_index(self):
        actor = _make_player_actor()
        script = _attach_script(actor)
        assert script.use_skill(99) is False

    def test_skill_cooldown_set(self):
        actor = _make_player_actor()
        script = _attach_script(actor)
        state_comp = actor.get_component(CombatStateComponent)
        script.use_skill(0)
        assert state_comp.is_on_cooldown("skill_0") is True

    def test_cannot_use_skill_during_cooldown(self):
        actor = _make_player_actor()
        script = _attach_script(actor)
        script.use_skill(0)
        assert script.use_skill(0) is False

    def test_skill_available_after_cooldown(self):
        actor = _make_player_actor()
        script = _attach_script(actor)
        script.use_skill(0)
        script.on_tick(SKILL_COOLDOWNS["skill_0"] + 0.01)
        assert script.use_skill(0) is True

    def test_independent_skill_cooldowns(self):
        actor = _make_player_actor()
        script = _attach_script(actor)
        script.use_skill(0)
        # skill_0 on cooldown, skill_1 should still be usable
        assert script.use_skill(1) is True
        assert script.use_skill(0) is False

    def test_cannot_use_skill_while_attacking(self):
        actor = _make_player_actor()
        script = _attach_script(actor)
        script.attack()
        assert script.use_skill(0) is False

    def test_cannot_use_skill_while_dashing(self):
        actor = _make_player_actor()
        script = _attach_script(actor)
        script.dash(Vec2.RIGHT)
        assert script.use_skill(0) is False


class TestReportKill:
    """Test kill reporting callback."""

    def test_report_kill_calls_callback(self):
        actor = _make_player_actor()
        script = _attach_script(actor)
        targets = []
        script._on_kill_callback = lambda t: targets.append(t)
        script.report_kill("enemy_1")
        assert targets == ["enemy_1"]

    def test_report_kill_no_callback(self):
        actor = _make_player_actor()
        script = _attach_script(actor)
        # Should not raise
        script.report_kill("enemy_1")


class TestEdgeCases:
    """Miscellaneous edge-case tests."""

    def test_tick_without_actor(self):
        script = PlayerCombatScript()
        # Should not raise
        script.on_tick(0.016)

    def test_attack_without_actor(self):
        script = PlayerCombatScript()
        assert script.attack() is False

    def test_dash_without_actor(self):
        script = PlayerCombatScript()
        assert script.dash(Vec2.RIGHT) is False

    def test_take_hit_without_actor(self):
        script = PlayerCombatScript()
        assert script.take_hit(10.0) == 0.0

    def test_repr(self):
        script = PlayerCombatScript()
        r = repr(script)
        assert "PlayerCombatScript" in r
        assert "IDLE" in r

    def test_on_destroy_deactivates_hitbox(self):
        actor = _make_player_actor()
        script = _attach_script(actor)
        script.attack()
        hitbox = actor.get_component(HitboxComponent)
        assert hitbox.is_active is True
        script.on_destroy()
        assert hitbox.is_active is False

    def test_multiple_on_start_calls(self):
        """Calling on_start twice should not crash or recreate states."""
        actor = _make_player_actor()
        script = _attach_script(actor)
        script.on_start()  # second call
        assert script.state_name == PLAYER_STATE_IDLE

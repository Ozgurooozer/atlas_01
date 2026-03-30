"""Tests for combat components."""
import pytest
from world.components.health_component import HealthComponent
from world.components.combat_stats_component import CombatStatsComponent
from world.components.combatant_component import CombatantComponent
from world.components.hitbox_component import HitboxComponent
from world.components.hurtbox_component import HurtboxComponent
from world.components.combat_state_component import CombatStateComponent


class TestHealthComponent:
    def test_create_default(self):
        h = HealthComponent()
        assert h.hp == 100.0
        assert h.max_hp == 100.0
        assert h.is_dead is False

    def test_create_custom(self):
        h = HealthComponent(max_hp=200.0, hp=150.0)
        assert h.max_hp == 200.0
        assert h.hp == 150.0

    def test_hp_ratio(self):
        h = HealthComponent(max_hp=100.0, hp=75.0)
        assert h.hp_ratio == 0.75

    def test_hp_ratio_zero(self):
        h = HealthComponent(max_hp=0.0, hp=0.0)
        assert h.hp_ratio == 0.0

    def test_take_damage(self):
        h = HealthComponent(max_hp=100.0)
        actual = h.take_damage(30.0)
        assert actual == 30.0
        assert h.hp == 70.0

    def test_take_damage_kills(self):
        h = HealthComponent(max_hp=100.0)
        h.take_damage(100.0)
        assert h.is_dead is True
        assert h.hp == 0.0

    def test_take_damage_overkill(self):
        h = HealthComponent(max_hp=50.0)
        h.take_damage(200.0)
        assert h.is_dead is True
        assert h.hp == 0.0

    def test_take_damage_no_negative(self):
        h = HealthComponent(max_hp=100.0)
        actual = h.take_damage(-10.0)
        assert actual == 0.0

    def test_take_damage_dead(self):
        h = HealthComponent(max_hp=100.0)
        h.take_damage(100.0)
        actual = h.take_damage(10.0)
        assert actual == 0.0

    def test_heal(self):
        h = HealthComponent(max_hp=100.0)
        h.take_damage(30.0)
        actual = h.heal(20.0)
        assert actual == 20.0
        assert h.hp == 90.0

    def test_heal_overheal(self):
        h = HealthComponent(max_hp=100.0)
        h.take_damage(10.0)
        actual = h.heal(50.0)
        assert actual == 10.0
        assert h.hp == 100.0

    def test_heal_dead(self):
        h = HealthComponent(max_hp=100.0)
        h.take_damage(100.0)
        actual = h.heal(50.0)
        assert actual == 0.0

    def test_invincible(self):
        h = HealthComponent(max_hp=100.0)
        h.set_invincible(1.0)
        assert h.is_invincible is True
        actual = h.take_damage(50.0)
        assert actual == 0.0
        assert h.hp == 100.0

    def test_invincible_tick(self):
        h = HealthComponent(max_hp=100.0)
        h.set_invincible(0.5)
        h.on_tick(0.3)
        assert h.is_invincible is True
        h.on_tick(0.3)
        assert h.is_invincible is False

    def test_on_death_callback(self):
        h = HealthComponent(max_hp=100.0)
        died = []
        h.on_death(lambda: died.append(True))
        h.take_damage(100.0)
        assert len(died) == 1

    def test_on_damage_callback(self):
        h = HealthComponent(max_hp=100.0)
        amounts = []
        h.on_damage(lambda amt: amounts.append(amt))
        h.take_damage(20.0)
        assert amounts == [20.0]

    def test_on_heal_callback(self):
        h = HealthComponent(max_hp=100.0)
        h.take_damage(30.0)
        heals = []
        h.on_heal(lambda amt: heals.append(amt))
        h.heal(10.0)
        assert heals == [10.0]

    def test_reset(self):
        h = HealthComponent(max_hp=100.0)
        h.take_damage(80.0)
        h.reset()
        assert h.hp == 100.0
        assert h.is_dead is False

    def test_serialize_deserialize(self):
        h = HealthComponent(max_hp=200.0, hp=150.0)
        data = h.serialize()
        h2 = HealthComponent()
        h2.deserialize(data)
        assert h2.max_hp == 200.0
        assert h2.hp == 150.0


class TestCombatStatsComponent:
    def test_defaults(self):
        s = CombatStatsComponent()
        assert s.attack == 10.0
        assert s.defense == 5.0
        assert s.speed == 200.0

    def test_bonus_attack(self):
        s = CombatStatsComponent()
        s.add_bonus("attack", 5.0)
        assert s.attack == 15.0

    def test_multiplier_attack(self):
        s = CombatStatsComponent()
        s.add_multiplier("attack", 1.5)
        assert s.attack == 15.0

    def test_combined_modifiers(self):
        s = CombatStatsComponent()
        s.add_bonus("attack", 10.0)
        s.add_multiplier("attack", 2.0)
        assert s.attack == 40.0

    def test_remove_all_modifiers(self):
        s = CombatStatsComponent()
        s.add_bonus("attack", 50.0)
        s.add_multiplier("attack", 2.0)
        s.remove_all_modifiers()
        assert s.attack == 10.0

    def test_crit_chance_clamp(self):
        s = CombatStatsComponent()
        s.add_bonus("crit_chance", 2.0)
        assert s.crit_chance == 1.0

    def test_calculate_damage(self):
        s = CombatStatsComponent(attack=20.0)
        assert s.calculate_damage(False) == 20.0

    def test_calculate_crit_damage(self):
        s = CombatStatsComponent(attack=20.0, crit_multiplier=2.0)
        assert s.calculate_damage(True) == 40.0

    def test_roll_crit(self):
        s = CombatStatsComponent(crit_chance=1.0)  # 100% crit
        assert s.roll_crit() is True

    def test_roll_no_crit(self):
        s = CombatStatsComponent(crit_chance=0.0)
        assert s.roll_crit() is False

    def test_serialize_deserialize(self):
        s = CombatStatsComponent(attack=50.0, defense=30.0)
        data = s.serialize()
        s2 = CombatStatsComponent()
        s2.deserialize(data)
        assert s2.base_attack == 50.0
        assert s2.base_defense == 30.0


class TestCombatantComponent:
    def test_default_team(self):
        c = CombatantComponent()
        assert c.team == CombatantComponent.TEAM_ENEMY

    def test_player_team(self):
        c = CombatantComponent(team=CombatantComponent.TEAM_PLAYER)
        assert c.team == CombatantComponent.TEAM_PLAYER

    def test_hostility(self):
        player = CombatantComponent(team=CombatantComponent.TEAM_PLAYER)
        enemy = CombatantComponent(team=CombatantComponent.TEAM_ENEMY)
        assert player.is_hostile_to(CombatantComponent.TEAM_ENEMY) is True
        assert enemy.is_hostile_to(CombatantComponent.TEAM_PLAYER) is True

    def test_same_team_not_hostile(self):
        c1 = CombatantComponent(team=CombatantComponent.TEAM_PLAYER)
        c2 = CombatantComponent(team=CombatantComponent.TEAM_PLAYER)
        assert c1.is_hostile_to(CombatantComponent.TEAM_PLAYER) is False

    def test_neutral_not_hostile(self):
        player = CombatantComponent(team=CombatantComponent.TEAM_PLAYER)
        neutral = CombatantComponent(team=CombatantComponent.TEAM_NEUTRAL)
        assert player.is_hostile_to(CombatantComponent.TEAM_NEUTRAL) is False

    def test_target(self):
        c = CombatantComponent()
        c.current_target = "actor1"  # type: ignore
        assert c.current_target == "actor1"


class TestHitboxComponent:
    def test_create(self):
        h = HitboxComponent()
        assert h.is_active is False
        assert h.can_hit is False

    def test_activate(self):
        h = HitboxComponent()
        h.activate()
        assert h.is_active is True
        assert h.can_hit is True

    def test_deactivate(self):
        h = HitboxComponent()
        h.activate()
        h.deactivate()
        assert h.is_active is False
        assert h.can_hit is False

    def test_register_hit(self):
        h = HitboxComponent()
        h.hits_max = 3
        h.activate()
        assert h.register_hit(1) is True
        assert h.register_hit(1) is False  # Same target
        assert h.register_hit(2) is True

    def test_max_hits(self):
        h = HitboxComponent()
        h.hits_max = 1
        h.activate()
        h.register_hit(1)
        assert h.can_hit is False

    def test_serialize(self):
        h = HitboxComponent(width=60, height=60, damage=25)
        data = h.serialize()
        assert data["width"] == 60
        assert data["base_damage"] == 25


class TestHurtboxComponent:
    def test_create(self):
        h = HurtboxComponent()
        assert h.is_enabled is True

    def test_disable(self):
        h = HurtboxComponent()
        h.disable()
        assert h.is_enabled is False

    def test_enable(self):
        h = HurtboxComponent()
        h.disable()
        h.enable()
        assert h.is_enabled is True

    def test_serialize(self):
        h = HurtboxComponent(width=40, height=60, tag="player_body")
        data = h.serialize()
        assert data["width"] == 40
        assert data["tag"] == "player_body"


class TestCombatStateComponent:
    def test_create(self):
        s = CombatStateComponent()
        assert s.is_stunned is False

    def test_stun(self):
        s = CombatStateComponent()
        s.apply_stun(1.0)
        assert s.is_stunned is True
        s.on_tick(0.5)
        assert s.is_stunned is True
        s.on_tick(0.6)
        assert s.is_stunned is False

    def test_knockback(self):
        s = CombatStateComponent()
        s.apply_knockback(200, -100)
        assert s.knockback_x == 200
        assert s.knockback_y == -100

    def test_knockback_decay(self):
        s = CombatStateComponent()
        s.apply_knockback(200, 0)
        s.on_tick(0.5)
        assert s.knockback_x < 200

    def test_cooldown(self):
        s = CombatStateComponent()
        s.set_cooldown("attack", 1.0)
        assert s.is_on_cooldown("attack") is True
        s.on_tick(1.0)
        assert s.is_on_cooldown("attack") is False

    def test_status_effect(self):
        s = CombatStateComponent()
        s.apply_status("POISON", 3.0)
        assert s.has_status("POISON") is True
        assert s.get_status_duration("POISON") == 3.0

    def test_status_expires(self):
        s = CombatStateComponent()
        s.apply_status("POISON", 1.0)
        s.on_tick(1.5)
        assert s.has_status("POISON") is False

    def test_remove_status(self):
        s = CombatStateComponent()
        s.apply_status("POISON", 5.0)
        s.remove_status("POISON")
        assert s.has_status("POISON") is False

    def test_serialize(self):
        s = CombatStateComponent()
        s.apply_stun(2.0)
        data = s.serialize()
        assert data["is_stunned"] is True

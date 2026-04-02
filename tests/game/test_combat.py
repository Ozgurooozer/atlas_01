"""Tests for game.combat module."""
from game.combat.model import DamageData, DamageType, CombatResult, CombatEventType, StatusEffectType
from game.combat.system import CombatSystem
from game.combat.effects import StatusEffectProcessor, TICK_INTERVAL
from core.eventbus import EventBus
from core.vec import Vec2


class TestDamageData:
    def test_default_values(self):
        d = DamageData()
        assert d.amount == 0.0
        assert d.damage_type == DamageType.PHYSICAL
        assert d.is_crit is False
        assert d.source is None
        assert d.target is None
        assert d.final_damage == 0.0

    def test_final_damage_clamps_negative(self):
        d = DamageData(amount=-10.0)
        assert d.final_damage == 0.0

    def test_final_damage_positive(self):
        d = DamageData(amount=25.0)
        assert d.final_damage == 25.0

    def test_all_damage_types_exist(self):
        assert DamageType.PHYSICAL
        assert DamageType.MAGICAL
        assert DamageType.FIRE
        assert DamageType.POISON
        assert DamageType.ICE
        assert DamageType.TRUE


class TestCombatResult:
    def test_default_values(self):
        r = CombatResult()
        assert r.raw_damage == 0.0
        assert r.final_damage == 0.0
        assert r.was_crit is False
        assert r.was_dodged is False
        assert r.target_died is False


class TestCombatEventType:
    def test_all_events_exist(self):
        assert CombatEventType.DAMAGE_DEALT
        assert CombatEventType.DAMAGE_RECEIVED
        assert CombatEventType.HEAL
        assert CombatEventType.DEATH
        assert CombatEventType.CRITICAL_HIT


class TestStatusEffectType:
    def test_all_effects_exist(self):
        assert StatusEffectType.POISON
        assert StatusEffectType.BURN
        assert StatusEffectType.STUN
        assert StatusEffectType.SLOW
        assert StatusEffectType.BLEED
        assert StatusEffectType.FREEZE
        assert StatusEffectType.SHIELD


class TestCombatSystem:
    def test_create(self):
        cs = CombatSystem()
        assert cs.name == "CombatSystem"
        assert cs.is_active is False

    def test_start_end_combat(self):
        bus = EventBus()
        cs = CombatSystem(event_bus=bus)
        cs.start_combat()
        assert cs.is_active is True
        cs.end_combat()
        assert cs.is_active is False

    def test_calculate_damage_basic(self):
        cs = CombatSystem()
        result = cs.calculate_damage(20.0)
        assert result.raw_damage == 20.0
        assert result.final_damage == 20.0
        assert result.defense_reduction == 0.0
        assert result.was_crit is False

    def test_calculate_damage_zero(self):
        cs = CombatSystem()
        result = cs.calculate_damage(0.0)
        assert result.final_damage == 0.0

    def test_calculate_damage_no_negative(self):
        cs = CombatSystem()
        result = cs.calculate_damage(-5.0)
        assert result.final_damage == 0.0

    def test_apply_damage_basic(self):
        from world.components.health_component import HealthComponent
        cs = CombatSystem()
        health = HealthComponent(max_hp=100.0)
        dd = DamageData(amount=20.0)
        result = cs.apply_damage(dd, health)
        assert result.final_damage == 20.0
        assert health.hp == 80.0

    def test_apply_damage_kills(self):
        from world.components.health_component import HealthComponent
        cs = CombatSystem()
        health = HealthComponent(max_hp=100.0)
        dd = DamageData(amount=150.0)
        result = cs.apply_damage(dd, health)
        assert health.is_dead is True
        assert result.target_died is True
        assert result.overkill == 50.0

    def test_apply_damage_invincible(self):
        from world.components.health_component import HealthComponent
        cs = CombatSystem()
        health = HealthComponent(max_hp=100.0)
        health.set_invincible(1.0)
        dd = DamageData(amount=50.0)
        result = cs.apply_damage(dd, health)
        assert result.final_damage == 0.0
        assert health.hp == 100.0

    def test_apply_damage_dead_target(self):
        from world.components.health_component import HealthComponent
        cs = CombatSystem()
        health = HealthComponent(max_hp=100.0)
        health.take_damage(200.0)
        dd = DamageData(amount=10.0)
        result = cs.apply_damage(dd, health)
        assert result.was_dodged is False  # Not dodged, already dead

    def test_apply_heal(self):
        from world.components.health_component import HealthComponent
        cs = CombatSystem()
        health = HealthComponent(max_hp=100.0)
        health.take_damage(30.0)
        actual = cs.apply_heal(20.0, health)
        assert actual == 20.0
        assert health.hp == 90.0

    def test_apply_heal_overheal(self):
        from world.components.health_component import HealthComponent
        cs = CombatSystem()
        health = HealthComponent(max_hp=100.0)
        health.take_damage(10.0)
        actual = cs.apply_heal(50.0, health)
        assert actual == 10.0
        assert health.hp == 100.0

    def test_apply_damage_with_knockback(self):
        from world.components.health_component import HealthComponent
        from world.components.combat_state_component import CombatStateComponent
        cs = CombatSystem()
        health = HealthComponent(max_hp=100.0)
        state = CombatStateComponent()
        dd = DamageData(amount=10.0, knockback=Vec2(200, 0))
        cs.apply_damage(dd, health, state)
        assert state.knockback_x == 200.0

    def test_apply_damage_with_status(self):
        from world.components.health_component import HealthComponent
        from world.components.combat_state_component import CombatStateComponent
        cs = CombatSystem()
        health = HealthComponent(max_hp=100.0)
        state = CombatStateComponent()
        dd = DamageData(amount=10.0, status_effect=StatusEffectType.POISON, status_duration=3.0)
        cs.apply_damage(dd, health, state)
        assert state.has_status("POISON")


class TestStatusEffectProcessor:
    def test_create(self):
        sp = StatusEffectProcessor()
        assert sp.name == "StatusEffectProcessor"

    def test_poison_tick(self):
        from world.components.health_component import HealthComponent
        from world.components.combat_state_component import CombatStateComponent
        sp = StatusEffectProcessor()
        health = HealthComponent(max_hp=100.0)
        state = CombatStateComponent()
        state.apply_status("POISON", 5.0)
        # Use a mock actor since process expects one
        class FakeActor:
            pass
        actor = FakeActor()
        # Process for exactly one tick interval
        sp.process(actor, health, state, TICK_INTERVAL)
        assert health.hp < 100.0  # Should have taken poison damage

    def test_no_effect_when_dead(self):
        from world.components.health_component import HealthComponent
        from world.components.combat_state_component import CombatStateComponent
        sp = StatusEffectProcessor()
        health = HealthComponent(max_hp=100.0)
        health.take_damage(200.0)
        state = CombatStateComponent()
        state.apply_status("POISON", 5.0)
        class FakeActor:
            pass
        actor = FakeActor()
        sp.process(actor, health, state, TICK_INTERVAL)
        assert health.hp == 0.0

    def test_freeze_applies_stun(self):
        from world.components.health_component import HealthComponent
        from world.components.combat_state_component import CombatStateComponent
        sp = StatusEffectProcessor()
        health = HealthComponent(max_hp=100.0)
        state = CombatStateComponent()
        state.apply_status("FREEZE", 2.0)
        class FakeActor:
            pass
        actor = FakeActor()
        sp.process(actor, health, state, 0.1)
        assert state.is_stunned is True

    def test_cleanup(self):
        sp = StatusEffectProcessor()
        sp._tick_accumulators[42] = 1.0
        sp.cleanup(42)
        assert 42 not in sp._tick_accumulators

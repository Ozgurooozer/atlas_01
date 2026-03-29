"""Tests for game.ai module."""
import pytest
from game.ai.archetypes import AIArchetype, MeleeChaserArchetype, RangedKiterArchetype, TankChargerArchetype


class TestMeleeChaserArchetype:
    def test_create(self):
        a = MeleeChaserArchetype()
        assert a.name == "MeleeChaser"
        assert a.chase_speed == 150.0
        assert a.attack_range == 40.0

    def test_config(self):
        a = MeleeChaserArchetype()
        cfg = a.get_config()
        assert "chase_speed" in cfg
        assert "max_hp" in cfg


class TestRangedKiterArchetype:
    def test_create(self):
        a = RangedKiterArchetype()
        assert a.prefers_ranged is True
        assert a.projectile_speed == 300.0
        assert a.attack_range == 250.0


class TestTankChargerArchetype:
    def test_create(self):
        a = TankChargerArchetype()
        assert a.max_hp == 120.0
        assert a.attack_damage == 20.0
        assert a.chase_speed == 60.0


class TestAIArchetype:
    def test_base_config(self):
        a = AIArchetype()
        cfg = a.get_config()
        assert len(cfg) == 6

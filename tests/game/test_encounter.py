"""
Room Encounter Scripting Tests.

Tests for Encounter, ThreatBudget, EncounterGenerator, and WaveSystem.
Layer 4 (Game/Run), depends on core.object, game.run.game_rng.

TDD: RED phase first, then GREEN.
"""
from __future__ import annotations


class TestEncounter:
    """Tests for the Encounter class."""

    def test_create_encounter(self):
        """Encounter can be created with defaults."""
        from game.run.encounter import Encounter
        enc = Encounter()
        assert enc is not None

    def test_encounter_inherits_object(self):
        """Encounter inherits from core.object.Object."""
        from game.run.encounter import Encounter
        from core.object import Object
        enc = Encounter()
        assert isinstance(enc, Object)

    def test_encounter_enemy_spawns(self):
        """Encounter stores enemy spawn data."""
        from game.run.encounter import Encounter
        spawns = [
            {"enemy_type": "melee_chaser", "count": 3, "position": [100, 200]},
            {"enemy_type": "ranged_kiter", "count": 1, "position": [500, 100]},
        ]
        enc = Encounter(enemy_spawns=spawns)
        assert len(enc.enemy_spawns) == 2
        assert enc.enemy_spawns[0]["enemy_type"] == "melee_chaser"
        assert enc.enemy_spawns[0]["count"] == 3

    def test_encounter_trigger_type(self):
        """Encounter stores trigger type."""
        from game.run.encounter import Encounter
        enc = Encounter(trigger_type="on_enter")
        assert enc.trigger_type == "on_enter"

    def test_encounter_trigger_on_wave_clear(self):
        """Encounter supports on_wave_clear trigger."""
        from game.run.encounter import Encounter
        enc = Encounter(trigger_type="on_wave_clear")
        assert enc.trigger_type == "on_wave_clear"

    def test_encounter_trigger_on_timer(self):
        """Encounter supports on_timer trigger."""
        from game.run.encounter import Encounter
        enc = Encounter(trigger_type="on_timer")
        assert enc.trigger_type == "on_timer"

    def test_encounter_timer_delay(self):
        """Encounter stores timer delay for on_timer triggers."""
        from game.run.encounter import Encounter
        enc = Encounter(trigger_type="on_timer", timer_delay=5.0)
        assert enc.timer_delay == 5.0

    def test_encounter_default_timer_delay(self):
        """Default timer delay is 0.0."""
        from game.run.encounter import Encounter
        enc = Encounter()
        assert enc.timer_delay == 0.0

    def test_encounter_serialize(self):
        """Encounter serializes to dict."""
        from game.run.encounter import Encounter
        spawns = [{"enemy_type": "melee_chaser", "count": 2, "position": [50, 100]}]
        enc = Encounter(enemy_spawns=spawns, trigger_type="on_enter")
        data = enc.serialize()
        assert data["__class__"] == "Encounter"
        assert data["trigger_type"] == "on_enter"
        assert len(data["enemy_spawns"]) == 1

    def test_encounter_deserialize(self):
        """Encounter deserializes from dict."""
        from game.run.encounter import Encounter
        spawns = [{"enemy_type": "tank_charger", "count": 1, "position": [300, 400]}]
        enc = Encounter(enemy_spawns=spawns, trigger_type="on_timer", timer_delay=3.0)
        data = enc.serialize()
        enc2 = Encounter()
        enc2.deserialize(data)
        assert enc2.trigger_type == "on_timer"
        assert enc2.timer_delay == 3.0
        assert len(enc2.enemy_spawns) == 1
        assert enc2.enemy_spawns[0]["enemy_type"] == "tank_charger"

    def test_encounter_roundtrip(self):
        """Encounter roundtrip preserves all data."""
        from game.run.encounter import Encounter
        spawns = [
            {"enemy_type": "melee_chaser", "count": 5, "position": [100, 200]},
            {"enemy_type": "ranged_kiter", "count": 2, "position": [400, 300]},
        ]
        enc = Encounter(enemy_spawns=spawns, trigger_type="on_wave_clear")
        data = enc.serialize()
        enc2 = Encounter()
        enc2.deserialize(data)
        assert enc2.trigger_type == enc.trigger_type
        assert enc2.enemy_spawns == enc.enemy_spawns


class TestThreatBudget:
    """Tests for the ThreatBudget class."""

    def test_create_budget(self):
        """ThreatBudget can be created."""
        from game.run.encounter import ThreatBudget
        budget = ThreatBudget(budget=10.0)
        assert budget is not None

    def test_inherits_object(self):
        """ThreatBudget inherits from core.object.Object."""
        from game.run.encounter import ThreatBudget
        from core.object import Object
        budget = ThreatBudget(budget=5.0)
        assert isinstance(budget, Object)

    def test_initial_remaining(self):
        """Initial remaining equals budget."""
        from game.run.encounter import ThreatBudget
        budget = ThreatBudget(budget=10.0)
        assert budget.remaining == 10.0

    def test_initial_used_is_zero(self):
        """Initial used is 0.0."""
        from game.run.encounter import ThreatBudget
        budget = ThreatBudget(budget=10.0)
        assert budget.used == 0.0

    def test_add_cost(self):
        """add_cost deducts from remaining and adds to used."""
        from game.run.encounter import ThreatBudget
        budget = ThreatBudget(budget=10.0)
        budget.add_cost(3.0)
        assert budget.used == 3.0
        assert budget.remaining == 7.0

    def test_add_cost_multiple(self):
        """Multiple add_cost calls accumulate correctly."""
        from game.run.encounter import ThreatBudget
        budget = ThreatBudget(budget=10.0)
        budget.add_cost(3.0)
        budget.add_cost(2.5)
        budget.add_cost(1.0)
        assert budget.used == 6.5
        assert budget.remaining == 3.5

    def test_add_cost_exact_budget(self):
        """Can spend exactly the budget."""
        from game.run.encounter import ThreatBudget
        budget = ThreatBudget(budget=5.0)
        budget.add_cost(5.0)
        assert budget.remaining == 0.0
        assert budget.used == 5.0

    def test_reset(self):
        """reset() restores remaining to budget and used to 0."""
        from game.run.encounter import ThreatBudget
        budget = ThreatBudget(budget=10.0)
        budget.add_cost(7.0)
        budget.reset()
        assert budget.remaining == 10.0
        assert budget.used == 0.0

    def test_remaining_property(self):
        """remaining is a read-only computed property."""
        from game.run.encounter import ThreatBudget
        budget = ThreatBudget(budget=8.0)
        budget.add_cost(2.0)
        assert budget.remaining == 6.0

    def test_serialize(self):
        """ThreatBudget serializes to dict."""
        from game.run.encounter import ThreatBudget
        budget = ThreatBudget(budget=15.0)
        budget.add_cost(4.0)
        data = budget.serialize()
        assert data["__class__"] == "ThreatBudget"
        assert data["budget"] == 15.0
        assert data["used"] == 4.0

    def test_deserialize(self):
        """ThreatBudget deserializes from dict."""
        from game.run.encounter import ThreatBudget
        budget = ThreatBudget(budget=20.0)
        budget.add_cost(8.0)
        data = budget.serialize()
        budget2 = ThreatBudget()
        budget2.deserialize(data)
        assert budget2.budget == 20.0
        assert budget2.used == 8.0
        assert budget2.remaining == 12.0


class TestEncounterGenerator:
    """Tests for the EncounterGenerator class."""

    def test_create_generator(self):
        """EncounterGenerator can be created."""
        from game.run.encounter import EncounterGenerator
        gen = EncounterGenerator()
        assert gen is not None

    def test_inherits_object(self):
        """EncounterGenerator inherits from core.object.Object."""
        from game.run.encounter import EncounterGenerator
        from core.object import Object
        gen = EncounterGenerator()
        assert isinstance(gen, Object)

    def test_generate_basic(self):
        """generate returns a list of Encounter."""
        from game.run.encounter import EncounterGenerator, ThreatBudget
        from game.run.game_rng import GameRNG
        gen = EncounterGenerator()
        budget = ThreatBudget(budget=10.0)
        rng = GameRNG(seed=42)
        templates = ["melee_chaser", "ranged_kiter"]
        result = gen.generate(budget, templates, rng)
        assert isinstance(result, list)
        assert len(result) >= 1
        for enc in result:
            assert enc.enemy_spawns

    def test_generate_respects_budget(self):
        """Generated encounters don't exceed budget."""
        from game.run.encounter import EncounterGenerator, ThreatBudget
        from game.run.game_rng import GameRNG
        gen = EncounterGenerator()
        budget = ThreatBudget(budget=5.0)
        rng = GameRNG(seed=42)
        templates = ["melee_chaser", "ranged_kiter", "tank_charger"]
        result = gen.generate(budget, templates, rng)
        total_cost = budget.used
        assert total_cost <= 5.0 + 0.01  # small float tolerance

    def test_enemy_costs(self):
        """Enemy type costs are correct."""
        from game.run.encounter import EncounterGenerator
        assert EncounterGenerator.COST_MELEE == 1.0
        assert EncounterGenerator.COST_RANGED == 1.5
        assert EncounterGenerator.COST_TANK == 2.0

    def test_generate_empty_templates(self):
        """generate with empty templates returns empty list."""
        from game.run.encounter import EncounterGenerator, ThreatBudget
        from game.run.game_rng import GameRNG
        gen = EncounterGenerator()
        budget = ThreatBudget(budget=10.0)
        rng = GameRNG(seed=42)
        result = gen.generate(budget, [], rng)
        assert result == []

    def test_generate_zero_budget(self):
        """generate with zero budget returns empty list."""
        from game.run.encounter import EncounterGenerator, ThreatBudget
        from game.run.game_rng import GameRNG
        gen = EncounterGenerator()
        budget = ThreatBudget(budget=0.0)
        rng = GameRNG(seed=42)
        templates = ["melee_chaser"]
        result = gen.generate(budget, templates, rng)
        assert result == []

    def test_generate_deterministic(self):
        """Same seed produces same encounters."""
        from game.run.encounter import EncounterGenerator, ThreatBudget
        from game.run.game_rng import GameRNG
        gen = EncounterGenerator()
        budget1 = ThreatBudget(budget=10.0)
        budget2 = ThreatBudget(budget=10.0)
        rng1 = GameRNG(seed=99)
        rng2 = GameRNG(seed=99)
        templates = ["melee_chaser", "ranged_kiter"]
        result1 = gen.generate(budget1, templates, rng1)
        result2 = gen.generate(budget2, templates, rng2)
        assert len(result1) == len(result2)
        for e1, e2 in zip(result1, result2):
            assert e1.enemy_spawns == e2.enemy_spawns

    def test_serialize(self):
        """EncounterGenerator serializes."""
        from game.run.encounter import EncounterGenerator
        gen = EncounterGenerator()
        data = gen.serialize()
        assert data["__class__"] == "EncounterGenerator"

    def test_deserialize(self):
        """EncounterGenerator deserializes."""
        from game.run.encounter import EncounterGenerator
        gen = EncounterGenerator()
        data = gen.serialize()
        gen2 = EncounterGenerator()
        gen2.deserialize(data)
        assert gen2 is not None


class TestWaveSystem:
    """Tests for the WaveSystem class."""

    def test_create_wave_system(self):
        """WaveSystem can be created."""
        from game.run.encounter import WaveSystem
        ws = WaveSystem()
        assert ws is not None

    def test_inherits_object(self):
        """WaveSystem inherits from core.object.Object."""
        from game.run.encounter import WaveSystem
        from core.object import Object
        ws = WaveSystem()
        assert isinstance(ws, Object)

    def test_set_waves(self):
        """Waves can be set on the system."""
        from game.run.encounter import WaveSystem, Encounter
        enc1 = Encounter()
        enc2 = Encounter()
        ws = WaveSystem()
        ws.waves = [enc1, enc2]
        assert len(ws.waves) == 2

    def test_initial_current_wave_is_zero(self):
        """Initial current_wave index is 0."""
        from game.run.encounter import WaveSystem
        ws = WaveSystem()
        assert ws.current_wave == 0

    def test_is_complete_empty(self):
        """Empty wave system is complete."""
        from game.run.encounter import WaveSystem
        ws = WaveSystem()
        assert ws.is_complete is True

    def test_is_complete_false_with_waves(self):
        """Wave system with waves is not complete initially."""
        from game.run.encounter import WaveSystem, Encounter
        ws = WaveSystem()
        ws.waves = [Encounter()]
        assert ws.is_complete is False

    def test_advance_wave(self):
        """advance_wave increments current_wave."""
        from game.run.encounter import WaveSystem, Encounter
        ws = WaveSystem()
        ws.waves = [Encounter(), Encounter(), Encounter()]
        ws.advance_wave()
        assert ws.current_wave == 1
        ws.advance_wave()
        assert ws.current_wave == 2

    def test_advance_wave_complete(self):
        """advancing past all waves sets is_complete."""
        from game.run.encounter import WaveSystem, Encounter
        ws = WaveSystem()
        ws.waves = [Encounter(), Encounter()]
        ws.advance_wave()
        assert ws.is_complete is False
        ws.advance_wave()
        assert ws.is_complete is True

    def test_advance_wave_past_end(self):
        """advancing past end doesn't crash."""
        from game.run.encounter import WaveSystem, Encounter
        ws = WaveSystem()
        ws.waves = [Encounter()]
        ws.advance_wave()
        ws.advance_wave()  # past end
        assert ws.is_complete is True

    def test_current_encounter(self):
        """current_encounter returns the current wave's Encounter."""
        from game.run.encounter import WaveSystem, Encounter
        enc = Encounter(trigger_type="on_enter")
        ws = WaveSystem()
        ws.waves = [enc]
        assert ws.current_encounter is enc

    def test_current_encounter_none_when_complete(self):
        """current_encounter returns None when all waves cleared."""
        from game.run.encounter import WaveSystem, Encounter
        ws = WaveSystem()
        ws.waves = [Encounter()]
        ws.advance_wave()
        assert ws.current_encounter is None

    def test_serialize(self):
        """WaveSystem serializes to dict."""
        from game.run.encounter import WaveSystem, Encounter
        ws = WaveSystem()
        ws.waves = [Encounter()]
        ws.advance_wave()
        data = ws.serialize()
        assert data["__class__"] == "WaveSystem"
        assert data["current_wave"] == 1
        assert len(data["waves"]) == 1

    def test_deserialize(self):
        """WaveSystem deserializes from dict."""
        from game.run.encounter import WaveSystem, Encounter
        ws = WaveSystem()
        ws.waves = [Encounter(trigger_type="on_timer", timer_delay=2.0)]
        ws.advance_wave()
        data = ws.serialize()
        ws2 = WaveSystem()
        ws2.deserialize(data)
        assert ws2.current_wave == 1
        assert len(ws2.waves) == 1
        assert ws2.waves[0].trigger_type == "on_timer"
        assert ws2.waves[0].timer_delay == 2.0

    def test_serialize_deserialize_roundtrip(self):
        """Full roundtrip preserves all wave data."""
        from game.run.encounter import WaveSystem, Encounter
        spawns = [{"enemy_type": "melee_chaser", "count": 4, "position": [200, 300]}]
        ws = WaveSystem()
        ws.waves = [
            Encounter(enemy_spawns=spawns, trigger_type="on_enter"),
            Encounter(trigger_type="on_wave_clear"),
        ]
        data = ws.serialize()
        ws2 = WaveSystem()
        ws2.deserialize(data)
        assert ws2.current_wave == ws.current_wave
        assert len(ws2.waves) == 2
        assert ws2.waves[0].trigger_type == "on_enter"
        assert ws2.waves[1].trigger_type == "on_wave_clear"

"""
Game RNG Tests.

Seeded pseudo-random number generator for deterministic game logic.
Layer 4 (Game/Run), depends on core.object.

TDD: RED phase.
"""
from __future__ import annotations
import pytest


class TestGameRNGBasics:
    """Core GameRNG behavior."""

    def test_create_with_seed(self):
        from game.run.game_rng import GameRNG
        rng = GameRNG(seed=42)
        assert rng.seed == 42

    def test_create_default_seed(self):
        from game.run.game_rng import GameRNG
        rng = GameRNG()
        assert rng.seed is not None

    def test_random_float(self):
        from game.run.game_rng import GameRNG
        rng = GameRNG(seed=42)
        val = rng.random()
        assert 0.0 <= val < 1.0

    def test_random_int(self):
        from game.run.game_rng import GameRNG
        rng = GameRNG(seed=42)
        val = rng.randint(1, 10)
        assert 1 <= val <= 10

    def test_random_choice(self):
        from game.run.game_rng import GameRNG
        rng = GameRNG(seed=42)
        items = ["a", "b", "c"]
        val = rng.choice(items)
        assert val in items

    def test_random_shuffle_in_place(self):
        from game.run.game_rng import GameRNG
        rng = GameRNG(seed=42)
        items = [1, 2, 3, 4, 5]
        rng.shuffle(items)
        assert len(items) == 5
        assert set(items) == {1, 2, 3, 4, 5}

    def test_random_shuffle_deterministic(self):
        from game.run.game_rng import GameRNG
        rng1 = GameRNG(seed=42)
        rng2 = GameRNG(seed=42)
        a = [1, 2, 3, 4, 5]
        b = [1, 2, 3, 4, 5]
        rng1.shuffle(a)
        rng2.shuffle(b)
        assert a == b

    def test_random_range(self):
        from game.run.game_rng import GameRNG
        rng = GameRNG(seed=42)
        val = rng.randrange(0, 100, 5)
        assert 0 <= val < 100


class TestGameRNGDeterminism:
    """Same seed produces same sequence."""

    def test_same_seed_same_floats(self):
        from game.run.game_rng import GameRNG
        rng1 = GameRNG(seed=12345)
        rng2 = GameRNG(seed=12345)
        for _ in range(100):
            assert rng1.random() == rng2.random()

    def test_same_seed_same_ints(self):
        from game.run.game_rng import GameRNG
        rng1 = GameRNG(seed=999)
        rng2 = GameRNG(seed=999)
        for _ in range(50):
            assert rng1.randint(1, 100) == rng2.randint(1, 100)

    def test_different_seed_different_sequence(self):
        from game.run.game_rng import GameRNG
        rng1 = GameRNG(seed=1)
        rng2 = GameRNG(seed=2)
        results_different = False
        for _ in range(20):
            if rng1.random() != rng2.random():
                results_different = True
                break
        assert results_different

    def test_room_seed_determinism(self):
        from game.run.game_rng import GameRNG
        seed1 = GameRNG.room_seed(run_seed=42, room_index=0)
        seed2 = GameRNG.room_seed(run_seed=42, room_index=0)
        assert seed1 == seed2

    def test_room_seed_different_per_room(self):
        from game.run.game_rng import GameRNG
        seed0 = GameRNG.room_seed(run_seed=42, room_index=0)
        seed1 = GameRNG.room_seed(run_seed=42, room_index=1)
        assert seed0 != seed1


class TestGameRNGState:
    """State save/restore for deterministic replay."""

    def test_get_state(self):
        from game.run.game_rng import GameRNG
        rng = GameRNG(seed=42)
        rng.random()
        rng.random()
        state = rng.get_state()
        assert isinstance(state, int)
        assert state > 0

    def test_set_state(self):
        from game.run.game_rng import GameRNG
        rng1 = GameRNG(seed=42)
        rng1.random()
        rng1.random()
        state = rng1.get_state()
        val = rng1.random()

        rng2 = GameRNG(seed=42)
        rng2.random()
        rng2.random()
        rng2.set_state(state)
        assert rng2.random() == val

    def test_serialize(self):
        from game.run.game_rng import GameRNG
        rng = GameRNG(seed=42)
        rng.random()
        data = rng.serialize()
        assert "seed" in data
        assert "state" in data

    def test_deserialize(self):
        from game.run.game_rng import GameRNG
        rng1 = GameRNG(seed=42)
        rng1.random()
        data = rng1.serialize()
        rng2 = GameRNG()
        rng2.deserialize(data)
        assert rng1.random() == rng2.random()


class TestGameRNGWeightedChoice:
    """Weighted random selection."""

    def test_weighted_choice_basic(self):
        from game.run.game_rng import GameRNG
        rng = GameRNG(seed=42)
        items = ["a", "b", "c"]
        weights = [10, 5, 1]
        result = rng.weighted_choice(items, weights)
        assert result in items

    def test_weighted_choice_single_item(self):
        from game.run.game_rng import GameRNG
        rng = GameRNG(seed=42)
        result = rng.weighted_choice(["only"], [1])
        assert result == "only"

    def test_weighted_choice_deterministic(self):
        from game.run.game_rng import GameRNG
        rng1 = GameRNG(seed=42)
        rng2 = GameRNG(seed=42)
        items = ["a", "b", "c"]
        weights = [10, 5, 1]
        for _ in range(20):
            assert rng1.weighted_choice(items, weights) == rng2.weighted_choice(items, weights)

    def test_weighted_choice_distribution(self):
        from game.run.game_rng import GameRNG
        rng = GameRNG(seed=42)
        items = ["heavy", "light"]
        weights = [100, 1]
        counts = {"heavy": 0, "light": 0}
        for _ in range(1000):
            result = rng.weighted_choice(items, weights)
            counts[result] += 1
        assert counts["heavy"] > counts["light"]

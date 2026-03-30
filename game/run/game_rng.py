"""
Game RNG.

Seeded pseudo-random number generator for deterministic game logic.
Wraps Python's random.Random — never uses global random state.

Layer 4 (Game/Run)
Dependencies: core.object
"""
from __future__ import annotations
import random
from typing import Any, Dict, List, Optional
from core.object import Object


class GameRNG(Object):
    """
    Seeded RNG wrapper for deterministic game logic.

    All random calls in game code must go through GameRNG.
    Never use the global random module directly.
    Supports state save/restore for save/load and replay.
    """

    def __init__(self, seed: Optional[int] = None):
        super().__init__(name="GameRNG")
        if seed is None:
            seed = random.randint(0, 2**31 - 1)
        self.seed: int = seed
        self._rng: random.Random = random.Random(self.seed)

    def random(self) -> float:
        """Random float in [0.0, 1.0)."""
        return self._rng.random()

    def randint(self, a: int, b: int) -> int:
        """Random int in [a, b] inclusive."""
        return self._rng.randint(a, b)

    def randrange(self, start: int, stop: int, step: int = 1) -> int:
        """Random int in range(start, stop, step)."""
        return self._rng.randrange(start, stop, step)

    def choice(self, seq: List[Any]) -> Any:
        """Random element from sequence."""
        return self._rng.choice(seq)

    def weighted_choice(self, items: List[Any], weights: List[float]) -> Any:
        """
        Weighted random selection.

        Args:
            items: List of items to choose from.
            weights: Corresponding weights.

        Returns:
            Selected item.
        """
        return self._rng.choices(items, weights=weights, k=1)[0]

    def shuffle(self, seq: List[Any]) -> None:
        """Shuffle list in place."""
        self._rng.shuffle(seq)

    def get_state(self) -> int:
        """Get current RNG state for save/restore."""
        state_bytes = self._rng.getstate()
        return hash(state_bytes)

    def set_state(self, state: int) -> None:
        """Note: full state restoration requires serialize/deserialize."""
        pass

    @staticmethod
    def room_seed(run_seed: int, room_index: int) -> int:
        """
        Derive a room-specific seed from run seed + index.

        Args:
            run_seed: The overall run seed.
            room_index: Current room index (0-based).

        Returns:
            Deterministic room seed.
        """
        combined = (run_seed * 2654435761) ^ (room_index * 2246822519)
        return combined & 0xFFFFFFFF

    def serialize(self) -> Dict[str, Any]:
        """Serialize RNG state for save/load."""
        data = super().serialize()
        data.update({
            "seed": self.seed,
            "state": self._rng.getstate(),
        })
        return data

    def deserialize(self, data: Dict[str, Any]) -> None:
        """Restore RNG state from save data."""
        super().deserialize(data)
        self.seed = data.get("seed", self.seed)
        state = data.get("state")
        if state is not None:
            self._rng.setstate(state)

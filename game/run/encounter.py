"""
Room Encounter Scripting.

Defines encounters, threat budgets, encounter generation, and wave systems
for room combat encounters in runs.

Layer: 4 (Game/Run)
Dependencies: core.object, game.run.game_rng
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional

from core.object import Object
from game.run.game_rng import GameRNG


class Encounter(Object):
    """Defines a combat encounter with enemy spawns and trigger conditions."""

    def __init__(
        self,
        enemy_spawns: Optional[List[Dict[str, Any]]] = None,
        trigger_type: str = "on_enter",
        timer_delay: float = 0.0,
    ):
        """Create a new Encounter.

        Args:
            enemy_spawns: List of dicts with enemy_type, count, position.
            trigger_type: One of 'on_enter', 'on_wave_clear', 'on_timer'.
            timer_delay: Delay in seconds for 'on_timer' triggers.
        """
        super().__init__(name="Encounter")
        self.enemy_spawns: List[Dict[str, Any]] = enemy_spawns or []
        self.trigger_type: str = trigger_type
        self.timer_delay: float = timer_delay

    def serialize(self) -> Dict[str, Any]:
        """Serialize the encounter to a dictionary."""
        data = super().serialize()
        data.update({
            "enemy_spawns": [dict(s) for s in self.enemy_spawns],
            "trigger_type": self.trigger_type,
            "timer_delay": self.timer_delay,
        })
        return data

    def deserialize(self, data: Dict[str, Any]) -> None:
        """Restore the encounter from a dictionary.

        Args:
            data: Dictionary containing encounter data.
        """
        super().deserialize(data)
        self.enemy_spawns = [dict(s) for s in data.get("enemy_spawns", [])]
        self.trigger_type = data.get("trigger_type", "on_enter")
        self.timer_delay = data.get("timer_delay", 0.0)


class ThreatBudget(Object):
    """Tracks available threat budget for encounter generation."""

    def __init__(self, budget: float = 0.0):
        """Create a new ThreatBudget.

        Args:
            budget: Total threat budget available.
        """
        super().__init__(name="ThreatBudget")
        self.budget: float = budget
        self._used: float = 0.0

    @property
    def used(self) -> float:
        """Get the amount of budget currently used."""
        return self._used

    @property
    def remaining(self) -> float:
        """Get the remaining budget."""
        return self.budget - self._used

    def add_cost(self, cost: float) -> None:
        """Spend cost from the budget.

        Args:
            cost: Amount of threat to spend.
        """
        self._used += cost

    def reset(self) -> None:
        """Reset used budget to zero."""
        self._used = 0.0

    def serialize(self) -> Dict[str, Any]:
        """Serialize the threat budget to a dictionary."""
        data = super().serialize()
        data.update({
            "budget": self.budget,
            "used": self._used,
        })
        return data

    def deserialize(self, data: Dict[str, Any]) -> None:
        """Restore the threat budget from a dictionary.

        Args:
            data: Dictionary containing budget data.
        """
        super().deserialize(data)
        self.budget = data.get("budget", 0.0)
        self._used = data.get("used", 0.0)


class EncounterGenerator(Object):
    """Generates encounters based on threat budget and enemy templates."""

    COST_MELEE: float = 1.0
    COST_RANGED: float = 1.5
    COST_TANK: float = 2.0

    def __init__(self):
        """Create a new EncounterGenerator."""
        super().__init__(name="EncounterGenerator")

    @staticmethod
    def _get_cost(enemy_type: str) -> float:
        """Get the threat cost for an enemy type.

        Args:
            enemy_type: Name of the enemy type.

        Returns:
            Threat cost value.
        """
        costs = {
            "melee_chaser": EncounterGenerator.COST_MELEE,
            "ranged_kiter": EncounterGenerator.COST_RANGED,
            "tank_charger": EncounterGenerator.COST_TANK,
        }
        return costs.get(enemy_type, 1.0)

    def generate(
        self,
        budget: ThreatBudget,
        templates: List[str],
        rng: GameRNG,
    ) -> List[Encounter]:
        """Generate encounters that fit within the threat budget.

        Args:
            budget: ThreatBudget to constrain total cost.
            templates: List of enemy type strings to choose from.
            rng: Seeded RNG for deterministic generation.

        Returns:
            List of Encounter instances.
        """
        if not templates or budget.remaining <= 0:
            return []
        encounter = Encounter(trigger_type="on_enter")
        attempts = 0
        max_attempts = 50
        while budget.remaining > 0 and attempts < max_attempts:
            enemy_type = rng.choice(templates)
            cost = self._get_cost(enemy_type)
            if cost > budget.remaining:
                attempts += 1
                continue
            count = rng.randint(1, 3)
            total = cost * count
            if total > budget.remaining:
                count = max(1, int(budget.remaining / cost))
                total = cost * count
            budget.add_cost(total)
            x = rng.randint(50, 750)
            y = rng.randint(100, 500)
            encounter.enemy_spawns.append({
                "enemy_type": enemy_type,
                "count": count,
                "position": [x, y],
            })
            attempts += 1
        if not encounter.enemy_spawns:
            return []
        return [encounter]

    def serialize(self) -> Dict[str, Any]:
        """Serialize the generator to a dictionary."""
        return super().serialize()

    def deserialize(self, data: Dict[str, Any]) -> None:
        """Restore the generator from a dictionary.

        Args:
            data: Dictionary containing generator data.
        """
        super().deserialize(data)


class WaveSystem(Object):
    """Manages a sequence of combat encounter waves."""

    def __init__(self):
        """Create a new WaveSystem."""
        super().__init__(name="WaveSystem")
        self._waves: List[Encounter] = []
        self._current_wave: int = 0

    @property
    def waves(self) -> List[Encounter]:
        """Get the list of wave encounters."""
        return list(self._waves)

    @waves.setter
    def waves(self, value: List[Encounter]) -> None:
        """Set the list of wave encounters."""
        self._waves = list(value)

    @property
    def current_wave(self) -> int:
        """Get the current wave index (0-based)."""
        return self._current_wave

    @property
    def is_complete(self) -> bool:
        """Check if all waves have been cleared."""
        return self._current_wave >= len(self._waves)

    @property
    def current_encounter(self) -> Optional[Encounter]:
        """Get the current wave's Encounter, or None if complete."""
        if self.is_complete:
            return None
        return self._waves[self._current_wave]

    def advance_wave(self) -> None:
        """Advance to the next wave."""
        if self.is_complete:
            return
        self._current_wave += 1

    def serialize(self) -> Dict[str, Any]:
        """Serialize the wave system to a dictionary."""
        data = super().serialize()
        data.update({
            "current_wave": self._current_wave,
            "waves": [w.serialize() for w in self._waves],
        })
        return data

    def deserialize(self, data: Dict[str, Any]) -> None:
        """Restore the wave system from a dictionary.

        Args:
            data: Dictionary containing wave system data.
        """
        super().deserialize(data)
        self._current_wave = data.get("current_wave", 0)
        wave_data = data.get("waves", [])
        self._waves = []
        for wd in wave_data:
            enc = Encounter()
            enc.deserialize(wd)
            self._waves.append(enc)

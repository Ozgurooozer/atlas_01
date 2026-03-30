"""
Combatant Component.

Marks an Actor as a combat participant with team/faction and targeting.

Layer: 3 (World/Components)
Dependencies: core.object
"""
from __future__ import annotations
from typing import Any, Dict, Optional, TYPE_CHECKING
from world.component import Component

if TYPE_CHECKING:
    from world.actor import Actor


class CombatantComponent(Component):
    """
    Identifies an Actor as a combatant with team affiliation.

    Class constants:
        TEAM_PLAYER: Player team identifier.
        TEAM_ENEMY: Enemy team identifier.
        TEAM_NEUTRAL: Neutral (non-hostile) team identifier.

    Attributes:
        team: Team/faction string identifier.
        faction: Sub-faction within a team.
        is_targetable: Whether this combatant can be targeted.
        threat_value: AI threat priority value.
    """

    TEAM_PLAYER = "player"
    TEAM_ENEMY = "enemy"
    TEAM_NEUTRAL = "neutral"

    def __init__(self, team: str = TEAM_ENEMY):
        """
        Initialize the CombatantComponent.

        Args:
            team: Team identifier (default TEAM_ENEMY).
        """
        super().__init__()
        self.team: str = team
        self.faction: str = ""
        self.is_targetable: bool = True
        self.threat_value: float = 1.0
        self._current_target: Optional[Actor] = None

    @property
    def current_target(self) -> Optional[Actor]:
        """Get the currently targeted Actor."""
        return self._current_target

    @current_target.setter
    def current_target(self, actor: Optional[Actor]) -> None:
        """Set the currently targeted Actor."""
        self._current_target = actor

    def is_hostile_to(self, other_team: str) -> bool:
        """
        Check if this combatant is hostile to another team.

        Neutral teams are never hostile to anyone.

        Args:
            other_team: The team to check hostility against.

        Returns:
            True if the teams are hostile to each other.
        """
        if self.team == other_team:
            return False
        if self.team == CombatantComponent.TEAM_NEUTRAL:
            return False
        if other_team == CombatantComponent.TEAM_NEUTRAL:
            return False
        return True

    def serialize(self) -> Dict[str, Any]:
        """Serialize the component."""
        data = super().serialize()
        data.update({
            "team": self.team,
            "faction": self.faction,
            "is_targetable": self.is_targetable,
            "threat_value": self.threat_value,
        })
        return data

    def deserialize(self, data: Dict[str, Any]) -> None:
        """Deserialize the component."""
        super().deserialize(data)
        self.team = data.get("team", CombatantComponent.TEAM_ENEMY)
        self.faction = data.get("faction", "")
        self.is_targetable = data.get("is_targetable", True)
        self.threat_value = data.get("threat_value", 1.0)

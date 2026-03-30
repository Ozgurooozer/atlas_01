"""
Room Template Library.

Provides room layout templates for procedural room generation.
Includes 15 built-in default templates across categories:
combat_small, combat_medium, combat_large, boss_arena, treasure_room.

Layer: 4 (Game/Run)
Dependencies: core.object, game.run.game_rng
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from core.object import Object
from game.run.game_rng import GameRNG


@dataclass
class RoomTemplate:
    """Defines a room layout with platforms, spawn zones, and doors."""

    name: str = ""
    width: int = 800
    height: int = 600
    platforms: list[dict[str, int]] = field(default_factory=list)
    spawn_zones: list[dict[str, int]] = field(default_factory=list)
    door_locations: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize this template to a dictionary."""
        return {
            "name": self.name,
            "width": self.width,
            "height": self.height,
            "platforms": [dict(p) for p in self.platforms],
            "spawn_zones": [dict(s) for s in self.spawn_zones],
            "door_locations": [dict(d) for d in self.door_locations],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> RoomTemplate:
        """Create a RoomTemplate from a dictionary."""
        return cls(
            name=data.get("name", ""),
            width=data.get("width", 800),
            height=data.get("height", 600),
            platforms=[dict(p) for p in data.get("platforms", [])],
            spawn_zones=[dict(s) for s in data.get("spawn_zones", [])],
            door_locations=[dict(d) for d in data.get("door_locations", [])],
        )


class RoomTemplateLibrary(Object):
    """Library of room templates with no-repeat random selection."""

    def __init__(self, name: str | None = None):
        """Create a new RoomTemplateLibrary."""
        super().__init__(name=name or "RoomTemplateLibrary")
        self._templates: Dict[str, RoomTemplate] = {}
        self._recent_names: List[str] = []
        self._recent_count: int = 3

    def load(self, templates_data: List[Dict[str, Any]]) -> None:
        """Load templates from a list of dicts."""
        for td in templates_data:
            tmpl = RoomTemplate.from_dict(td)
            self._templates[tmpl.name] = tmpl

    def load_defaults(self) -> None:
        """Load the 15 built-in default templates."""
        defaults = self._build_defaults()
        for tmpl in defaults:
            self._templates[tmpl.name] = tmpl

    def get_template(self, name: str) -> Optional[RoomTemplate]:
        """Get a template by name. Returns None if not found."""
        return self._templates.get(name)

    def get_random(self, rng: GameRNG) -> Optional[RoomTemplate]:
        """Get a random template, excluding recently used ones."""
        available = self._available_templates()
        if not available:
            return None
        chosen = rng.choice(available)
        self._recent_names.append(chosen.name)
        if len(self._recent_names) > self._recent_count:
            self._recent_names = self._recent_names[-self._recent_count:]
        return chosen

    def track_recent(self, count: int) -> None:
        """Set how many recent templates to exclude from random."""
        self._recent_count = count
        if len(self._recent_names) > self._recent_count:
            self._recent_names = self._recent_names[-self._recent_count:]

    @property
    def all_templates(self) -> List[RoomTemplate]:
        """Get all loaded templates."""
        return list(self._templates.values())

    def _available_templates(self) -> List[RoomTemplate]:
        """Get templates not in recent list."""
        recent_set = set(self._recent_names)
        return [t for t in self._templates.values() if t.name not in recent_set]

    def serialize(self) -> Dict[str, Any]:
        """Serialize library to dict."""
        data = super().serialize()
        data["templates"] = [t.to_dict() for t in self.all_templates]
        data["recent_names"] = list(self._recent_names)
        data["recent_count"] = self._recent_count
        return data

    def deserialize(self, data: Dict[str, Any]) -> None:
        """Restore library from dict."""
        super().deserialize(data)
        templates_data = data.get("templates", [])
        for td in templates_data:
            tmpl = RoomTemplate.from_dict(td)
            self._templates[tmpl.name] = tmpl
        self._recent_names = list(data.get("recent_names", []))
        self._recent_count = data.get("recent_count", 3)

    @staticmethod
    def _build_defaults() -> List[RoomTemplate]:
        """Build the 15 default templates."""
        templates: List[RoomTemplate] = []
        # 5 combat_small: 800x600, 2-3 platforms
        templates.append(RoomTemplate(
            name="combat_small_01", width=800, height=600,
            platforms=[
                {"x": 0, "y": 500, "w": 350, "h": 20},
                {"x": 450, "y": 500, "w": 350, "h": 20},
            ],
            spawn_zones=[{"x": 100, "y": 400, "w": 60, "h": 100}],
            door_locations=[{"side": "right", "x": 790, "y": 480}],
        ))
        templates.append(RoomTemplate(
            name="combat_small_02", width=800, height=600,
            platforms=[
                {"x": 0, "y": 500, "w": 800, "h": 20},
                {"x": 300, "y": 350, "w": 200, "h": 20},
            ],
            spawn_zones=[{"x": 50, "y": 400, "w": 60, "h": 100}],
            door_locations=[{"side": "right", "x": 790, "y": 480}],
        ))
        templates.append(RoomTemplate(
            name="combat_small_03", width=800, height=600,
            platforms=[
                {"x": 0, "y": 500, "w": 250, "h": 20},
                {"x": 550, "y": 500, "w": 250, "h": 20},
                {"x": 300, "y": 380, "w": 200, "h": 20},
            ],
            spawn_zones=[{"x": 620, "y": 400, "w": 60, "h": 100}],
            door_locations=[{"side": "right", "x": 790, "y": 480}],
        ))
        templates.append(RoomTemplate(
            name="combat_small_04", width=800, height=600,
            platforms=[
                {"x": 0, "y": 500, "w": 400, "h": 20},
                {"x": 400, "y": 500, "w": 400, "h": 20},
                {"x": 200, "y": 360, "w": 400, "h": 20},
            ],
            spawn_zones=[{"x": 350, "y": 260, "w": 60, "h": 100}],
            door_locations=[{"side": "right", "x": 790, "y": 480}],
        ))
        templates.append(RoomTemplate(
            name="combat_small_05", width=800, height=600,
            platforms=[
                {"x": 0, "y": 500, "w": 800, "h": 20},
                {"x": 0, "y": 300, "w": 150, "h": 20},
                {"x": 650, "y": 300, "w": 150, "h": 20},
            ],
            spawn_zones=[{"x": 400, "y": 400, "w": 60, "h": 100}],
            door_locations=[{"side": "right", "x": 790, "y": 480}],
        ))
        # 5 combat_medium: 1000x700, 3-4 platforms
        templates.append(RoomTemplate(
            name="combat_medium_01", width=1000, height=700,
            platforms=[
                {"x": 0, "y": 600, "w": 400, "h": 20},
                {"x": 600, "y": 600, "w": 400, "h": 20},
                {"x": 350, "y": 450, "w": 300, "h": 20},
            ],
            spawn_zones=[{"x": 100, "y": 500, "w": 60, "h": 100}],
            door_locations=[{"side": "right", "x": 990, "y": 580}],
        ))
        templates.append(RoomTemplate(
            name="combat_medium_02", width=1000, height=700,
            platforms=[
                {"x": 0, "y": 600, "w": 300, "h": 20},
                {"x": 350, "y": 600, "w": 300, "h": 20},
                {"x": 700, "y": 600, "w": 300, "h": 20},
                {"x": 200, "y": 420, "w": 250, "h": 20},
            ],
            spawn_zones=[{"x": 800, "y": 500, "w": 60, "h": 100}],
            door_locations=[{"side": "right", "x": 990, "y": 580}],
        ))
        templates.append(RoomTemplate(
            name="combat_medium_03", width=1000, height=700,
            platforms=[
                {"x": 0, "y": 600, "w": 500, "h": 20},
                {"x": 500, "y": 600, "w": 500, "h": 20},
                {"x": 100, "y": 420, "w": 200, "h": 20},
                {"x": 700, "y": 420, "w": 200, "h": 20},
            ],
            spawn_zones=[{"x": 450, "y": 500, "w": 60, "h": 100}],
            door_locations=[{"side": "right", "x": 990, "y": 580}],
        ))
        templates.append(RoomTemplate(
            name="combat_medium_04", width=1000, height=700,
            platforms=[
                {"x": 0, "y": 600, "w": 1000, "h": 20},
                {"x": 200, "y": 440, "w": 250, "h": 20},
                {"x": 550, "y": 440, "w": 250, "h": 20},
            ],
            spawn_zones=[{"x": 500, "y": 500, "w": 60, "h": 100}],
            door_locations=[{"side": "right", "x": 990, "y": 580}],
        ))
        templates.append(RoomTemplate(
            name="combat_medium_05", width=1000, height=700,
            platforms=[
                {"x": 0, "y": 600, "w": 350, "h": 20},
                {"x": 650, "y": 600, "w": 350, "h": 20},
                {"x": 0, "y": 400, "w": 200, "h": 20},
                {"x": 800, "y": 400, "w": 200, "h": 20},
            ],
            spawn_zones=[{"x": 470, "y": 500, "w": 60, "h": 100}],
            door_locations=[{"side": "right", "x": 990, "y": 580}],
        ))
        # 3 combat_large: 1200x800, 4-5 platforms
        templates.append(RoomTemplate(
            name="combat_large_01", width=1200, height=800,
            platforms=[
                {"x": 0, "y": 700, "w": 400, "h": 20},
                {"x": 400, "y": 700, "w": 400, "h": 20},
                {"x": 800, "y": 700, "w": 400, "h": 20},
                {"x": 250, "y": 520, "w": 300, "h": 20},
            ],
            spawn_zones=[{"x": 100, "y": 600, "w": 60, "h": 100}],
            door_locations=[{"side": "right", "x": 1190, "y": 680}],
        ))
        templates.append(RoomTemplate(
            name="combat_large_02", width=1200, height=800,
            platforms=[
                {"x": 0, "y": 700, "w": 600, "h": 20},
                {"x": 600, "y": 700, "w": 600, "h": 20},
                {"x": 150, "y": 530, "w": 250, "h": 20},
                {"x": 800, "y": 530, "w": 250, "h": 20},
                {"x": 500, "y": 380, "w": 200, "h": 20},
            ],
            spawn_zones=[{"x": 600, "y": 600, "w": 60, "h": 100}],
            door_locations=[{"side": "right", "x": 1190, "y": 680}],
        ))
        templates.append(RoomTemplate(
            name="combat_large_03", width=1200, height=800,
            platforms=[
                {"x": 0, "y": 700, "w": 300, "h": 20},
                {"x": 450, "y": 700, "w": 300, "h": 20},
                {"x": 900, "y": 700, "w": 300, "h": 20},
                {"x": 200, "y": 520, "w": 250, "h": 20},
                {"x": 750, "y": 520, "w": 250, "h": 20},
            ],
            spawn_zones=[{"x": 550, "y": 600, "w": 60, "h": 100}],
            door_locations=[{"side": "right", "x": 1190, "y": 680}],
        ))
        # 1 boss_arena: 1400x900, central platform
        templates.append(RoomTemplate(
            name="boss_arena_01", width=1400, height=900,
            platforms=[
                {"x": 200, "y": 800, "w": 1000, "h": 20},
                {"x": 500, "y": 650, "w": 400, "h": 20},
            ],
            spawn_zones=[{"x": 200, "y": 700, "w": 80, "h": 100}],
            door_locations=[
                {"side": "left", "x": 10, "y": 780},
                {"side": "right", "x": 1390, "y": 780},
            ],
        ))
        # 1 treasure_room: 600x400, no enemies, single platform
        templates.append(RoomTemplate(
            name="treasure_room_01", width=600, height=400,
            platforms=[{"x": 50, "y": 320, "w": 500, "h": 20}],
            spawn_zones=[{"x": 270, "y": 220, "w": 60, "h": 100}],
            door_locations=[{"side": "left", "x": 10, "y": 300}],
        ))
        return templates

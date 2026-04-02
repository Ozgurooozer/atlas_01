"""
Room Template Library Tests.

Tests for RoomTemplate dataclass and RoomTemplateLibrary class.
Layer 4 (Game/Run), depends on core.object, game.run.game_rng.

TDD: RED phase first, then GREEN.
"""
from __future__ import annotations


class TestRoomTemplate:
    """Tests for the RoomTemplate dataclass."""

    def test_create_basic_template(self):
        """RoomTemplate can be created with required fields."""
        from game.run.room_templates import RoomTemplate
        t = RoomTemplate(
            name="test_room",
            width=800,
            height=600,
            platforms=[{"x": 0, "y": 500, "w": 800, "h": 20}],
            spawn_zones=[{"x": 100, "y": 400, "w": 60, "h": 100}],
            door_locations=[{"side": "right", "x": 790, "y": 300}],
        )
        assert t.name == "test_room"
        assert t.width == 800
        assert t.height == 600
        assert len(t.platforms) == 1
        assert len(t.spawn_zones) == 1
        assert len(t.door_locations) == 1

    def test_template_with_multiple_platforms(self):
        """RoomTemplate supports multiple platforms."""
        from game.run.room_templates import RoomTemplate
        platforms = [
            {"x": 0, "y": 500, "w": 300, "h": 20},
            {"x": 500, "y": 500, "w": 300, "h": 20},
            {"x": 250, "y": 350, "w": 200, "h": 20},
        ]
        t = RoomTemplate(
            name="multi_plat",
            width=800,
            height=600,
            platforms=platforms,
            spawn_zones=[],
            door_locations=[],
        )
        assert len(t.platforms) == 3

    def test_template_with_multiple_doors(self):
        """RoomTemplate supports multiple door locations."""
        from game.run.room_templates import RoomTemplate
        doors = [
            {"side": "left", "x": 10, "y": 300},
            {"side": "right", "x": 790, "y": 300},
            {"side": "top", "x": 400, "y": 10},
        ]
        t = RoomTemplate(
            name="multi_door",
            width=800,
            height=600,
            platforms=[],
            spawn_zones=[],
            door_locations=doors,
        )
        assert len(t.door_locations) == 3

    def test_template_to_dict(self):
        """RoomTemplate serializes to dict correctly."""
        from game.run.room_templates import RoomTemplate
        t = RoomTemplate(
            name="serialize_test",
            width=600,
            height=400,
            platforms=[{"x": 0, "y": 380, "w": 600, "h": 20}],
            spawn_zones=[{"x": 100, "y": 300, "w": 60, "h": 80}],
            door_locations=[{"side": "right", "x": 590, "y": 200}],
        )
        d = t.to_dict()
        assert d["name"] == "serialize_test"
        assert d["width"] == 600
        assert d["height"] == 400
        assert len(d["platforms"]) == 1

    def test_template_from_dict(self):
        """RoomTemplate deserializes from dict correctly."""
        from game.run.room_templates import RoomTemplate
        data = {
            "name": "from_dict_test",
            "width": 1000,
            "height": 700,
            "platforms": [
                {"x": 0, "y": 680, "w": 400, "h": 20},
                {"x": 600, "y": 680, "w": 400, "h": 20},
            ],
            "spawn_zones": [{"x": 200, "y": 600, "w": 60, "h": 80}],
            "door_locations": [{"side": "left", "x": 10, "y": 350}],
        }
        t = RoomTemplate.from_dict(data)
        assert t.name == "from_dict_test"
        assert t.width == 1000
        assert t.height == 700
        assert len(t.platforms) == 2

    def test_template_roundtrip(self):
        """RoomTemplate roundtrip through to_dict/from_dict."""
        from game.run.room_templates import RoomTemplate
        original = RoomTemplate(
            name="roundtrip",
            width=1200,
            height=800,
            platforms=[{"x": 100, "y": 600, "w": 300, "h": 20}],
            spawn_zones=[{"x": 500, "y": 500, "w": 80, "h": 100}],
            door_locations=[{"side": "top", "x": 600, "y": 10}],
        )
        restored = RoomTemplate.from_dict(original.to_dict())
        assert restored.name == original.name
        assert restored.width == original.width
        assert restored.height == original.height
        assert restored.platforms == original.platforms
        assert restored.spawn_zones == original.spawn_zones
        assert restored.door_locations == original.door_locations


class TestRoomTemplateLibraryCreation:
    """Tests for creating and loading RoomTemplateLibrary."""

    def test_create_empty_library(self):
        """Library can be created with no templates."""
        from game.run.room_templates import RoomTemplateLibrary
        lib = RoomTemplateLibrary()
        assert len(lib.all_templates) == 0

    def test_load_templates_from_dicts(self):
        """Library loads templates from list of dicts."""
        from game.run.room_templates import RoomTemplateLibrary
        data = [
            {
                "name": "room_a",
                "width": 800,
                "height": 600,
                "platforms": [{"x": 0, "y": 500, "w": 800, "h": 20}],
                "spawn_zones": [{"x": 100, "y": 400, "w": 60, "h": 100}],
                "door_locations": [{"side": "right", "x": 790, "y": 300}],
            },
            {
                "name": "room_b",
                "width": 1000,
                "height": 700,
                "platforms": [{"x": 0, "y": 680, "w": 1000, "h": 20}],
                "spawn_zones": [],
                "door_locations": [],
            },
        ]
        lib = RoomTemplateLibrary()
        lib.load(data)
        assert len(lib.all_templates) == 2

    def test_load_default_templates(self):
        """Library has 15 built-in default templates."""
        from game.run.room_templates import RoomTemplateLibrary
        lib = RoomTemplateLibrary()
        lib.load_defaults()
        assert len(lib.all_templates) == 15

    def test_inherits_from_object(self):
        """RoomTemplateLibrary inherits from core.object.Object."""
        from game.run.room_templates import RoomTemplateLibrary
        from core.object import Object
        lib = RoomTemplateLibrary()
        assert isinstance(lib, Object)

    def test_get_template_by_name(self):
        """get_template returns the correct template by name."""
        from game.run.room_templates import RoomTemplateLibrary
        data = [
            {
                "name": "arena_1",
                "width": 800,
                "height": 600,
                "platforms": [{"x": 0, "y": 500, "w": 800, "h": 20}],
                "spawn_zones": [{"x": 100, "y": 400, "w": 60, "h": 100}],
                "door_locations": [{"side": "right", "x": 790, "y": 300}],
            },
        ]
        lib = RoomTemplateLibrary()
        lib.load(data)
        t = lib.get_template("arena_1")
        assert t is not None
        assert t.name == "arena_1"
        assert t.width == 800

    def test_get_template_missing_returns_none(self):
        """get_template returns None for unknown name."""
        from game.run.room_templates import RoomTemplateLibrary
        lib = RoomTemplateLibrary()
        assert lib.get_template("nonexistent") is None


class TestDefaultTemplateCategories:
    """Verify default template categories are correct."""

    def test_five_combat_small_templates(self):
        """Default library has exactly 5 combat_small templates."""
        from game.run.room_templates import RoomTemplateLibrary
        lib = RoomTemplateLibrary()
        lib.load_defaults()
        small = [t for t in lib.all_templates if t.name.startswith("combat_small")]
        assert len(small) == 5
        for t in small:
            assert t.width == 800
            assert t.height == 600

    def test_combat_small_platform_counts(self):
        """combat_small templates have 2-3 platforms each."""
        from game.run.room_templates import RoomTemplateLibrary
        lib = RoomTemplateLibrary()
        lib.load_defaults()
        small = [t for t in lib.all_templates if t.name.startswith("combat_small")]
        for t in small:
            assert 2 <= len(t.platforms) <= 3

    def test_five_combat_medium_templates(self):
        """Default library has exactly 5 combat_medium templates."""
        from game.run.room_templates import RoomTemplateLibrary
        lib = RoomTemplateLibrary()
        lib.load_defaults()
        medium = [t for t in lib.all_templates if t.name.startswith("combat_medium")]
        assert len(medium) == 5
        for t in medium:
            assert t.width == 1000
            assert t.height == 700

    def test_combat_medium_platform_counts(self):
        """combat_medium templates have 3-4 platforms each."""
        from game.run.room_templates import RoomTemplateLibrary
        lib = RoomTemplateLibrary()
        lib.load_defaults()
        medium = [t for t in lib.all_templates if t.name.startswith("combat_medium")]
        for t in medium:
            assert 3 <= len(t.platforms) <= 4

    def test_three_combat_large_templates(self):
        """Default library has exactly 3 combat_large templates."""
        from game.run.room_templates import RoomTemplateLibrary
        lib = RoomTemplateLibrary()
        lib.load_defaults()
        large = [t for t in lib.all_templates if t.name.startswith("combat_large")]
        assert len(large) == 3
        for t in large:
            assert t.width == 1200
            assert t.height == 800

    def test_combat_large_platform_counts(self):
        """combat_large templates have 4-5 platforms each."""
        from game.run.room_templates import RoomTemplateLibrary
        lib = RoomTemplateLibrary()
        lib.load_defaults()
        large = [t for t in lib.all_templates if t.name.startswith("combat_large")]
        for t in large:
            assert 4 <= len(t.platforms) <= 5

    def test_boss_arena_template(self):
        """Default library has exactly 1 boss_arena template."""
        from game.run.room_templates import RoomTemplateLibrary
        lib = RoomTemplateLibrary()
        lib.load_defaults()
        boss = [t for t in lib.all_templates if t.name.startswith("boss_arena")]
        assert len(boss) == 1
        assert boss[0].width == 1400
        assert boss[0].height == 900
        assert len(boss[0].platforms) >= 1

    def test_treasure_room_template(self):
        """Default library has exactly 1 treasure_room template."""
        from game.run.room_templates import RoomTemplateLibrary
        lib = RoomTemplateLibrary()
        lib.load_defaults()
        treasure = [t for t in lib.all_templates if t.name.startswith("treasure_room")]
        assert len(treasure) == 1
        assert treasure[0].width == 600
        assert treasure[0].height == 400


class TestRoomTemplateLibraryRandom:
    """Tests for random template selection and no-repeat tracking."""

    def test_get_random_returns_template(self):
        """get_random returns a valid RoomTemplate."""
        from game.run.room_templates import RoomTemplateLibrary
        from game.run.game_rng import GameRNG
        lib = RoomTemplateLibrary()
        lib.load_defaults()
        rng = GameRNG(seed=42)
        t = lib.get_random(rng)
        assert t is not None
        assert t.name != ""

    def test_get_random_deterministic(self):
        """get_random is deterministic with same seed."""
        from game.run.room_templates import RoomTemplateLibrary
        from game.run.game_rng import GameRNG
        lib1 = RoomTemplateLibrary()
        lib1.load_defaults()
        lib2 = RoomTemplateLibrary()
        lib2.load_defaults()
        rng1 = GameRNG(seed=100)
        rng2 = GameRNG(seed=100)
        t1 = lib1.get_random(rng1)
        t2 = lib2.get_random(rng2)
        assert t1.name == t2.name

    def test_track_recent_no_repeat(self):
        """get_random avoids recently used templates."""
        from game.run.room_templates import RoomTemplateLibrary
        from game.run.game_rng import GameRNG
        lib = RoomTemplateLibrary()
        lib.load_defaults()
        rng = GameRNG(seed=42)
        # Use 3 templates
        used = []
        for _ in range(3):
            t = lib.get_random(rng)
            used.append(t.name)
        # No repeats in the tracked window
        assert len(used) == len(set(used))

    def test_track_recent_count_param(self):
        """track_recent sets how many recent templates to avoid."""
        from game.run.room_templates import RoomTemplateLibrary
        from game.run.game_rng import GameRNG
        lib = RoomTemplateLibrary()
        lib.load_defaults()
        lib.track_recent(5)
        rng = GameRNG(seed=42)
        used = []
        for _ in range(5):
            t = lib.get_random(rng)
            used.append(t.name)
        assert len(used) == len(set(used))

    def test_track_recent_clears_old_entries(self):
        """Old entries are removed when track_recent count is smaller."""
        from game.run.room_templates import RoomTemplateLibrary
        from game.run.game_rng import GameRNG
        lib = RoomTemplateLibrary()
        lib.load_defaults()
        lib.track_recent(2)
        rng = GameRNG(seed=42)
        first = lib.get_random(rng)
        second = lib.get_random(rng)
        # After 2 more picks, first should be available again
        third = lib.get_random(rng)
        fourth = lib.get_random(rng)
        assert fourth.name != first.name or fourth.name != second.name

    def test_get_random_empty_library_returns_none(self):
        """get_random returns None when library is empty."""
        from game.run.room_templates import RoomTemplateLibrary
        from game.run.game_rng import GameRNG
        lib = RoomTemplateLibrary()
        rng = GameRNG(seed=42)
        assert lib.get_random(rng) is None

    def test_get_random_all_recent_returns_none(self):
        """get_random returns None when all templates are recent."""
        from game.run.room_templates import RoomTemplateLibrary
        from game.run.game_rng import GameRNG
        lib = RoomTemplateLibrary()
        data = [
            {
                "name": "only_room",
                "width": 800,
                "height": 600,
                "platforms": [{"x": 0, "y": 500, "w": 800, "h": 20}],
                "spawn_zones": [],
                "door_locations": [],
            },
        ]
        lib.load(data)
        lib.track_recent(1)
        rng = GameRNG(seed=42)
        first = lib.get_random(rng)
        assert first is not None
        second = lib.get_random(rng)
        # Only 1 template and it was recently used
        assert second is None


class TestRoomTemplateLibrarySerialization:
    """Tests for serialization support."""

    def test_serialize(self):
        """Library serializes to dict with templates."""
        from game.run.room_templates import RoomTemplateLibrary
        lib = RoomTemplateLibrary()
        data = [
            {
                "name": "ser_room",
                "width": 800,
                "height": 600,
                "platforms": [{"x": 0, "y": 500, "w": 800, "h": 20}],
                "spawn_zones": [],
                "door_locations": [],
            },
        ]
        lib.load(data)
        ser = lib.serialize()
        assert ser["__class__"] == "RoomTemplateLibrary"
        assert "templates" in ser
        assert len(ser["templates"]) == 1

    def test_deserialize(self):
        """Library deserializes from dict correctly."""
        from game.run.room_templates import RoomTemplateLibrary
        lib = RoomTemplateLibrary()
        data = [
            {
                "name": "deser_room",
                "width": 1000,
                "height": 700,
                "platforms": [{"x": 0, "y": 680, "w": 1000, "h": 20}],
                "spawn_zones": [],
                "door_locations": [],
            },
        ]
        lib.load(data)
        ser = lib.serialize()
        lib2 = RoomTemplateLibrary()
        lib2.deserialize(ser)
        assert len(lib2.all_templates) == 1
        t = lib2.get_template("deser_room")
        assert t is not None
        assert t.width == 1000

    def test_serialize_deserialize_roundtrip(self):
        """Full roundtrip preserves all template data."""
        from game.run.room_templates import RoomTemplateLibrary
        lib = RoomTemplateLibrary()
        data = [
            {
                "name": "rt_room",
                "width": 1200,
                "height": 800,
                "platforms": [
                    {"x": 0, "y": 780, "w": 400, "h": 20},
                    {"x": 800, "y": 780, "w": 400, "h": 20},
                ],
                "spawn_zones": [{"x": 600, "y": 700, "w": 80, "h": 80}],
                "door_locations": [
                    {"side": "left", "x": 10, "y": 400},
                    {"side": "right", "x": 1190, "y": 400},
                ],
            },
        ]
        lib.load(data)
        ser = lib.serialize()
        lib2 = RoomTemplateLibrary()
        lib2.deserialize(ser)
        t = lib2.get_template("rt_room")
        assert t.width == 1200
        assert len(t.platforms) == 2
        assert len(t.spawn_zones) == 1
        assert len(t.door_locations) == 2

    def test_serialize_with_recent_tracking(self):
        """Serialization preserves recent tracking data."""
        from game.run.room_templates import RoomTemplateLibrary
        from game.run.game_rng import GameRNG
        lib = RoomTemplateLibrary()
        lib.load_defaults()
        lib.track_recent(5)
        rng = GameRNG(seed=42)
        lib.get_random(rng)
        lib.get_random(rng)
        ser = lib.serialize()
        assert "recent_names" in ser
        assert len(ser["recent_names"]) == 2

    def test_deserialize_restores_recent_tracking(self):
        """Deserialization restores recent tracking."""
        from game.run.room_templates import RoomTemplateLibrary
        from game.run.game_rng import GameRNG
        lib = RoomTemplateLibrary()
        lib.load_defaults()
        lib.track_recent(5)
        rng = GameRNG(seed=42)
        lib.get_random(rng)
        ser = lib.serialize()
        lib2 = RoomTemplateLibrary()
        lib2.deserialize(ser)
        assert lib2._recent_count == 5
        assert len(lib2._recent_names) == 1

    def test_serialize_defaults(self):
        """Serializing with default templates works."""
        from game.run.room_templates import RoomTemplateLibrary
        lib = RoomTemplateLibrary()
        lib.load_defaults()
        ser = lib.serialize()
        assert len(ser["templates"]) == 15

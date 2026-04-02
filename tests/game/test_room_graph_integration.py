"""
Room Graph Integration Tests.

Integrates RoomGraph with GameRNG, RoomTemplateLibrary, and EncounterGenerator.
Layer 4 (Game/Run).

TDD: RED phase — tests for enhanced RoomGraph.
"""
from __future__ import annotations


class TestRoomGraphGameRNGIntegration:
    """RoomGraph uses GameRNG instead of global random."""

    def test_room_graph_uses_game_rng(self):
        from game.run.room import RoomGraph
        graph = RoomGraph(seed=42)
        graph.generate_game_rng(room_count=8)
        assert len(graph.rooms) == 8
        assert graph.rooms[0].room_type.name == "START"
        assert graph.rooms[-1].room_type.name == "BOSS"

    def test_deterministic_with_game_rng(self):
        from game.run.room import RoomGraph
        g1 = RoomGraph(seed=999)
        g2 = RoomGraph(seed=999)
        g1.generate_game_rng(room_count=8)
        g2.generate_game_rng(room_count=8)
        for i in range(8):
            assert g1.rooms[i].room_type == g2.rooms[i].room_type
            assert g1.rooms[i].seed == g2.rooms[i].seed

    def test_different_seeds_different_rooms(self):
        from game.run.room import RoomGraph
        g1 = RoomGraph(seed=1)
        g2 = RoomGraph(seed=2)
        g1.generate_game_rng(room_count=8)
        g2.generate_game_rng(room_count=8)
        seeds_differ = any(
            g1.rooms[i].seed != g2.rooms[i].seed for i in range(8)
        )
        assert seeds_differ

    def test_advance_still_works(self):
        from game.run.room import RoomGraph
        graph = RoomGraph(seed=42)
        graph.generate_game_rng(room_count=5)
        r1 = graph.advance()
        assert r1 is not None
        r2 = graph.advance()
        assert r2 is not None
        assert r1.room_id != r2.room_id


class TestRoomTemplateAssignment:
    """Rooms can be assigned templates from RoomTemplateLibrary."""

    def test_assign_template_to_room(self):
        from game.run.room import Room
        from game.run.room_templates import RoomTemplateLibrary
        lib = RoomTemplateLibrary()
        lib.load_defaults()
        tmpl = lib.get_template("combat_small_01")
        room = Room()
        room.template_name = tmpl.name
        room.template_width = tmpl.width
        room.template_height = tmpl.height
        assert room.template_name == "combat_small_01"
        assert room.template_width == 800

    def test_assign_template_from_library(self):
        from game.run.room import Room
        from game.run.room_templates import RoomTemplateLibrary
        lib = RoomTemplateLibrary()
        lib.load_defaults()
        from game.run.game_rng import GameRNG
        rng = GameRNG(seed=42)
        tmpl = lib.get_random(rng)
        room = Room()
        room.template_name = tmpl.name
        assert tmpl is not None


class TestRoomGraphFlowValidation:
    """Validate generated room graph flow."""

    def test_start_room_first(self):
        from game.run.room import RoomGraph, RoomType
        graph = RoomGraph(seed=42)
        graph.generate_game_rng(room_count=10)
        assert graph.rooms[0].room_type == RoomType.START

    def test_boss_room_last(self):
        from game.run.room import RoomGraph, RoomType
        graph = RoomGraph(seed=42)
        graph.generate_game_rng(room_count=10)
        assert graph.rooms[-1].room_type == RoomType.BOSS

    def test_has_combat_rooms(self):
        from game.run.room import RoomGraph, RoomType
        graph = RoomGraph(seed=42)
        graph.generate_game_rng(room_count=10)
        combat_count = sum(
            1 for r in graph.rooms if r.room_type == RoomType.COMBAT
        )
        assert combat_count >= 3

    def test_has_non_combat_rooms(self):
        from game.run.room import RoomGraph, RoomType
        graph = RoomGraph(seed=42)
        graph.generate_game_rng(room_count=10)
        non_combat = [
            r for r in graph.rooms
            if r.room_type in (RoomType.SHOP, RoomType.REST, RoomType.TREASURE, RoomType.REWARD)
        ]
        assert len(non_combat) >= 2

    def test_room_seeds_differ(self):
        from game.run.room import RoomGraph
        graph = RoomGraph(seed=42)
        graph.generate_game_rng(room_count=10)
        seeds = [r.seed for r in graph.rooms]
        assert len(set(seeds)) >= len(seeds) - 1  # Allow near-duplicates


class TestRoomGraphSerialization:
    """Roundtrip serialization with GameRNG-generated rooms."""

    def test_serialize_deserialize_roundtrip(self):
        from game.run.room import RoomGraph
        graph = RoomGraph(seed=42)
        graph.generate_game_rng(room_count=8)
        graph.advance()
        graph.advance()
        data = graph.serialize()

        graph2 = RoomGraph(seed=0)
        graph2.deserialize(data)
        assert len(graph2.rooms) == 8
        assert graph2.current_index == 1
        assert graph2.rooms[0].room_type == graph.rooms[0].room_type

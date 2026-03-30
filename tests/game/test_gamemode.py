"""
Tests for GameMode base class.

GameMode defines the rules and state of the game.
It manages the game flow and player interaction.

Layer: 4 (Game)
"""

import pytest
from core.object import Object
from core.guid import GUID
from game.gamemode import GameMode
from world.world import World


class TestGameModeInheritance:
    """Test that GameMode inherits from Object."""

    def test_gamemode_is_object(self):
        """GameMode should be an instance of Object."""
        gm = GameMode()
        assert isinstance(gm, Object)

    def test_gamemode_has_guid(self):
        """GameMode should have a GUID."""
        gm = GameMode()
        assert hasattr(gm, "guid")
        assert isinstance(gm.guid, GUID)

    def test_gamemode_has_name(self):
        """GameMode should have a name."""
        gm = GameMode(name="TestGameMode")
        assert gm.name == "TestGameMode"


class TestGameModeWorld:
    """Test GameMode world reference."""

    def test_gamemode_has_world(self):
        """GameMode should have world property."""
        gm = GameMode()
        assert hasattr(gm, "world")

    def test_gamemode_world_default_none(self):
        """GameMode world should default to None."""
        gm = GameMode()
        assert gm.world is None

    def test_gamemode_world_can_be_set(self):
        """GameMode world can be set."""
        gm = GameMode()
        world = World()
        gm.world = world
        assert gm.world is world


class TestGameModeLifecycle:
    """Test GameMode lifecycle hooks."""

    def test_gamemode_has_on_start(self):
        """GameMode should have on_start method."""
        gm = GameMode()
        assert hasattr(gm, "on_start")
        assert callable(gm.on_start)

    def test_gamemode_has_on_end(self):
        """GameMode should have on_end method."""
        gm = GameMode()
        assert hasattr(gm, "on_end")
        assert callable(gm.on_end)

    def test_gamemode_has_on_tick(self):
        """GameMode should have on_tick method."""
        gm = GameMode()
        assert hasattr(gm, "on_tick")
        assert callable(gm.on_tick)

    def test_on_start_can_be_overridden(self):
        """on_start can be overridden in subclass."""
        results = []

        class CustomGameMode(GameMode):
            def on_start(self):
                results.append("started")

        gm = CustomGameMode()
        gm.on_start()
        assert "started" in results

    def test_on_tick_receives_delta_time(self):
        """on_tick should receive delta_time."""
        results = []

        class CustomGameMode(GameMode):
            def on_tick(self, delta_time: float):
                results.append(delta_time)

        gm = CustomGameMode()
        gm.on_tick(0.016)
        assert 0.016 in results


class TestGameModeState:
    """Test GameMode state management."""

    def test_gamemode_has_is_running(self):
        """GameMode should have is_running property."""
        gm = GameMode()
        assert hasattr(gm, "is_running")

    def test_is_running_default_false(self):
        """is_running should default to False."""
        gm = GameMode()
        assert gm.is_running is False

    def test_start_sets_is_running(self):
        """start() should set is_running to True."""
        gm = GameMode()
        gm.start()
        assert gm.is_running is True

    def test_end_sets_is_running_false(self):
        """end() should set is_running to False."""
        gm = GameMode()
        gm.start()
        gm.end()
        assert gm.is_running is False

    def test_start_calls_on_start(self):
        """start() should call on_start."""
        results = []

        class CustomGameMode(GameMode):
            def on_start(self):
                results.append("called")

        gm = CustomGameMode()
        gm.start()
        assert "called" in results

    def test_end_calls_on_end(self):
        """end() should call on_end."""
        results = []

        class CustomGameMode(GameMode):
            def on_end(self):
                results.append("called")

        gm = CustomGameMode()
        gm.start()
        gm.end()
        assert "called" in results


class TestGameModeTick:
    """Test GameMode tick functionality."""

    def test_gamemode_has_tick(self):
        """GameMode should have tick method."""
        gm = GameMode()
        assert hasattr(gm, "tick")
        assert callable(gm.tick)

    def test_tick_calls_on_tick_when_running(self):
        """tick() should call on_tick when running."""
        results = []

        class CustomGameMode(GameMode):
            def on_tick(self, delta_time: float):
                results.append(delta_time)

        gm = CustomGameMode()
        gm.start()
        gm.tick(0.016)
        assert 0.016 in results

    def test_tick_skips_when_not_running(self):
        """tick() should skip when not running."""
        results = []

        class CustomGameMode(GameMode):
            def on_tick(self, delta_time: float):
                results.append(delta_time)

        gm = CustomGameMode()
        gm.tick(0.016)  # Not started
        assert len(results) == 0


class TestGameModeSerialization:
    """Test GameMode serialization."""

    def test_gamemode_serialize(self):
        """GameMode should serialize basic properties."""
        gm = GameMode(name="Level1")
        data = gm.serialize()
        assert data["name"] == "Level1"

    def test_gamemode_deserialize(self):
        """GameMode should deserialize basic properties."""
        gm = GameMode()
        data = {"name": "DeserializedMode"}
        gm.deserialize(data)
        assert gm.name == "DeserializedMode"


class TestGameModeRepr:
    """Test GameMode string representation."""

    def test_gamemode_repr(self):
        """GameMode should have useful repr."""
        gm = GameMode(name="TestMode")
        repr_str = repr(gm)
        assert "GameMode" in repr_str
        assert "TestMode" in repr_str

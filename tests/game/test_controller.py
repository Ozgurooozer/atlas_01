"""
Tests for Controller classes.

Controller handles input and controls an Actor.

Layer: 4 (Game)
"""

from core.object import Object
from core.guid import GUID
from game.controller import Controller, PlayerController
from world.actor import Actor


class TestControllerInheritance:
    """Test that Controller inherits from Object."""

    def test_controller_is_object(self):
        """Controller should be an instance of Object."""
        ctrl = Controller()
        assert isinstance(ctrl, Object)

    def test_controller_has_guid(self):
        """Controller should have a GUID."""
        ctrl = Controller()
        assert hasattr(ctrl, "guid")
        assert isinstance(ctrl.guid, GUID)

    def test_controller_has_name(self):
        """Controller should have a name."""
        ctrl = Controller(name="TestController")
        assert ctrl.name == "TestController"


class TestControllerPawn:
    """Test Controller pawn (controlled actor) management."""

    def test_controller_has_pawn(self):
        """Controller should have pawn property."""
        ctrl = Controller()
        assert hasattr(ctrl, "pawn")

    def test_pawn_default_none(self):
        """Controller pawn should default to None."""
        ctrl = Controller()
        assert ctrl.pawn is None

    def test_pawn_can_be_set(self):
        """Controller pawn can be set."""
        ctrl = Controller()
        actor = Actor()
        ctrl.pawn = actor
        assert ctrl.pawn is actor

    def test_possess_sets_pawn(self):
        """possess() should set the pawn."""
        ctrl = Controller()
        actor = Actor()
        ctrl.possess(actor)
        assert ctrl.pawn is actor

    def test_unpossess_clears_pawn(self):
        """unpossess() should clear the pawn."""
        ctrl = Controller()
        actor = Actor()
        ctrl.possess(actor)
        ctrl.unpossess()
        assert ctrl.pawn is None


class TestControllerLifecycle:
    """Test Controller lifecycle hooks."""

    def test_controller_has_on_possess(self):
        """Controller should have on_possess method."""
        ctrl = Controller()
        assert hasattr(ctrl, "on_possess")
        assert callable(ctrl.on_possess)

    def test_controller_has_on_unpossess(self):
        """Controller should have on_unpossess method."""
        ctrl = Controller()
        assert hasattr(ctrl, "on_unpossess")
        assert callable(ctrl.on_unpossess)

    def test_possess_calls_on_possess(self):
        """possess() should call on_possess."""
        results = []

        class CustomController(Controller):
            def on_possess(self, pawn):
                results.append(pawn)

        ctrl = CustomController()
        actor = Actor()
        ctrl.possess(actor)
        assert actor in results

    def test_unpossess_calls_on_unpossess(self):
        """unpossess() should call on_unpossess."""
        results = []

        class CustomController(Controller):
            def on_unpossess(self):
                results.append("unpossessed")

        ctrl = CustomController()
        actor = Actor()
        ctrl.possess(actor)
        ctrl.unpossess()
        assert "unpossessed" in results


class TestPlayerControllerInheritance:
    """Test that PlayerController inherits from Controller."""

    def test_player_controller_is_controller(self):
        """PlayerController should be a Controller."""
        pc = PlayerController()
        assert isinstance(pc, Controller)

    def test_player_controller_is_object(self):
        """PlayerController should be an Object."""
        pc = PlayerController()
        assert isinstance(pc, Object)


class TestPlayerControllerInput:
    """Test PlayerController input handling."""

    def test_player_controller_has_on_input(self):
        """PlayerController should have on_input method."""
        pc = PlayerController()
        assert hasattr(pc, "on_input")
        assert callable(pc.on_input)

    def test_on_input_receives_action(self):
        """on_input should receive action name."""
        results = []

        class CustomPC(PlayerController):
            def on_input(self, action: str, pressed: bool):
                results.append((action, pressed))

        pc = CustomPC()
        pc.on_input("jump", True)
        assert ("jump", True) in results


class TestControllerTick:
    """Test Controller tick functionality."""

    def test_controller_has_tick(self):
        """Controller should have tick method."""
        ctrl = Controller()
        assert hasattr(ctrl, "tick")
        assert callable(ctrl.tick)

    def test_controller_has_on_tick(self):
        """Controller should have on_tick method."""
        ctrl = Controller()
        assert hasattr(ctrl, "on_tick")
        assert callable(ctrl.on_tick)

    def test_tick_calls_on_tick(self):
        """tick() should call on_tick."""
        results = []

        class CustomController(Controller):
            def on_tick(self, delta_time: float):
                results.append(delta_time)

        ctrl = CustomController()
        ctrl.tick(0.016)
        assert 0.016 in results


class TestControllerEnabled:
    """Test Controller enabled state."""

    def test_controller_has_enabled(self):
        """Controller should have enabled property."""
        ctrl = Controller()
        assert hasattr(ctrl, "enabled")

    def test_controller_enabled_by_default(self):
        """Controller should be enabled by default."""
        ctrl = Controller()
        assert ctrl.enabled is True

    def test_disabled_controller_skips_tick(self):
        """Disabled controller should skip on_tick."""
        results = []

        class CustomController(Controller):
            def on_tick(self, delta_time: float):
                results.append(delta_time)

        ctrl = CustomController()
        ctrl.enabled = False
        ctrl.tick(0.016)
        assert len(results) == 0


class TestControllerSerialization:
    """Test Controller serialization."""

    def test_controller_serialize(self):
        """Controller should serialize basic properties."""
        ctrl = Controller(name="Player1")
        data = ctrl.serialize()
        assert data["name"] == "Player1"

    def test_controller_deserialize(self):
        """Controller should deserialize basic properties."""
        ctrl = Controller()
        data = {"name": "DeserializedController"}
        ctrl.deserialize(data)
        assert ctrl.name == "DeserializedController"


class TestControllerRepr:
    """Test Controller string representation."""

    def test_controller_repr(self):
        """Controller should have useful repr."""
        ctrl = Controller(name="TestController")
        repr_str = repr(ctrl)
        assert "Controller" in repr_str
        assert "TestController" in repr_str

"""
Room Transition Manager Tests.

Tests for RoomTransitionManager class with state machine, callbacks,
and serialization support.
Layer 4 (Game/Run), depends on core.object.

TDD: RED phase first, then GREEN.
"""
from __future__ import annotations
import pytest


class TestTransitionStates:
    """Tests for transition state constants."""

    def test_states_exist(self):
        """All three states must be defined."""
        from game.run.transition import TransitionState
        assert hasattr(TransitionState, "IDLE")
        assert hasattr(TransitionState, "FADING_OUT")
        assert hasattr(TransitionState, "FADING_IN")


class TestTransitionManagerCreation:
    """Tests for creating RoomTransitionManager."""

    def test_create(self):
        """Manager can be created."""
        from game.run.transition import RoomTransitionManager
        mgr = RoomTransitionManager()
        assert mgr is not None

    def test_inherits_from_object(self):
        """Manager inherits from core.object.Object."""
        from game.run.transition import RoomTransitionManager
        from core.object import Object
        mgr = RoomTransitionManager()
        assert isinstance(mgr, Object)

    def test_initial_state_is_idle(self):
        """Manager starts in IDLE state."""
        from game.run.transition import RoomTransitionManager, TransitionState
        mgr = RoomTransitionManager()
        assert mgr.is_transitioning is False
        assert mgr.state == TransitionState.IDLE

    def test_initial_progress_is_zero(self):
        """Initial transition progress is 0.0."""
        from game.run.transition import RoomTransitionManager
        mgr = RoomTransitionManager()
        assert mgr.transition_progress == 0.0

    def test_default_fade_duration(self):
        """Default fade duration is 0.5 seconds."""
        from game.run.transition import RoomTransitionManager
        mgr = RoomTransitionManager()
        assert mgr.fade_duration == 0.5


class TestTransitionTo:
    """Tests for starting a transition."""

    def test_transition_to_starts_transition(self):
        """transition_to begins a fade-out."""
        from game.run.transition import RoomTransitionManager, TransitionState
        mgr = RoomTransitionManager()
        mgr.transition_to("next_room")
        assert mgr.is_transitioning is True
        assert mgr.state == TransitionState.FADING_OUT

    def test_transition_to_stores_room_name(self):
        """transition_to stores the target room name."""
        from game.run.transition import RoomTransitionManager
        mgr = RoomTransitionManager()
        mgr.transition_to("boss_room")
        assert mgr.target_room == "boss_room"

    def test_transition_to_with_direction(self):
        """transition_to accepts a direction parameter."""
        from game.run.transition import RoomTransitionManager
        mgr = RoomTransitionManager()
        mgr.transition_to("next_room", direction="left")
        assert mgr.direction == "left"

    def test_transition_to_default_direction(self):
        """transition_to defaults to 'right' direction."""
        from game.run.transition import RoomTransitionManager
        mgr = RoomTransitionManager()
        mgr.transition_to("next_room")
        assert mgr.direction == "right"

    def test_transition_to_raises_when_already_transitioning(self):
        """transition_to raises when already in a transition."""
        from game.run.transition import RoomTransitionManager
        mgr = RoomTransitionManager()
        mgr.transition_to("room_a")
        with pytest.raises(RuntimeError):
            mgr.transition_to("room_b")

    def test_transition_to_fires_start_callback(self):
        """on_transition_start callback fires on transition_to."""
        from game.run.transition import RoomTransitionManager
        mgr = RoomTransitionManager()
        started = []
        mgr.on_transition_start(lambda name: started.append(name))
        mgr.transition_to("test_room")
        assert len(started) == 1
        assert started[0] == "test_room"


class TestTransitionTick:
    """Tests for tick-based progression."""

    def test_tick_advances_progress_fading_out(self):
        """tick advances progress during FADING_OUT."""
        from game.run.transition import RoomTransitionManager, TransitionState
        mgr = RoomTransitionManager()
        mgr.transition_to("room")
        assert mgr.state == TransitionState.FADING_OUT
        mgr.tick(0.1)
        assert mgr.transition_progress > 0.0

    def test_tick_transitions_to_fading_in_at_half(self):
        """State changes to FADING_IN when progress reaches 1.0 in fade-out."""
        from game.run.transition import RoomTransitionManager, TransitionState
        mgr = RoomTransitionManager()
        mgr.fade_duration = 0.5
        mgr.transition_to("room")
        # Tick past the fade-out duration
        mgr.tick(0.3)
        mgr.tick(0.3)
        assert mgr.state == TransitionState.FADING_IN

    def test_tick_fires_complete_callback(self):
        """on_transition_complete fires when transition finishes."""
        from game.run.transition import RoomTransitionManager
        mgr = RoomTransitionManager()
        mgr.fade_duration = 0.5
        completed = []
        mgr.on_transition_complete(lambda name: completed.append(name))
        mgr.transition_to("done_room")
        mgr.tick(0.6)
        mgr.tick(0.6)
        assert mgr.state == RoomTransitionManager.get_idle_state()
        assert len(completed) == 1
        assert completed[0] == "done_room"

    def test_tick_complete_returns_to_idle(self):
        """After complete, manager returns to IDLE state."""
        from game.run.transition import RoomTransitionManager, TransitionState
        mgr = RoomTransitionManager()
        mgr.fade_duration = 0.5
        mgr.transition_to("room")
        mgr.tick(0.6)
        mgr.tick(0.6)
        assert mgr.state == TransitionState.IDLE
        assert mgr.is_transitioning is False

    def test_tick_complete_resets_progress(self):
        """Progress resets to 0.0 after completion."""
        from game.run.transition import RoomTransitionManager
        mgr = RoomTransitionManager()
        mgr.fade_duration = 0.5
        mgr.transition_to("room")
        mgr.tick(0.6)
        mgr.tick(0.6)
        assert mgr.transition_progress == 0.0

    def test_tick_no_op_when_idle(self):
        """tick does nothing when IDLE."""
        from game.run.transition import RoomTransitionManager
        mgr = RoomTransitionManager()
        mgr.tick(1.0)
        assert mgr.transition_progress == 0.0
        assert mgr.is_transitioning is False

    def test_progress_goes_to_1_at_fade_out_end(self):
        """Progress reaches ~1.0 at end of fade-out."""
        from game.run.transition import RoomTransitionManager
        mgr = RoomTransitionManager()
        mgr.fade_duration = 1.0
        mgr.transition_to("room")
        mgr.tick(1.0)
        assert mgr.transition_progress >= 0.99

    def test_progress_decreases_during_fade_in(self):
        """Progress decreases from 1.0 to 0.0 during FADING_IN."""
        from game.run.transition import RoomTransitionManager, TransitionState
        mgr = RoomTransitionManager()
        mgr.fade_duration = 1.0
        mgr.transition_to("room")
        mgr.tick(1.0)  # Complete fade-out
        assert mgr.state == TransitionState.FADING_IN
        mgr.tick(0.5)
        assert mgr.transition_progress < 1.0


class TestCancel:
    """Tests for cancelling transitions."""

    def test_cancel_during_fade_out(self):
        """cancel() returns to IDLE during FADING_OUT."""
        from game.run.transition import RoomTransitionManager, TransitionState
        mgr = RoomTransitionManager()
        mgr.transition_to("room")
        assert mgr.state == TransitionState.FADING_OUT
        mgr.cancel()
        assert mgr.state == TransitionState.IDLE
        assert mgr.is_transitioning is False

    def test_cancel_during_fade_in(self):
        """cancel() returns to IDLE during FADING_IN."""
        from game.run.transition import RoomTransitionManager, TransitionState
        mgr = RoomTransitionManager()
        mgr.fade_duration = 0.5
        mgr.transition_to("room")
        mgr.tick(0.6)
        assert mgr.state == TransitionState.FADING_IN
        mgr.cancel()
        assert mgr.state == TransitionState.IDLE

    def test_cancel_resets_progress(self):
        """cancel() resets progress to 0.0."""
        from game.run.transition import RoomTransitionManager
        mgr = RoomTransitionManager()
        mgr.transition_to("room")
        mgr.tick(0.1)
        assert mgr.transition_progress > 0.0
        mgr.cancel()
        assert mgr.transition_progress == 0.0

    def test_cancel_no_op_when_idle(self):
        """cancel() does nothing when IDLE."""
        from game.run.transition import RoomTransitionManager
        mgr = RoomTransitionManager()
        mgr.cancel()  # Should not raise
        assert mgr.is_transitioning is False

    def test_cancel_does_not_fire_complete(self):
        """cancel() does NOT fire on_transition_complete."""
        from game.run.transition import RoomTransitionManager
        mgr = RoomTransitionManager()
        completed = []
        mgr.on_transition_complete(lambda name: completed.append(name))
        mgr.transition_to("room")
        mgr.cancel()
        assert len(completed) == 0


class TestTransitionSerialization:
    """Tests for serialization support."""

    def test_serialize(self):
        """Manager serializes correctly."""
        from game.run.transition import RoomTransitionManager
        mgr = RoomTransitionManager()
        data = mgr.serialize()
        assert data["__class__"] == "RoomTransitionManager"
        assert "fade_duration" in data

    def test_deserialize(self):
        """Manager deserializes correctly."""
        from game.run.transition import RoomTransitionManager
        mgr = RoomTransitionManager()
        mgr.fade_duration = 1.0
        data = mgr.serialize()
        mgr2 = RoomTransitionManager()
        mgr2.deserialize(data)
        assert mgr2.fade_duration == 1.0

    def test_serialize_during_transition(self):
        """Manager serializes state during active transition."""
        from game.run.transition import RoomTransitionManager, TransitionState
        mgr = RoomTransitionManager()
        mgr.transition_to("active_room", direction="up")
        data = mgr.serialize()
        assert data["state"] == TransitionState.FADING_OUT.name
        assert data["target_room"] == "active_room"
        assert data["direction"] == "up"

    def test_deserialize_restores_transition(self):
        """Manager restores active transition on deserialize."""
        from game.run.transition import RoomTransitionManager, TransitionState
        mgr = RoomTransitionManager()
        mgr.fade_duration = 0.8
        mgr.transition_to("restored_room", direction="down")
        data = mgr.serialize()
        mgr2 = RoomTransitionManager()
        mgr2.deserialize(data)
        assert mgr2.state == TransitionState.FADING_OUT
        assert mgr2.target_room == "restored_room"
        assert mgr2.direction == "down"
        assert mgr2.fade_duration == 0.8

    def test_serialize_deserialize_roundtrip(self):
        """Full roundtrip preserves all manager state."""
        from game.run.transition import RoomTransitionManager
        mgr = RoomTransitionManager()
        mgr.fade_duration = 1.2
        data = mgr.serialize()
        mgr2 = RoomTransitionManager()
        mgr2.deserialize(data)
        assert mgr2.fade_duration == 1.2
        assert mgr2.state == mgr.state

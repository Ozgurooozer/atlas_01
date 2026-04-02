"""
Hit-Stop Tests.

Freeze frame system for combat impact.
Layer 4 (Game/Combat), depends on core.object.

TDD: RED phase.
"""
from __future__ import annotations


class TestHitStopBasics:
    """Core HitStopController behavior."""

    def test_create_with_default_values(self):
        from game.combat.hit_stop import HitStopController
        ctrl = HitStopController()
        assert not ctrl.is_active
        assert ctrl.remaining_frames == 0
        assert ctrl.max_frames == 10

    def test_create_with_custom_max(self):
        from game.combat.hit_stop import HitStopController
        ctrl = HitStopController(max_frames=20)
        assert ctrl.max_frames == 20

    def test_request_starts_freeze(self):
        from game.combat.hit_stop import HitStopController
        ctrl = HitStopController()
        ctrl.request(frames=3)
        assert ctrl.is_active
        assert ctrl.remaining_frames == 3

    def test_request_clamps_to_max(self):
        from game.combat.hit_stop import HitStopController
        ctrl = HitStopController(max_frames=5)
        ctrl.request(frames=100)
        assert ctrl.remaining_frames == 5

    def test_request_zero_frames_no_effect(self):
        from game.combat.hit_stop import HitStopController
        ctrl = HitStopController()
        ctrl.request(frames=0)
        assert not ctrl.is_active

    def test_request_negative_frames_no_effect(self):
        from game.combat.hit_stop import HitStopController
        ctrl = HitStopController()
        ctrl.request(frames=-1)
        assert not ctrl.is_active

    def test_request_overwrites_previous(self):
        from game.combat.hit_stop import HitStopController
        ctrl = HitStopController()
        ctrl.request(frames=5)
        ctrl.request(frames=2)
        assert ctrl.remaining_frames == 2


class TestHitStopTick:
    """Tick decrements freeze counter."""

    def test_tick_decrements_remaining(self):
        from game.combat.hit_stop import HitStopController
        ctrl = HitStopController()
        ctrl.request(frames=3)
        ctrl.tick()
        assert ctrl.remaining_frames == 2
        assert ctrl.is_active

    def test_tick_reaches_zero_deactivates(self):
        from game.combat.hit_stop import HitStopController
        ctrl = HitStopController()
        ctrl.request(frames=2)
        ctrl.tick()
        ctrl.tick()
        assert not ctrl.is_active
        assert ctrl.remaining_frames == 0

    def test_tick_when_inactive_no_effect(self):
        from game.combat.hit_stop import HitStopController
        ctrl = HitStopController()
        ctrl.tick()
        assert not ctrl.is_active
        assert ctrl.remaining_frames == 0

    def test_tick_full_cycle(self):
        from game.combat.hit_stop import HitStopController
        ctrl = HitStopController()
        ctrl.request(frames=5)
        for _ in range(5):
            ctrl.tick()
        assert not ctrl.is_active

    def test_tick_returns_true_when_active(self):
        from game.combat.hit_stop import HitStopController
        ctrl = HitStopController()
        ctrl.request(frames=2)
        assert ctrl.tick() is True

    def test_tick_returns_false_when_deactivated(self):
        from game.combat.hit_stop import HitStopController
        ctrl = HitStopController()
        ctrl.request(frames=1)
        ctrl.tick()  # goes to 0
        assert ctrl.tick() is False


class TestHitStopPresets:
    """Combat hit type presets."""

    def test_preset_light(self):
        from game.combat.hit_stop import HitStopController
        ctrl = HitStopController()
        ctrl.request_light()
        assert ctrl.is_active
        assert ctrl.remaining_frames == 1

    def test_preset_heavy(self):
        from game.combat.hit_stop import HitStopController
        ctrl = HitStopController()
        ctrl.request_heavy()
        assert ctrl.is_active
        assert ctrl.remaining_frames == 3

    def test_preset_critical(self):
        from game.combat.hit_stop import HitStopController
        ctrl = HitStopController()
        ctrl.request_critical()
        assert ctrl.is_active
        assert ctrl.remaining_frames == 4

    def test_preset_kill(self):
        from game.combat.hit_stop import HitStopController
        ctrl = HitStopController()
        ctrl.request_kill()
        assert ctrl.is_active
        assert ctrl.remaining_frames == 6


class TestHitStopCancel:
    """Cancel active freeze."""

    def test_cancel_deactivates(self):
        from game.combat.hit_stop import HitStopController
        ctrl = HitStopController()
        ctrl.request(frames=5)
        ctrl.cancel()
        assert not ctrl.is_active
        assert ctrl.remaining_frames == 0

    def test_cancel_when_inactive_no_error(self):
        from game.combat.hit_stop import HitStopController
        ctrl = HitStopController()
        ctrl.cancel()
        assert not ctrl.is_active


class TestHitStopSerialize:
    """Serialization support."""

    def test_serialize_empty(self):
        from game.combat.hit_stop import HitStopController
        ctrl = HitStopController()
        data = ctrl.serialize()
        assert "remaining_frames" in data
        assert "max_frames" in data

    def test_serialize_with_state(self):
        from game.combat.hit_stop import HitStopController
        ctrl = HitStopController()
        ctrl.request(frames=5)
        data = ctrl.serialize()
        assert data["remaining_frames"] == 5

    def test_deserialize(self):
        from game.combat.hit_stop import HitStopController
        ctrl = HitStopController()
        ctrl.request(frames=5)
        data = ctrl.serialize()
        ctrl2 = HitStopController()
        ctrl2.deserialize(data)
        assert ctrl2.remaining_frames == 5
        assert ctrl2.is_active

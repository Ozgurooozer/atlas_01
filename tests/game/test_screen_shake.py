"""
Screen Shake Tests.

Camera shake system for combat impact feedback.
Layer 4 (Game/Camera), depends on core.object, core.vec.

TDD: RED phase.
"""
from __future__ import annotations
import pytest
from core.vec import Vec2


class TestScreenShakeBasics:
    """Core ScreenShake behavior."""

    def test_create_default(self):
        from game.camera.screen_shake import ScreenShake
        shake = ScreenShake()
        assert not shake.is_active
        assert shake.offset == Vec2(0, 0)

    def test_trigger_starts_shake(self):
        from game.camera.screen_shake import ScreenShake
        shake = ScreenShake()
        shake.trigger(amplitude=3.0, duration=0.2)
        assert shake.is_active

    def test_trigger_with_direction(self):
        from game.camera.screen_shake import ScreenShake
        shake = ScreenShake()
        shake.trigger(amplitude=3.0, duration=0.2, direction=Vec2(1, 0))
        assert shake.is_active

    def test_trigger_stores_params(self):
        from game.camera.screen_shake import ScreenShake
        shake = ScreenShake()
        shake.trigger(amplitude=5.0, frequency=20.0, duration=0.3)
        assert shake.is_active

    def test_offset_returns_vec2(self):
        from game.camera.screen_shake import ScreenShake
        shake = ScreenShake()
        offset = shake.offset
        assert isinstance(offset, Vec2)
        assert offset.x == 0
        assert offset.y == 0


class TestScreenShakeTick:
    """Tick behavior over time."""

    def test_tick_updates_elapsed(self):
        from game.camera.screen_shake import ScreenShake
        shake = ScreenShake()
        shake.trigger(amplitude=3.0, duration=0.3)
        shake.tick(dt=0.1)
        assert shake.is_active

    def test_tick_reaches_end_deactivates(self):
        from game.camera.screen_shake import ScreenShake
        shake = ScreenShake()
        shake.trigger(amplitude=3.0, duration=0.2)
        shake.tick(dt=0.1)
        shake.tick(dt=0.1)
        assert not shake.is_active

    def test_tick_when_inactive_no_error(self):
        from game.camera.screen_shake import ScreenShake
        shake = ScreenShake()
        shake.tick(dt=0.1)
        assert not shake.is_active

    def test_tick_generates_nonzero_offset_when_active(self):
        from game.camera.screen_shake import ScreenShake
        shake = ScreenShake()
        shake.trigger(amplitude=10.0, frequency=30.0, duration=0.5)
        shake.tick(dt=0.016)
        offset = shake.offset
        assert isinstance(offset, Vec2)

    def test_offset_zero_when_inactive(self):
        from game.camera.screen_shake import ScreenShake
        shake = ScreenShake()
        shake.trigger(amplitude=3.0, duration=0.2)
        shake.tick(dt=0.2)
        assert not shake.is_active
        assert shake.offset == Vec2(0, 0)

    def test_amplitude_decay(self):
        from game.camera.screen_shake import ScreenShake
        shake = ScreenShake()
        shake.trigger(amplitude=10.0, duration=1.0)
        offset_early = shake.offset
        shake.tick(dt=0.5)
        offset_late = shake.offset
        assert isinstance(offset_early, Vec2)
        assert isinstance(offset_late, Vec2)


class TestScreenShakePresets:
    """Combat hit presets."""

    def test_preset_hit(self):
        from game.camera.screen_shake import ScreenShake
        shake = ScreenShake()
        shake.trigger_hit()
        assert shake.is_active

    def test_preset_heavy_hit(self):
        from game.camera.screen_shake import ScreenShake
        shake = ScreenShake()
        shake.trigger_heavy()
        assert shake.is_active

    def test_preset_explosion(self):
        from game.camera.screen_shake import ScreenShake
        shake = ScreenShake()
        shake.trigger_explosion()
        assert shake.is_active


class TestScreenShakeCancel:
    """Cancel behavior."""

    def test_cancel_deactivates(self):
        from game.camera.screen_shake import ScreenShake
        shake = ScreenShake()
        shake.trigger(amplitude=3.0, duration=1.0)
        shake.cancel()
        assert not shake.is_active

    def test_cancel_clears_offset(self):
        from game.camera.screen_shake import ScreenShake
        shake = ScreenShake()
        shake.trigger(amplitude=10.0, duration=1.0)
        shake.cancel()
        assert shake.offset == Vec2(0, 0)


class TestScreenShakeSerialize:
    """Serialization support."""

    def test_serialize_empty(self):
        from game.camera.screen_shake import ScreenShake
        shake = ScreenShake()
        data = shake.serialize()
        assert "amplitude" in data
        assert "duration" in data

    def test_serialize_with_state(self):
        from game.camera.screen_shake import ScreenShake
        shake = ScreenShake()
        shake.trigger(amplitude=5.0, duration=0.5)
        data = shake.serialize()
        assert data["amplitude"] == 5.0

    def test_deserialize(self):
        from game.camera.screen_shake import ScreenShake
        shake = ScreenShake()
        shake.trigger(amplitude=5.0, duration=0.5)
        data = shake.serialize()
        shake2 = ScreenShake()
        shake2.deserialize(data)
        assert shake2.is_active

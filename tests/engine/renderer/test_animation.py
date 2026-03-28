"""Tests for animation system.

Layer: 2 (Engine)
"""

from __future__ import annotations

import pytest


class TestAnimationFrame:
    """Test AnimationFrame class."""

    def test_frame_creation(self):
        """Test basic frame creation."""
        from engine.renderer.animation import AnimationFrame
        from engine.renderer.texture import UVRegion

        uv = UVRegion(0, 0, 1, 1)
        frame = AnimationFrame(uv=uv, duration=0.1)

        assert frame.uv == uv
        assert frame.duration == 0.1

    def test_frame_default_duration(self):
        """Test frame has default duration."""
        from engine.renderer.animation import AnimationFrame
        from engine.renderer.texture import UVRegion

        uv = UVRegion(0, 0, 1, 1)
        frame = AnimationFrame(uv=uv)

        assert frame.duration > 0

    def test_frame_invalid_duration(self):
        """Test frame rejects invalid duration."""
        from engine.renderer.animation import AnimationFrame
        from engine.renderer.texture import UVRegion

        uv = UVRegion(0, 0, 1, 1)
        with pytest.raises(ValueError):
            AnimationFrame(uv=uv, duration=0)


class TestAnimation:
    """Test Animation class."""

    def test_animation_creation(self):
        """Test basic animation creation."""
        from engine.renderer.animation import Animation, AnimationFrame
        from engine.renderer.texture import UVRegion

        frames = [
            AnimationFrame(UVRegion(0, 0, 0.5, 0.5), 0.1),
            AnimationFrame(UVRegion(0.5, 0, 0.5, 0.5), 0.1),
        ]
        anim = Animation(name="walk", frames=frames)

        assert anim.name == "walk"
        assert anim.frame_count == 2

    def test_animation_modes(self):
        """Test animation has correct modes."""
        from engine.renderer.animation import Animation

        assert Animation.LOOP == "loop"
        assert Animation.ONE_SHOT == "one_shot"
        assert Animation.PING_PONG == "ping_pong"

    def test_animation_empty_frames_error(self):
        """Test animation rejects empty frames."""
        from engine.renderer.animation import Animation

        with pytest.raises(ValueError):
            Animation(name="empty", frames=[])


class TestAnimationPlayer:
    """Test AnimationPlayer class."""

    def test_player_creation(self):
        """Test basic player creation."""
        from engine.renderer.animation import AnimationPlayer

        player = AnimationPlayer()

        assert not player.is_playing
        assert not player.is_finished
        assert player.current_frame_index == 0

    def test_player_play(self):
        """Test player starts playing."""
        from engine.renderer.animation import AnimationPlayer, Animation, AnimationFrame
        from engine.renderer.texture import UVRegion

        player = AnimationPlayer()
        frames = [AnimationFrame(UVRegion(0, 0, 1, 1), 0.1)]
        anim = Animation(name="test", frames=frames)

        player.play(anim)

        assert player.is_playing

    def test_player_pause_resume(self):
        """Test player pause and resume."""
        from engine.renderer.animation import AnimationPlayer, Animation, AnimationFrame
        from engine.renderer.texture import UVRegion

        player = AnimationPlayer()
        frames = [AnimationFrame(UVRegion(0, 0, 1, 1), 0.1)]
        anim = Animation(name="test", frames=frames)

        player.play(anim)
        player.pause()
        assert not player.is_playing

        player.resume()
        assert player.is_playing

    def test_player_update_advances_frame(self):
        """Test player update advances frame."""
        from engine.renderer.animation import AnimationPlayer, Animation, AnimationFrame
        from engine.renderer.texture import UVRegion

        player = AnimationPlayer()
        frames = [
            AnimationFrame(UVRegion(0, 0, 0.5, 0.5), 0.1),
            AnimationFrame(UVRegion(0.5, 0, 0.5, 0.5), 0.1),
        ]
        anim = Animation(name="test", frames=frames)

        player.play(anim)
        player.update(0.15)

        assert player.current_frame_index == 1

    def test_player_loop_mode(self):
        """Test loop mode wraps around."""
        from engine.renderer.animation import AnimationPlayer, Animation, AnimationFrame
        from engine.renderer.texture import UVRegion

        player = AnimationPlayer()
        frames = [
            AnimationFrame(UVRegion(0, 0, 0.5, 0.5), 0.1),
            AnimationFrame(UVRegion(0.5, 0, 0.5, 0.5), 0.1),
        ]
        anim = Animation(name="test", frames=frames, mode=Animation.LOOP)

        player.play(anim)
        player.update(0.15)
        player.update(0.15)

        assert player.current_frame_index == 0  # Looped back

    def test_player_speed_control(self):
        """Test speed multiplier."""
        from engine.renderer.animation import AnimationPlayer

        player = AnimationPlayer()
        player.speed = 2.0

        assert player.speed == 2.0

    def test_player_one_shot_finished(self):
        """Test one-shot finishes correctly."""
        from engine.renderer.animation import AnimationPlayer, Animation, AnimationFrame
        from engine.renderer.texture import UVRegion

        player = AnimationPlayer()
        frames = [
            AnimationFrame(UVRegion(0, 0, 0.5, 0.5), 0.1),
            AnimationFrame(UVRegion(0.5, 0, 0.5, 0.5), 0.1),
        ]
        anim = Animation(name="test", frames=frames, mode=Animation.ONE_SHOT)

        player.play(anim)
        player.update(0.15)
        player.update(0.15)

        assert player.is_finished
        assert not player.is_playing

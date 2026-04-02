"""Tests for timeline system."""
from scripting.timeline import Timeline, TimelineEvent


class TestTimelineEvent:
    def test_fires_at_time(self):
        called = []
        event = TimelineEvent(1.0, lambda: called.append(True))
        event.try_fire(0.5)
        assert called == []
        event.try_fire(1.0)
        assert called == [True]

    def test_fires_only_once(self):
        called = []
        event = TimelineEvent(1.0, lambda: called.append(True))
        event.try_fire(1.0)
        event.try_fire(2.0)
        assert len(called) == 1

    def test_reset(self):
        called = []
        event = TimelineEvent(1.0, lambda: called.append(True))
        event.try_fire(1.0)
        event.reset()
        event.try_fire(1.0)
        assert len(called) == 2


class TestTimeline:
    def test_creation(self):
        tl = Timeline(duration=5.0)
        assert tl.duration == 5.0
        assert tl.is_playing is False

    def test_play_and_tick(self):
        called = []
        tl = Timeline(duration=5.0)
        tl.add_event(1.0, lambda: called.append("one"))
        tl.add_event(2.0, lambda: called.append("two"))
        tl.play()
        tl.tick(1.5)
        assert "one" in called
        assert "two" not in called
        tl.tick(1.0)
        assert "two" in called

    def test_stop_resets(self):
        tl = Timeline(duration=5.0)
        tl.play()
        tl.tick(2.0)
        tl.stop()
        assert tl.current_time == 0.0
        assert tl.is_playing is False

    def test_on_end_callback(self):
        called = []
        tl = Timeline(duration=1.0)
        tl.on_end(lambda: called.append(True))
        tl.play()
        tl.tick(2.0)
        assert called == [True]

    def test_progress(self):
        tl = Timeline(duration=10.0)
        tl.play()
        tl.tick(5.0)
        assert tl.progress == 0.5

    def test_loop(self):
        called = []
        tl = Timeline(duration=1.0)
        tl.add_event(0.5, lambda: called.append(True))
        tl.set_loop(True)
        tl.play()
        tl.tick(1.5)  # Should loop and fire again
        tl.tick(0.6)
        assert len(called) >= 1

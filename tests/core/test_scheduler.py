"""
Tests for core/scheduler.py - Time-based callback scheduler.

TDD Phase: RED - These tests are written BEFORE implementation.

Scheduler provides:
- call_later(delay, callback): Execute callback after delay seconds
- call_every(interval, callback): Execute callback every interval seconds
- cancel(handle): Cancel a scheduled callback
- tick(dt): Process pending callbacks (call from game loop)

Layer: 1 (Core)
Dependencies: None (stdlib only)
"""

from __future__ import annotations

from typing import List


class TestSchedulerBasics:
    """Basic scheduler functionality tests."""

    def test_scheduler_exists(self):
        """Scheduler class should exist."""
        from core.scheduler import Scheduler
        assert Scheduler is not None

    def test_scheduler_has_call_later(self):
        """Scheduler should have call_later method."""
        from core.scheduler import Scheduler
        scheduler = Scheduler()
        assert hasattr(scheduler, 'call_later')
        assert callable(scheduler.call_later)

    def test_scheduler_has_call_every(self):
        """Scheduler should have call_every method."""
        from core.scheduler import Scheduler
        scheduler = Scheduler()
        assert hasattr(scheduler, 'call_every')
        assert callable(scheduler.call_every)

    def test_scheduler_has_cancel(self):
        """Scheduler should have cancel method."""
        from core.scheduler import Scheduler
        scheduler = Scheduler()
        assert hasattr(scheduler, 'cancel')
        assert callable(scheduler.cancel)

    def test_scheduler_has_tick(self):
        """Scheduler should have tick method."""
        from core.scheduler import Scheduler
        scheduler = Scheduler()
        assert hasattr(scheduler, 'tick')
        assert callable(scheduler.tick)

    def test_call_later_returns_handle(self):
        """call_later should return a handle (int)."""
        from core.scheduler import Scheduler
        scheduler = Scheduler()
        handle = scheduler.call_later(1.0, lambda: None)
        assert isinstance(handle, int)

    def test_call_every_returns_handle(self):
        """call_every should return a handle (int)."""
        from core.scheduler import Scheduler
        scheduler = Scheduler()
        handle = scheduler.call_every(1.0, lambda: None)
        assert isinstance(handle, int)

    def test_scheduler_handles_are_unique(self):
        """Each scheduled callback should get a unique handle."""
        from core.scheduler import Scheduler
        scheduler = Scheduler()
        handle1 = scheduler.call_later(1.0, lambda: None)
        handle2 = scheduler.call_later(2.0, lambda: None)
        handle3 = scheduler.call_every(0.5, lambda: None)
        assert handle1 != handle2
        assert handle2 != handle3
        assert handle1 != handle3


class TestSchedulerDelayed:
    """Tests for delayed callbacks (call_later)."""

    def test_call_later_executes_after_delay(self):
        """Callback should execute after specified delay."""
        from core.scheduler import Scheduler
        scheduler = Scheduler()
        executed: List[bool] = []

        scheduler.call_later(0.5, lambda: executed.append(True))

        # Before delay
        scheduler.tick(0.25)
        assert len(executed) == 0

        # At delay
        scheduler.tick(0.25)
        assert len(executed) == 1

    def test_call_later_executes_once(self):
        """Delayed callback should only execute once."""
        from core.scheduler import Scheduler
        scheduler = Scheduler()
        count: List[int] = [0]

        scheduler.call_later(0.5, lambda: count.__setitem__(0, count[0] + 1))

        # Execute
        scheduler.tick(0.5)
        assert count[0] == 1

        # Should not execute again
        scheduler.tick(0.5)
        assert count[0] == 1

    def test_call_later_with_zero_delay(self):
        """Zero delay should execute on next tick."""
        from core.scheduler import Scheduler
        scheduler = Scheduler()
        executed: List[bool] = []

        scheduler.call_later(0.0, lambda: executed.append(True))
        scheduler.tick(0.0)

        assert len(executed) == 1

    def test_call_later_with_negative_delay(self):
        """Negative delay should execute immediately."""
        from core.scheduler import Scheduler
        scheduler = Scheduler()
        executed: List[bool] = []

        scheduler.call_later(-1.0, lambda: executed.append(True))
        scheduler.tick(0.0)

        assert len(executed) == 1

    def test_multiple_call_later_different_delays(self):
        """Multiple delayed callbacks should execute in order."""
        from core.scheduler import Scheduler
        scheduler = Scheduler()
        order: List[int] = []

        scheduler.call_later(1.0, lambda: order.append(2))
        scheduler.call_later(0.5, lambda: order.append(1))
        scheduler.call_later(1.5, lambda: order.append(3))

        scheduler.tick(0.5)  # 0.5s elapsed
        assert order == [1]

        scheduler.tick(0.5)  # 1.0s elapsed
        assert order == [1, 2]

        scheduler.tick(0.5)  # 1.5s elapsed
        assert order == [1, 2, 3]

    def test_call_later_removed_after_execution(self):
        """Executed callbacks should be removed from scheduler."""
        from core.scheduler import Scheduler
        scheduler = Scheduler()
        count: List[int] = [0]

        scheduler.call_later(0.1, lambda: count.__setitem__(0, count[0] + 1))

        # Execute
        scheduler.tick(0.1)
        assert count[0] == 1

        # Multiple more ticks should not re-execute
        scheduler.tick(0.1)
        scheduler.tick(0.1)
        scheduler.tick(0.1)
        assert count[0] == 1


class TestSchedulerRepeated:
    """Tests for repeated callbacks (call_every)."""

    def test_call_every_executes_at_interval(self):
        """Callback should execute at specified interval."""
        from core.scheduler import Scheduler
        scheduler = Scheduler()
        count: List[int] = [0]

        scheduler.call_every(0.5, lambda: count.__setitem__(0, count[0] + 1))

        scheduler.tick(0.5)
        assert count[0] == 1

        scheduler.tick(0.5)
        assert count[0] == 2

        scheduler.tick(0.5)
        assert count[0] == 3

    def test_call_every_continues_until_cancelled(self):
        """Repeated callback should continue until cancelled."""
        from core.scheduler import Scheduler
        scheduler = Scheduler()
        count: List[int] = [0]

        handle = scheduler.call_every(0.25, lambda: count.__setitem__(0, count[0] + 1))

        scheduler.tick(0.25)
        scheduler.tick(0.25)
        assert count[0] == 2

        scheduler.cancel(handle)

        scheduler.tick(0.25)
        scheduler.tick(0.25)
        assert count[0] == 2  # No more executions

    def test_call_every_accumulates_time(self):
        """Scheduler should accumulate time for partial ticks."""
        from core.scheduler import Scheduler
        scheduler = Scheduler()
        count: List[int] = [0]

        scheduler.call_every(0.3, lambda: count.__setitem__(0, count[0] + 1))

        # 0.1 + 0.1 + 0.1 = 0.3, should execute once
        scheduler.tick(0.1)
        scheduler.tick(0.1)
        scheduler.tick(0.1)
        assert count[0] == 1

    def test_call_every_handles_large_tick(self):
        """Large tick should execute callback multiple times."""
        from core.scheduler import Scheduler
        scheduler = Scheduler()
        count: List[int] = [0]

        scheduler.call_every(0.2, lambda: count.__setitem__(0, count[0] + 1))

        # 1.0 second tick should execute 5 times
        scheduler.tick(1.0)
        assert count[0] == 5

    def test_call_every_zero_interval(self):
        """Zero interval should execute every tick."""
        from core.scheduler import Scheduler
        scheduler = Scheduler()
        count: List[int] = [0]

        scheduler.call_every(0.0, lambda: count.__setitem__(0, count[0] + 1))

        scheduler.tick(0.1)
        assert count[0] == 1

        scheduler.tick(0.1)
        assert count[0] == 2

    def test_call_every_with_callback_return_value(self):
        """Callback return value should be ignored."""
        from core.scheduler import Scheduler
        scheduler = Scheduler()
        count: List[int] = [0]

        # Callback returns a value, should not cause error
        def callback() -> str:
            count.__setitem__(0, count[0] + 1)
            return "result"

        scheduler.call_every(0.1, callback)
        scheduler.tick(0.1)

        assert count[0] == 1

    def test_multiple_call_every_different_intervals(self):
        """Multiple repeated callbacks with different intervals."""
        from core.scheduler import Scheduler
        scheduler = Scheduler()
        results: List[str] = []

        scheduler.call_every(0.2, lambda: results.append('A'))
        scheduler.call_every(0.3, lambda: results.append('B'))

        # Use values that divide evenly to avoid floating point issues
        # 0.8 / 0.2 = 4, 0.8 / 0.3 = 2.67 -> 2
        scheduler.tick(0.8)

        assert results.count('A') == 4
        assert results.count('B') == 2


class TestSchedulerCancel:
    """Tests for canceling scheduled callbacks."""

    def test_cancel_delayed_callback(self):
        """Should be able to cancel a delayed callback."""
        from core.scheduler import Scheduler
        scheduler = Scheduler()
        executed: List[bool] = []

        handle = scheduler.call_later(0.5, lambda: executed.append(True))
        scheduler.cancel(handle)
        scheduler.tick(0.5)

        assert len(executed) == 0

    def test_cancel_repeated_callback(self):
        """Should be able to cancel a repeated callback."""
        from core.scheduler import Scheduler
        scheduler = Scheduler()
        count: List[int] = [0]

        handle = scheduler.call_every(0.1, lambda: count.__setitem__(0, count[0] + 1))
        scheduler.tick(0.1)
        assert count[0] == 1

        scheduler.cancel(handle)
        scheduler.tick(0.1)
        assert count[0] == 1  # No more executions

    def test_cancel_returns_true_if_found(self):
        """cancel should return True if callback was found."""
        from core.scheduler import Scheduler
        scheduler = Scheduler()

        handle = scheduler.call_later(1.0, lambda: None)
        result = scheduler.cancel(handle)

        assert result is True

    def test_cancel_returns_false_if_not_found(self):
        """cancel should return False if callback was not found."""
        from core.scheduler import Scheduler
        scheduler = Scheduler()

        result = scheduler.cancel(999)  # Non-existent handle

        assert result is False

    def test_cancel_already_executed(self):
        """Canceling an already-executed callback should return False."""
        from core.scheduler import Scheduler
        scheduler = Scheduler()

        handle = scheduler.call_later(0.1, lambda: None)
        scheduler.tick(0.1)  # Execute

        result = scheduler.cancel(handle)
        assert result is False


class TestSchedulerEdge:
    """Edge case tests."""

    def test_tick_with_zero_dt(self):
        """tick(0.0) should not cause issues."""
        from core.scheduler import Scheduler
        scheduler = Scheduler()
        count: List[int] = [0]

        scheduler.call_every(0.1, lambda: count.__setitem__(0, count[0] + 1))
        scheduler.tick(0.0)
        scheduler.tick(0.0)

        assert count[0] == 0

    def test_callback_raises_exception(self):
        """Exception in callback should not crash scheduler."""
        from core.scheduler import Scheduler
        scheduler = Scheduler()
        count: List[int] = [0]

        def bad_callback():
            raise ValueError("Test exception")

        def good_callback():
            count.__setitem__(0, count[0] + 1)

        scheduler.call_later(0.1, bad_callback)
        scheduler.call_later(0.1, good_callback)

        # Should not raise, good_callback should still execute
        scheduler.tick(0.1)

        assert count[0] == 1

    def test_callback_schedules_new_callback(self):
        """Callback should be able to schedule new callbacks."""
        from core.scheduler import Scheduler
        scheduler = Scheduler()
        order: List[int] = []

        def schedule_another():
            order.append(1)
            scheduler.call_later(0.1, lambda: order.append(2))

        scheduler.call_later(0.1, schedule_another)

        scheduler.tick(0.1)
        assert order == [1]

        scheduler.tick(0.1)
        assert order == [1, 2]

    def test_scheduler_clear_all(self):
        """Should be able to clear all scheduled callbacks."""
        from core.scheduler import Scheduler
        scheduler = Scheduler()
        executed: List[int] = []

        scheduler.call_later(0.1, lambda: executed.append(1))
        scheduler.call_later(0.2, lambda: executed.append(2))
        scheduler.call_every(0.1, lambda: executed.append(3))

        scheduler.clear()
        scheduler.tick(0.3)

        assert len(executed) == 0


class TestSchedulerReflection:
    """Tests for scheduler reflection/serialization support."""

    def test_scheduler_has_pending_count(self):
        """Scheduler should track pending callback count."""
        from core.scheduler import Scheduler
        scheduler = Scheduler()

        assert scheduler.pending_count == 0

        scheduler.call_later(1.0, lambda: None)
        assert scheduler.pending_count == 1

        scheduler.call_every(0.5, lambda: None)
        assert scheduler.pending_count == 2

    def test_scheduler_has_call_later_count(self):
        """Scheduler should track call_later count."""
        from core.scheduler import Scheduler
        scheduler = Scheduler()

        scheduler.call_later(1.0, lambda: None)
        scheduler.call_later(2.0, lambda: None)
        scheduler.call_every(0.5, lambda: None)

        assert scheduler.delayed_count == 2

    def test_scheduler_has_repeating_count(self):
        """Scheduler should track call_every count."""
        from core.scheduler import Scheduler
        scheduler = Scheduler()

        scheduler.call_later(1.0, lambda: None)
        scheduler.call_every(0.5, lambda: None)
        scheduler.call_every(1.0, lambda: None)

        assert scheduler.repeating_count == 2

"""
EventBus System Tests.

Tests for publish/subscribe event system.
EventBus enables loose coupling between engine components.
"""

import pytest


class TestEventBusCreation:
    """Test EventBus creation."""

    def test_eventbus_creation(self):
        """EventBus should be creatable."""
        from core.eventbus import EventBus
        bus = EventBus()
        assert bus is not None

    def test_eventbus_singleton(self):
        """EventBus should be accessible as singleton."""
        from core.eventbus import event_bus
        assert event_bus is not None

    def test_eventbus_singleton_same_instance(self):
        """EventBus singleton should return same instance."""
        from core.eventbus import event_bus, get_event_bus
        bus1 = event_bus
        bus2 = get_event_bus()
        assert bus1 is bus2


class TestEventBusSubscribe:
    """Test EventBus subscription."""

    def test_subscribe(self):
        """Should be able to subscribe to an event."""
        from core.eventbus import EventBus
        bus = EventBus()

        called = []

        def handler(data):
            called.append(data)

        bus.subscribe("test.event", handler)
        bus.publish("test.event", {"value": 42})
        assert len(called) == 1
        assert called[0] == {"value": 42}

    def test_multiple_subscribers(self):
        """Multiple handlers should receive same event."""
        from core.eventbus import EventBus
        bus = EventBus()

        calls = []

        def handler1(data):
            calls.append(("h1", data))

        def handler2(data):
            calls.append(("h2", data))

        bus.subscribe("test.event", handler1)
        bus.subscribe("test.event", handler2)
        bus.publish("test.event", {"val": 1})

        assert len(calls) == 2
        assert ("h1", {"val": 1}) in calls
        assert ("h2", {"val": 1}) in calls

    def test_unsubscribe(self):
        """Should be able to unsubscribe."""
        from core.eventbus import EventBus
        bus = EventBus()

        calls = []

        def handler(data):
            calls.append(data)

        bus.subscribe("test.event", handler)
        bus.publish("test.event", {})
        assert len(calls) == 1

        bus.unsubscribe("test.event", handler)
        bus.publish("test.event", {})
        assert len(calls) == 1  # Still 1, not 2


class TestEventBusPublish:
    """Test EventBus publishing."""

    def test_publish_no_subscribers(self):
        """Publishing with no subscribers should not raise."""
        from core.eventbus import EventBus
        bus = EventBus()
        bus.publish("nonexistent.event", {"data": "value"})  # Should not raise

    def test_publish_with_data(self):
        """Published data should be received by handler."""
        from core.eventbus import EventBus
        bus = EventBus()

        received = []

        def handler(data):
            received.append(data)

        bus.subscribe("test.event", handler)
        bus.publish("test.event", {"key": "value", "number": 123})

        assert received[0] == {"key": "value", "number": 123}

    def test_publish_returns_false_if_no_handlers(self):
        """Publish should return False if no handlers."""
        from core.eventbus import EventBus
        bus = EventBus()
        result = bus.publish("nonexistent.event", {})
        assert result is False

    def test_publish_returns_true_if_handled(self):
        """Publish should return True if handled."""
        from core.eventbus import EventBus
        bus = EventBus()

        def handler(data):
            pass

        bus.subscribe("test.event", handler)
        result = bus.publish("test.event", {})
        assert result is True


class TestEventBusClear:
    """Test EventBus clear functionality."""

    def test_clear_all(self):
        """Clear should remove all subscriptions."""
        from core.eventbus import EventBus
        bus = EventBus()

        calls = []

        def handler(data):
            calls.append(data)

        bus.subscribe("test.event", handler)
        bus.clear()
        bus.publish("test.event", {})

        assert len(calls) == 0

    def test_clear_specific_event(self):
        """Clear should remove specific event subscriptions."""
        from core.eventbus import EventBus
        bus = EventBus()

        calls1 = []
        calls2 = []

        def handler1(data):
            calls1.append(data)

        def handler2(data):
            calls2.append(data)

        bus.subscribe("event.one", handler1)
        bus.subscribe("event.two", handler2)

        bus.clear("event.one")

        bus.publish("event.one", {})
        bus.publish("event.two", {})

        assert len(calls1) == 0
        assert len(calls2) == 1

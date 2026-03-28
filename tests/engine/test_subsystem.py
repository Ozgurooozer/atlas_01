"""
ISubsystem Interface Tests.

Tests for the subsystem interface that all engine subsystems must implement.
Renderer, Physics, Audio, Input, Asset - all implement ISubsystem.
"""

import pytest


class TestISubsystemInterface:
    """Test ISubsystem interface contract."""

    def test_isubsystem_is_abstract(self):
        """ISubsystem must be an abstract class."""
        from engine.subsystem import ISubsystem
        from abc import ABC
        assert issubclass(ISubsystem, ABC)

    def test_isubsystem_has_name_property(self):
        """ISubsystem must have name property."""
        from engine.subsystem import ISubsystem
        assert hasattr(ISubsystem, 'name')
        prop = getattr(ISubsystem, 'name')
        assert getattr(prop.fget, '__isabstractmethod__', False)

    def test_isubsystem_has_initialize_method(self):
        """ISubsystem must have initialize abstract method."""
        from engine.subsystem import ISubsystem
        assert hasattr(ISubsystem, 'initialize')
        method = getattr(ISubsystem, 'initialize')
        assert getattr(method, '__isabstractmethod__', False)

    def test_isubsystem_has_tick_method(self):
        """ISubsystem must have tick abstract method."""
        from engine.subsystem import ISubsystem
        assert hasattr(ISubsystem, 'tick')
        method = getattr(ISubsystem, 'tick')
        assert getattr(method, '__isabstractmethod__', False)

    def test_isubsystem_has_shutdown_method(self):
        """ISubsystem must have shutdown abstract method."""
        from engine.subsystem import ISubsystem
        assert hasattr(ISubsystem, 'shutdown')
        method = getattr(ISubsystem, 'shutdown')
        assert getattr(method, '__isabstractmethod__', False)

    def test_isubsystem_cannot_be_instantiated(self):
        """ISubsystem cannot be instantiated directly."""
        from engine.subsystem import ISubsystem
        with pytest.raises(TypeError):
            ISubsystem()


class TestSubsystemImplementation:
    """Test a concrete implementation of ISubsystem."""

    def test_concrete_subsystem_creation(self):
        """A concrete subsystem should be creatable."""
        from engine.subsystem import ISubsystem

        class MockSubsystem(ISubsystem):
            def __init__(self):
                self._initialized = False
                self._tick_count = 0
                self._shutdown = False

            @property
            def name(self) -> str:
                return "mock"

            def initialize(self, engine: "Engine") -> None:
                self._initialized = True

            def tick(self, dt: float) -> None:
                self._tick_count += 1

            def shutdown(self) -> None:
                self._shutdown = True

        subsystem = MockSubsystem()
        assert subsystem is not None
        assert subsystem.name == "mock"
        assert subsystem._initialized is False
        assert subsystem._tick_count == 0
        assert subsystem._shutdown is False

    def test_concrete_subsystem_initialize(self):
        """Concrete subsystem initialize should work."""
        from engine.subsystem import ISubsystem

        class MockSubsystem(ISubsystem):
            def __init__(self):
                self._initialized = False

            @property
            def name(self) -> str:
                return "mock"

            def initialize(self, engine: "Engine") -> None:
                self._initialized = True

            def tick(self, dt: float) -> None:
                pass

            def shutdown(self) -> None:
                pass

        subsystem = MockSubsystem()
        subsystem.initialize(None)
        assert subsystem._initialized is True

    def test_concrete_subsystem_tick(self):
        """Concrete subsystem tick should work."""
        from engine.subsystem import ISubsystem

        class MockSubsystem(ISubsystem):
            def __init__(self):
                self._tick_count = 0

            @property
            def name(self) -> str:
                return "mock"

            def initialize(self, engine: "Engine") -> None:
                pass

            def tick(self, dt: float) -> None:
                self._tick_count += 1

            def shutdown(self) -> None:
                pass

        subsystem = MockSubsystem()
        subsystem.tick(0.016)
        subsystem.tick(0.016)
        assert subsystem._tick_count == 2

    def test_concrete_subsystem_shutdown(self):
        """Concrete subsystem shutdown should work."""
        from engine.subsystem import ISubsystem

        class MockSubsystem(ISubsystem):
            def __init__(self):
                self._shutdown = False

            @property
            def name(self) -> str:
                return "mock"

            def initialize(self, engine: "Engine") -> None:
                pass

            def tick(self, dt: float) -> None:
                pass

            def shutdown(self) -> None:
                self._shutdown = True

        subsystem = MockSubsystem()
        subsystem.shutdown()
        assert subsystem._shutdown is True

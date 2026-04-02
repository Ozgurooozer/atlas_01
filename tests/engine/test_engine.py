"""
Engine Class Tests.

Tests for the Engine class - the main subsystem manager.
Engine manages lifecycle of all subsystems (Renderer, Physics, etc).
"""



class TestEngineCreation:
    """Test Engine creation."""

    def test_engine_creation(self):
        """Engine should be creatable."""
        from engine.engine import Engine
        engine = Engine()
        assert engine is not None

    def test_engine_has_subsystems_dict(self):
        """Engine should have subsystems dictionary."""
        from engine.engine import Engine
        engine = Engine()
        assert hasattr(engine, '_subsystems')

    def test_engine_empty_initially(self):
        """Engine should have no subsystems initially."""
        from engine.engine import Engine
        engine = Engine()
        assert len(engine._subsystems) == 0


class TestEngineRegisterSubsystem:
    """Test Engine subsystem registration."""

    def test_register_subsystem(self):
        """Should be able to register a subsystem."""
        from engine.engine import Engine
        from engine.subsystem import ISubsystem

        class MockSubsystem(ISubsystem):
            @property
            def name(self) -> str:
                return "mock"

            def initialize(self, engine: "Engine") -> None:
                pass

            def tick(self, dt: float) -> None:
                pass

            def shutdown(self) -> None:
                pass

        engine = Engine()
        subsystem = MockSubsystem()
        engine.register_subsystem(subsystem)

        assert "mock" in engine._subsystems
        assert engine._subsystems["mock"] is subsystem

    def test_get_subsystem(self):
        """Should be able to get a registered subsystem."""
        from engine.engine import Engine
        from engine.subsystem import ISubsystem

        class MockSubsystem(ISubsystem):
            @property
            def name(self) -> str:
                return "mock"

            def initialize(self, engine: "Engine") -> None:
                pass

            def tick(self, dt: float) -> None:
                pass

            def shutdown(self) -> None:
                pass

        engine = Engine()
        subsystem = MockSubsystem()
        engine.register_subsystem(subsystem)

        retrieved = engine.get_subsystem("mock")
        assert retrieved is subsystem

    def test_get_nonexistent_subsystem_returns_none(self):
        """Getting nonexistent subsystem should return None."""
        from engine.engine import Engine
        engine = Engine()
        result = engine.get_subsystem("nonexistent")
        assert result is None


class TestEngineLifecycle:
    """Test Engine lifecycle methods."""

    def test_initialize_calls_subsystem_initialize(self):
        """Engine.initialize should call initialize on all subsystems."""
        from engine.engine import Engine
        from engine.subsystem import ISubsystem

        class MockSubsystem(ISubsystem):
            def __init__(self):
                self.initialized = False

            @property
            def name(self) -> str:
                return "mock"

            def initialize(self, engine: "Engine") -> None:
                self.initialized = True

            def tick(self, dt: float) -> None:
                pass

            def shutdown(self) -> None:
                pass

        engine = Engine()
        subsystem = MockSubsystem()
        engine.register_subsystem(subsystem)
        engine.initialize()

        assert subsystem.initialized is True

    def test_tick_calls_subsystem_tick(self):
        """Engine.tick should call tick on all subsystems."""
        from engine.engine import Engine
        from engine.subsystem import ISubsystem

        class MockSubsystem(ISubsystem):
            def __init__(self):
                self.tick_count = 0

            @property
            def name(self) -> str:
                return "mock"

            def initialize(self, engine: "Engine") -> None:
                pass

            def tick(self, dt: float) -> None:
                self.tick_count += 1

            def shutdown(self) -> None:
                pass

        engine = Engine()
        subsystem = MockSubsystem()
        engine.register_subsystem(subsystem)

        engine.tick(0.016)
        engine.tick(0.016)
        engine.tick(0.016)

        assert subsystem.tick_count == 3

    def test_shutdown_calls_subsystem_shutdown(self):
        """Engine.shutdown should call shutdown on all subsystems."""
        from engine.engine import Engine
        from engine.subsystem import ISubsystem

        class MockSubsystem(ISubsystem):
            def __init__(self):
                self.shutdown_called = False

            @property
            def name(self) -> str:
                return "mock"

            def initialize(self, engine: "Engine") -> None:
                pass

            def tick(self, dt: float) -> None:
                pass

            def shutdown(self) -> None:
                self.shutdown_called = True

        engine = Engine()
        subsystem = MockSubsystem()
        engine.register_subsystem(subsystem)
        engine.shutdown()

        assert subsystem.shutdown_called is True


class TestEngineMultipleSubsystems:
    """Test Engine with multiple subsystems."""

    def test_register_multiple_subsystems(self):
        """Engine should handle multiple subsystems."""
        from engine.engine import Engine
        from engine.subsystem import ISubsystem

        class SubA(ISubsystem):
            @property
            def name(self) -> str:
                return "sub_a"

            def initialize(self, engine: "Engine") -> None:
                pass

            def tick(self, dt: float) -> None:
                pass

            def shutdown(self) -> None:
                pass

        class SubB(ISubsystem):
            @property
            def name(self) -> str:
                return "sub_b"

            def initialize(self, engine: "Engine") -> None:
                pass

            def tick(self, dt: float) -> None:
                pass

            def shutdown(self) -> None:
                pass

        engine = Engine()
        engine.register_subsystem(SubA())
        engine.register_subsystem(SubB())

        assert len(engine._subsystems) == 2
        assert engine.get_subsystem("sub_a") is not None
        assert engine.get_subsystem("sub_b") is not None

    def test_tick_all_subsystems(self):
        """Engine.tick should call tick on all subsystems."""
        from engine.engine import Engine
        from engine.subsystem import ISubsystem

        class CountingSubsystem(ISubsystem):
            def __init__(self, name_str: str):
                self._name = name_str
                self.tick_count = 0

            @property
            def name(self) -> str:
                return self._name

            def initialize(self, engine: "Engine") -> None:
                pass

            def tick(self, dt: float) -> None:
                self.tick_count += 1

            def shutdown(self) -> None:
                pass

        engine = Engine()
        sub_a = CountingSubsystem("sub_a")
        sub_b = CountingSubsystem("sub_b")
        engine.register_subsystem(sub_a)
        engine.register_subsystem(sub_b)

        engine.tick(0.016)

        assert sub_a.tick_count == 1
        assert sub_b.tick_count == 1

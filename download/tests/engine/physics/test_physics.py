"""
Tests for Physics subsystem.

Physics provides 2D physics simulation.
Uses headless implementation for CI compatibility.

Layer: 2 (Engine)
"""

import pytest
from engine.subsystem import ISubsystem
from engine.physics.physics import IPhysics, Physics2D


class TestPhysicsInterface:
    """Test that Physics2D implements IPhysics."""

    def test_physics_is_subsystem(self):
        """Physics2D should be a ISubsystem."""
        assert issubclass(Physics2D, ISubsystem)

    def test_physics_implements_iphysics(self):
        """Physics2D should implement IPhysics interface."""
        assert issubclass(Physics2D, IPhysics)


class TestPhysicsName:
    """Test Physics name property."""

    def test_physics_has_name(self):
        """Physics should have name property."""
        physics = Physics2D()
        assert hasattr(physics, "name")

    def test_physics_name_is_physics(self):
        """Physics name should be 'physics'."""
        physics = Physics2D()
        assert physics.name == "physics"


class TestPhysicsInitialization:
    """Test Physics initialization."""

    def test_physics_has_initialize(self):
        """Physics should have initialize method."""
        physics = Physics2D()
        assert hasattr(physics, "initialize")
        assert callable(physics.initialize)

    def test_physics_initialize_accepts_engine(self):
        """Physics initialize should accept engine parameter."""
        physics = Physics2D()
        physics.initialize(None)  # Should not raise


class TestPhysicsTick:
    """Test Physics tick functionality."""

    def test_physics_has_tick(self):
        """Physics should have tick method."""
        physics = Physics2D()
        assert hasattr(physics, "tick")
        assert callable(physics.tick)

    def test_physics_tick_steps_simulation(self):
        """Physics tick should step the simulation."""
        physics = Physics2D()
        physics.initialize(None)
        physics.tick(0.016)  # Should not raise


class TestPhysicsShutdown:
    """Test Physics shutdown."""

    def test_physics_has_shutdown(self):
        """Physics should have shutdown method."""
        physics = Physics2D()
        assert hasattr(physics, "shutdown")
        assert callable(physics.shutdown)

    def test_physics_shutdown_clears_bodies(self):
        """Physics shutdown should clear bodies."""
        physics = Physics2D()
        physics.initialize(None)
        physics.shutdown()
        assert physics.body_count == 0


class TestPhysicsGravity:
    """Test Physics gravity."""

    def test_physics_has_gravity(self):
        """Physics should have gravity property."""
        physics = Physics2D()
        assert hasattr(physics, "gravity")

    def test_gravity_default(self):
        """Physics gravity should default to (0, -900)."""
        physics = Physics2D()
        assert physics.gravity == (0.0, -900.0)

    def test_gravity_can_be_set(self):
        """Physics gravity can be set."""
        physics = Physics2D()
        physics.gravity = (0.0, -500.0)
        assert physics.gravity == (0.0, -500.0)


class TestPhysicsBodyCreation:
    """Test Physics body creation."""

    def test_physics_has_create_body(self):
        """Physics should have create_body method."""
        physics = Physics2D()
        assert hasattr(physics, "create_body")
        assert callable(physics.create_body)

    def test_create_body_returns_id(self):
        """create_body should return a body ID."""
        physics = Physics2D()
        physics.initialize(None)
        body_id = physics.create_body(mass=1.0, moment=100.0)
        assert isinstance(body_id, int)
        assert body_id > 0

    def test_body_count_increases(self):
        """Creating body increases body_count."""
        physics = Physics2D()
        physics.initialize(None)
        initial_count = physics.body_count
        physics.create_body(mass=1.0, moment=100.0)
        assert physics.body_count == initial_count + 1


class TestPhysicsBodyPosition:
    """Test Physics body position."""

    def test_physics_has_set_body_position(self):
        """Physics should have set_body_position method."""
        physics = Physics2D()
        assert hasattr(physics, "set_body_position")

    def test_set_body_position(self):
        """set_body_position should work."""
        physics = Physics2D()
        physics.initialize(None)
        body_id = physics.create_body(mass=1.0, moment=100.0)
        physics.set_body_position(body_id, 100.0, 200.0)
        pos = physics.get_body_position(body_id)
        assert pos == (100.0, 200.0)

    def test_physics_has_get_body_position(self):
        """Physics should have get_body_position method."""
        physics = Physics2D()
        assert hasattr(physics, "get_body_position")


class TestPhysicsBodyVelocity:
    """Test Physics body velocity."""

    def test_physics_has_set_body_velocity(self):
        """Physics should have set_body_velocity method."""
        physics = Physics2D()
        assert hasattr(physics, "set_body_velocity")

    def test_set_body_velocity(self):
        """set_body_velocity should work."""
        physics = Physics2D()
        physics.initialize(None)
        body_id = physics.create_body(mass=1.0, moment=100.0)
        physics.set_body_velocity(body_id, 10.0, 20.0)
        vel = physics.get_body_velocity(body_id)
        assert vel == (10.0, 20.0)

    def test_physics_has_get_body_velocity(self):
        """Physics should have get_body_velocity method."""
        physics = Physics2D()
        assert hasattr(physics, "get_body_velocity")


class TestPhysicsRemoveBody:
    """Test Physics body removal."""

    def test_physics_has_remove_body(self):
        """Physics should have remove_body method."""
        physics = Physics2D()
        assert hasattr(physics, "remove_body")

    def test_remove_body_decreases_count(self):
        """Removing body decreases body_count."""
        physics = Physics2D()
        physics.initialize(None)
        body_id = physics.create_body(mass=1.0, moment=100.0)
        physics.remove_body(body_id)
        assert physics.body_count == 0


class TestPhysicsEnabled:
    """Test Physics enabled state."""

    def test_physics_has_enabled(self):
        """Physics should have enabled property."""
        physics = Physics2D()
        assert hasattr(physics, "enabled")

    def test_physics_enabled_by_default(self):
        """Physics should be enabled by default."""
        physics = Physics2D()
        assert physics.enabled is True

    def test_disabled_physics_skips_tick(self):
        """Disabled physics should not step simulation."""
        physics = Physics2D()
        physics.initialize(None)
        physics.enabled = False
        physics.tick(0.016)  # Should not raise

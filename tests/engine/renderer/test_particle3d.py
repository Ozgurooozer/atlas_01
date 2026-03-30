"""Tests for 3D particle system."""
import pytest
from core.vec import Vec2, Vec3
from core.color import Color


class TestParticle3D:
    """Test suite for 3D particles."""

    def test_particle3d_creation(self):
        """Particle3D should store position, velocity, and life."""
        from engine.renderer.particle3d import Particle3D
        
        p = Particle3D(
            position=Vec3(100, 200, 50),
            velocity=Vec3(10, 20, 5),
            life=2.0
        )
        
        assert p.position.x == 100
        assert p.position.y == 200
        assert p.position.z == 50
        assert p.velocity.x == 10
        assert p.life == 2.0
        assert p.max_life == 2.0

    def test_particle3d_update(self):
        """Particle3D should update position based on velocity."""
        from engine.renderer.particle3d import Particle3D
        
        p = Particle3D(
            position=Vec3(0, 0, 0),
            velocity=Vec3(10, 0, 0),
            life=1.0
        )
        
        p.update(dt=0.1)
        
        # Should have moved by velocity * dt
        assert p.position.x == 1.0  # 10 * 0.1
        assert p.life == 0.9  # Decreased by dt

    def test_particle3d_is_alive(self):
        """Particle3D should report alive status."""
        from engine.renderer.particle3d import Particle3D
        
        p = Particle3D(position=Vec3(0, 0, 0), velocity=Vec3(0, 0, 0), life=1.0)
        
        assert p.is_alive() is True
        
        p.life = 0
        assert p.is_alive() is False
        
        p.life = -1
        assert p.is_alive() is False

    def test_particle_size_over_life(self):
        """Particle should support size curve over life."""
        from engine.renderer.particle3d import Particle3D
        
        p = Particle3D(position=Vec3(0, 0, 0), velocity=Vec3(0, 0, 0), life=1.0)
        p.size_over_life = [1.0, 0.5, 0.0]  # Start big, end small
        
        # At start of life
        p.life = 1.0
        size = p.get_current_size()
        assert size > 0.5
        
        # Near end of life
        p.life = 0.1
        size = p.get_current_size()
        assert size <= 0.5


class TestParticleEmitter3D:
    """Test suite for 3D particle emitters."""

    def test_emitter_creation(self):
        """ParticleEmitter3D should initialize with default values."""
        from engine.renderer.particle3d import ParticleEmitter3D
        
        emitter = ParticleEmitter3D()
        
        assert emitter.emission_rate == 10
        assert emitter.burst_count == 0
        assert len(emitter.particles) == 0

    def test_emitter_emit_particle(self):
        """Emitter should emit particles."""
        from engine.renderer.particle3d import ParticleEmitter3D
        
        emitter = ParticleEmitter3D()
        emitter.position = Vec3(100, 200, 0)
        
        emitter.emit(count=5)
        
        assert len(emitter.particles) == 5

    def test_emitter_burst(self):
        """Emitter should support burst emission."""
        from engine.renderer.particle3d import ParticleEmitter3D
        
        emitter = ParticleEmitter3D()
        emitter.burst_count = 50
        
        emitter.burst()
        
        assert len(emitter.particles) == 50

    def test_emitter_update(self):
        """Emitter should update all particles."""
        from engine.renderer.particle3d import ParticleEmitter3D
        
        emitter = ParticleEmitter3D()
        emitter.emission_rate = 0  # Disable auto-emission for test
        emitter.emit(count=3)
        
        # Reset positions and give velocity
        for p in emitter.particles:
            p.position = Vec3(0, 0, 0)
            p.velocity = Vec3(10, 0, 0)
        
        # Update
        emitter.update(dt=0.1)
        
        # Particles should have moved
        for p in emitter.particles:
            assert p.position.x > 0

    def test_emitter_remove_dead_particles(self):
        """Emitter should clean up dead particles."""
        from engine.renderer.particle3d import ParticleEmitter3D
        
        emitter = ParticleEmitter3D()
        emitter.emission_rate = 0  # Disable auto-emission
        emitter.emit(count=5)
        
        # Kill all particles
        for p in emitter.particles:
            p.life = 0
        
        emitter.update(dt=0.1)
        
        # Dead particles should be removed
        assert len(emitter.particles) == 0


class TestParticleRenderer3D:
    """Test suite for 3D particle renderer."""

    def test_renderer_creation(self):
        """ParticleRenderer3D should initialize with capacity."""
        from engine.renderer.particle3d import ParticleRenderer3D
        
        renderer = ParticleRenderer3D(max_particles=10000)
        
        assert renderer.max_particles == 10000

    def test_renderer_batch_particles(self):
        """Renderer should batch particles for efficient rendering."""
        from engine.renderer.particle3d import ParticleRenderer3D, ParticleEmitter3D
        
        renderer = ParticleRenderer3D()
        emitter = ParticleEmitter3D()
        emitter.emit(count=100)
        
        # Submit particles to renderer
        batch = renderer.batch_particles(emitter.particles)
        
        assert len(batch) <= 100


class TestEmissionShapes:
    """Test suite for particle emission shapes."""

    def test_box_emission(self):
        """Should emit particles within box volume."""
        from engine.renderer.particle3d import BoxEmitter, Particle3D
        
        box = BoxEmitter(size=Vec3(100, 100, 100))
        
        particle = box.emit_particle()
        
        # Particle should be within box bounds
        assert -50 <= particle.position.x <= 50
        assert -50 <= particle.position.y <= 50
        assert -50 <= particle.position.z <= 50

    def test_sphere_emission(self):
        """Should emit particles within sphere volume."""
        from engine.renderer.particle3d import SphereEmitter
        from math import sqrt
        
        sphere = SphereEmitter(radius=50.0)
        
        particle = sphere.emit_particle()
        
        # Distance from center should be <= radius
        dist = sqrt(
            particle.position.x ** 2 +
            particle.position.y ** 2 +
            particle.position.z ** 2
        )
        assert dist <= 50.0

    def test_cone_emission(self):
        """Should emit particles within cone volume."""
        from engine.renderer.particle3d import ConeEmitter
        
        cone = ConeEmitter(angle=30.0, length=100.0)
        
        particle = cone.emit_particle()
        
        # Velocity should point in cone direction
        assert particle.velocity.z > 0  # Moving forward

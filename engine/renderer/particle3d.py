"""3D particle system for 2.5D rendering.

Provides 3D-positioned particles with velocity, color gradients, and emission shapes.

Layer: 2 (Engine)
Dependencies: core.vec, core.color
"""
from typing import List, Optional, Tuple
from math import sqrt, sin, cos, pi, radians
import random
from core.vec import Vec2, Vec3
from core.color import Color


class Particle3D:
    """Single 3D particle with position, velocity, and life.
    
    A particle exists in 3D space (X, Y, Z) with velocity and a limited lifespan.
    Supports size and color curves over life for rich visual effects.
    
    Usage:
        p = Particle3D(
            position=Vec3(100, 200, 50),
            velocity=Vec3(10, 20, 5),
            life=2.0
        )
        p.update(dt=0.016)
    """
    
    def __init__(self, position: Vec3, velocity: Vec3, life: float,
                 color: Color = None, size: float = 1.0):
        """Initialize 3D particle.
        
        Args:
            position: Initial position
            velocity: Initial velocity
            life: Lifespan in seconds
            color: Particle color
            size: Particle size
        """
        self.position = position
        self.velocity = velocity
        self.life = life
        self.max_life = life
        self.color = color or Color.white()
        self.size = size
        
        # Curves for size and color over life
        self.size_over_life: Optional[List[float]] = None
        self.color_over_life: Optional[List[Color]] = None
    
    def update(self, dt: float) -> None:
        """Update particle position and life.
        
        Args:
            dt: Delta time in seconds
        """
        # Update position
        self.position.x += self.velocity.x * dt
        self.position.y += self.velocity.y * dt
        self.position.z += self.velocity.z * dt
        
        # Decrease life
        self.life -= dt
    
    def is_alive(self) -> bool:
        """Check if particle is still alive."""
        return self.life > 0
    
    def get_life_ratio(self) -> float:
        """Get life ratio (1.0 = full, 0.0 = dead)."""
        if self.max_life <= 0:
            return 0.0
        return max(0.0, self.life / self.max_life)
    
    def get_current_size(self) -> float:
        """Get current size based on size_over_life curve."""
        if not self.size_over_life:
            return self.size
        
        ratio = 1.0 - self.get_life_ratio()
        
        # Sample from curve
        index = int(ratio * (len(self.size_over_life) - 1))
        index = max(0, min(index, len(self.size_over_life) - 1))
        
        return self.size * self.size_over_life[index]
    
    def get_current_color(self) -> Color:
        """Get current color based on color_over_life gradient."""
        if not self.color_over_life:
            return self.color
        
        ratio = 1.0 - self.get_life_ratio()
        
        # Sample from gradient
        index = int(ratio * (len(self.color_over_life) - 1))
        index = max(0, min(index, len(self.color_over_life) - 1))
        
        return self.color_over_life[index]


class ParticleEmitter3D:
    """Emits 3D particles with configurable rate and shape.
    
    Supports continuous emission or burst emission. Can use various
    emission shapes (box, sphere, cone) for different effects.
    
    Usage:
        emitter = ParticleEmitter3D()
        emitter.position = Vec3(100, 200, 0)
        emitter.emission_rate = 100  # particles/second
        emitter.emit(count=10)
    """
    
    def __init__(self):
        """Initialize particle emitter with defaults."""
        self.position = Vec3(0, 0, 0)
        self.emission_rate = 10  # particles per second
        self.burst_count = 0
        self.particles: List[Particle3D] = []
        self._emission_accumulator = 0.0
        
        # Default emission shape
        self.emission_shape = "point"
        self.emission_size = Vec3(10, 10, 10)
    
    def emit(self, count: int = 1) -> None:
        """Emit particles.
        
        Args:
            count: Number of particles to emit
        """
        for _ in range(count):
            particle = self._create_particle()
            self.particles.append(particle)
    
    def burst(self) -> None:
        """Emit burst of particles."""
        if self.burst_count > 0:
            self.emit(self.burst_count)
    
    def _create_particle(self) -> Particle3D:
        """Create a new particle at emitter position.
        
        Returns:
            New particle
        """
        # Get emission position based on shape
        pos = self._get_emission_position()
        
        # Random velocity
        velocity = Vec3(
            (random.random() - 0.5) * 100,
            (random.random() - 0.5) * 100,
            random.random() * 50
        )
        
        # Create particle
        particle = Particle3D(
            position=pos,
            velocity=velocity,
            life=1.0 + random.random()
        )
        
        # Set size curve (start big, end small)
        particle.size_over_life = [1.0, 0.8, 0.6, 0.3, 0.0]
        
        return particle
    
    def _get_emission_position(self) -> Vec3:
        """Get random emission position based on shape.
        
        Returns:
            Emission position
        """
        if self.emission_shape == "box":
            return Vec3(
                self.position.x + (random.random() - 0.5) * self.emission_size.x,
                self.position.y + (random.random() - 0.5) * self.emission_size.y,
                self.position.z + (random.random() - 0.5) * self.emission_size.z
            )
        elif self.emission_shape == "sphere":
            # Random point in sphere
            r = random.random() * (self.emission_size.x / 2)
            theta = random.random() * 2 * pi
            phi = random.random() * pi
            
            return Vec3(
                self.position.x + r * sin(phi) * cos(theta),
                self.position.y + r * sin(phi) * sin(theta),
                self.position.z + r * cos(phi)
            )
        else:  # point
            return Vec3(self.position.x, self.position.y, self.position.z)
    
    def update(self, dt: float) -> None:
        """Update all particles and emit new ones.
        
        Args:
            dt: Delta time in seconds
        """
        # Update existing particles
        for particle in self.particles:
            particle.update(dt)
        
        # Remove dead particles
        self.particles = [p for p in self.particles if p.is_alive()]
        
        # Emit new particles based on rate
        self._emission_accumulator += self.emission_rate * dt
        emit_count = int(self._emission_accumulator)
        
        if emit_count > 0:
            self._emission_accumulator -= emit_count
            self.emit(emit_count)


class ParticleRenderer3D:
    """Renders 3D particles with batching and depth sorting.
    
    Optimizes rendering by batching particles with similar properties
    and sorting by depth for correct transparency.
    
    Usage:
        renderer = ParticleRenderer3D(max_particles=10000)
        renderer.render_particles(particles)
    """
    
    MAX_PARTICLES = 50000
    
    def __init__(self, max_particles: int = 10000):
        """Initialize particle renderer.
        
        Args:
            max_particles: Maximum particles to render
        """
        self.max_particles = min(max_particles, self.MAX_PARTICLES)
    
    def batch_particles(self, particles: List[Particle3D]) -> List[Particle3D]:
        """Batch particles for efficient rendering.
        
        Filters to max capacity and sorts by depth.
        
        Args:
            particles: All particles to render
            
        Returns:
            Batched particles
        """
        # Limit to max capacity
        if len(particles) > self.max_particles:
            particles = particles[:self.max_particles]
        
        # Sort by depth (Z position) for correct transparency
        return sorted(particles, key=lambda p: p.position.z, reverse=True)
    
    def depth_sort_particles(self, particles: List[Particle3D]) -> List[Particle3D]:
        """Sort particles by depth for correct rendering order.
        
        Args:
            particles: Particles to sort
            
        Returns:
            Sorted particles (back to front)
        """
        # Sort by Y + Z for isometric depth
        return sorted(
            particles,
            key=lambda p: p.position.y + p.position.z * 0.5,
            reverse=True
        )


class BoxEmitter:
    """Emits particles within a box volume.
    
    Usage:
        box = BoxEmitter(size=Vec3(100, 100, 100))
        particle = box.emit_particle()
    """
    
    def __init__(self, size: Vec3):
        """Initialize box emitter.
        
        Args:
            size: Box dimensions
        """
        self.size = size
    
    def emit_particle(self) -> Particle3D:
        """Emit particle within box.
        
        Returns:
            New particle
        """
        pos = Vec3(
            (random.random() - 0.5) * self.size.x,
            (random.random() - 0.5) * self.size.y,
            (random.random() - 0.5) * self.size.z
        )
        
        return Particle3D(
            position=pos,
            velocity=Vec3(0, 0, 0),
            life=1.0
        )


class SphereEmitter:
    """Emits particles within a sphere volume.
    
    Usage:
        sphere = SphereEmitter(radius=50.0)
        particle = sphere.emit_particle()
    """
    
    def __init__(self, radius: float):
        """Initialize sphere emitter.
        
        Args:
            radius: Sphere radius
        """
        self.radius = radius
    
    def emit_particle(self) -> Particle3D:
        """Emit particle within sphere.
        
        Returns:
            New particle
        """
        # Random point in sphere
        r = random.random() * self.radius
        theta = random.random() * 2 * pi
        phi = random.random() * pi
        
        pos = Vec3(
            r * sin(phi) * cos(theta),
            r * sin(phi) * sin(theta),
            r * cos(phi)
        )
        
        return Particle3D(
            position=pos,
            velocity=Vec3(0, 0, 0),
            life=1.0
        )


class ConeEmitter:
    """Emits particles in a cone shape.
    
    Useful for directional effects like fire, sparks, etc.
    
    Usage:
        cone = ConeEmitter(angle=30.0, length=100.0)
        particle = cone.emit_particle()
    """
    
    def __init__(self, angle: float, length: float):
        """Initialize cone emitter.
        
        Args:
            angle: Cone angle in degrees
            length: Cone length
        """
        self.angle = angle
        self.length = length
    
    def emit_particle(self) -> Particle3D:
        """Emit particle within cone.
        
        Returns:
            New particle
        """
        # Random distance along cone
        dist = random.random() * self.length
        
        # Random angle within cone
        angle_rad = radians(self.angle)
        spread = (random.random() - 0.5) * 2 * angle_rad
        
        # Calculate position
        pos = Vec3(
            dist * sin(spread),
            dist * sin(spread),
            dist * cos(spread)
        )
        
        # Velocity points outward
        velocity = Vec3(
            sin(spread) * 50,
            sin(spread) * 50,
            cos(spread) * 100
        )
        
        return Particle3D(
            position=pos,
            velocity=velocity,
            life=1.0
        )

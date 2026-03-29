"""
Particle System for efficient visual effects.

Uses a ring buffer for fixed-size particle pool and supports
GPU instancing via SpriteBatch.

Layer: 2 (Engine)
Dependencies: core.vec, core.color, engine.renderer.sprite, engine.renderer.batch
"""

from __future__ import annotations
import random
from typing import List, Optional, Tuple
from core.vec import Vec2
from core.color import Color
from engine.renderer.sprite import Sprite
from engine.renderer.batch import SpriteBatch
from engine.renderer.texture import Texture


class Particle:
    """Single particle data."""
    def __init__(self):
        self.position = Vec2.zero()
        self.velocity = Vec2.zero()
        self.color = Color.white()
        self.size = Vec2(1.0, 1.0)
        self.rotation = 0.0
        self.angular_velocity = 0.0
        self.life = 0.0
        self.max_life = 1.0
        self.active = False


class ParticleEmitter:
    """
    Particle emitter using a fixed-size pool.
    
    Attributes:
        texture: Texture used for all particles.
        max_particles: Maximum number of active particles.
    """
    
    def __init__(self, texture: Texture, max_particles: int = 1000):
        self.texture = texture
        self.max_particles = max_particles
        self._pool = [Particle() for _ in range(max_particles)]
        self._next_index = 0
        self._active_count = 0
        
        # Emitter settings
        self.position = Vec2.zero()
        self.emit_rate = 10.0 # particles per second
        self._emit_timer = 0.0
        
    def emit(self, count: int = 1, **kwargs):
        """Spawn particles from the pool."""
        for _ in range(count):
            p = self._pool[self._next_index]
            p.active = True
            p.life = 0.0
            p.position = Vec2(self.position.x, self.position.y)
            
            # Default random values if not provided
            p.velocity = kwargs.get('velocity', Vec2(random.uniform(-50, 50), random.uniform(-50, 50)))
            p.max_life = kwargs.get('max_life', random.uniform(0.5, 2.0))
            p.color = kwargs.get('color', Color.white())
            p.size = kwargs.get('size', Vec2(8.0, 8.0))
            p.rotation = kwargs.get('rotation', random.uniform(0, 360))
            p.angular_velocity = kwargs.get('angular_velocity', random.uniform(-90, 90))
            
            self._next_index = (self._next_index + 1) % self.max_particles
            
    def update(self, dt: float):
        """Update all active particles."""
        self._active_count = 0
        for p in self._pool:
            if not p.active:
                continue
                
            p.life += dt
            if p.life >= p.max_life:
                p.active = False
                continue
                
            # Physics update
            p.position += p.velocity * dt
            p.rotation += p.angular_velocity * dt
            self._active_count += 1
            
    def draw(self, batch: SpriteBatch):
        """Draw all active particles using the batch."""
        # Create a temporary sprite to reuse for drawing
        # This avoids allocating thousands of Sprite objects
        temp_sprite = Sprite(self.texture)
        
        for p in self._pool:
            if not p.active:
                continue
                
            # Calculate alpha based on life
            alpha = 1.0 - (p.life / p.max_life)
            
            temp_sprite.position = p.position
            temp_sprite.width = p.size.x
            temp_sprite.height = p.size.y
            temp_sprite.rotation = p.rotation
            temp_sprite.color = (
                int(p.color.r * 255),
                int(p.color.g * 255),
                int(p.color.b * 255),
                int(alpha * 255)
            )
            
            batch.draw(temp_sprite)
            
    @property
    def active_count(self) -> int:
        return self._active_count

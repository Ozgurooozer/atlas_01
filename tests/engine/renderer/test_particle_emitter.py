import pytest
from engine.renderer.particle import ParticleEmitter
from engine.renderer.texture import Texture
from engine.renderer.batch import SpriteBatch
from unittest.mock import MagicMock

def test_particle_emitter_lifecycle():
    """Gereksinim 5.4, 5.5: Süresi dolan parçacıklar kaldırılır."""
    tex = Texture(64, 64)
    emitter = ParticleEmitter(tex, max_particles=10)
    
    # Emit 5 particles with 1.0s life
    emitter.emit(5, max_life=1.0)
    assert emitter.active_count == 0 # update() hasn't run yet
    
    emitter.update(0.1)
    assert emitter.active_count == 5
    
    # Advance time past life
    emitter.update(1.0)
    assert emitter.active_count == 0

def test_particle_emitter_ring_buffer():
    """Gereksinim 5.4, 5.5: Maksimum kapasitede en eski parçacık değiştirilir."""
    tex = Texture(64, 64)
    emitter = ParticleEmitter(tex, max_particles=2)
    
    # Emit 2 particles
    emitter.emit(1, max_life=10.0) # P1
    emitter.emit(1, max_life=10.0) # P2
    emitter.update(0.1)
    assert emitter.active_count == 2
    
    # Emit 3rd particle (should overwrite P1)
    emitter.emit(1, max_life=5.0) # P3 (overwrites P1)
    emitter.update(0.1)
    assert emitter.active_count == 2
    
    # Verify P3 is there (life is different)
    active_lives = [p.max_life for p in emitter._pool if p.active]
    assert 5.0 in active_lives
    assert 10.0 in active_lives

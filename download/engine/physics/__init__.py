"""
Physics Subsystem.

Provides 2D physics using Pymunk and collision detection.

Layer: 2 (Engine)
Dependencies: engine.subsystem
"""

from engine.physics.physics import IPhysics, Physics2D
from engine.physics.aabb import AABB
from engine.physics.overlap import OverlapDetector
from engine.physics.spatial import SpatialHash

__all__ = [
    # Physics
    "IPhysics",
    "Physics2D",
    # Collision
    "AABB",
    "OverlapDetector",
    "SpatialHash",
]

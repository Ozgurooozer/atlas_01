"""
ECS Components package.

Contains standard components for the Entity-Component-System.
"""

from world.components.engine_context import EngineContext
from world.components.sprite_component import SpriteComponent
from world.components.physics_component import PhysicsComponent
from world.components.camera_component import CameraComponent
from world.components.script_component import ScriptComponent

__all__ = [
    "EngineContext",
    "SpriteComponent",
    "PhysicsComponent",
    "CameraComponent",
    "ScriptComponent",
]

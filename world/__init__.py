"""
World Layer.

Contains the game world, actors, and components.
Actors are objects that exist in the world.
Components are modular behaviors attached to actors.

Layer: 3 (World)
Dependencies: core (Layer 1)
"""

from world.component import Component
from world.actor import Actor
from world.transform import TransformComponent
from world.world import World

__all__ = [
    "Component",
    "Actor",
    "TransformComponent",
    "World",
]

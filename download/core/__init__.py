"""
Core Layer (Layer 1).

Foundation layer for the entire engine. Contains:
- Object: Base class for everything
- GUID: Unique identifiers
- Reflection: Property metadata system
- EventBus: Loose coupling via events
- Serializer: JSON serialization
- Vec2, Vec3: Vector math utilities
- Scheduler: Time-based callback system
"""

from core.guid import GUID
from core.object import Object
from core.reflection import reflect, get_properties, PropertyMeta
from core.eventbus import EventBus
from core.serializer import Serializer
from core.vec import Vec2, Vec3
from core.scheduler import Scheduler

__all__ = [
    'GUID',
    'Object',
    'reflect',
    'get_properties',
    'PropertyMeta',
    'EventBus',
    'Serializer',
    'Vec2',
    'Vec3',
    'Scheduler',
]

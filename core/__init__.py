"""
Core Layer (Layer 1).

Foundation layer for the entire engine. Contains:
- Object: Base class for everything
- GUID: Unique identifiers
- Reflection: Property metadata system
- EventBus: Loose coupling via events
- Serializer: msgspec serialization
- Vec2, Vec3: Vector math utilities
- Color: RGBA color utilities
- Scheduler: Time-based callback system
"""

from core.color import Color
from core.guid import GUID
from core.object import Object
from core.reflection import reflect, get_properties, get_property_value, set_property_value, PropertyMeta
from core.eventbus import EventBus
from core.serializer import Serializer
from core.vec import Vec2, Vec3
from core.scheduler import Scheduler

__all__ = [
    'Color',
    'GUID',
    'Object',
    'reflect',
    'get_properties',
    'get_property_value',
    'set_property_value',
    'PropertyMeta',
    'EventBus',
    'Serializer',
    'Vec2',
    'Vec3',
    'Scheduler',
]

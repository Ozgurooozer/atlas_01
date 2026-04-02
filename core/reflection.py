"""
Reflection System.

Provides property metadata for automatic Editor display and Serialization.
Uses @reflect decorator to mark properties for discovery.

Layer: 1 (Core)
Dependencies: None
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable, List, Optional


@dataclass
class PropertyMeta:
    """
    Metadata for a reflected property.

    Contains information needed by:
    - Editor: How to display the property
    - Serializer: How to serialize the property
    - Validator: Constraints (min, max, etc.)

    Attributes:
        name: Property name (set automatically)
        type_hint: Type string ("float", "int", "str", "bool", etc.)
        default: Default value
        category: Grouping category for Editor
        min: Minimum value for numeric types
        max: Maximum value for numeric types
        readonly: If True, property cannot be edited
        description: Human-readable description
    """
    name: str
    type_hint: str
    default: Any = None
    category: str = "Default"
    min: Optional[float] = None
    max: Optional[float] = None
    readonly: bool = False
    description: str = ""


class ReflectedProperty(property):
    """
    Property subclass that can hold PropertyMeta.

    Standard Python property objects cannot have custom attributes.
    This subclass allows us to store _property_meta directly.
    """

    def __init__(self, fget=None, fset=None, fdel=None, doc=None, meta: PropertyMeta = None):
        super().__init__(fget, fset, fdel, doc)
        self._property_meta = meta

    def getter(self, fget):
        """Return a new ReflectedProperty with the getter."""
        return type(self)(fget, self.fset, self.fdel, self.__doc__, self._property_meta)

    def setter(self, fset):
        """Return a new ReflectedProperty with the setter."""
        return type(self)(self.fget, fset, self.fdel, self.__doc__, self._property_meta)

    def deleter(self, fdel):
        """Return a new ReflectedProperty with the deleter."""
        return type(self)(self.fget, self.fset, fdel, self.__doc__, self._property_meta)


def reflect(type_hint: str, **kwargs) -> Callable:
    """
    Decorator to mark a property for reflection.

    Usage:
        class HealthComponent(Component):
            @reflect("float", min=0, max=100, category="Stats")
            def max_health(self) -> float:
                return self._max_health

            @max_health.setter
            def max_health(self, value: float):
                self._max_health = value

    Args:
        type_hint: Type string ("float", "int", "str", "bool", etc.)
        **kwargs: Additional PropertyMeta arguments

    Returns:
        Decorated property
    """
    def decorator(func):
        # Create PropertyMeta
        meta = PropertyMeta(
            name=func.__name__,
            type_hint=type_hint,
            **kwargs
        )

        # Create ReflectedProperty with meta
        return ReflectedProperty(func, meta=meta)

    return decorator


def get_properties(cls_or_instance) -> List[PropertyMeta]:
    """
    Get all reflected properties for a class or instance.

    Args:
        cls_or_instance: Class or instance to inspect

    Returns:
        List of PropertyMeta for all reflected properties
    """
    if not isinstance(cls_or_instance, type):
        cls = type(cls_or_instance)
    else:
        cls = cls_or_instance

    properties = []
    seen_names = set()

    # getattr üzerinden MRO'yu dolaş — vars() inherited property'leri kaçırabilir
    for name in dir(cls):
        if name.startswith("_"):
            continue
        try:
            value = getattr(cls, name)
        except AttributeError:
            continue
        if isinstance(value, property) and hasattr(value, '_property_meta'):
            meta = value._property_meta
            if meta.name not in seen_names:
                seen_names.add(meta.name)
                properties.append(meta)

    return properties


def get_property_value(instance: object, property_name: str) -> Any:
    """
    Get the value of a reflected property.

    Args:
        instance: Object instance
        property_name: Name of the property

    Returns:
        Property value

    Raises:
        AttributeError: If property doesn't exist
    """
    cls = type(instance)
    prop = getattr(cls, property_name, None)
    if prop is None:
        raise AttributeError(f"No property '{property_name}' on {cls.__name__}")

    return prop.fget(instance)


def set_property_value(instance: object, property_name: str, value: Any) -> None:
    """
    Set the value of a reflected property.

    Args:
        instance: Object instance
        property_name: Name of the property
        value: Value to set

    Raises:
        AttributeError: If property doesn't exist or is readonly
    """
    cls = type(instance)
    prop = getattr(cls, property_name, None)
    if prop is None:
        raise AttributeError(f"No property '{property_name}' on {cls.__name__}")

    if prop.fset is None:
        raise AttributeError(f"Property '{property_name}' is readonly")

    prop.fset(instance, value)

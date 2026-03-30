"""Prefab System - Object templates and instancing.

Provides reusable object templates for efficient entity creation.

Layer: 3 (World)
Dependencies: core.object
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from copy import deepcopy

_MISSING = object()  # Sentinel for missing default


@dataclass
class ComponentData:
    """Component definition for prefabs.
    
    Attributes:
        type: Component type name
        properties: Component property values
    """
    type: str
    properties: Dict[str, Any] = field(default_factory=dict)


class Prefab:
    """Object template for creating instances.
    
    Defines a reusable entity template with components and properties.
    """
    
    def __init__(self, name: str = ""):
        """Initialize prefab.
        
        Args:
            name: Prefab identifier
        """
        self.name = name
        self.components: List[ComponentData] = []
        self.properties: Dict[str, Any] = {}
    
    def add_component(self, component: ComponentData) -> None:
        """Add component to prefab.
        
        Args:
            component: Component data to add
        """
        self.components.append(component)
    
    def set_property(self, name: str, value: Any) -> None:
        """Set prefab property.
        
        Args:
            name: Property name
            value: Property value
        """
        self.properties[name] = value
    
    def get_property(self, name: str, default: Any = _MISSING) -> Any:
        """Get prefab property.

        Args:
            name: Property name
            default: Default value if not found

        Returns:
            Property value

        Raises:
            KeyError: If property not found and no default given
        """
        if name in self.properties:
            return self.properties[name]
        if default is not _MISSING:
            return default
        raise KeyError(f"Property '{name}' not found in prefab '{self.name}'")
    
    def clone(self, new_name: Optional[str] = None) -> "Prefab":
        """Clone this prefab.
        
        Args:
            new_name: Optional name for clone
            
        Returns:
            Independent copy of this prefab
        """
        clone = Prefab(new_name or f"{self.name}_clone")
        clone.components = deepcopy(self.components)
        clone.properties = deepcopy(self.properties)
        return clone


class PrefabInstance:
    """Instance of a prefab with optional overrides.
    
    Represents a specific instantiation of a prefab with
    potential property overrides.
    """
    
    def __init__(self, prefab: Prefab):
        """Initialize instance.
        
        Args:
            prefab: Base prefab for this instance
        """
        self.prefab = prefab
        self.overrides: Dict[str, Any] = {}
    
    def set_override(self, name: str, value: Any) -> None:
        """Set property override.
        
        Args:
            name: Property name
            value: Override value
        """
        self.overrides[name] = value
    
    def get_property(self, name: str, default: Any = None) -> Any:
        """Get property value.
        
        Checks overrides first, then prefab.
        
        Args:
            name: Property name
            default: Default value if not found
            
        Returns:
            Property value
        """
        if name in self.overrides:
            return self.overrides[name]
        return self.prefab.get_property(name, default)
    
    def apply_to(self, obj: Any) -> None:
        """Apply prefab components to object.
        
        Args:
            obj: Object to apply components to
        """
        for comp_data in self.prefab.components:
            # Merge properties with overrides
            props = dict(comp_data.properties)
            
            # Apply any matching overrides
            for key, value in self.overrides.items():
                if key in props:
                    props[key] = value
            
            # Add component to object if it has the method
            if hasattr(obj, 'add_component'):
                obj.add_component(comp_data.type, **props)


class PrefabManager:
    """Central registry for prefabs.
    
    Manages prefab definitions and creates instances.
    """
    
    def __init__(self):
        """Initialize prefab manager."""
        self._prefabs: Dict[str, Prefab] = {}
    
    @property
    def prefabs(self) -> Dict[str, Prefab]:
        """Get all registered prefabs (read-only view)."""
        return dict(self._prefabs)
    
    def register(self, prefab: Prefab) -> None:
        """Register a prefab.
        
        Args:
            prefab: Prefab to register
        """
        self._prefabs[prefab.name] = prefab
    
    def unregister(self, name: str) -> bool:
        """Unregister a prefab.
        
        Args:
            name: Prefab name to remove
            
        Returns:
            True if removed, False if not found
        """
        if name in self._prefabs:
            del self._prefabs[name]
            return True
        return False
    
    def get(self, name: str) -> Optional[Prefab]:
        """Get prefab by name.
        
        Args:
            name: Prefab name
            
        Returns:
            Prefab or None if not found
        """
        return self._prefabs.get(name)
    
    def has(self, name: str) -> bool:
        """Check if prefab exists.
        
        Args:
            name: Prefab name to check
            
        Returns:
            True if prefab exists
        """
        return name in self._prefabs
    
    def create_instance(self, name: str) -> PrefabInstance:
        """Create instance of prefab.
        
        Args:
            name: Prefab name
            
        Returns:
            New prefab instance
            
        Raises:
            KeyError: If prefab not found
        """
        prefab = self.get(name)
        if prefab is None:
            raise KeyError(f"Prefab '{name}' not found")
        return PrefabInstance(prefab)
    
    def get_all_names(self) -> List[str]:
        """Get all registered prefab names.
        
        Returns:
            List of prefab names
        """
        return list(self._prefabs.keys())
    
    def clear(self) -> None:
        """Clear all registered prefabs."""
        self._prefabs.clear()
    
    def create_from_instance(self, name: str, factory: Any) -> Any:
        """Create object instance using factory.
        
        Args:
            name: Prefab name
            factory: Callable that creates objects
            
        Returns:
            Created object with prefab applied
        """
        prefab_instance = self.create_instance(name)
        obj = factory()
        prefab_instance.apply_to(obj)
        return obj

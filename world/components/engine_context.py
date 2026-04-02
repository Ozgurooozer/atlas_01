"""
EngineContext for Dependency Injection.

Provides a way to inject engine-level systems (Renderer, Physics)
into components without tight coupling.

Layer: 3 (World)
Dependencies: None (Duck typing for Engine systems)
"""

from __future__ import annotations
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    # Avoid circular imports
    pass


class EngineContext:
    """
    Dependency Injection container for engine systems.
    
    Components can have 'renderer' or 'physics' attributes that
    are automatically populated when the component is injected.
    """

    def __init__(self, renderer: Any = None, physics: Any = None) -> None:
        """
        Initialize the context with engine systems.
        
        Args:
            renderer: The Renderer2D instance.
            physics: The PhysicsSystem instance.
        """
        self._renderer = renderer
        self._physics = physics

    @property
    def renderer(self) -> Any:
        """Get the renderer system."""
        return self._renderer

    @property
    def physics(self) -> Any:
        """Get the physics system."""
        return self._physics

    def inject(self, component: Any) -> None:
        """
        Inject systems into a component based on its attributes.
        
        Args:
            component: The component instance to inject into.
        """
        # Inject renderer if component has a 'renderer' attribute
        if hasattr(component, "renderer"):
            component.renderer = self._renderer
            
        # Inject physics if component has a 'physics' attribute
        if hasattr(component, "physics"):
            component.physics = self._physics

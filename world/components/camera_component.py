"""
CameraComponent for 2D camera control.

Provides a way to attach a Camera to an Actor and control its
properties and behavior.

Layer: 3 (World)
Dependencies: world.component, engine.renderer.camera
"""

from __future__ import annotations
from typing import Any, Dict, Optional, Tuple, TYPE_CHECKING

from world.component import Component
from world.transform import TransformComponent

if TYPE_CHECKING:
    from engine.renderer.camera import Camera
    from world.actor import Actor


class CameraComponent(Component):
    """
    Component that manages a Camera for an Actor.
    
    Attributes:
        camera: The Camera instance to manage.
        follow_owner: Whether the camera should follow the actor.
    """

    def __init__(self, camera: Optional[Camera] = None, follow_owner: bool = False, name: str = None) -> None:
        """
        Initialize the CameraComponent.
        
        Args:
            camera: The Camera instance to manage.
            follow_owner: Whether the camera should follow the actor.
            name: Optional name.
        """
        super().__init__(name)
        self.camera = camera
        self.follow_owner = follow_owner
        self.enabled = True

    def on_attach(self, owner: Actor) -> None:
        """
        Called when the component is attached to an actor.
        
        Args:
            owner: The actor this component is attached to.
        """
        super().on_attach(owner)
        if self.camera and self.follow_owner:
            # Try to follow TransformComponent if available, otherwise follow Actor
            transform = owner.get_component(TransformComponent)
            if transform:
                self.camera.follow_target = transform
            else:
                self.camera.follow_target = owner

    def on_tick(self, dt: float) -> None:
        """
        Update the camera.
        
        Args:
            dt: Delta time in seconds.
        """
        if self.camera and self.enabled:
            self.camera.update(dt)

    @property
    def zoom(self) -> float:
        """Get camera zoom level."""
        return self.camera.zoom if self.camera else 1.0

    @zoom.setter
    def zoom(self, value: float) -> None:
        """Set camera zoom level."""
        if self.camera:
            self.camera.zoom = value

    @property
    def rotation(self) -> float:
        """Get camera rotation in degrees."""
        return self.camera.rotation if self.camera else 0.0

    @rotation.setter
    def rotation(self, value: float) -> None:
        """Set camera rotation in degrees."""
        if self.camera:
            self.camera.rotation = value

    @property
    def viewport_size(self) -> Tuple[int, int]:
        """Get camera viewport size (width, height)."""
        if self.camera:
            return (self.camera.viewport_width, self.camera.viewport_height)
        return (800, 600)

    @viewport_size.setter
    def viewport_size(self, value: Tuple[int, int]) -> None:
        """Set camera viewport size (width, height)."""
        if self.camera:
            self.camera.resize(value[0], value[1])

    def serialize(self) -> Dict[str, Any]:
        """Serialize the component."""
        data = super().serialize()
        data["follow_owner"] = self.follow_owner
        data["enabled"] = self.enabled
        if self.camera:
            data["zoom"] = self.camera.zoom
            data["rotation"] = self.camera.rotation
        return data

    def deserialize(self, data: Dict[str, Any]) -> None:
        """Deserialize the component."""
        super().deserialize(data)
        if "follow_owner" in data:
            self.follow_owner = data["follow_owner"]
        if "enabled" in data:
            self.enabled = data["enabled"]
        if self.camera:
            if "zoom" in data:
                self.camera.zoom = data["zoom"]
            if "rotation" in data:
                self.camera.rotation = data["rotation"]

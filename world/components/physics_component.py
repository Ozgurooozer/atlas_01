"""
PhysicsComponent for 2D physics.

Provides a way to attach a physics body to an Actor and synchronize
its transform with the physics simulation.

Layer: 3 (World)
Dependencies: world.component, world.transform
"""

from __future__ import annotations
from typing import Any, Callable, Dict, Optional, TYPE_CHECKING

from world.component import Component
from world.transform import TransformComponent

if TYPE_CHECKING:
    from world.actor import Actor


class PhysicsComponent(Component):
    """
    Component that manages a physics body for an Actor.
    
    Attributes:
        mass: Mass of the physics body.
        moment: Moment of inertia of the physics body.
        physics: The PhysicsSystem instance (injected).
        body_id: ID of the physics body in the physics system.
        on_collision: Optional callback for collision events.
    """

    def __init__(self, mass: float = 1.0, moment: float = 100.0, name: str = None) -> None:
        """
        Initialize the PhysicsComponent.
        
        Args:
            mass: Mass of the physics body.
            moment: Moment of inertia.
            name: Optional name.
        """
        super().__init__(name)
        self.mass = mass
        self.moment = moment
        self.physics: Any = None  # Injected by EngineContext
        self.body_id: Optional[int] = None
        self.on_collision: Optional[Callable] = None

    def on_attach(self, owner: Actor) -> None:
        """
        Called when the component is attached to an actor.
        
        Args:
            owner: The actor this component is attached to.
        """
        super().on_attach(owner)
        if self.physics:
            # Create physics body
            self.body_id = self.physics.create_body(self.mass, self.moment)
            
            # Initial sync from transform to physics
            self.sync_to_physics()

    def on_detach(self) -> None:
        """Called when the component is detached from an actor."""
        if self.physics and self.body_id is not None:
            self.physics.remove_body(self.body_id)
            self.body_id = None
        super().on_detach()

    def on_tick(self, dt: float) -> None:
        """
        Update the actor's transform from the physics body.
        
        Args:
            dt: Delta time in seconds.
        """
        if not self.physics or self.body_id is None or not self.owner:
            return

        transform = self.owner.get_component(TransformComponent)
        if transform:
            # Sync from physics to transform
            pos = self.physics.get_body_position(self.body_id)
            transform.position = pos
            
            # Optional: Sync rotation if supported by physics system
            if hasattr(self.physics, "get_body_rotation"):
                transform.rotation = self.physics.get_body_rotation(self.body_id)

    def sync_to_physics(self) -> None:
        """Force synchronize the transform position to the physics body."""
        if not self.physics or self.body_id is None or not self.owner:
            return

        transform = self.owner.get_component(TransformComponent)
        if transform:
            x, y = transform.position
            self.physics.set_body_position(self.body_id, x, y)
            
            if hasattr(self.physics, "set_body_rotation"):
                self.physics.set_body_rotation(self.body_id, transform.rotation)

    @property
    def velocity(self) -> tuple:
        """Get body velocity (vx, vy)."""
        if self.physics and self.body_id is not None:
            return self.physics.get_body_velocity(self.body_id)
        return (0.0, 0.0)

    @velocity.setter
    def velocity(self, value: tuple) -> None:
        """Set body velocity (vx, vy)."""
        if self.physics and self.body_id is not None:
            self.physics.set_body_velocity(self.body_id, value[0], value[1])

    def serialize(self) -> Dict[str, Any]:
        """Serialize the component."""
        data = super().serialize()
        data["mass"] = self.mass
        data["moment"] = self.moment
        return data

    def deserialize(self, data: Dict[str, Any]) -> None:
        """Deserialize the component."""
        super().deserialize(data)
        if "mass" in data:
            self.mass = float(data["mass"])
        if "moment" in data:
            self.moment = float(data["moment"])

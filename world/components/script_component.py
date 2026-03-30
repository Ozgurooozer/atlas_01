"""
ScriptComponent for gameplay logic.

Provides a way to attach custom scripts to an Actor and delegate
lifecycle events to them with error isolation.

Layer: 3 (World)
Dependencies: world.component
"""

from __future__ import annotations
import logging
from typing import Any, Dict, Optional, TYPE_CHECKING

from world.component import Component

if TYPE_CHECKING:
    from world.actor import Actor


class ScriptComponent(Component):
    """
    Component that delegates lifecycle events to a script object.
    
    Attributes:
        script: The script object (duck-typed).
        blackboard: Shared data dictionary for the script.
    """

    def __init__(self, script: Any, blackboard: Optional[Dict[str, Any]] = None, name: str = None) -> None:
        """
        Initialize the ScriptComponent.
        
        Args:
            script: The script object containing lifecycle methods.
            blackboard: Optional shared data dictionary.
            name: Optional name.
        """
        super().__init__(name)
        self.script = script
        self.blackboard = blackboard if blackboard is not None else {}

    def on_attach(self, owner: Actor) -> None:
        """
        Called when the component is attached to an actor.
        
        Args:
            owner: The actor this component is attached to.
        """
        super().on_attach(owner)
        
        # Inject actor and blackboard into script
        try:
            self.script.actor = owner
            self.script.blackboard = self.blackboard
        except Exception:
            logging.exception(f"Failed to inject actor/blackboard into script on {owner.name}")

        # Call on_start if it exists
        if hasattr(self.script, "on_start"):
            try:
                self.script.on_start()
            except Exception:
                logging.exception(f"Error in script.on_start on {owner.name}")

    def on_tick(self, dt: float) -> None:
        """
        Update the script.
        
        Args:
            dt: Delta time in seconds.
        """
        if hasattr(self.script, "on_tick"):
            try:
                self.script.on_tick(dt)
            except Exception:
                logging.exception(f"Error in script.on_tick on {self.owner.name if self.owner else 'Unknown'}")

    def on_detach(self) -> None:
        """Called when the component is detached from an actor."""
        if hasattr(self.script, "on_destroy"):
            try:
                self.script.on_destroy()
            except Exception:
                logging.exception(f"Error in script.on_destroy on {self.owner.name if self.owner else 'Unknown'}")
        super().on_detach()

    def serialize(self) -> Dict[str, Any]:
        """Serialize the component."""
        data = super().serialize()
        # Script itself is usually not serialized directly, but blackboard is
        data["blackboard"] = self.blackboard
        return data

    def deserialize(self, data: Dict[str, Any]) -> None:
        """Deserialize the component."""
        super().deserialize(data)
        if "blackboard" in data:
            self.blackboard.update(data["blackboard"])

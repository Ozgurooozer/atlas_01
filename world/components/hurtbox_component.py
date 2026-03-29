"""
Hurtbox Component.

Defines a damage-receiving area. Connected to HealthComponent.

Layer: 3 (World/Components)
Dependencies: core.object
"""
from __future__ import annotations
from typing import Any, Dict
from world.component import Component


class HurtboxComponent(Component):
    """
    Damage-receiving area linked to HealthComponent.

    A hurtbox defines the area where an entity can receive damage
    from overlapping HitboxComponents.

    Attributes:
        width: Width of the hurtbox in world units.
        height: Height of the hurtbox in world units.
        tag: Identifier tag for the hurtbox (e.g. 'body', 'head').
        is_enabled: Whether the hurtbox can receive damage.
        offset_x: X offset from owner position.
        offset_y: Y offset from owner position.
    """

    def __init__(
        self,
        width: float = 30.0,
        height: float = 50.0,
        tag: str = "body",
    ):
        """
        Initialize the HurtboxComponent.

        Args:
            width: Width of the hurtbox.
            height: Height of the hurtbox.
            tag: Tag identifier for the hurtbox.
        """
        super().__init__()
        self.width: float = width
        self.height: float = height
        self.tag: str = tag
        self.is_enabled: bool = True
        self.offset_x: float = 0.0
        self.offset_y: float = 0.0

    def enable(self) -> None:
        """Enable the hurtbox to receive damage."""
        self.is_enabled = True

    def disable(self) -> None:
        """Disable the hurtbox to prevent damage."""
        self.is_enabled = False

    def serialize(self) -> Dict[str, Any]:
        """Serialize the component."""
        data = super().serialize()
        data.update({
            "width": self.width,
            "height": self.height,
            "tag": self.tag,
            "offset_x": self.offset_x,
            "offset_y": self.offset_y,
        })
        return data

    def deserialize(self, data: Dict[str, Any]) -> None:
        """Deserialize the component."""
        super().deserialize(data)
        self.width = data.get("width", 30.0)
        self.height = data.get("height", 50.0)
        self.tag = data.get("tag", "body")
        self.offset_x = data.get("offset_x", 0.0)
        self.offset_y = data.get("offset_y", 0.0)

"""
Hitbox Component.

Defines an attack hitbox that deals damage on overlap with hurtboxes.

Layer: 3 (World/Components)
Dependencies: core.object
"""
from __future__ import annotations
from typing import Any, Dict
from world.component import Component


class HitboxComponent(Component):
    """
    Attack hitbox for dealing damage.

    A hitbox is activated during attacks and checks for overlap with
    HurtboxComponents. Tracks hit targets to prevent multi-hitting.

    Attributes:
        width: Width of the hitbox in world units.
        height: Height of the hitbox in world units.
        base_damage: Base damage dealt on hit.
        knockback: Knockback force applied on hit.
        tag: Identifier tag for the hitbox (e.g. 'slash', 'projectile').
        is_active: Whether the hitbox is currently active.
        hit_targets: Set of entity IDs already hit this activation.
        hits_max: Maximum number of targets per activation.
        offset_x: X offset from owner position.
        offset_y: Y offset from owner position.
    """

    def __init__(
        self,
        width: float = 40.0,
        height: float = 40.0,
        damage: float = 10.0,
        knockback: float = 0.0,
        tag: str = "attack",
    ):
        """
        Initialize the HitboxComponent.

        Args:
            width: Width of the hitbox.
            height: Height of the hitbox.
            damage: Base damage to deal.
            knockback: Knockback force.
            tag: Tag identifier for the hitbox.
        """
        super().__init__()
        self.width: float = width
        self.height: float = height
        self.base_damage: float = damage
        self.knockback: float = knockback
        self.tag: str = tag
        self.is_active: bool = False
        self.hit_targets: set = set()  # Prevent multi-hit per attack
        self.hits_max: int = 1  # Max targets per activation
        self.offset_x: float = 0.0
        self.offset_y: float = 0.0

    @property
    def can_hit(self) -> bool:
        """Whether the hitbox can still hit targets."""
        return self.is_active and len(self.hit_targets) < self.hits_max

    def activate(self) -> None:
        """Activate the hitbox and clear previous hit targets."""
        self.is_active = True
        self.hit_targets.clear()

    def deactivate(self) -> None:
        """Deactivate the hitbox and clear hit targets."""
        self.is_active = False
        self.hit_targets.clear()

    def register_hit(self, target_id: int) -> bool:
        """
        Register a target as hit. Prevents multi-hitting the same target.

        Args:
            target_id: Unique ID of the hit target.

        Returns:
            True if this is a new hit, False if already registered.
        """
        if target_id in self.hit_targets:
            return False
        self.hit_targets.add(target_id)
        return True

    def serialize(self) -> Dict[str, Any]:
        """Serialize the component."""
        data = super().serialize()
        data.update({
            "width": self.width,
            "height": self.height,
            "base_damage": self.base_damage,
            "knockback": self.knockback,
            "tag": self.tag,
            "hits_max": self.hits_max,
            "offset_x": self.offset_x,
            "offset_y": self.offset_y,
        })
        return data

    def deserialize(self, data: Dict[str, Any]) -> None:
        """Deserialize the component."""
        super().deserialize(data)
        self.width = data.get("width", 40.0)
        self.height = data.get("height", 40.0)
        self.base_damage = data.get("base_damage", 10.0)
        self.knockback = data.get("knockback", 0.0)
        self.tag = data.get("tag", "attack")
        self.hits_max = data.get("hits_max", 1)
        self.offset_x = data.get("offset_x", 0.0)
        self.offset_y = data.get("offset_y", 0.0)

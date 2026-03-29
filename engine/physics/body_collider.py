"""
PhysicsBodyCollider - Köprü: Physics body ↔ AABB collision.

Physics body hareket ettiğinde AABB'yi otomatik günceller.

Layer: 2 (Engine)
Dependencies: engine.physics.physics, engine.physics.aabb, engine.physics.overlap
"""
from __future__ import annotations
from typing import Dict, Optional
from engine.physics.physics import Physics2D
from engine.physics.aabb import AABB
from engine.physics.overlap import OverlapDetector


class PhysicsBodyCollider:
    """
    Binds a Physics2D body to an OverlapDetector collider.

    When tick() is called, reads body position from Physics2D
    and updates the corresponding AABB in OverlapDetector.

    Example:
        >>> physics = Physics2D()
        >>> detector = OverlapDetector()
        >>> bridge = PhysicsBodyCollider(physics, detector)
        >>> body_id = physics.create_body()
        >>> collider_id = bridge.register(body_id, width=32, height=32)
        >>> physics.set_body_position(body_id, 100, 200)
        >>> bridge.sync()  # AABB now at (84, 184, 32, 32)
    """

    def __init__(self, physics: Physics2D, detector: OverlapDetector) -> None:
        self._physics = physics
        self._detector = detector
        # body_id -> (collider_id, half_w, half_h)
        self._bindings: Dict[int, tuple] = {}

    def register(
        self,
        body_id: int,
        width: float,
        height: float,
        tags: list | None = None,
    ) -> int:
        """
        Register a physics body as a collider.

        Creates an AABB centered on the body's current position.

        Args:
            body_id: Physics body ID.
            width: Collider width.
            height: Collider height.
            tags: Optional collision tags.

        Returns:
            Collider ID in the OverlapDetector.
        """
        x, y = self._physics.get_body_position(body_id)
        aabb = AABB.from_center(x, y, width, height)
        collider_id = self._detector.register_collider(aabb, tags)
        self._bindings[body_id] = (collider_id, width / 2, height / 2)
        return collider_id

    def unregister(self, body_id: int) -> None:
        """Remove binding and collider for a body."""
        if body_id not in self._bindings:
            return
        collider_id, _, _ = self._bindings.pop(body_id)
        self._detector.unregister_collider(collider_id)

    def sync(self) -> None:
        """
        Sync all AABB positions from current physics body positions.

        Call this after physics.tick() each frame.
        """
        for body_id, (collider_id, hw, hh) in self._bindings.items():
            try:
                x, y = self._physics.get_body_position(body_id)
            except KeyError:
                continue
            new_aabb = AABB.from_center(x, y, hw * 2, hh * 2)
            self._detector.update_collider(collider_id, new_aabb)

    def get_collider_id(self, body_id: int) -> Optional[int]:
        """Get collider ID for a body."""
        binding = self._bindings.get(body_id)
        return binding[0] if binding else None

    @property
    def binding_count(self) -> int:
        return len(self._bindings)

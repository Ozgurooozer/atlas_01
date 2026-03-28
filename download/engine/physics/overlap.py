"""
Overlap Detection System.

Manages colliders and detects overlaps between them.

Layer: 2 (Engine)
Dependencies: engine.physics.aabb, engine.physics.spatial
"""

from __future__ import annotations
from typing import Callable, Dict, List, Optional, Set, Tuple

from engine.physics.aabb import AABB
from engine.physics.spatial import SpatialHash


class OverlapDetector:
    """
    Overlap detection system using spatial hashing.

    Manages colliders and efficiently detects overlaps using
    broad phase (spatial hash) and narrow phase (AABB overlap).

    Example:
        >>> detector = OverlapDetector()
        >>> id1 = detector.register_collider(AABB(0, 0, 50, 50), tags=["player"])
        >>> id2 = detector.register_collider(AABB(25, 25, 50, 50), tags=["enemy"])
        >>> overlaps = detector.check_overlaps(id1)
        >>> id2 in overlaps
        True

    Attributes:
        on_overlap_begin: Callback when overlap starts (collider_id, other_id).
        on_overlap_end: Callback when overlap ends (collider_id, other_id).
    """

    def __init__(self, cell_size: int = 100):
        """
        Create an overlap detector.

        Args:
            cell_size: Cell size for spatial hashing.
        """
        self._spatial_hash = SpatialHash(cell_size=cell_size)
        self._colliders: Dict[int, Tuple[AABB, List[str]]] = {}
        self._next_id: int = 1
        self._active_overlaps: Dict[int, Set[int]] = {}

        # Callbacks
        self.on_overlap_begin: Optional[Callable[[int, int], None]] = None
        self.on_overlap_end: Optional[Callable[[int, int], None]] = None

    def register_collider(
        self,
        aabb: AABB,
        tags: List[str] | None = None
    ) -> int:
        """
        Register a new collider.

        Args:
            aabb: The AABB for this collider.
            tags: Optional tags for filtering.

        Returns:
            Unique collider ID.
        """
        collider_id = self._next_id
        self._next_id += 1

        self._colliders[collider_id] = (aabb, tags or [])
        self._spatial_hash.insert(collider_id, aabb)
        self._active_overlaps[collider_id] = set()

        return collider_id

    def unregister_collider(self, collider_id: int) -> None:
        """
        Unregister a collider.

        Args:
            collider_id: ID of collider to remove.
        """
        if collider_id not in self._colliders:
            return

        aabb, _ = self._colliders[collider_id]
        self._spatial_hash.remove(collider_id, aabb)
        del self._colliders[collider_id]

        if collider_id in self._active_overlaps:
            del self._active_overlaps[collider_id]

        for other_id, overlaps in self._active_overlaps.items():
            overlaps.discard(collider_id)

    def has_collider(self, collider_id: int) -> bool:
        """
        Check if a collider exists.

        Args:
            collider_id: Collider ID to check.

        Returns:
            True if collider exists.
        """
        return collider_id in self._colliders

    def update_collider(self, collider_id: int, new_aabb: AABB) -> None:
        """
        Update a collider's AABB.

        Args:
            collider_id: Collider ID to update.
            new_aabb: New AABB for the collider.
        """
        if collider_id not in self._colliders:
            return

        old_aabb, tags = self._colliders[collider_id]

        self._spatial_hash.remove(collider_id, old_aabb)
        self._spatial_hash.insert(collider_id, new_aabb)

        self._colliders[collider_id] = (new_aabb, tags)

    def check_overlaps(
        self,
        collider_id: int,
        filter_tags: List[str] | None = None
    ) -> Set[int]:
        """
        Check for overlaps with a specific collider.

        Args:
            collider_id: Collider ID to check.
            filter_tags: Optional tags to filter.

        Returns:
            Set of overlapping collider IDs.
        """
        if collider_id not in self._colliders:
            return set()

        aabb, _ = self._colliders[collider_id]

        # Broad phase: get nearby candidates
        nearby = self._spatial_hash.query_nearby(aabb)

        # Narrow phase: check actual overlaps
        overlaps = set()
        for other_id in nearby:
            if other_id == collider_id:
                continue

            other_aabb, other_tags = self._colliders[other_id]

            # Tag filter
            if filter_tags:
                if not any(tag in other_tags for tag in filter_tags):
                    continue

            # AABB overlap check
            if aabb.overlaps(other_aabb):
                overlaps.add(other_id)

        return overlaps

    def tick(self) -> None:
        """
        Process overlap events for all colliders.

        Calls on_overlap_begin and on_overlap_end callbacks.
        Should be called once per frame.
        """
        new_overlaps: Dict[int, Set[int]] = {}

        for collider_id in self._colliders:
            new_overlaps[collider_id] = self.check_overlaps(collider_id)

        # Detect overlap events
        for collider_id, current_overlaps in new_overlaps.items():
            previous_overlaps = self._active_overlaps.get(collider_id, set())

            # Overlap began
            for other_id in current_overlaps - previous_overlaps:
                if self.on_overlap_begin:
                    self.on_overlap_begin(collider_id, other_id)

            # Overlap ended
            for other_id in previous_overlaps - current_overlaps:
                if self.on_overlap_end:
                    self.on_overlap_end(collider_id, other_id)

        # Update active overlaps
        self._active_overlaps = new_overlaps

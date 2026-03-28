"""
Spatial Hash for Broad Phase Collision Detection.

Optimizes collision detection by dividing space into cells
and only checking nearby colliders.

Layer: 2 (Engine)
Dependencies: engine.physics.aabb
"""

from __future__ import annotations
from typing import Dict, Set, Tuple

from engine.physics.aabb import AABB


class SpatialHash:
    """
    Spatial hash for efficient broad phase collision detection.

    Divides space into a grid of cells. Each AABB is stored in
    all cells it overlaps. Querying for nearby colliders only
    checks the relevant cells.

    Example:
        >>> sh = SpatialHash(cell_size=100)
        >>> sh.insert(1, AABB(0, 0, 50, 50))
        >>> sh.insert(2, AABB(60, 60, 50, 50))
        >>> nearby = sh.query_nearby(AABB(0, 0, 50, 50))
        >>> 1 in nearby and 2 in nearby
        True

    Attributes:
        cell_size: Size of each grid cell.
    """

    def __init__(self, cell_size: int = 100):
        """
        Create a spatial hash.

        Args:
            cell_size: Size of each grid cell.
        """
        self.cell_size = cell_size
        self._cells: Dict[Tuple[int, int], Set[int]] = {}

    def _get_cell(self, x: float, y: float) -> Tuple[int, int]:
        """
        Get cell coordinates for a point.

        Args:
            x: X coordinate.
            y: Y coordinate.

        Returns:
            Tuple of (cell_x, cell_y).
        """
        return (int(x // self.cell_size), int(y // self.cell_size))

    def get_cells_for_aabb(self, aabb: AABB) -> Set[Tuple[int, int]]:
        """
        Get all cells an AABB overlaps.

        Args:
            aabb: The AABB to check.

        Returns:
            Set of cell coordinates.
        """
        min_cell = self._get_cell(aabb.left, aabb.bottom)
        max_cell = self._get_cell(aabb.right, aabb.top)

        cells = set()
        for cx in range(min_cell[0], max_cell[0] + 1):
            for cy in range(min_cell[1], max_cell[1] + 1):
                cells.add((cx, cy))

        return cells

    def insert(self, collider_id: int, aabb: AABB) -> None:
        """
        Insert a collider into the spatial hash.

        Args:
            collider_id: Unique ID for this collider.
            aabb: The collider's AABB.
        """
        cells = self.get_cells_for_aabb(aabb)

        for cell in cells:
            if cell not in self._cells:
                self._cells[cell] = set()
            self._cells[cell].add(collider_id)

    def remove(self, collider_id: int, aabb: AABB) -> None:
        """
        Remove a collider from the spatial hash.

        Args:
            collider_id: ID of collider to remove.
            aabb: The collider's AABB.
        """
        cells = self.get_cells_for_aabb(aabb)

        for cell in cells:
            if cell in self._cells:
                self._cells[cell].discard(collider_id)
                if not self._cells[cell]:
                    del self._cells[cell]

    def query_nearby(self, aabb: AABB) -> Set[int]:
        """
        Find all collider IDs near the given AABB.

        Args:
            aabb: The AABB to query around.

        Returns:
            Set of nearby collider IDs.
        """
        cells = self.get_cells_for_aabb(aabb)
        nearby = set()

        for cell in cells:
            if cell in self._cells:
                nearby.update(self._cells[cell])

        return nearby

    def clear(self) -> None:
        """Clear all colliders from the spatial hash."""
        self._cells.clear()

"""Optimization System - Spatial hashing, frustum culling, batching.

Provides performance optimizations for 2.5D rendering.

Layer: 2 (Engine)
Dependencies: core.vec
"""
from typing import List, Dict, Set, Tuple, Optional
from math import sqrt
from core.vec import Vec2, Vec3
from core.color import Color


class SpatialHash:
    """Spatial hash grid for efficient object queries.
    
    Divides world into cells and stores objects by cell position
    for O(1) neighborhood queries.
    """
    
    def __init__(self, cell_size: float = 100.0):
        """Initialize spatial hash.
        
        Args:
            cell_size: Size of each grid cell in world units
        """
        self.cell_size = cell_size
        self._cells: Dict[Tuple[int, int], Set[int]] = {}
        self._object_cells: Dict[int, Set[Tuple[int, int]]] = {}
        self._object_positions: Dict[int, Vec2] = {}
        self._next_id = 0
    
    def _get_cell(self, x: float, y: float) -> Tuple[int, int]:
        """Get cell coordinates for world position."""
        return (int(x // self.cell_size), int(y // self.cell_size))
    
    def insert(self, position: Vec2) -> int:
        """Insert object into spatial hash.
        
        Args:
            position: Object world position
            
        Returns:
            Object ID for later operations
        """
        obj_id = self._next_id
        self._next_id += 1
        
        cell = self._get_cell(position.x, position.y)
        
        # Add to cell
        if cell not in self._cells:
            self._cells[cell] = set()
        self._cells[cell].add(obj_id)
        
        # Track object
        if obj_id not in self._object_cells:
            self._object_cells[obj_id] = set()
        self._object_cells[obj_id].add(cell)
        
        self._object_positions[obj_id] = position
        
        return obj_id
    
    def remove(self, obj_id: int) -> bool:
        """Remove object from spatial hash.
        
        Args:
            obj_id: Object ID to remove
            
        Returns:
            True if removed, False if not found
        """
        if obj_id not in self._object_cells:
            return False
        
        # Remove from all cells
        for cell in self._object_cells[obj_id]:
            if cell in self._cells:
                self._cells[cell].discard(obj_id)
                if not self._cells[cell]:
                    del self._cells[cell]
        
        # Clean up
        del self._object_cells[obj_id]
        if obj_id in self._object_positions:
            del self._object_positions[obj_id]
        
        return True
    
    def update(self, obj_id: int, new_position: Vec2) -> bool:
        """Update object position.
        
        Args:
            obj_id: Object ID
            new_position: New world position
            
        Returns:
            True if updated, False if not found
        """
        if obj_id not in self._object_cells:
            return False
        
        new_cell = self._get_cell(new_position.x, new_position.y)
        old_cells = self._object_cells[obj_id]
        
        # Check if cell changed
        if new_cell not in old_cells:
            # Remove from old cells
            for cell in list(old_cells):
                if cell in self._cells:
                    self._cells[cell].discard(obj_id)
                    if not self._cells[cell]:
                        del self._cells[cell]
            
            # Add to new cell
            if new_cell not in self._cells:
                self._cells[new_cell] = set()
            self._cells[new_cell].add(obj_id)
            
            # Update tracking
            old_cells.clear()
            old_cells.add(new_cell)
        
        self._object_positions[obj_id] = new_position
        return True
    
    def query_radius(self, center: Vec2, radius: float) -> List[int]:
        """Query objects within radius.
        
        Args:
            center: Query center
            radius: Query radius
            
        Returns:
            List of object IDs within radius
        """
        result = []
        radius_sq = radius * radius
        
        # Calculate cell range
        min_cell = self._get_cell(center.x - radius, center.y - radius)
        max_cell = self._get_cell(center.x + radius, center.y + radius)
        
        # Check cells in range
        for cx in range(min_cell[0], max_cell[0] + 1):
            for cy in range(min_cell[1], max_cell[1] + 1):
                cell = (cx, cy)
                if cell in self._cells:
                    for obj_id in self._cells[cell]:
                        pos = self._object_positions.get(obj_id)
                        if pos:
                            dx = pos.x - center.x
                            dy = pos.y - center.y
                            if dx * dx + dy * dy <= radius_sq:
                                result.append(obj_id)
        
        return result
    
    def query_rect(self, min_x: float, min_y: float, 
                   max_x: float, max_y: float) -> List[int]:
        """Query objects within rectangle."""
        result = []
        
        min_cell = self._get_cell(min_x, min_y)
        max_cell = self._get_cell(max_x, max_y)
        
        for cx in range(min_cell[0], max_cell[0] + 1):
            for cy in range(min_cell[1], max_cell[1] + 1):
                cell = (cx, cy)
                if cell in self._cells:
                    for obj_id in self._cells[cell]:
                        pos = self._object_positions.get(obj_id)
                        if pos and min_x <= pos.x <= max_x and min_y <= pos.y <= max_y:
                            result.append(obj_id)
        
        return result
    
    def get_count(self) -> int:
        """Get total object count."""
        return len(self._object_positions)
    
    def clear(self) -> None:
        """Clear all objects."""
        self._cells.clear()
        self._object_cells.clear()
        self._object_positions.clear()
        self._next_id = 0


class FrustumCuller:
    """Frustum culling for view-based object filtering.
    
    Removes objects outside the visible view area.
    """
    
    def __init__(self, view_width: float, view_height: float):
        """Initialize culler.
        
        Args:
            view_width: View width in world units
            view_height: View height in world units
        """
        self.view_width = view_width
        self.view_height = view_height
        self.view_center = Vec2(0, 0)
        self.padding = 100.0  # Extra padding for safety
    
    def set_view(self, center: Vec2, width: Optional[float] = None,
                 height: Optional[float] = None) -> None:
        """Update view parameters.
        
        Args:
            center: View center position
            width: Optional new width
            height: Optional new height
        """
        self.view_center = center
        if width is not None:
            self.view_width = width
        if height is not None:
            self.view_height = height
    
    def is_visible(self, position: Vec2, size: float = 0.0) -> bool:
        """Check if object is within view frustum.
        
        Args:
            position: Object position
            size: Object size for margin
            
        Returns:
            True if visible
        """
        half_w = (self.view_width / 2) + self.padding + size
        half_h = (self.view_height / 2) + self.padding + size
        
        min_x = self.view_center.x - half_w
        max_x = self.view_center.x + half_w
        min_y = self.view_center.y - half_h
        max_y = self.view_center.y + half_h
        
        return (min_x <= position.x <= max_x and
                min_y <= position.y <= max_y)
    
    def get_view_bounds(self) -> Tuple[float, float, float, float]:
        """Get current view bounds.
        
        Returns:
            (min_x, min_y, max_x, max_y)
        """
        half_w = (self.view_width / 2) + self.padding
        half_h = (self.view_height / 2) + self.padding
        
        return (
            self.view_center.x - half_w,
            self.view_center.y - half_h,
            self.view_center.x + half_w,
            self.view_center.y + half_h
        )
    
    def cull_objects(self, objects: List[Tuple[Vec2, float]]) -> List[int]:
        """Cull objects and return indices of visible ones.
        
        Args:
            objects: List of (position, size) tuples
            
        Returns:
            Indices of visible objects
        """
        visible = []
        for i, (pos, size) in enumerate(objects):
            if self.is_visible(pos, size):
                visible.append(i)
        return visible


class RenderBatch:
    """Batch renderer for efficient draw calls.
    
    Groups similar draw operations to reduce state changes.
    """
    
    def __init__(self, max_size: int = 1000):
        """Initialize batch.
        
        Args:
            max_size: Maximum objects per batch
        """
        self.max_size = max_size
        self.objects: List[Tuple[str, Vec2, float, Color]] = []
        self.batches_created = 0
    
    def add(self, obj_type: str, position: Vec2, size: float, color) -> bool:
        """Add object to batch.
        
        Args:
            obj_type: Object type/category
            position: Object position
            size: Object size
            color: Object color
            
        Returns:
            True if added, False if batch full
        """
        if len(self.objects) >= self.max_size:
            return False
        
        self.objects.append((obj_type, position, size, color))
        return True
    
    def flush(self) -> List[Tuple[str, Vec2, float, Color]]:
        """Flush batch and return objects."""
        result = self.objects.copy()
        self.objects.clear()
        self.batches_created += 1
        return result
    
    def is_full(self) -> bool:
        """Check if batch is full."""
        return len(self.objects) >= self.max_size
    
    def is_empty(self) -> bool:
        """Check if batch is empty."""
        return len(self.objects) == 0
    
    def get_count(self) -> int:
        """Get current object count."""
        return len(self.objects)


class BatchedRenderer:
    """Manages multiple render batches."""
    
    def __init__(self, batch_size: int = 1000):
        """Initialize batched renderer.
        
        Args:
            batch_size: Maximum objects per batch
        """
        self.batch_size = batch_size
        self.batches: List[RenderBatch] = []
        self.current_batch: Optional[RenderBatch] = None
        self._ensure_batch()
    
    def _ensure_batch(self) -> None:
        """Ensure we have a non-full batch."""
        if self.current_batch is None or self.current_batch.is_full():
            self.current_batch = RenderBatch(self.batch_size)
            self.batches.append(self.current_batch)
    
    def submit(self, obj_type: str, position: Vec2, size: float, color) -> None:
        """Submit object for rendering.
        
        Args:
            obj_type: Object type
            position: Object position
            size: Object size
            color: Object color
        """
        self._ensure_batch()
        
        if not self.current_batch.add(obj_type, position, size, color):
            # Batch is full, create new one
            self._ensure_batch()
            self.current_batch.add(obj_type, position, size, color)
    
    def get_all_batches(self) -> List[RenderBatch]:
        """Get all non-empty batches."""
        return [b for b in self.batches if not b.is_empty()]
    
    def flush_all(self) -> List[List[Tuple]]:
        """Flush all batches."""
        result = []
        for batch in self.batches:
            if not batch.is_empty():
                result.append(batch.flush())
        self.batches.clear()
        self.current_batch = None
        self._ensure_batch()
        return result
    
    def get_stats(self) -> Dict[str, int]:
        """Get rendering statistics."""
        total_objects = sum(b.get_count() for b in self.batches)
        return {
            'batch_count': len(self.batches),
            'total_objects': total_objects,
            'max_batch_size': self.batch_size
        }
    
    def clear(self) -> None:
        """Clear all batches."""
        self.batches.clear()
        self.current_batch = None
        self._ensure_batch()


class OptimizationManager:
    """Central optimization manager combining all techniques."""
    
    def __init__(self, cell_size: float = 100.0, batch_size: int = 1000):
        """Initialize optimization manager.
        
        Args:
            cell_size: Spatial hash cell size
            batch_size: Render batch size
        """
        self.spatial_hash = SpatialHash(cell_size)
        self.culler = FrustumCuller(1024, 768)
        self.batcher = BatchedRenderer(batch_size)
        
        self.stats = {
            'culled_count': 0,
            'visible_count': 0,
            'batches_created': 0
        }
    
    def register_object(self, position: Vec2) -> int:
        """Register object for optimization.
        
        Args:
            position: Object position
            
        Returns:
            Object ID
        """
        return self.spatial_hash.insert(position)
    
    def update_object(self, obj_id: int, position: Vec2) -> bool:
        """Update object position.
        
        Args:
            obj_id: Object ID
            position: New position
            
        Returns:
            True if updated
        """
        return self.spatial_hash.update(obj_id, position)
    
    def remove_object(self, obj_id: int) -> bool:
        """Remove object from optimization."""
        return self.spatial_hash.remove(obj_id)
    
    def prepare_frame(self, view_center: Vec2, view_size: Tuple[float, float]) -> None:
        """Prepare frame with culling and batching.
        
        Args:
            view_center: Camera/view center
            view_size: View width and height
        """
        # Update culler
        self.culler.set_view(view_center, view_size[0], view_size[1])
        
        # Reset stats
        self.stats['culled_count'] = 0
        self.stats['visible_count'] = 0
    
    def submit_if_visible(self, obj_id: int, obj_type: str, size: float, color) -> bool:
        """Submit object if visible.
        
        Args:
            obj_id: Object ID
            obj_type: Object type
            size: Object size
            color: Object color
            
        Returns:
            True if visible and submitted
        """
        position = self.spatial_hash._object_positions.get(obj_id)
        if position is None:
            return False
        
        if self.culler.is_visible(position, size):
            self.batcher.submit(obj_type, position, size, color)
            self.stats['visible_count'] += 1
            return True
        else:
            self.stats['culled_count'] += 1
            return False
    
    def get_stats(self) -> Dict[str, int]:
        """Get optimization statistics."""
        batch_stats = self.batcher.get_stats()
        return {
            **self.stats,
            **batch_stats,
            'spatial_objects': self.spatial_hash.get_count()
        }
    
    def clear(self) -> None:
        """Clear all optimization data."""
        self.spatial_hash.clear()
        self.batcher.clear()
        self.stats = {
            'culled_count': 0,
            'visible_count': 0,
            'batches_created': 0
        }

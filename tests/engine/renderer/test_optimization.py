"""Tests for Optimization system.

Test-First Development for Optimization (Days 18-19)
"""
from engine.renderer.optimization import (
    SpatialHash, FrustumCuller,
    RenderBatch, BatchedRenderer,
    OptimizationManager
)
from core.vec import Vec2


class TestSpatialHash:
    """Test spatial hash grid."""
    
    def test_initialization(self):
        """Test spatial hash creation."""
        sh = SpatialHash(cell_size=50.0)
        assert sh.cell_size == 50.0
        assert sh.get_count() == 0
    
    def test_insert(self):
        """Test object insertion."""
        sh = SpatialHash(cell_size=100.0)
        
        obj_id = sh.insert(Vec2(50, 50))
        
        assert obj_id == 0
        assert sh.get_count() == 1
    
    def test_insert_multiple(self):
        """Test multiple insertions."""
        sh = SpatialHash(cell_size=100.0)
        
        id1 = sh.insert(Vec2(10, 10))
        id2 = sh.insert(Vec2(20, 20))
        id3 = sh.insert(Vec2(30, 30))
        
        assert id1 == 0
        assert id2 == 1
        assert id3 == 2
        assert sh.get_count() == 3
    
    def test_remove(self):
        """Test object removal."""
        sh = SpatialHash(cell_size=100.0)
        obj_id = sh.insert(Vec2(50, 50))
        
        result = sh.remove(obj_id)
        
        assert result is True
        assert sh.get_count() == 0
    
    def test_remove_missing(self):
        """Test removing non-existent object."""
        sh = SpatialHash(cell_size=100.0)
        
        result = sh.remove(999)
        
        assert result is False
    
    def test_update_position(self):
        """Test position update."""
        sh = SpatialHash(cell_size=100.0)
        obj_id = sh.insert(Vec2(50, 50))
        
        result = sh.update(obj_id, Vec2(150, 150))
        
        assert result is True
    
    def test_update_missing(self):
        """Test updating non-existent object."""
        sh = SpatialHash(cell_size=100.0)
        
        result = sh.update(999, Vec2(50, 50))
        
        assert result is False
    
    def test_query_radius(self):
        """Test radius query."""
        sh = SpatialHash(cell_size=100.0)
        
        # Insert objects at different positions
        sh.insert(Vec2(0, 0))      # Near center
        sh.insert(Vec2(50, 50))    # Near center
        sh.insert(Vec2(500, 500))  # Far away
        
        # Query near center
        results = sh.query_radius(Vec2(0, 0), 100)
        
        assert len(results) >= 2
    
    def test_query_radius_excludes_far(self):
        """Test radius query excludes distant objects."""
        sh = SpatialHash(cell_size=100.0)
        
        id_near = sh.insert(Vec2(50, 50))
        id_far = sh.insert(Vec2(500, 500))
        
        results = sh.query_radius(Vec2(0, 0), 100)
        
        assert id_near in results
        assert id_far not in results
    
    def test_query_rect(self):
        """Test rectangle query."""
        sh = SpatialHash(cell_size=100.0)
        
        sh.insert(Vec2(50, 50))   # Inside rect
        sh.insert(Vec2(150, 150)) # Inside rect
        sh.insert(Vec2(500, 500)) # Outside rect
        
        results = sh.query_rect(0, 0, 200, 200)
        
        assert len(results) == 2
    
    def test_clear(self):
        """Test clearing all objects."""
        sh = SpatialHash(cell_size=100.0)
        sh.insert(Vec2(10, 10))
        sh.insert(Vec2(20, 20))
        
        sh.clear()
        
        assert sh.get_count() == 0


class TestFrustumCuller:
    """Test frustum culling."""
    
    def test_initialization(self):
        """Test culler creation."""
        culler = FrustumCuller(1024, 768)
        
        assert culler.view_width == 1024
        assert culler.view_height == 768
    
    def test_is_visible_center(self):
        """Test object at center is visible."""
        culler = FrustumCuller(100, 100)
        culler.set_view(Vec2(0, 0))
        
        assert culler.is_visible(Vec2(0, 0)) is True
    
    def test_is_visible_outside(self):
        """Test object outside view is not visible."""
        culler = FrustumCuller(100, 100)
        culler.set_view(Vec2(0, 0))
        
        assert culler.is_visible(Vec2(1000, 1000)) is False
    
    def test_is_visible_with_padding(self):
        """Test padding extends visible area."""
        culler = FrustumCuller(100, 100)
        culler.set_view(Vec2(0, 0))
        culler.padding = 50
        
        # Just outside normal view but inside padding
        assert culler.is_visible(Vec2(60, 0)) is True
    
    def test_set_view(self):
        """Test updating view."""
        culler = FrustumCuller(100, 100)
        
        culler.set_view(Vec2(100, 100), 200, 200)
        
        assert culler.view_center.x == 100
        assert culler.view_width == 200
    
    def test_get_view_bounds(self):
        """Test getting view bounds."""
        culler = FrustumCuller(100, 100)
        culler.set_view(Vec2(0, 0))
        
        bounds = culler.get_view_bounds()
        
        assert len(bounds) == 4
        assert bounds[0] < bounds[2]  # min_x < max_x
        assert bounds[1] < bounds[3]  # min_y < max_y
    
    def test_cull_objects(self):
        """Test culling multiple objects."""
        culler = FrustumCuller(100, 100)
        culler.set_view(Vec2(0, 0))
        
        objects = [
            (Vec2(0, 0), 10),      # Visible
            (Vec2(50, 50), 10),    # Visible
            (Vec2(500, 500), 10),  # Culled
        ]
        
        visible = culler.cull_objects(objects)
        
        assert len(visible) == 2
        assert 0 in visible
        assert 1 in visible
        assert 2 not in visible


class TestRenderBatch:
    """Test render batching."""
    
    def test_initialization(self):
        """Test batch creation."""
        batch = RenderBatch(max_size=100)
        
        assert batch.max_size == 100
        assert batch.is_empty() is True
    
    def test_add_object(self):
        """Test adding object to batch."""
        batch = RenderBatch(max_size=10)
        
        result = batch.add('sprite', Vec2(10, 20), 32, None)
        
        assert result is True
        assert batch.get_count() == 1
    
    def test_batch_full(self):
        """Test batch rejects when full."""
        batch = RenderBatch(max_size=2)
        batch.add('sprite', Vec2(0, 0), 32, None)
        batch.add('sprite', Vec2(0, 0), 32, None)
        
        result = batch.add('sprite', Vec2(0, 0), 32, None)
        
        assert result is False
    
    def test_flush(self):
        """Test flushing batch."""
        batch = RenderBatch(max_size=10)
        batch.add('sprite', Vec2(10, 20), 32, None)
        batch.add('sprite', Vec2(30, 40), 32, None)
        
        objects = batch.flush()
        
        assert len(objects) == 2
        assert batch.is_empty() is True
        assert batch.batches_created == 1
    
    def test_is_full(self):
        """Test full detection."""
        batch = RenderBatch(max_size=1)
        batch.add('sprite', Vec2(0, 0), 32, None)
        
        assert batch.is_full() is True


class TestBatchedRenderer:
    """Test batched renderer."""
    
    def test_initialization(self):
        """Test renderer creation."""
        renderer = BatchedRenderer(batch_size=100)
        
        assert renderer.batch_size == 100
        assert len(renderer.batches) == 1  # Initial batch
    
    def test_submit(self):
        """Test submitting object."""
        renderer = BatchedRenderer(batch_size=10)
        
        renderer.submit('sprite', Vec2(0, 0), 32, None)
        
        stats = renderer.get_stats()
        assert stats['total_objects'] == 1
    
    def test_auto_batch_creation(self):
        """Test automatic batch creation when full."""
        renderer = BatchedRenderer(batch_size=2)
        
        renderer.submit('sprite', Vec2(0, 0), 32, None)
        renderer.submit('sprite', Vec2(0, 0), 32, None)
        renderer.submit('sprite', Vec2(0, 0), 32, None)  # Triggers new batch
        
        stats = renderer.get_stats()
        assert stats['batch_count'] == 2
    
    def test_flush_all(self):
        """Test flushing all batches."""
        renderer = BatchedRenderer(batch_size=10)
        renderer.submit('sprite', Vec2(0, 0), 32, None)
        renderer.submit('sprite', Vec2(10, 10), 32, None)
        
        batches = renderer.flush_all()
        
        assert len(batches) == 1
        assert len(batches[0]) == 2
    
    def test_clear(self):
        """Test clearing all."""
        renderer = BatchedRenderer(batch_size=10)
        renderer.submit('sprite', Vec2(0, 0), 32, None)
        
        renderer.clear()
        
        stats = renderer.get_stats()
        assert stats['total_objects'] == 0


class TestOptimizationManager:
    """Test combined optimization manager."""
    
    def test_initialization(self):
        """Test manager creation."""
        opt = OptimizationManager(cell_size=100, batch_size=1000)
        
        assert opt.spatial_hash is not None
        assert opt.culler is not None
        assert opt.batcher is not None
    
    def test_register_object(self):
        """Test object registration."""
        opt = OptimizationManager()
        
        obj_id = opt.register_object(Vec2(50, 50))
        
        assert obj_id == 0
    
    def test_update_object(self):
        """Test object update."""
        opt = OptimizationManager()
        obj_id = opt.register_object(Vec2(50, 50))
        
        result = opt.update_object(obj_id, Vec2(100, 100))
        
        assert result is True
    
    def test_remove_object(self):
        """Test object removal."""
        opt = OptimizationManager()
        obj_id = opt.register_object(Vec2(50, 50))
        
        result = opt.remove_object(obj_id)
        
        assert result is True
    
    def test_prepare_frame(self):
        """Test frame preparation."""
        opt = OptimizationManager()
        opt.prepare_frame(Vec2(0, 0), (1024, 768))
        
        # Stats should be reset
        assert opt.stats['culled_count'] == 0
        assert opt.stats['visible_count'] == 0
    
    def test_submit_if_visible(self):
        """Test submitting visible objects."""
        opt = OptimizationManager()
        obj_id = opt.register_object(Vec2(0, 0))
        
        opt.prepare_frame(Vec2(0, 0), (100, 100))
        result = opt.submit_if_visible(obj_id, 'sprite', 10, None)
        
        assert result is True
        assert opt.stats['visible_count'] == 1
    
    def test_cull_invisible(self):
        """Test culling invisible objects."""
        opt = OptimizationManager()
        obj_id = opt.register_object(Vec2(1000, 1000))
        
        opt.prepare_frame(Vec2(0, 0), (100, 100))
        result = opt.submit_if_visible(obj_id, 'sprite', 10, None)
        
        assert result is False
        assert opt.stats['culled_count'] == 1
    
    def test_get_stats(self):
        """Test statistics."""
        opt = OptimizationManager()
        opt.register_object(Vec2(0, 0))
        opt.register_object(Vec2(50, 50))
        
        stats = opt.get_stats()
        
        assert 'spatial_objects' in stats
        assert stats['spatial_objects'] == 2
    
    def test_clear(self):
        """Test clearing all data."""
        opt = OptimizationManager()
        opt.register_object(Vec2(0, 0))
        
        opt.clear()
        
        assert opt.spatial_hash.get_count() == 0

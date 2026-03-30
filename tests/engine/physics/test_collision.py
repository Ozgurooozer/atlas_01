"""
Collision Detection Tests.

Tests for AABB collision, overlap detection, and spatial hashing.

Layer: 2 (Engine)
"""

import pytest


class TestAABB:
    """Tests for AABB (Axis-Aligned Bounding Box)."""

    def test_aabb_creation(self):
        """Test creating an AABB."""
        from engine.physics.aabb import AABB
        
        aabb = AABB(x=0, y=0, width=100, height=50)
        
        assert aabb.x == 0
        assert aabb.y == 0
        assert aabb.width == 100
        assert aabb.height == 50

    def test_aabb_from_center(self):
        """Test creating AABB from center point."""
        from engine.physics.aabb import AABB
        
        aabb = AABB.from_center(center_x=100, center_y=100, width=50, height=50)
        
        assert aabb.x == 75  # 100 - 25
        assert aabb.y == 75  # 100 - 25
        assert aabb.width == 50
        assert aabb.height == 50

    def test_aabb_bounds(self):
        """Test AABB boundary properties."""
        from engine.physics.aabb import AABB
        
        aabb = AABB(x=10, y=20, width=100, height=50)
        
        # Left, Right, Bottom, Top
        assert aabb.left == 10
        assert aabb.right == 110
        assert aabb.bottom == 20
        assert aabb.top == 70

    def test_aabb_center(self):
        """Test AABB center property."""
        from engine.physics.aabb import AABB
        
        aabb = AABB(x=0, y=0, width=100, height=50)
        
        assert aabb.center_x == 50
        assert aabb.center_y == 25

    def test_aabb_contains_point(self):
        """Test point containment."""
        from engine.physics.aabb import AABB
        
        aabb = AABB(x=0, y=0, width=100, height=100)
        
        assert aabb.contains_point(50, 50) is True
        assert aabb.contains_point(0, 0) is True
        assert aabb.contains_point(100, 100) is True
        assert aabb.contains_point(150, 50) is False
        assert aabb.contains_point(50, 150) is False

    def test_aabb_overlaps_aabb(self):
        """Test AABB vs AABB overlap."""
        from engine.physics.aabb import AABB
        
        aabb1 = AABB(x=0, y=0, width=100, height=100)
        aabb2 = AABB(x=50, y=50, width=100, height=100)
        aabb3 = AABB(x=200, y=200, width=100, height=100)
        
        assert aabb1.overlaps(aabb2) is True
        assert aabb1.overlaps(aabb3) is False
        assert aabb2.overlaps(aabb3) is False

    def test_aabb_no_overlap_edge_touching(self):
        """Test that edge-touching AABBs don't overlap."""
        from engine.physics.aabb import AABB
        
        aabb1 = AABB(x=0, y=0, width=100, height=100)
        aabb2 = AABB(x=100, y=0, width=100, height=100)  # Touches edge
        
        assert aabb1.overlaps(aabb2) is False


class TestOverlapDetector:
    """Tests for overlap detection system."""

    def test_overlap_detector_creation(self):
        """Test creating an overlap detector."""
        from engine.physics.overlap import OverlapDetector
        
        detector = OverlapDetector()
        
        assert detector is not None

    def test_register_collider(self):
        """Test registering a collider."""
        from engine.physics.aabb import AABB
        from engine.physics.overlap import OverlapDetector
        
        detector = OverlapDetector()
        aabb = AABB(x=0, y=0, width=50, height=50)
        
        collider_id = detector.register_collider(aabb, tags=["player"])
        
        assert collider_id is not None
        assert detector.has_collider(collider_id)

    def test_unregister_collider(self):
        """Test unregistering a collider."""
        from engine.physics.aabb import AABB
        from engine.physics.overlap import OverlapDetector
        
        detector = OverlapDetector()
        aabb = AABB(x=0, y=0, width=50, height=50)
        
        collider_id = detector.register_collider(aabb)
        detector.unregister_collider(collider_id)
        
        assert detector.has_collider(collider_id) is False

    def test_check_overlaps(self):
        """Test checking for overlaps."""
        from engine.physics.aabb import AABB
        from engine.physics.overlap import OverlapDetector
        
        detector = OverlapDetector()
        
        aabb1 = AABB(x=0, y=0, width=100, height=100)
        aabb2 = AABB(x=50, y=50, width=100, height=100)
        
        id1 = detector.register_collider(aabb1, tags=["player"])
        id2 = detector.register_collider(aabb2, tags=["enemy"])
        
        overlaps = detector.check_overlaps(id1)
        
        assert len(overlaps) == 1
        assert id2 in overlaps

    def test_check_overlaps_by_tag(self):
        """Test checking overlaps by tag."""
        from engine.physics.aabb import AABB
        from engine.physics.overlap import OverlapDetector
        
        detector = OverlapDetector()
        
        aabb1 = AABB(x=0, y=0, width=100, height=100)
        aabb2 = AABB(x=50, y=50, width=100, height=100)
        aabb3 = AABB(x=200, y=200, width=100, height=100)
        
        id1 = detector.register_collider(aabb1, tags=["player"])
        id2 = detector.register_collider(aabb2, tags=["enemy"])
        id3 = detector.register_collider(aabb3, tags=["enemy"])
        
        # Check player vs enemies
        overlaps = detector.check_overlaps(id1, filter_tags=["enemy"])
        
        assert len(overlaps) == 1
        assert id2 in overlaps
        assert id3 not in overlaps

    def test_update_collider_position(self):
        """Test updating collider position."""
        from engine.physics.aabb import AABB
        from engine.physics.overlap import OverlapDetector
        
        detector = OverlapDetector()
        
        aabb1 = AABB(x=0, y=0, width=50, height=50)
        aabb2 = AABB(x=100, y=100, width=50, height=50)
        
        id1 = detector.register_collider(aabb1)
        id2 = detector.register_collider(aabb2)
        
        # No overlap initially
        assert len(detector.check_overlaps(id1)) == 0
        
        # Move aabb1 to overlap aabb2
        detector.update_collider(id1, AABB(x=90, y=90, width=50, height=50))
        
        # Now should overlap
        assert len(detector.check_overlaps(id1)) == 1


class TestOverlapEvents:
    """Tests for overlap event callbacks."""

    def test_on_overlap_begin(self):
        """Test on_overlap_begin callback."""
        from engine.physics.aabb import AABB
        from engine.physics.overlap import OverlapDetector
        
        detector = OverlapDetector()
        events = []
        
        def on_overlap(collider_id, other_id):
            events.append(("begin", collider_id, other_id))
        
        detector.on_overlap_begin = on_overlap
        
        aabb1 = AABB(x=0, y=0, width=100, height=100)
        aabb2 = AABB(x=50, y=50, width=100, height=100)
        
        id1 = detector.register_collider(aabb1)
        id2 = detector.register_collider(aabb2)
        
        detector.tick()
        
        assert len(events) == 2  # Both colliders should get events

    def test_on_overlap_end(self):
        """Test on_overlap_end callback when colliders separate."""
        from engine.physics.aabb import AABB
        from engine.physics.overlap import OverlapDetector
        
        detector = OverlapDetector()
        events = []
        
        def on_overlap_end(collider_id, other_id):
            events.append(("end", collider_id, other_id))
        
        detector.on_overlap_end = on_overlap_end
        
        aabb1 = AABB(x=0, y=0, width=100, height=100)
        aabb2 = AABB(x=50, y=50, width=100, height=100)
        
        id1 = detector.register_collider(aabb1)
        id2 = detector.register_collider(aabb2)
        
        # First tick - overlap begins
        detector.tick()
        
        # Move apart
        detector.update_collider(id1, AABB(x=0, y=0, width=50, height=50))
        detector.update_collider(id2, AABB(x=200, y=200, width=50, height=50))
        
        # Second tick - overlap ends
        detector.tick()
        
        assert len(events) == 2  # Both should get end events


class TestSpatialHash:
    """Tests for spatial hash (broad phase optimization)."""

    def test_spatial_hash_creation(self):
        """Test creating a spatial hash."""
        from engine.physics.spatial import SpatialHash
        
        sh = SpatialHash(cell_size=100)
        
        assert sh.cell_size == 100

    def test_insert_aabb(self):
        """Test inserting AABB into spatial hash."""
        from engine.physics.aabb import AABB
        from engine.physics.spatial import SpatialHash
        
        sh = SpatialHash(cell_size=100)
        aabb = AABB(x=50, y=50, width=100, height=100)
        
        sh.insert(1, aabb)
        
        # Should be in multiple cells
        cells = sh.get_cells_for_aabb(aabb)
        assert len(cells) > 0

    def test_query_nearby(self):
        """Test querying nearby colliders."""
        from engine.physics.aabb import AABB
        from engine.physics.spatial import SpatialHash
        
        sh = SpatialHash(cell_size=100)
        
        aabb1 = AABB(x=0, y=0, width=50, height=50)
        aabb2 = AABB(x=60, y=60, width=50, height=50)
        aabb3 = AABB(x=500, y=500, width=50, height=50)
        
        sh.insert(1, aabb1)
        sh.insert(2, aabb2)
        sh.insert(3, aabb3)
        
        nearby = sh.query_nearby(aabb1)
        
        assert 1 in nearby
        assert 2 in nearby
        assert 3 not in nearby  # Too far away

    def test_clear(self):
        """Test clearing spatial hash."""
        from engine.physics.aabb import AABB
        from engine.physics.spatial import SpatialHash
        
        sh = SpatialHash(cell_size=100)
        aabb = AABB(x=0, y=0, width=50, height=50)
        
        sh.insert(1, aabb)
        sh.clear()
        
        nearby = sh.query_nearby(aabb)
        assert len(nearby) == 0

    def test_remove(self):
        """Test removing from spatial hash."""
        from engine.physics.aabb import AABB
        from engine.physics.spatial import SpatialHash
        
        sh = SpatialHash(cell_size=100)
        
        aabb1 = AABB(x=0, y=0, width=50, height=50)
        aabb2 = AABB(x=60, y=60, width=50, height=50)
        
        sh.insert(1, aabb1)
        sh.insert(2, aabb2)
        
        sh.remove(1, aabb1)
        
        nearby = sh.query_nearby(aabb2)
        assert 1 not in nearby
        assert 2 in nearby

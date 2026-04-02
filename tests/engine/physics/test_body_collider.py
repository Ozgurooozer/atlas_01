"""Tests for PhysicsBodyCollider bridge."""
from engine.physics.physics import Physics2D
from engine.physics.overlap import OverlapDetector
from engine.physics.body_collider import PhysicsBodyCollider


class TestPhysicsBodyCollider:
    def setup_method(self):
        self.physics = Physics2D()
        self.detector = OverlapDetector()
        self.bridge = PhysicsBodyCollider(self.physics, self.detector)

    def test_register(self):
        body_id = self.physics.create_body()
        collider_id = self.bridge.register(body_id, width=32, height=32)
        assert collider_id is not None
        assert self.detector.has_collider(collider_id)
        assert self.bridge.binding_count == 1

    def test_sync_updates_aabb(self):
        body_id = self.physics.create_body()
        collider_id = self.bridge.register(body_id, width=32, height=32)

        # Move body
        self.physics.set_body_position(body_id, 100, 200)
        self.bridge.sync()

        # Check overlap with a box at new position
        from engine.physics.aabb import AABB
        nearby = self.detector._spatial_hash.query_nearby(
            AABB.from_center(100, 200, 10, 10)
        )
        assert collider_id in nearby

    def test_unregister(self):
        body_id = self.physics.create_body()
        collider_id = self.bridge.register(body_id, width=32, height=32)
        self.bridge.unregister(body_id)
        assert not self.detector.has_collider(collider_id)
        assert self.bridge.binding_count == 0

    def test_get_collider_id(self):
        body_id = self.physics.create_body()
        collider_id = self.bridge.register(body_id, width=32, height=32)
        assert self.bridge.get_collider_id(body_id) == collider_id

    def test_sync_after_physics_tick(self):
        body_id = self.physics.create_body()
        self.physics.set_body_position(body_id, 0, 0)
        self.physics.set_body_velocity(body_id, 100, 0)
        collider_id = self.bridge.register(body_id, width=10, height=10)

        self.physics.tick(1.0)  # body moves to ~(100, -900)
        self.bridge.sync()

        from engine.physics.aabb import AABB
        nearby = self.detector._spatial_hash.query_nearby(
            AABB.from_center(100, -900, 5, 5)
        )
        assert collider_id in nearby

    def test_two_bodies_collide_after_sync(self):
        b1 = self.physics.create_body()
        b2 = self.physics.create_body()
        self.physics.set_body_position(b1, 0, 0)
        self.physics.set_body_position(b2, 200, 0)

        c1 = self.bridge.register(b1, width=50, height=50)
        c2 = self.bridge.register(b2, width=50, height=50)

        # Move b2 close to b1
        self.physics.set_body_position(b2, 20, 0)
        self.bridge.sync()

        overlaps = self.detector.check_overlaps(c1)
        assert c2 in overlaps

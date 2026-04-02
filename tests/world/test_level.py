"""Tests for Level system.

class MockObject:
    """Simple mock for testing."""
    def __init__(self):
        self.call_count = 0
        self.call_args = None

class MockCallback:
    """Simple mock for testing."""
    def __init__(self):
        self.call_count = 0
        self.call_args = None

    def __call__(self, *args, **kwargs):
        self.call_count += 1
        self.call_args = (args, kwargs)


Test-First Development for Level management
"""
import pytest
from world.level import Level, LevelManager, SpawnPoint, TileMap
from world.actor import Actor
from core.vec import Vec3


class TestSpawnPoint:
    """Test spawn point."""
    
    def test_initialization(self):
        """Test spawn point creation."""
        point = SpawnPoint(Vec3(100, 200, 0), "player_start")
        
        assert point.position.x == 100
        assert point.position.y == 200
        assert point.name == "player_start"
    
    def test_initialization_defaults(self):
        """Test spawn point with defaults."""
        point = SpawnPoint(Vec3(0, 0, 0))
        
        assert point.name == "default"


class TestTileMap:
    """Test tile map."""
    
    def test_initialization(self):
        """Test tile map creation."""
        tilemap = TileMap(width=10, height=8, tile_size=32)
        
        assert tilemap.width == 10
        assert tilemap.height == 8
        assert tilemap.tile_size == 32
    
    def test_set_get_tile(self):
        """Test setting and getting tiles."""
        tilemap = TileMap(5, 5)
        
        tilemap.set_tile(2, 3, "grass")
        
        assert tilemap.get_tile(2, 3) == "grass"
    
    def test_get_tile_default(self):
        """Test getting unset tile returns default."""
        tilemap = TileMap(5, 5, default_tile="empty")
        
        assert tilemap.get_tile(0, 0) == "empty"
    
    def test_get_tile_out_of_bounds(self):
        """Test out of bounds returns None."""
        tilemap = TileMap(5, 5)
        
        assert tilemap.get_tile(10, 10) is None
    
    def test_set_tile_out_of_bounds(self):
        """Test setting out of bounds is ignored."""
        tilemap = TileMap(5, 5)
        
        tilemap.set_tile(10, 10, "grass")  # Should not raise
        
        assert tilemap.get_tile(10, 10) is None
    
    def test_world_to_tile(self):
        """Test world to tile conversion."""
        tilemap = TileMap(10, 10, tile_size=32)
        
        tx, ty = tilemap.world_to_tile(64, 96)
        
        assert tx == 2
        assert ty == 3
    
    def test_tile_to_world(self):
        """Test tile to world conversion."""
        tilemap = TileMap(10, 10, tile_size=32)
        
        x, y = tilemap.tile_to_world(2, 3)
        
        assert x == 64
        assert y == 96
    
    def test_get_neighbors(self):
        """Test getting neighboring tiles."""
        tilemap = TileMap(5, 5)
        tilemap.set_tile(1, 2, "center")
        tilemap.set_tile(0, 2, "left")
        tilemap.set_tile(2, 2, "right")
        tilemap.set_tile(1, 1, "up")
        tilemap.set_tile(1, 3, "down")
        
        neighbors = tilemap.get_neighbors(1, 2)
        
        assert neighbors["left"] == "left"
        assert neighbors["right"] == "right"
        assert neighbors["up"] == "up"
        assert neighbors["down"] == "down"


class TestLevel:
    """Test level."""
    
    def test_initialization(self):
        """Test level creation."""
        level = Level(name="test_level")
        
        assert level.name == "test_level"
        assert level.actors == []
        assert level.is_loaded is False
    
    def test_add_actor(self):
        """Test adding actor to level."""
        level = Level()
        actor = MagicMock(spec=Actor)
        
        level.add_actor(actor)
        
        assert actor in level.actors
    
    def test_remove_actor(self):
        """Test removing actor from level."""
        level = Level()
        actor = MagicMock(spec=Actor)
        level.add_actor(actor)
        
        level.remove_actor(actor)
        
        assert actor not in level.actors
    
    def test_add_spawn_point(self):
        """Test adding spawn point."""
        level = Level()
        point = SpawnPoint(Vec3(100, 200, 0), "start")
        
        level.add_spawn_point(point)
        
        assert "start" in level.spawn_points
        assert level.spawn_points["start"] == point
    
    def test_get_spawn_point(self):
        """Test getting spawn point."""
        level = Level()
        point = SpawnPoint(Vec3(100, 200, 0), "start")
        level.add_spawn_point(point)
        
        retrieved = level.get_spawn_point("start")
        
        assert retrieved == point
    
    def test_get_spawn_point_missing(self):
        """Test getting missing spawn point returns None."""
        level = Level()
        
        assert level.get_spawn_point("nonexistent") is None
    
    def test_set_tile_map(self):
        """Test setting tile map."""
        level = Level()
        tilemap = TileMap(10, 10)
        
        level.set_tile_map(tilemap)
        
        assert level.tile_map == tilemap
    
    def test_load_unload(self):
        """Test load and unload."""
        level = Level()
        
        level.load()
        assert level.is_loaded is True
        
        level.unload()
        assert level.is_loaded is False
    
    def test_load_calls_on_load(self):
        """Test load calls on_load callback."""
        level = Level()
        on_load = MockCallback()
        level.on_load = on_load
        
        level.load()
        
        on_load.assert_called_once()
    
    def test_update(self):
        """Test update ticks actors."""
        level = Level()
        actor = MagicMock(spec=Actor)
        level.add_actor(actor)
        level.load()
        
        level.update(0.016)
        
        actor.tick.assert_called_once_with(0.016)
    
    def test_update_not_loaded(self):
        """Test update does nothing when not loaded."""
        level = Level()
        actor = MagicMock(spec=Actor)
        level.add_actor(actor)
        
        level.update(0.016)
        
        actor.tick.assert_not_called()
    
    def test_get_actors_by_tag(self):
        """Test getting actors by tag."""
        level = Level()
        actor1 = MagicMock(spec=Actor)
        actor1.tags = ["enemy"]
        actor2 = MagicMock(spec=Actor)
        actor2.tags = ["player"]
        
        level.add_actor(actor1)
        level.add_actor(actor2)
        
        enemies = level.get_actors_by_tag("enemy")
        
        assert actor1 in enemies
        assert actor2 not in enemies
    
    def test_get_all_actors_with_tag(self):
        """Test getting all actors with specific tag."""
        level = Level()
        actor1 = MagicMock(spec=Actor)
        actor1.tags = ["enemy", "boss"]
        actor2 = MagicMock(spec=Actor)
        actor2.tags = ["enemy"]
        
        level.add_actor(actor1)
        level.add_actor(actor2)
        
        enemies = level.get_actors_by_tag("enemy")
        
        assert len(enemies) == 2
        assert actor1 in enemies
        assert actor2 in enemies
    
    def test_clear_actors(self):
        """Test clearing all actors."""
        level = Level()
        actor1 = MagicMock(spec=Actor)
        actor2 = MagicMock(spec=Actor)
        level.add_actor(actor1)
        level.add_actor(actor2)
        
        level.clear_actors()
        
        assert level.actors == []


class TestLevelManager:
    """Test level manager."""
    
    def test_initialization(self):
        """Test manager creation."""
        manager = LevelManager()
        
        assert manager.levels == {}
        assert manager.current_level is None
    
    def test_register_level(self):
        """Test registering level."""
        manager = LevelManager()
        level = Level(name="test")
        
        manager.register_level(level)
        
        assert "test" in manager.levels
    
    def test_load_level(self):
        """Test loading level."""
        manager = LevelManager()
        level = Level(name="test")
        manager.register_level(level)
        
        manager.load_level("test")
        
        assert manager.current_level == level
        assert level.is_loaded is True
    
    def test_load_level_not_found(self):
        """Test loading non-existent level raises error."""
        manager = LevelManager()
        
        with pytest.raises(KeyError):
            manager.load_level("nonexistent")
    
    def test_unload_current_level(self):
        """Test unloading current level."""
        manager = LevelManager()
        level = Level(name="test")
        manager.register_level(level)
        manager.load_level("test")
        
        manager.unload_current()
        
        assert manager.current_level is None
        assert level.is_loaded is False
    
    def test_get_current_level(self):
        """Test getting current level."""
        manager = LevelManager()
        level = Level(name="test")
        manager.register_level(level)
        manager.load_level("test")
        
        current = manager.get_current_level()
        
        assert current == level
    
    def test_update_current(self):
        """Test update propagates to current level."""
        manager = LevelManager()
        level = Level(name="test")
        level.update = MockObject()
        manager.register_level(level)
        manager.load_level("test")
        
        manager.update(0.016)
        
        level.update.assert_called_once_with(0.016)
    
    def test_reload_level(self):
        """Test reloading current level."""
        manager = LevelManager()
        level = Level(name="test")
        level.load = MockObject()
        level.unload = MockObject()
        manager.register_level(level)
        manager.load_level("test")
        
        manager.reload_level()
        
        # unload called twice (initial load + reload)
        assert level.unload.call_count == 2
        assert level.load.call_count == 2  # Initial + reload

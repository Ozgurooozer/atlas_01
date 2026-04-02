"""Level System - Game level management.

Provides level/scene management with tile maps, spawn points,
and actor management for game worlds.

Layer: 3 (World)
Dependencies: core.object, core.vec, world.actor
"""
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field

from core.vec import Vec3


@dataclass
class SpawnPoint:
    """Spawn point for entities in a level.
    
    Attributes:
        position: World position for spawning
        name: Identifier for this spawn point
        tags: Optional tags for categorization
    """
    position: Vec3
    name: str = "default"
    tags: List[str] = field(default_factory=list)


class TileMap:
    """2D grid-based tile map for level layout.
    
    Stores tile data in a grid and provides coordinate conversions.
    """
    
    def __init__(self, width: int, height: int, tile_size: float = 32.0,
                 default_tile: Any = None):
        """Initialize tile map.
        
        Args:
            width: Grid width in tiles
            height: Grid height in tiles
            tile_size: Size of each tile in world units
            default_tile: Default tile value
        """
        self.width = width
        self.height = height
        self.tile_size = tile_size
        self.default_tile = default_tile
        
        # 2D grid storage
        self._tiles: List[List[Any]] = [
            [default_tile for _ in range(width)]
            for _ in range(height)
        ]
    
    def _is_valid(self, x: int, y: int) -> bool:
        """Check if coordinates are valid."""
        return 0 <= x < self.width and 0 <= y < self.height
    
    def set_tile(self, x: int, y: int, tile: Any) -> None:
        """Set tile at grid position.
        
        Args:
            x: Grid x coordinate
            y: Grid y coordinate
            tile: Tile data to set
        """
        if self._is_valid(x, y):
            self._tiles[y][x] = tile
    
    def get_tile(self, x: int, y: int) -> Any:
        """Get tile at grid position.
        
        Args:
            x: Grid x coordinate
            y: Grid y coordinate
            
        Returns:
            Tile data or None if out of bounds
        """
        if self._is_valid(x, y):
            return self._tiles[y][x]
        return None
    
    def world_to_tile(self, world_x: float, world_y: float) -> tuple:
        """Convert world position to tile coordinates.
        
        Args:
            world_x: World x position
            world_y: World y position
            
        Returns:
            (tile_x, tile_y) tuple
        """
        return (int(world_x / self.tile_size), int(world_y / self.tile_size))
    
    def tile_to_world(self, tile_x: int, tile_y: int) -> tuple:
        """Convert tile coordinates to world position.
        
        Args:
            tile_x: Tile x coordinate
            tile_y: Tile y coordinate
            
        Returns:
            (world_x, world_y) tuple
        """
        return (tile_x * self.tile_size, tile_y * self.tile_size)
    
    def get_neighbors(self, x: int, y: int) -> Dict[str, Any]:
        """Get neighboring tiles.
        
        Args:
            x: Center tile x
            y: Center tile y
            
        Returns:
            Dict with keys 'left', 'right', 'up', 'down'
        """
        return {
            "left": self.get_tile(x - 1, y),
            "right": self.get_tile(x + 1, y),
            "up": self.get_tile(x, y - 1),
            "down": self.get_tile(x, y + 1)
        }


class Level:
    """Game level containing actors, tile map, and spawn points.
    
    Manages all entities in a single game scene/level.
    """
    
    def __init__(self, name: str = ""):
        """Initialize level.
        
        Args:
            name: Level identifier
        """
        self.name = name
        self.actors: List[Any] = []
        self.spawn_points: Dict[str, SpawnPoint] = {}
        self.tile_map: Optional[TileMap] = None
        self.is_loaded: bool = False
        
        # Callbacks
        self.on_load: Optional[Callable] = None
        self.on_unload: Optional[Callable] = None
    
    def add_actor(self, actor: Any) -> None:
        """Add actor to level.
        
        Args:
            actor: Actor to add
        """
        if actor not in self.actors:
            self.actors.append(actor)
    
    def remove_actor(self, actor: Any) -> bool:
        """Remove actor from level.
        
        Args:
            actor: Actor to remove
            
        Returns:
            True if removed, False if not found
        """
        if actor in self.actors:
            self.actors.remove(actor)
            return True
        return False
    
    def clear_actors(self) -> None:
        """Remove all actors from level."""
        self.actors.clear()
    
    def add_spawn_point(self, point: SpawnPoint) -> None:
        """Add spawn point to level.
        
        Args:
            point: Spawn point to add
        """
        self.spawn_points[point.name] = point
    
    def get_spawn_point(self, name: str) -> Optional[SpawnPoint]:
        """Get spawn point by name.
        
        Args:
            name: Spawn point name
            
        Returns:
            SpawnPoint or None if not found
        """
        return self.spawn_points.get(name)
    
    def set_tile_map(self, tile_map: TileMap) -> None:
        """Set tile map for this level.
        
        Args:
            tile_map: Tile map to use
        """
        self.tile_map = tile_map
    
    def load(self) -> None:
        """Load the level."""
        self.is_loaded = True
        if self.on_load:
            self.on_load()
    
    def unload(self) -> None:
        """Unload the level."""
        self.is_loaded = False
        if self.on_unload:
            self.on_unload()
    
    def update(self, dt: float) -> None:
        """Update all actors in level.
        
        Args:
            dt: Delta time
        """
        if not self.is_loaded:
            return
        
        for actor in self.actors:
            if hasattr(actor, 'tick') and hasattr(actor, 'enabled'):
                if actor.enabled:
                    actor.tick(dt)
            elif hasattr(actor, 'tick'):
                actor.tick(dt)
    
    def get_actors_by_tag(self, tag: str) -> List[Any]:
        """Get all actors with specific tag.
        
        Args:
            tag: Tag to search for
            
        Returns:
            List of actors with the tag
        """
        result = []
        for actor in self.actors:
            actor_tags = getattr(actor, 'tags', [])
            if tag in actor_tags:
                result.append(actor)
        return result


class LevelManager:
    """Manages multiple levels and level transitions.
    
    Central manager for level loading, unloading, and switching.
    """
    
    def __init__(self):
        """Initialize level manager."""
        self.levels: Dict[str, Level] = {}
        self.current_level: Optional[Level] = None
    
    def register_level(self, level: Level) -> None:
        """Register a level with the manager.
        
        Args:
            level: Level to register
        """
        self.levels[level.name] = level
    
    def load_level(self, name: str) -> Level:
        """Load a level by name.
        
        Args:
            name: Level name to load
            
        Returns:
            Loaded level
            
        Raises:
            KeyError: If level not found
        """
        if name not in self.levels:
            raise KeyError(f"Level '{name}' not found")
        
        # Unload current if exists
        if self.current_level:
            self.current_level.unload()
        
        # Load new level
        level = self.levels[name]
        level.load()
        self.current_level = level
        
        return level
    
    def unload_current(self) -> None:
        """Unload current level."""
        if self.current_level:
            self.current_level.unload()
            self.current_level = None
    
    def get_current_level(self) -> Optional[Level]:
        """Get currently loaded level.
        
        Returns:
            Current level or None
        """
        return self.current_level
    
    def update(self, dt: float) -> None:
        """Update current level.
        
        Args:
            dt: Delta time
        """
        if self.current_level:
            self.current_level.update(dt)
    
    def reload_level(self) -> None:
        """Reload current level."""
        if self.current_level:
            name = self.current_level.name
            self.current_level.unload()
            self.load_level(name)

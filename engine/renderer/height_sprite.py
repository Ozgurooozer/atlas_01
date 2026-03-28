"""Height sprite and height map system for 2.5D rendering.

Provides elevation/depth support for isometric sprites.

Layer: 2 (Engine)
Dependencies: core.vec, engine.renderer.isometric
"""
from core.vec import Vec2
from engine.renderer.isometric import IsometricProjection


class HeightSprite:
    """Sprite with height/elevation support for 2.5D rendering.
    
    A HeightSprite has a base position (X,Y on the floor) and a height
    (Z elevation above the floor). This enables:
    - Sprite jumping/flying
    - Platform stacking
    - Depth-based occlusion
    - Height-based shadow offset
    
    Usage:
        sprite = HeightSprite(
            base_position=Vec2(100, 200),
            height=50.0  # 50 units above floor
        )
        screen_pos = sprite.get_screen_position(iso_projection)
    """
    
    def __init__(self, base_position: Vec2, height: float = 0.0):
        """Initialize height sprite.
        
        Args:
            base_position: X,Y position on the floor
            height: Z elevation above floor (0 = on floor)
        """
        self.base_position = base_position
        self.height = height
        self._depth_offset = 0.5  # Height contribution to depth
    
    def get_depth_sort_key(self) -> float:
        """Calculate depth sort key for proper layering.
        
        Objects are rendered back-to-front based on:
        - Y position (higher Y = further back)
        - Height (higher = slightly further back)
        
        Returns:
            Sort key (lower values rendered first)
        """
        return self.base_position.y + self.height * self._depth_offset
    
    def get_screen_position(self, projection: IsometricProjection) -> Vec2:
        """Get screen position with height offset.
        
        Args:
            projection: Isometric projection instance
            
        Returns:
            Screen position with height applied
        """
        # Get base screen position
        base_screen = projection.world_to_screen(self.base_position)
        
        # Apply height offset (moves sprite up on screen)
        return projection.apply_height_offset(base_screen, self.height)
    
    def set_height(self, height: float) -> None:
        """Set sprite height.
        
        Args:
            height: New height value
        """
        self.height = max(0.0, height)
    
    def change_height(self, delta: float) -> None:
        """Modify height by delta.
        
        Args:
            delta: Height change (positive = up, negative = down)
        """
        self.set_height(self.height + delta)
    
    def __eq__(self, other: object) -> bool:
        """Check equality based on base position and height."""
        if not isinstance(other, HeightSprite):
            return False
        return (self.base_position == other.base_position and 
                self.height == other.height)
    
    def __hash__(self) -> int:
        """Hash for use in sets/dicts."""
        return hash((self.base_position.x, self.base_position.y, self.height))


class HeightMap:
    """2D grid of height values for terrain elevation.
    
    HeightMap stores elevation data for the game world, enabling:
    - Terrain height queries
    - Sprite-to-terrain alignment
    - Slope calculations
    - Water level detection
    
    Usage:
        height_map = HeightMap(width=20, height=20, tile_size=64)
        height_map.set_height(5, 5, 100.0)  # Hill at grid (5,5)
        
        # Apply to sprite
        height_map.apply_to_sprite(sprite)
    """
    
    def __init__(self, width: int, height: int, tile_size: int = 64):
        """Initialize height map.
        
        Args:
            width: Grid width in tiles
            height: Grid height in tiles
            tile_size: Size of each tile in pixels/world units
        """
        self.width = width
        self.height = height
        self.tile_size = tile_size
        
        # Initialize flat heightmap (all zeros)
        self._data = [[0.0 for _ in range(height)] for _ in range(width)]
    
    def set_height(self, x: int, y: int, height: float) -> None:
        """Set height at grid position.
        
        Args:
            x: Grid X coordinate
            y: Grid Y coordinate
            height: Elevation value
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            self._data[x][y] = height
    
    def get_height(self, x: int, y: int) -> float:
        """Get height at grid position.
        
        Args:
            x: Grid X coordinate
            y: Grid Y coordinate
            
        Returns:
            Height value (0 if out of bounds)
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            return self._data[x][y]
        return 0.0
    
    def get_height_at_world(self, world_pos: Vec2) -> float:
        """Get height at world position.
        
        Converts world position to grid coordinates and returns height.
        
        Args:
            world_pos: World position (X, Y)
            
        Returns:
            Height at that position
        """
        # Convert world to grid coordinates
        grid_x = int(world_pos.x / self.tile_size)
        grid_y = int(world_pos.y / self.tile_size)
        
        return self.get_height(grid_x, grid_y)
    
    def apply_to_sprite(self, sprite: HeightSprite) -> None:
        """Apply height map elevation to sprite.
        
        Sets sprite's height to the terrain height at its position.
        
        Args:
            sprite: HeightSprite to modify
        """
        height = self.get_height_at_world(sprite.base_position)
        sprite.set_height(height)
    
    def get_slope(self, x: int, y: int) -> Vec2:
        """Calculate slope at grid position.
        
        Returns slope direction based on neighboring heights.
        
        Args:
            x: Grid X coordinate
            y: Grid Y coordinate
            
        Returns:
            Slope vector (X=slope east-west, Y=slope north-south)
        """
        # Sample neighboring heights
        left = self.get_height(x - 1, y)
        right = self.get_height(x + 1, y)
        up = self.get_height(x, y - 1)
        down = self.get_height(x, y + 1)
        
        # Calculate slope
        slope_x = (right - left) / 2.0
        slope_y = (down - up) / 2.0
        
        return Vec2(slope_x, slope_y)
    
    def load_from_image(self, image_path: str) -> None:
        """Load heightmap from grayscale image.
        
        Args:
            image_path: Path to heightmap image
        """
        # TODO: Implement Pillow image loading
        # For now, placeholder
        pass

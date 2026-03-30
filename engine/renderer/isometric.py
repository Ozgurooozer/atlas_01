"""Isometric projection system for 2.5D rendering.

Provides world-to-screen and screen-to-world coordinate conversion
for isometric/2.5D games.

Layer: 2 (Engine)
Dependencies: core.vec
"""
from math import cos, sin, radians
from core.vec import Vec2


class IsometricProjection:
    """Converts between world and screen coordinates for isometric projection.
    
    Isometric projection maps 2D world coordinates (X, Y) to 2D screen coordinates
    using the classic isometric transform:
    - screen_x = (world_x - world_y) * cos(30°) * tile_size/2 + offset_x
    - screen_y = (world_x + world_y) * sin(30°) * tile_size/2 + offset_y
    
    Usage:
        iso = IsometricProjection(screen_width=800, screen_height=600)
        screen_pos = iso.world_to_screen(Vec2(100, 200))
        world_pos = iso.screen_to_world(Vec2(400, 300))
    """
    
    def __init__(self, screen_width: int = 800, screen_height: int = 600, 
                 tile_size: int = 64):
        """Initialize isometric projection.
        
        Args:
            screen_width: Screen width in pixels
            screen_height: Screen height in pixels
            tile_size: Size of one isometric tile in pixels
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.tile_size = tile_size
        
        # Isometric angle constants (30 degrees)
        self._cos_angle = cos(radians(30))
        self._sin_angle = sin(radians(30))
        
        # Screen center for offset
        self._offset_x = screen_width / 2
        self._offset_y = screen_height / 2
    
    def world_to_screen(self, world_pos: Vec2) -> Vec2:
        """Convert world coordinates to screen coordinates.
        
        Args:
            world_pos: World position (X, Y)
            
        Returns:
            Screen position in pixels
        """
        # Isometric projection formula
        screen_x = (world_pos.x - world_pos.y) * self._cos_angle * self.tile_size / 2
        screen_y = (world_pos.x + world_pos.y) * self._sin_angle * self.tile_size / 2
        
        # Add offset to center on screen
        return Vec2(
            screen_x + self._offset_x,
            screen_y + self._offset_y
        )
    
    def screen_to_world(self, screen_pos: Vec2) -> Vec2:
        """Convert screen coordinates to world coordinates.
        
        Args:
            screen_pos: Screen position in pixels
            
        Returns:
            World position (X, Y)
        """
        # Remove offset
        x = screen_pos.x - self._offset_x
        y = screen_pos.y - self._offset_y
        
        # Inverse isometric projection
        # x = (X - Y) * cos * size/2
        # y = (X + Y) * sin * size/2
        
        cos_factor = self._cos_angle * self.tile_size / 2
        sin_factor = self._sin_angle * self.tile_size / 2
        
        # Solve for X and Y
        # X - Y = x / cos_factor
        # X + Y = y / sin_factor
        
        diff = x / cos_factor
        sum_val = y / sin_factor
        
        world_x = (sum_val + diff) / 2
        world_y = (sum_val - diff) / 2
        
        return Vec2(world_x, world_y)
    
    def get_depth_sort_key(self, world_pos: Vec2, height: float = 0) -> float:
        """Calculate depth sort key for proper layering.
        
        In isometric projection, objects are sorted by:
        - Y position (back-to-front)
        - Height offset (higher = further back)
        
        Args:
            world_pos: World position
            height: Height/elevation offset
            
        Returns:
            Sort key (lower = render first)
        """
        return world_pos.y + world_pos.x + height * 0.5
    
    def apply_height_offset(self, screen_pos: Vec2, height: float) -> Vec2:
        """Apply height offset to screen position.
        
        Higher objects appear shifted up on screen.
        
        Args:
            screen_pos: Base screen position
            height: Height in world units
            
        Returns:
            Screen position with height offset
        """
        # Height moves sprite up (negative Y)
        height_pixel = height * self._sin_angle * self.tile_size / 2
        return Vec2(screen_pos.x, screen_pos.y - height_pixel)


class IsometricCamera:
    """Camera system for isometric view with smooth follow and zoom.
    
    Features:
    - Smooth target following
    - Zoom in/out
    - Configurable view angle
    - View bounds clamping
    
    Usage:
        camera = IsometricCamera()
        camera.follow_target(player.position, dt=0.016)
        screen_pos = camera.world_to_screen(object.position)
    """
    
    def __init__(self, x: float = 0, y: float = 0):
        """Initialize camera.
        
        Args:
            x: Initial X position
            y: Initial Y position
        """
        self.position = Vec2(x, y)
        self.zoom = 1.0
        self.view_angle = 30.0
        self._smooth_speed = 5.0
    
    def follow_target(self, target: Vec2, dt: float, speed: float = 5.0) -> None:
        """Smoothly follow a target position.
        
        Args:
            target: Target world position to follow
            dt: Delta time in seconds
            speed: Follow speed (higher = faster)
        """
        # Calculate direction to target
        diff = target - self.position
        
        # Apply smooth interpolation
        if diff.length() > 0.01:
            move = diff * min(speed * dt, 1.0)
            self.position = self.position + move
    
    def set_zoom_level(self, zoom: float) -> None:
        """Set camera zoom level.
        
        Args:
            zoom: Zoom factor (1.0 = normal, 2.0 = 2x zoomed in)
        """
        self.zoom = max(0.1, min(zoom, 5.0))
    
    def set_view_angle(self, angle: float) -> None:
        """Set isometric view angle.
        
        Args:
            angle: Angle in degrees (typical: 30° for isometric)
        """
        self.view_angle = max(15.0, min(angle, 45.0))
    
    def world_to_screen(self, world_pos: Vec2, projection: IsometricProjection) -> Vec2:
        """Convert world to screen with camera offset and zoom.
        
        Args:
            world_pos: World position
            projection: Isometric projection instance
            
        Returns:
            Screen position
        """
        # Apply camera offset
        relative_pos = world_pos - self.position
        
        # Use projection with zoom
        screen = projection.world_to_screen(relative_pos)
        
        # Apply zoom from center of screen
        center = Vec2(projection.screen_width / 2, projection.screen_height / 2)
        zoomed = center + (screen - center) * self.zoom
        
        return zoomed

"""Directional sprite system for 2.5D rendering.

Provides 8-way directional sprites, billboard sprites, and smooth rotation.

Layer: 2 (Engine)
Dependencies: core.vec
"""
from typing import List, Optional, Dict
from math import atan2, degrees, radians, sin, cos, pi, fabs
from core.vec import Vec2


class DirectionalSprite:
    """8-way directional sprite for characters.
    
    Supports 8 directions (N, NE, E, SE, S, SW, W, NW) with automatic
    direction selection based on facing angle. Used for characters that
    need to face different directions visually.
    
    Usage:
        ds = DirectionalSprite()
        ds.add_direction(0, "player_N.png")   # North
        ds.add_direction(1, "player_NE.png") # North-East
        ...
        current_sprite = ds.get_sprite_for_angle(facing_angle)
    """
    
    def __init__(self):
        """Initialize directional sprite with no directions."""
        self.directions: Dict[int, str] = {}
        self.current_direction = 0
    
    def add_direction(self, direction_index: int, texture_path: str) -> None:
        """Add a direction texture.
        
        Args:
            direction_index: Direction index (0-7 for 8-way)
            texture_path: Path to texture file
        """
        self.directions[direction_index] = texture_path
    
    def get_sprite_for_angle(self, angle_degrees: float) -> Optional[str]:
        """Get the appropriate sprite for a facing angle.
        
        Args:
            angle_degrees: Facing angle in degrees (0 = North, clockwise)
            
        Returns:
            Texture path for the closest direction
        """
        if not self.directions:
            return None
        
        # Normalize angle to 0-360
        angle = angle_degrees % 360
        if angle < 0:
            angle += 360
        
        # Calculate direction index for 8-way
        # 0 = N (0°), 1 = NE (45°), 2 = E (90°), etc.
        direction = int((angle + 22.5) / 45) % 8
        
        self.current_direction = direction
        return self.directions.get(direction)


class DirectionManager:
    """Manages smooth direction changes for directional sprites.
    
    Provides angle-to-direction conversion and smooth rotation between
    directions using shortest path around the circle.
    
    Usage:
        dm = DirectionManager()
        direction = dm.angle_to_direction(45)  # Returns 1 (NE)
        new_angle = dm.smooth_direction_change(dt=0.016)
    """
    
    def __init__(self):
        """Initialize direction manager."""
        self.current_angle = 0.0
        self.target_angle = 0.0
        self.lerp_speed = 10.0
    
    def angle_to_direction(self, angle_degrees: float, num_directions: int = 8) -> int:
        """Convert angle to direction index.
        
        Args:
            angle_degrees: Angle in degrees (0 = North)
            num_directions: Number of directions (8 for 8-way)
            
        Returns:
            Direction index (0 to num_directions-1)
        """
        # Normalize angle
        angle = angle_degrees % 360
        if angle < 0:
            angle += 360
        
        # Calculate direction
        step = 360.0 / num_directions
        direction = int((angle + step / 2) / step) % num_directions
        
        return direction
    
    def smooth_direction_change(self, dt: float, speed: float = 10.0) -> float:
        """Smoothly interpolate towards target angle.
        
        Uses shortest path around the circle.
        
        Args:
            dt: Delta time in seconds
            speed: Rotation speed
            
        Returns:
            New current angle
        """
        # Calculate shortest delta
        delta = self._calculate_angle_delta(self.current_angle, self.target_angle)
        
        # Apply smoothing
        max_rotation = speed * dt * 360  # Max degrees per second
        
        if fabs(delta) <= max_rotation:
            self.current_angle = self.target_angle
        else:
            direction = 1 if delta > 0 else -1
            self.current_angle += direction * max_rotation
        
        # Normalize
        self.current_angle = self.current_angle % 360
        if self.current_angle < 0:
            self.current_angle += 360
        
        return self.current_angle
    
    def _calculate_angle_delta(self, current: float, target: float) -> float:
        """Calculate shortest angle delta.
        
        Args:
            current: Current angle
            target: Target angle
            
        Returns:
            Shortest delta (can be negative)
        """
        delta = target - current
        
        # Normalize to -180 to 180
        while delta > 180:
            delta -= 360
        while delta < -180:
            delta += 360
        
        return delta
    
    def mirror_if_needed(self, direction: int) -> tuple:
        """Check if sprite should be mirrored instead of using different texture.
        
        For some directions, it's more efficient to flip the sprite horizontally
        rather than use a separate texture.
        
        Args:
            direction: Direction index (0-7)
            
        Returns:
            Tuple of (use_direction, flip_horizontal)
        """
        # Directions: 0=N, 1=NE, 2=E, 3=SE, 4=S, 5=SW, 6=W, 7=NW
        # Can mirror: NE->NW (1->7), E->W (2->6), SE->SW (3->5)
        mirror_map = {
            0: (0, False),   # N - no mirror
            1: (1, False),   # NE - keep
            2: (2, False),   # E - keep
            3: (3, False),   # SE - keep
            4: (4, False),   # S - no mirror
            5: (3, True),    # SW - mirror SE
            6: (2, True),    # W - mirror E
            7: (1, True),    # NW - mirror NE
        }
        return mirror_map.get(direction, (direction, False))


class BillboardSprite:
    """Sprite that always faces the camera.
    
    Useful for trees, particles, or enemies that should always be
    visible from the camera's perspective regardless of camera angle.
    
    Usage:
        bb = BillboardSprite(texture="tree.png")
        bb.set_rotation_lock("Y")  # Only rotate on Y axis
    """
    
    def __init__(self, texture: str):
        """Initialize billboard sprite.
        
        Args:
            texture: Texture path
        """
        self.texture = texture
        self.position = Vec2(0, 0)
        self.always_face_camera = True
        self.rotation_lock: Optional[str] = None  # "X", "Y", "Z", or None
    
    def set_rotation_lock(self, axis: str) -> None:
        """Lock rotation to specific axis.
        
        Args:
            axis: "X", "Y", "Z", or None for full rotation
        """
        if axis in ("X", "Y", "Z", None):
            self.rotation_lock = axis


class BillboardManager:
    """Manages all billboard sprites in the scene.
    
    Updates all billboard rotations to face the camera each frame.
    
    Usage:
        manager = BillboardManager()
        manager.register_billboard(tree_billboard)
        manager.update_all(camera_position)
    """
    
    def __init__(self):
        """Initialize billboard manager."""
        self.billboards: List[BillboardSprite] = []
    
    def register_billboard(self, billboard: BillboardSprite) -> None:
        """Register a billboard for management.
        
        Args:
            billboard: Billboard to manage
        """
        self.billboards.append(billboard)
    
    def unregister_billboard(self, billboard: BillboardSprite) -> bool:
        """Unregister a billboard.
        
        Args:
            billboard: Billboard to remove
            
        Returns:
            True if removed
        """
        if billboard in self.billboards:
            self.billboards.remove(billboard)
            return True
        return False
    
    @staticmethod
    def calculate_face_angle(sprite_pos: Vec2, camera_pos: Vec2) -> float:
        """Calculate angle for sprite to face camera.
        
        Args:
            sprite_pos: Sprite position
            camera_pos: Camera position
            
        Returns:
            Angle in degrees
        """
        dx = camera_pos.x - sprite_pos.x
        dy = camera_pos.y - sprite_pos.y
        
        # Calculate angle from sprite to camera
        angle_rad = atan2(dy, dx)
        angle_deg = degrees(angle_rad)
        
        # Convert to 0-360 range with 0 = North
        angle = (90 - angle_deg) % 360
        
        return angle


class SpriteBlender:
    """Blends between sprites during direction transitions.
    
    Provides crossfade effects when changing sprite directions
    for smoother visual transitions.
    
    Usage:
        blender = SpriteBlender()
        factor = blender.get_blend_factor(progress=0.5)
    """
    
    def __init__(self):
        """Initialize sprite blender."""
        self.transition_duration = 0.15  # seconds
    
    def get_blend_factor(self, progress: float) -> float:
        """Get blend factor for transition.
        
        Args:
            progress: Transition progress (0.0 to 1.0)
            
        Returns:
            Blend factor (0.0 = old sprite, 1.0 = new sprite)
        """
        # Clamp to valid range
        progress = max(0.0, min(1.0, progress))
        
        # Ease in-out for smooth transition
        # Smoothstep: 3t^2 - 2t^3
        return progress * progress * (3.0 - 2.0 * progress)
    
    def crossfade_directions(self, old_sprite: str, new_sprite: str,
                            progress: float) -> tuple:
        """Calculate crossfade between two sprites.
        
        Args:
            old_sprite: Old sprite texture path
            new_sprite: New sprite texture path
            progress: Transition progress (0-1)
            
        Returns:
            Tuple of (primary_sprite, secondary_sprite, secondary_alpha)
        """
        factor = self.get_blend_factor(progress)
        
        if factor < 0.5:
            # Still mostly old sprite
            return (old_sprite, new_sprite, factor * 2.0)
        else:
            # Mostly new sprite
            return (new_sprite, old_sprite, (1.0 - factor) * 2.0)


class RotationSmoother:
    """Smooths rotation angles over time.
    
    Provides smooth interpolation for sprite rotations with
    configurable speed and easing.
    
    Usage:
        smoother = RotationSmoother()
        smoother.target_angle = 180
        current = smoother.lerp(speed=0.1)
    """
    
    def __init__(self):
        """Initialize rotation smoother."""
        self.current_angle = 0.0
        self.target_angle = 0.0
        self.lerp_speed = 0.1
    
    def lerp(self, speed: Optional[float] = None) -> float:
        """Interpolate towards target angle.
        
        Args:
            speed: Lerp factor (0-1), uses default if None
            
        Returns:
            New current angle
        """
        s = speed if speed is not None else self.lerp_speed
        
        # Calculate shortest path
        delta = self.target_angle - self.current_angle
        
        # Normalize to -180 to 180
        while delta > 180:
            delta -= 360
        while delta < -180:
            delta += 360
        
        # Apply lerp
        self.current_angle += delta * s
        
        # Normalize result
        self.current_angle = self.current_angle % 360
        if self.current_angle < 0:
            self.current_angle += 360
        
        return self.current_angle

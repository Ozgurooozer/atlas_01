"""Normal map lighting system for 2.5D rendering.

Provides 2D normal map-based lighting with 3D-positioned light sources.

Layer: 2 (Engine)
Dependencies: core.vec, core.color, engine.renderer.texture
"""
from typing import List, Tuple, Optional
from math import sqrt
from core.vec import Vec2, Vec3
from core.color import Color


class NormalMapTexture:
    """Texture with diffuse + normal map + specular for advanced lighting.
    
    Combines three texture components:
    - Diffuse: Base color (RGB)
    - Normal: Surface normals for lighting calculation (RGB)
    - Specular: Specular intensity (A channel or separate)
    
    Usage:
        nmt = NormalMapTexture()
        nmt.load_diffuse("player_diffuse.png")
        nmt.load_normal("player_normal.png")
    """
    
    def __init__(self):
        """Initialize normal map texture with no textures loaded."""
        self.diffuse: Optional[str] = None  # Texture path/handle
        self.normal: Optional[str] = None
        self.specular: Optional[str] = None
        self._loaded = False
    
    def load_diffuse(self, path: str) -> None:
        """Load diffuse (color) texture.
        
        Args:
            path: Path to diffuse texture file
        """
        self.diffuse = path
        self._check_loaded()
    
    def load_normal(self, path: str) -> None:
        """Load normal map texture.
        
        Args:
            path: Path to normal map file
        """
        self.normal = path
        self._check_loaded()
    
    def load_specular(self, path: str) -> None:
        """Load specular texture.
        
        Args:
            path: Path to specular texture file
        """
        self.specular = path
    
    def _check_loaded(self) -> None:
        """Check if essential textures are loaded."""
        self._loaded = self.diffuse is not None and self.normal is not None
    
    def is_ready(self) -> bool:
        """Check if normal map texture is ready for rendering."""
        return self._loaded


class NormalMapShader:
    """Shader for calculating normal map-based lighting.
    
    Performs per-pixel lighting calculations using normal maps
    to create pseudo-3D lighting effects on 2D sprites.
    
    Usage:
        shader = NormalMapShader()
        intensity = shader.calculate_lighting(normal, light_dir)
        final_color = shader.apply_to_sprite(sprite, lights)
    """
    
    def __init__(self):
        """Initialize normal map shader."""
        self.max_lights = 8  # Max lights per sprite
    
    def calculate_lighting(self, normal: Tuple[float, float, float], 
                          light_dir: Tuple[float, float, float]) -> float:
        """Calculate lighting intensity from normal and light direction.
        
        Uses Lambertian reflectance (dot product of normal and light).
        
        Args:
            normal: Surface normal (x, y, z) - should be normalized
            light_dir: Light direction (x, y, z) - should be normalized
            
        Returns:
            Light intensity (0.0 to 1.0)
        """
        # Calculate dot product
        dot = (normal[0] * light_dir[0] + 
               normal[1] * light_dir[1] + 
               normal[2] * light_dir[2])
        
        # Clamp to 0-1 range (no negative light)
        return max(0.0, min(1.0, dot))
    
    def apply_specular(self, normal: Tuple[float, float, float],
                      light_dir: Tuple[float, float, float],
                      view_dir: Tuple[float, float, float],
                      shininess: float = 32.0) -> float:
        """Calculate specular highlight (Blinn-Phong).
        
        Args:
            normal: Surface normal
            light_dir: Light direction (towards light)
            view_dir: View direction (towards camera)
            shininess: Specular exponent (higher = tighter highlight)
            
        Returns:
            Specular intensity (0.0 to 1.0)
        """
        # Calculate half vector
        half_x = light_dir[0] + view_dir[0]
        half_y = light_dir[1] + view_dir[1]
        half_z = light_dir[2] + view_dir[2]
        
        # Normalize half vector
        length = sqrt(half_x * half_x + half_y * half_y + half_z * half_z)
        if length > 0:
            half_x /= length
            half_y /= length
            half_z /= length
        
        # Dot product of normal and half vector
        dot = (normal[0] * half_x + 
               normal[1] * half_y + 
               normal[2] * half_z)
        
        # Apply shininess
        if dot > 0:
            return pow(dot, shininess)
        return 0.0
    
    def blend_normals(self, normal1: Tuple[float, float, float],
                     normal2: Tuple[float, float, float],
                     factor: float = 0.5) -> Tuple[float, float, float]:
        """Blend two normal vectors.
        
        Useful for combining detail normals with base normals.
        
        Args:
            normal1: First normal
            normal2: Second normal
            factor: Blend factor (0 = normal1, 1 = normal2)
            
        Returns:
            Blended normal (not normalized)
        """
        x = normal1[0] * (1 - factor) + normal2[0] * factor
        y = normal1[1] * (1 - factor) + normal2[1] * factor
        z = normal1[2] * (1 - factor) + normal2[2] * factor
        
        # Normalize
        length = sqrt(x * x + y * y + z * z)
        if length > 0:
            x /= length
            y /= length
            z /= length
        
        return (x, y, z)


class Light3D:
    """3D-positioned light source for 2.5D rendering.
    
    Represents a light with position (X, Y, Z), color, intensity,
    and attenuation range. Supports both point lights and spot lights.
    
    Usage:
        light = Light3D(
            position=Vec3(100, 200, 50),
            color=Color.white(),
            intensity=1.0,
            range=200.0
        )
    """
    
    def __init__(self, position: Vec3 = None, color: Color = None,
                 intensity: float = 1.0, range_value: float = 100.0):
        """Initialize 3D light.
        
        Args:
            position: Light position in world space (X, Y, Z)
            color: Light color
            intensity: Light brightness (0.0 to 1.0+)
            range_value: Light attenuation range in world units
        """
        self.position = position or Vec3(0, 0, 50)
        self.color = color or Color.white()
        self.intensity = max(0.0, intensity)
        self.range = max(1.0, range_value)
        self.enabled = True
    
    @property
    def height(self) -> float:
        """Get light height (Z position)."""
        return self.position.z
    
    @height.setter
    def height(self, value: float) -> None:
        """Set light height."""
        self.position.z = value
    
    def distance_to(self, point: Vec3) -> float:
        """Calculate distance to a point.
        
        Args:
            point: Target point
            
        Returns:
            Distance in world units
        """
        dx = self.position.x - point.x
        dy = self.position.y - point.y
        dz = self.position.z - point.z
        return sqrt(dx * dx + dy * dy + dz * dz)


class LightAttenuation:
    """Light attenuation (falloff) calculations.
    
    Calculates how light intensity decreases with distance.
    Uses inverse-square law with smoothing.
    """
    
    @staticmethod
    def calculate(light: Light3D, point: Vec3) -> float:
        """Calculate attenuation factor.
        
        Args:
            light: Light source
            point: Target point
            
        Returns:
            Attenuation factor (0.0 to 1.0)
        """
        distance = light.distance_to(point)
        
        if distance >= light.range:
            return 0.0
        
        # Inverse square with smoothing
        # atten = 1 / (1 + a*dist + b*dist^2)
        a = 0.5 / light.range
        b = 1.0 / (light.range * light.range)
        
        atten = 1.0 / (1.0 + a * distance + b * distance * distance)
        
        # Smooth falloff at edge
        if distance > light.range * 0.8:
            edge_factor = 1.0 - (distance - light.range * 0.8) / (light.range * 0.2)
            atten *= max(0.0, edge_factor)
        
        return atten


class LightManager:
    """Manages 3D lights in the scene.
    
    Handles up to 50 lights with culling by distance and sorting
    for optimal rendering. Supports adding/removing lights and
    querying visible lights for a given view.
    
    Usage:
        lm = LightManager()
        lm.add_light(Light3D(position=Vec3(100, 100, 50)))
        visible = lm.cull_lights(camera_position)
    """
    
    MAX_LIGHTS = 50
    
    def __init__(self):
        """Initialize light manager."""
        self._lights: List[Light3D] = []
    
    @property
    def light_count(self) -> int:
        """Get current number of lights."""
        return len(self._lights)
    
    def add_light(self, light: Light3D) -> bool:
        """Add a light to the manager.
        
        Args:
            light: Light to add
            
        Returns:
            True if added, False if at max capacity
        """
        if len(self._lights) >= self.MAX_LIGHTS:
            return False
        self._lights.append(light)
        return True
    
    def remove_light(self, light: Light3D) -> bool:
        """Remove a light from the manager.
        
        Args:
            light: Light to remove
            
        Returns:
            True if removed, False if not found
        """
        if light in self._lights:
            self._lights.remove(light)
            return True
        return False
    
    def clear(self) -> None:
        """Remove all lights."""
        self._lights.clear()
    
    def cull_lights(self, camera_pos: Vec2, max_distance: float = 500.0) -> List[Light3D]:
        """Cull lights that are too far from camera.
        
        Args:
            camera_pos: Camera position in 2D world
            max_distance: Maximum visible distance
            
        Returns:
            List of visible lights
        """
        visible = []
        
        for light in self._lights:
            if not light.enabled:
                continue
            
            # Calculate 2D distance to light
            dx = light.position.x - camera_pos.x
            dy = light.position.y - camera_pos.y
            dist_2d = sqrt(dx * dx + dy * dy)
            
            # Keep if within range
            if dist_2d <= max_distance + light.range:
                visible.append(light)
        
        return visible
    
    def sort_by_distance(self, point: Vec2) -> None:
        """Sort lights by distance to point (nearest first).
        
        Args:
            point: Reference point
        """
        def distance_key(light: Light3D) -> float:
            dx = light.position.x - point.x
            dy = light.position.y - point.y
            return dx * dx + dy * dy
        
        self._lights.sort(key=distance_key)
    
    def get_lights_for_sprite(self, sprite_pos: Vec2, max_lights: int = 8) -> List[Light3D]:
        """Get most relevant lights for a specific sprite.
        
        Args:
            sprite_pos: Sprite position
            max_lights: Maximum lights to return
            
        Returns:
            List of lights affecting the sprite
        """
        # Sort by distance
        self.sort_by_distance(sprite_pos)
        
        # Return closest lights
        return self._lights[:max_lights]

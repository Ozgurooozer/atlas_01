"""Volumetric effects system for 2.5D rendering.

Provides volumetric fog and light shafts (god rays) for atmospheric effects.

Layer: 2 (Engine)
Dependencies: core.vec, core.color
"""
from typing import List, Optional
from math import exp, sqrt
from core.vec import Vec3
from core.color import Color


class VolumetricFog:
    """Height-based volumetric fog for atmospheric depth.
    
    Creates fog that varies in density with height, producing realistic
    atmospheric perspective and depth cues.
    
    Usage:
        fog = VolumetricFog(density=0.5)
        fog.height_fog(fog_height=100.0, falloff=0.1)
        density = fog.get_density_at_height(50.0)
    """
    
    def __init__(self, density: float = 0.5, scattering: float = 1.0):
        """Initialize volumetric fog.
        
        Args:
            density: Base fog density (0-1)
            scattering: Light scattering coefficient
        """
        self.density = max(0.0, min(1.0, density))
        self.scattering = scattering
        
        # Height fog parameters
        self.height = 0.0
        self.falloff = 0.1
        self._use_height_fog = False
    
    def height_fog(self, fog_height: float, falloff: float = 0.1) -> None:
        """Enable height-based fog.
        
        Args:
            fog_height: Height of fog layer
            falloff: Density falloff rate (higher = faster falloff)
        """
        self.height = fog_height
        self.falloff = max(0.001, falloff)
        self._use_height_fog = True
    
    def get_density_at_height(self, y: float) -> float:
        """Get fog density at specific height.
        
        Args:
            y: Height in world units
            
        Returns:
            Fog density (0-1)
        """
        if not self._use_height_fog:
            return self.density
        
        # Exponential height fog
        # density = base_density * exp(-falloff * (height - y))
        delta = self.height - y
        
        if delta <= 0:
            # Below fog, full density
            return self.density
        
        # In/above fog layer
        height_factor = exp(-self.falloff * delta)
        return self.density * (1.0 - height_factor)
    
    def get_density_at_point(self, point: Vec3) -> float:
        """Get fog density at 3D point.
        
        Args:
            point: 3D position
            
        Returns:
            Fog density
        """
        return self.get_density_at_height(point.y)
    
    def calculate_transmittance(self, start: Vec3, end: Vec3) -> float:
        """Calculate light transmittance through fog.
        
        Args:
            start: Ray start point
            end: Ray end point
            
        Returns:
            Transmittance (1.0 = no fog, 0.0 = fully occluded)
        """
        # Sample density along ray
        steps = 16
        total_density = 0.0
        
        for i in range(steps):
            t = i / (steps - 1)
            point = Vec3(
                start.x + (end.x - start.x) * t,
                start.y + (end.y - start.y) * t,
                start.z + (end.z - start.z) * t
            )
            total_density += self.get_density_at_point(point)
        
        # Average density
        avg_density = total_density / steps
        
        # Beer-Lambert law: T = exp(-density * distance)
        distance = sqrt(
            (end.x - start.x) ** 2 +
            (end.y - start.y) ** 2 +
            (end.z - start.z) ** 2
        )
        
        transmittance = exp(-avg_density * distance * self.scattering)
        return transmittance


class LightShaft:
    """Light shaft (god ray) effect for dramatic lighting.
    
    Simulates light scattering through atmosphere, creating visible
    light beams from bright light sources.
    
    Usage:
        shaft = LightShaft(light_position=Vec3(100, 200, 150))
        shaft.intensity = 0.8
        occlusion = shaft.check_occlusion(object_pos)
    """
    
    def __init__(self, light_position: Vec3, intensity: float = 0.8):
        """Initialize light shaft.
        
        Args:
            light_position: Light source position
            intensity: Shaft brightness
        """
        self.light_position = light_position
        self.intensity = max(0.0, min(1.0, intensity))
        self.max_steps = 64
        self.step_size = 5.0
    
    def check_occlusion(self, point: Vec3, radius: float = 10.0) -> bool:
        """Check if point occludes the light.
        
        Args:
            point: Point to check
            radius: Occlusion radius
            
        Returns:
            True if point blocks light
        """
        dx = point.x - self.light_position.x
        dy = point.y - self.light_position.y
        dz = point.z - self.light_position.z
        
        dist = sqrt(dx * dx + dy * dy + dz * dz)
        
        return dist < radius
    
    def get_ray_march_steps(self, start: Vec3, end: Vec3) -> List[Vec3]:
        """Get ray marching sample points.
        
        Args:
            start: Ray start
            end: Ray end
            
        Returns:
            List of sample points
        """
        steps = min(self.max_steps, int(self._calculate_distance(start, end) / self.step_size))
        steps = max(4, steps)  # Minimum steps
        
        points = []
        for i in range(steps):
            t = i / (steps - 1)
            point = Vec3(
                start.x + (end.x - start.x) * t,
                start.y + (end.y - start.y) * t,
                start.z + (end.z - start.z) * t
            )
            points.append(point)
        
        return points
    
    def _calculate_distance(self, a: Vec3, b: Vec3) -> float:
        """Calculate distance between two 3D points."""
        dx = b.x - a.x
        dy = b.y - a.y
        dz = b.z - a.z
        return sqrt(dx * dx + dy * dy + dz * dz)
    
    def calculate_intensity_at_point(self, point: Vec3) -> float:
        """Calculate light shaft intensity at a point.
        
        Args:
            point: Sample point
            
        Returns:
            Shaft intensity
        """
        # Distance from light
        dist = self._calculate_distance(point, self.light_position)
        
        # Attenuation with distance
        if dist < 1.0:
            attenuation = 1.0
        else:
            attenuation = 1.0 / (1.0 + dist * 0.01)
        
        return self.intensity * attenuation


class VolumetricRenderer:
    """Renders volumetric effects (fog and light shafts).
    
    Combines fog and light shaft effects into final atmospheric image.
    
    Usage:
        renderer = VolumetricRenderer()
        fog_pass = renderer.render_fog(fog, 800, 600)
        shafts = renderer.composite_lightshafts(light_shafts)
        final = renderer.blend_with_scene(scene, fog_pass, shafts)
    """
    
    def __init__(self):
        """Initialize volumetric renderer."""
        self.fog_pass_enabled = True
        self.light_shaft_enabled = True
        self._fog_buffer: Optional[List[List[float]]] = None
    
    def render_fog(self, fog: VolumetricFog, screen_width: int,
                  screen_height: int) -> List[List[float]]:
        """Render fog pass to buffer.
        
        Args:
            fog: Fog settings
            screen_width: Screen width
            screen_height: Screen height
            
        Returns:
            Fog density buffer
        """
        # Initialize buffer
        buffer = [[0.0 for _ in range(screen_width)]
                  for _ in range(screen_height)]
        
        if not self.fog_pass_enabled:
            return buffer
        
        # Sample fog at each pixel
        # Simplified: just sample at a few heights
        for y in range(0, screen_height, 4):  # Sample every 4 pixels
            world_y = self._screen_y_to_world_y(y, screen_height)
            density = fog.get_density_at_height(world_y)
            
            for x in range(screen_width):
                buffer[y][x] = density
        
        self._fog_buffer = buffer
        return buffer
    
    def _screen_y_to_world_y(self, screen_y: int, screen_height: int) -> float:
        """Convert screen Y to approximate world Y."""
        # Simplified conversion
        return (screen_height - screen_y) * 0.5
    
    def composite_lightshafts(self, shafts: List[LightShaft]) -> List[List[float]]:
        """Composite light shafts into buffer.
        
        Args:
            shafts: Light shafts to render
            
        Returns:
            Light shaft intensity buffer
        """
        if not self.light_shaft_enabled or not shafts:
            return [[0.0]]
        
        # Create shaft buffer
        # For simplicity, just return a small buffer
        buffer = [[0.0 for _ in range(32)] for _ in range(32)]
        
        # Sample shafts
        for shaft in shafts:
            # Calculate shaft center in screen space
            # Simplified: just place at center
            cx, cy = 16, 16
            
            for y in range(32):
                for x in range(32):
                    # Distance from shaft center
                    dx = x - cx
                    dy = y - cy
                    dist = sqrt(dx * dx + dy * dy)
                    
                    # Gaussian falloff
                    if dist < 16:
                        intensity = shaft.intensity * (1.0 - dist / 16)
                        buffer[y][x] = max(buffer[y][x], intensity)
        
        return buffer
    
    def blend_with_scene(self, scene_color: Color, fog_density: float,
                        shaft_intensity: float) -> Color:
        """Blend volumetric effects with scene color.
        
        Args:
            scene_color: Original scene color
            fog_density: Fog density at point
            shaft_intensity: Light shaft intensity
            
        Returns:
            Final color with volumetric effects
        """
        # Apply fog
        fog_color = Color(0.7, 0.75, 0.8)  # Light gray fog
        fogged = Color.lerp(scene_color, fog_color, fog_density)
        
        # Add light shafts
        shaft_color = Color(1.0, 0.95, 0.8)  # Warm light
        final = Color.lerp(fogged, shaft_color, shaft_intensity * 0.5)
        
        return final

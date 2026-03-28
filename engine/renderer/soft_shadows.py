"""Soft shadow system for 2.5D rendering.

Provides soft shadow casting with Gaussian blur and height-based shadow offset.

Layer: 2 (Engine)
Dependencies: core.vec, engine.renderer.normal_lighting
"""
from typing import List, Tuple, Optional
from math import exp, sqrt, pow
from core.vec import Vec2


class ShadowCaster:
    """Object that casts shadows in the scene.
    
    Represents a rectangular object that blocks light and casts shadows.
    Shadow length and direction depend on light position and height.
    
    Usage:
        caster = ShadowCaster(
            position=Vec2(100, 200),
            width=32.0,
            height=32.0
        )
        shadow = caster.cast_shadow(light)
    """
    
    def __init__(self, position: Vec2, width: float, height: float):
        """Initialize shadow caster.
        
        Args:
            position: Center position in world
            width: Object width
            height: Object height
        """
        self.position = position
        self.width = width
        self.height = height
    
    def cast_shadow(self, light: 'ShadowLight') -> 'Shadow':
        """Cast shadow from this object.
        
        Args:
            light: Light source casting the shadow
            
        Returns:
            Shadow geometry
        """
        # Calculate shadow direction (away from light)
        light_pos = light.get_3d_position()
        
        # Vector from light to object center
        dx = self.position.x - light_pos[0]
        dy = self.position.y - light_pos[1]
        
        # Normalize direction
        length = sqrt(dx * dx + dy * dy)
        if length > 0:
            dx /= length
            dy /= length
        
        # Shadow length depends on light height (lower = longer shadow)
        if light.height > 0:
            # Inverse relationship: lower light = longer shadow
            shadow_len = (100.0 / light.height) * self.height * 0.5
        else:
            shadow_len = self.height * 2.0  # Very long shadow for ground-level light
        
        return Shadow(
            start_x=self.position.x,
            start_y=self.position.y,
            direction_x=dx,
            direction_y=dy,
            length=shadow_len,
            intensity=light.intensity
        )
    
    def check_self_shadow(self, light: 'ShadowLight') -> bool:
        """Check if object shadows itself (complex geometry).
        
        Args:
            light: Light source
            
        Returns:
            True if self-shadowing occurs
        """
        # Simplified: check if light is close to object plane
        # Real implementation would check face normals
        return light.height < self.height * 0.5


class Shadow:
    """Shadow geometry and properties.
    
    Represents a shadow as a ray/segment with direction and length.
    """
    
    def __init__(self, start_x: float, start_y: float,
                 direction_x: float, direction_y: float,
                 length: float, intensity: float):
        """Initialize shadow.
        
        Args:
            start_x: Shadow start X
            start_y: Shadow start Y
            direction_x: Shadow direction X (normalized)
            direction_y: Shadow direction Y (normalized)
            length: Shadow length in world units
            intensity: Shadow darkness (0-1)
        """
        self.start_x = start_x
        self.start_y = start_y
        self.direction_x = direction_x
        self.direction_y = direction_y
        self.length = length
        self.intensity = intensity


class ShadowLight:
    """Light source that casts shadows.
    
    3D-positioned light with height for height-based shadow calculation.
    
    Usage:
        light = ShadowLight(
            position=Vec2(100, 200),
            height=50.0,
            radius=150.0
        )
    """
    
    def __init__(self, position: Vec2, height: float = 50.0,
                 radius: float = 100.0, intensity: float = 0.8):
        """Initialize shadow light.
        
        Args:
            position: Light X,Y position
            height: Light Z elevation
            radius: Light influence radius
            intensity: Shadow darkness (0-1)
        """
        self.position = position
        self.height = height
        self.radius = radius
        self.intensity = max(0.0, min(1.0, intensity))
    
    def get_3d_position(self) -> Tuple[float, float, float]:
        """Get 3D position as tuple.
        
        Returns:
            (x, y, z) position
        """
        return (self.position.x, self.position.y, self.height)


class SoftShadowKernel:
    """Gaussian kernel for soft shadow blur operations.
    
    Generates kernels and performs blur calculations for soft shadows.
    """
    
    @staticmethod
    def generate_gaussian(radius: int, sigma: float) -> List[List[float]]:
        """Generate Gaussian kernel.
        
        Args:
            radius: Kernel radius (kernel size = radius*2+1)
            sigma: Standard deviation
            
        Returns:
            2D Gaussian kernel
        """
        size = radius * 2 + 1
        kernel = [[0.0 for _ in range(size)] for _ in range(size)]
        
        # Calculate Gaussian values
        total = 0.0
        for y in range(size):
            for x in range(size):
                # Distance from center
                dx = x - radius
                dy = y - radius
                
                # Gaussian function
                value = exp(-(dx * dx + dy * dy) / (2 * sigma * sigma))
                kernel[y][x] = value
                total += value
        
        # Normalize
        for y in range(size):
            for x in range(size):
                kernel[y][x] /= total
        
        return kernel
    
    @staticmethod
    def calculate_shadow_intensity(point: Vec2, caster: ShadowCaster,
                                    light: ShadowLight) -> float:
        """Calculate shadow intensity at a point.
        
        Args:
            point: Query point
            caster: Shadow casting object
            light: Light source
            
        Returns:
            Shadow intensity (0 = lit, 1 = fully shadowed)
        """
        # Cast shadow from caster
        shadow = caster.cast_shadow(light)
        
        # Calculate distance from point to shadow ray
        # Vector from shadow start to point
        dx = point.x - shadow.start_x
        dy = point.y - shadow.start_y
        
        # Project onto shadow direction
        dot = dx * shadow.direction_x + dy * shadow.direction_y
        
        # If behind shadow start, not in shadow
        if dot < 0:
            return 0.0
        
        # If beyond shadow length, not in shadow
        if dot > shadow.length:
            return 0.0
        
        # Calculate perpendicular distance
        proj_x = shadow.start_x + shadow.direction_x * dot
        proj_y = shadow.start_y + shadow.direction_y * dot
        
        perp_dx = point.x - proj_x
        perp_dy = point.y - proj_y
        perp_dist = sqrt(perp_dx * perp_dx + perp_dy * perp_dy)
        
        # Shadow width based on object size
        shadow_width = caster.width * 0.5
        
        # Soft edge: interpolate intensity
        if perp_dist < shadow_width * 0.5:
            return shadow.intensity
        elif perp_dist < shadow_width:
            # Soft penumbra
            t = (perp_dist - shadow_width * 0.5) / (shadow_width * 0.5)
            return shadow.intensity * (1.0 - t)
        
        return 0.0


class ShadowMap:
    """2D shadow map for accumulating soft shadows.
    
    Renders shadows from multiple casters into a texture with Gaussian blur.
    
    Usage:
        shadow_map = ShadowMap(width=256, height=256)
        shadow_map.generate_shadow_map(casters, light)
        shadow_map.blur_shadows(radius=3)
    """
    
    def __init__(self, width: int, height: int):
        """Initialize shadow map.
        
        Args:
            width: Shadow map width
            height: Shadow map height
        """
        self.width = width
        self.height = height
        self._data = [[0.0 for _ in range(width)] for _ in range(height)]
        self.is_generated = False
    
    def generate_shadow_map(self, casters: List[ShadowCaster],
                           light: ShadowLight) -> None:
        """Generate shadow map from casters.
        
        Args:
            casters: List of shadow casting objects
            light: Light source
        """
        # Clear shadow map
        for y in range(self.height):
            for x in range(self.width):
                self._data[y][x] = 0.0
        
        # Accumulate shadows
        for caster in casters:
            self._add_caster_shadow(caster, light)
        
        self.is_generated = True
    
    def _add_caster_shadow(self, caster: ShadowCaster, light: ShadowLight) -> None:
        """Add single caster shadow to map.
        
        Args:
            caster: Shadow caster
            light: Light source
        """
        # Simple rasterization of shadow
        shadow = caster.cast_shadow(light)
        
        # Rasterize shadow into grid
        steps = int(shadow.length)
        for i in range(steps):
            t = i / max(1, steps - 1)
            x = int(shadow.start_x + shadow.direction_x * shadow.length * t)
            y = int(shadow.start_y + shadow.direction_y * shadow.length * t)
            
            if 0 <= x < self.width and 0 <= y < self.height:
                # Accumulate shadow intensity
                self._data[y][x] = max(self._data[y][x], shadow.intensity)
    
    def blur_shadows(self, radius: int = 3, sigma: float = 1.5) -> None:
        """Apply Gaussian blur to shadows.
        
        Args:
            radius: Blur radius
            sigma: Gaussian sigma
        """
        if radius <= 0:
            return
        
        # Generate kernel
        kernel = SoftShadowKernel.generate_gaussian(radius, sigma)
        kernel_size = len(kernel)
        
        # Apply blur (separable for performance)
        # Horizontal pass
        temp = [[0.0 for _ in range(self.width)] for _ in range(self.height)]
        for y in range(self.height):
            for x in range(self.width):
                value = 0.0
                for kx in range(kernel_size):
                    sample_x = x + kx - radius
                    if 0 <= sample_x < self.width:
                        value += self._data[y][sample_x] * kernel[0][kx]
                temp[y][x] = value
        
        # Vertical pass
        for y in range(self.height):
            for x in range(self.width):
                value = 0.0
                for ky in range(kernel_size):
                    sample_y = y + ky - radius
                    if 0 <= sample_y < self.height:
                        value += temp[sample_y][x] * kernel[ky][0]
                self._data[y][x] = value

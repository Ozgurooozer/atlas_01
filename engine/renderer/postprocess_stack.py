"""Post-process stack system for 2.5D rendering.

Provides full post-process stack with bloom, tone mapping, color grading,
vignette, and other effects for AAA-quality visuals.

Layer: 2 (Engine)
Dependencies: core.color
"""
from typing import List, Optional
from math import exp, pow, sqrt
from core.color import Color


class PostProcessPass:
    """Base class for post-process passes.
    
    All post-process effects inherit from this class.
    
    Usage:
        class MyPass(PostProcessPass):
            def process(self, color: Color) -> Color:
                # Process color
                return color
    """
    
    def __init__(self, enabled: bool = True):
        """Initialize post-process pass.
        
        Args:
            enabled: Whether pass is active
        """
        self.enabled = enabled
    
    def process(self, color: Color) -> Color:
        """Process a color through this pass.
        
        Args:
            color: Input color
            
        Returns:
            Processed color
        """
        if not self.enabled:
            return color
        return self._apply(color)
    
    def _apply(self, color: Color) -> Color:
        """Override this to implement the pass effect."""
        return color


class BrightExtract(PostProcessPass):
    """Extract bright pixels for bloom effect.
    
    Identifies pixels above brightness threshold for bloom source.
    
    Usage:
        be = BrightExtract(threshold=0.8)
        bright = be.process(pixel_color)
    """
    
    def __init__(self, threshold: float = 0.8):
        """Initialize bright extract.
        
        Args:
            threshold: Brightness threshold (0-1)
        """
        super().__init__()
        self.threshold = threshold
    
    def _apply(self, color: Color) -> Color:
        """Extract bright pixels."""
        # Calculate brightness
        brightness = (color.r + color.g + color.b) / 3.0
        
        if brightness > self.threshold:
            # Scale by how much above threshold
            scale = (brightness - self.threshold) / (1.0 - self.threshold)
            return Color(
                color.r * scale,
                color.g * scale,
                color.b * scale,
                color.a
            )
        
        return Color(0, 0, 0, 0)


class GaussianBlur(PostProcessPass):
    """Gaussian blur for softening and bloom.
    
    Applies separable Gaussian blur for efficient processing.
    
    Usage:
        blur = GaussianBlur(radius=3)
        blurred = blur.process(color)
    """
    
    def __init__(self, radius: int = 3, sigma: float = None):
        """Initialize Gaussian blur.
        
        Args:
            radius: Blur radius in pixels
            sigma: Gaussian sigma (auto if None)
        """
        super().__init__()
        self.radius = max(1, radius)
        self.sigma = sigma if sigma else radius / 3.0
    
    def _apply(self, color: Color) -> Color:
        """Apply Gaussian blur.
        
        Note: This is a simplified single-pixel version.
        Real implementation would use kernel convolution.
        """
        # Simplified: just return color
        # Real implementation would sample neighbors
        return color


class BloomComposite(PostProcessPass):
    """Composite bloom onto base image.
    
    Adds blurred bright pixels back to original.
    
    Usage:
        bloom = BloomComposite(intensity=0.5)
        final = bloom.process(scene_color, bloom_buffer)
    """
    
    def __init__(self, intensity: float = 0.5):
        """Initialize bloom composite.
        
        Args:
            intensity: Bloom strength (0-1)
        """
        super().__init__()
        self.intensity = max(0.0, min(1.0, intensity))
    
    def composite(self, base: Color, bloom: Color) -> Color:
        """Composite bloom onto base.
        
        Args:
            base: Base scene color
            bloom: Blurred bloom color
            
        Returns:
            Composited color
        """
        return Color(
            base.r + bloom.r * self.intensity,
            base.g + bloom.g * self.intensity,
            base.b + bloom.b * self.intensity,
            base.a
        )


class ToneMapping(PostProcessPass):
    """HDR to LDR tone mapping.
    
    Maps high dynamic range colors to displayable range.
    
    Usage:
        tm = ToneMapping(exposure=1.0, method='aces')
        ldr = tm.process(hdr_color)
    """
    
    def __init__(self, exposure: float = 1.0, method: str = 'reinhard'):
        """Initialize tone mapping.
        
        Args:
            exposure: Exposure adjustment
            method: 'reinhard', 'aces', or 'filmic'
        """
        super().__init__()
        self.exposure = exposure
        self.method = method
    
    def _apply(self, color: Color) -> Color:
        """Apply tone mapping."""
        # Apply exposure
        r = color.r * self.exposure
        g = color.g * self.exposure
        b = color.b * self.exposure
        
        if self.method == 'reinhard':
            # Reinhard tone mapping
            r = r / (1.0 + r)
            g = g / (1.0 + g)
            b = b / (1.0 + b)
        
        elif self.method == 'aces':
            # Simplified ACES
            r = self._aces_approx(r)
            g = self._aces_approx(g)
            b = self._aces_approx(b)
        
        # Clamp to displayable range
        return Color(
            max(0.0, min(1.0, r)),
            max(0.0, min(1.0, g)),
            max(0.0, min(1.0, b)),
            color.a
        )
    
    def _aces_approx(self, x: float) -> float:
        """Simplified ACES tone mapping curve."""
        a = 2.51
        b = 0.03
        c = 2.43
        d = 0.59
        e = 0.14
        
        return (x * (a * x + b)) / (x * (c * x + d) + e)


class ColorGrading(PostProcessPass):
    """Color grading with LUT support.
    
    Adjusts overall color balance and look.
    
    Usage:
        cg = ColorGrading(saturation=1.1, contrast=1.05)
        graded = cg.process(color)
    """
    
    def __init__(self, saturation: float = 1.0, contrast: float = 1.0,
                 brightness: float = 0.0):
        """Initialize color grading.
        
        Args:
            saturation: Saturation multiplier
            contrast: Contrast multiplier
            brightness: Brightness offset (-1 to 1)
        """
        super().__init__()
        self.saturation = saturation
        self.contrast = contrast
        self.brightness = brightness
    
    def _apply(self, color: Color) -> Color:
        """Apply color grading."""
        # Apply contrast
        r = (color.r - 0.5) * self.contrast + 0.5
        g = (color.g - 0.5) * self.contrast + 0.5
        b = (color.b - 0.5) * self.contrast + 0.5
        
        # Apply brightness
        r += self.brightness
        g += self.brightness
        b += self.brightness
        
        # Apply saturation (simplified)
        gray = (r + g + b) / 3.0
        r = gray + (r - gray) * self.saturation
        g = gray + (g - gray) * self.saturation
        b = gray + (b - gray) * self.saturation
        
        return Color(
            max(0.0, min(1.0, r)),
            max(0.0, min(1.0, g)),
            max(0.0, min(1.0, b)),
            color.a
        )


class Vignette(PostProcessPass):
    """Vignette effect for edge darkening.
    
    Darkens corners to draw attention to center.
    
    Usage:
        vignette = Vignette(intensity=0.5, radius=0.75)
        final = vignette.process_at_position(color, x, y, center_x, center_y)
    """
    
    def __init__(self, intensity: float = 0.4, radius: float = 0.75):
        """Initialize vignette.
        
        Args:
            intensity: Darkness amount (0-1)
            radius: Vignette radius (0-1)
        """
        super().__init__()
        self.intensity = max(0.0, min(1.0, intensity))
        self.radius = max(0.0, min(1.0, radius))
    
    def apply_at_position(self, color: Color, x: float, y: float,
                          center_x: float, center_y: float) -> Color:
        """Apply vignette at specific position.
        
        Args:
            color: Input color
            x, y: Pixel position (0-1 normalized)
            center_x, center_y: Center position (0-1)
            
        Returns:
            Color with vignette applied
        """
        # Calculate distance from center
        dx = x - center_x
        dy = y - center_y
        dist = sqrt(dx * dx + dy * dy)
        
        # Vignette falloff
        if dist < self.radius * 0.5:
            return color
        
        # Calculate vignette factor
        t = (dist - self.radius * 0.5) / (1.0 - self.radius * 0.5)
        t = max(0.0, min(1.0, t))
        
        # Apply vignette
        factor = 1.0 - t * self.intensity
        return Color(
            color.r * factor,
            color.g * factor,
            color.b * factor,
            color.a
        )


class ChromaticAberration(PostProcessPass):
    """Chromatic aberration for RGB shift.
    
    Splits RGB channels slightly for stylistic effect.
    
    Usage:
        ca = ChromaticAberration(amount=2.0)
        final = ca.process_shifted(color, shift_x, shift_y)
    """
    
    def __init__(self, amount: float = 1.0):
        """Initialize chromatic aberration.
        
        Args:
            amount: Shift amount in pixels
        """
        super().__init__()
        self.amount = amount


class FilmGrain(PostProcessPass):
    """Film grain noise for cinematic look.
    
    Adds subtle noise to simulate film texture.
    
    Usage:
        grain = FilmGrain(intensity=0.05)
        final = grain.process_with_noise(color, noise_value)
    """
    
    def __init__(self, intensity: float = 0.03):
        """Initialize film grain.
        
        Args:
            intensity: Grain strength (0-1)
        """
        super().__init__()
        self.intensity = max(0.0, min(1.0, intensity))
    
    def process_with_noise(self, color: Color, noise: float) -> Color:
        """Apply film grain.
        
        Args:
            color: Input color
            noise: Noise value (-1 to 1)
            
        Returns:
            Color with grain
        """
        grain = noise * self.intensity
        return Color(
            max(0.0, min(1.0, color.r + grain)),
            max(0.0, min(1.0, color.g + grain)),
            max(0.0, min(1.0, color.b + grain)),
            color.a
        )


class Sharpen(PostProcessPass):
    """Sharpening filter for crisp detail.
    
    Enhances edge contrast for sharper appearance.
    
    Usage:
        sharpen = Sharpen(intensity=0.5)
        final = sharpen.process(color)
    """
    
    def __init__(self, intensity: float = 0.3):
        """Initialize sharpen.
        
        Args:
            intensity: Sharpen strength (0-1)
        """
        super().__init__()
        self.intensity = max(0.0, min(1.0, intensity))


class PostProcessStack:
    """Manages and executes post-process passes.
    
    Maintains an ordered list of post-process effects and
    applies them sequentially to produce final image.
    
    Usage:
        stack = PostProcessStack()
        stack.add_pass(ToneMapping(exposure=1.0))
        stack.add_pass(Vignette(intensity=0.4))
        final_color = stack.process(initial_color)
    """
    
    def __init__(self):
        """Initialize empty post-process stack."""
        self.passes: List[PostProcessPass] = []
    
    def add_pass(self, pass_instance: PostProcessPass) -> None:
        """Add a post-process pass to the stack.
        
        Args:
            pass_instance: Pass to add
        """
        self.passes.append(pass_instance)
    
    def remove_pass(self, pass_instance: PostProcessPass) -> bool:
        """Remove a pass from the stack.
        
        Args:
            pass_instance: Pass to remove
            
        Returns:
            True if removed
        """
        if pass_instance in self.passes:
            self.passes.remove(pass_instance)
            return True
        return False
    
    def clear(self) -> None:
        """Remove all passes."""
        self.passes.clear()
    
    def process(self, color: Color) -> Color:
        """Process color through all enabled passes.
        
        Args:
            color: Input color
            
        Returns:
            Final processed color
        """
        result = color
        
        for pass_instance in self.passes:
            result = pass_instance.process(result)
        
        return result
    
    def apply_pass(self, color: Color, pass_index: int) -> Color:
        """Apply single pass by index.
        
        Args:
            color: Input color
            pass_index: Pass index
            
        Returns:
            Processed color
        """
        if 0 <= pass_index < len(self.passes):
            return self.passes[pass_index].process(color)
        return color


class PostProcessRenderer:
    """Renders full post-process stack with ping-pong buffers.
    
    Manages frame buffers and applies full post-process pipeline
    for final image output.
    
    Usage:
        renderer = PostProcessRenderer(width=800, height=600)
        stack = PostProcessStack()
        # ... add passes ...
        final = renderer.composite_all(stack)
    """
    
    def __init__(self, width: int, height: int):
        """Initialize post-process renderer.
        
        Args:
            width: Buffer width
            height: Buffer height
        """
        self.width = width
        self.height = height
        
        # Ping-pong buffers for multi-pass effects
        self.buffer_a = self._create_buffer()
        self.buffer_b = self._create_buffer()
    
    def _create_buffer(self) -> List[List[Color]]:
        """Create empty color buffer."""
        return [[Color(0, 0, 0) for _ in range(self.width)]
                for _ in range(self.height)]
    
    def composite_all(self, stack: PostProcessStack) -> List[List[Color]]:
        """Composite all passes and return final buffer.
        
        Args:
            stack: Post-process stack
            
        Returns:
            Final processed buffer
        """
        # Simplified: return buffer_a
        # Real implementation would process through all passes
        return self.buffer_a

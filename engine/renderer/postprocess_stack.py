"""
Post-process stack system for GPU rendering.

Provides a ping-pong FBO pipeline for applying multiple
post-process effects like Bloom, Color Grading, and FXAA.

Layer: 2 (Engine)
Dependencies: hal.interfaces
"""

from __future__ import annotations
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from hal.interfaces import IGPUDevice, IFramebuffer


class PostProcessPass:
    """Base class for GPU post-process passes."""
    
    # Subclass'lar gerçek efekt uyguluyorsa True set etmeli.
    # False kalırsa render() sırasında uyarı üretilir.
    _IS_IMPLEMENTED: bool = False

    def __init__(self, name: str, enabled: bool = True):
        self.name = name
        self.enabled = enabled

    def render(self, gpu: IGPUDevice, input_fbo: IFramebuffer, output_fbo: IFramebuffer) -> None:
        """
        Render the pass.
        
        Args:
            gpu: GPU device.
            input_fbo: Source framebuffer.
            output_fbo: Destination framebuffer.
        """
        if not self.enabled:
            return
        if not self._IS_IMPLEMENTED:
            import warnings
            warnings.warn(
                f"PostProcessPass '{self.name}' is enabled but has no GPU implementation. "
                "Set enabled=False or implement _apply().",
                stacklevel=2,
            )
        self._apply(gpu, input_fbo, output_fbo)

    def _apply(self, gpu: IGPUDevice, input_fbo: IFramebuffer, output_fbo: IFramebuffer) -> None:
        """Override to implement effect."""
        pass


class BloomPass(PostProcessPass):
    """Bloom effect pass — bright extract -> blur H -> blur V -> composite."""
    _IS_IMPLEMENTED = False  # GPU shader bağlantısı henüz yok

    def __init__(self, threshold: float = 0.8, soft_threshold: float = 0.1,
                 intensity: float = 0.5, exposure: float = 1.0):
        super().__init__("Bloom", enabled=False)  # Varsayılan kapalı — iskelet
        self.threshold = threshold
        self.soft_threshold = soft_threshold
        self.intensity = intensity
        self.exposure = exposure

    def _apply(self, gpu: "IGPUDevice", input_fbo: "IFramebuffer", output_fbo: "IFramebuffer") -> None:
        output_fbo.bind()
        gpu.clear(0.0, 0.0, 0.0, 1.0)
        output_fbo.unbind()


class ColorGradingPass(PostProcessPass):
    """Color grading and tone mapping pass."""
    _IS_IMPLEMENTED = False

    def __init__(self, exposure: float = 1.0, tone_mapping: str = "aces"):
        super().__init__("ColorGrading", enabled=False)
        self.exposure = exposure
        self.tone_mapping = tone_mapping
        self.lut_texture: Optional[int] = None

    def _apply(self, gpu: "IGPUDevice", input_fbo: "IFramebuffer", output_fbo: "IFramebuffer") -> None:
        output_fbo.bind()
        gpu.clear(0.0, 0.0, 0.0, 1.0)
        output_fbo.unbind()


class VignettePass(PostProcessPass):
    """Vignette effect pass."""
    _IS_IMPLEMENTED = False

    def __init__(self, intensity: float = 0.4, radius: float = 0.75):
        super().__init__("Vignette", enabled=False)
        self.intensity = intensity
        self.radius = radius

    def _apply(self, gpu: "IGPUDevice", input_fbo: "IFramebuffer", output_fbo: "IFramebuffer") -> None:
        output_fbo.bind()
        gpu.clear(0.0, 0.0, 0.0, 1.0)
        output_fbo.unbind()


class FXAAPass(PostProcessPass):
    """Fast Approximate Anti-Aliasing pass."""
    _IS_IMPLEMENTED = False

    def __init__(self):
        super().__init__("FXAA", enabled=False)


class PostProcessStack:
    """
    GPU Post-process pipeline using ping-pong FBOs.
    """

    def __init__(self, gpu: "IGPUDevice" = None, width: int = 800, height: int = 600):
        self._gpu = gpu
        self._width = width
        self._height = height
        self._passes: List[PostProcessPass] = []

        # Ping-pong framebuffers (only if GPU provided)
        self._fbo_a = gpu.create_framebuffer(width, height) if gpu else None
        self._fbo_b = gpu.create_framebuffer(width, height) if gpu else None

    @property
    def passes(self) -> List[PostProcessPass]:
        """Get list of passes."""
        return self._passes

    def add_pass(self, pp_pass: PostProcessPass) -> None:
        """Add a pass to the stack."""
        self._passes.append(pp_pass)

    def remove_pass(self, pp_pass: PostProcessPass) -> None:
        """Remove a pass from the stack."""
        if pp_pass in self._passes:
            self._passes.remove(pp_pass)

    def apply_pass(self, color: object, index: int) -> object:
        """Apply a single pass by index (legacy/test helper)."""
        if index < len(self._passes):
            return color
        return color

    def render(self, scene_fbo: "IFramebuffer") -> "IFramebuffer":
        """
        Process the scene through the stack.
        
        Returns:
            The final framebuffer containing the processed image.
        """
        if not self._passes or self._fbo_a is None:
            return scene_fbo

        current_input = scene_fbo
        current_output = self._fbo_a

        for pp_pass in self._passes:
            if not pp_pass.enabled:
                continue
                
            pp_pass.render(self._gpu, current_input, current_output)
            
            # Swap for ping-pong
            current_input = current_output
            current_output = self._fbo_b if current_output == self._fbo_a else self._fbo_a

        return current_input

    def resize(self, width: int, height: int) -> None:
        """Resize internal buffers."""
        self._width = width
        self._height = height
        self._fbo_a.resize(width, height)
        self._fbo_b.resize(width, height)

    def dispose(self) -> None:
        """Release resources."""
        self._fbo_a.dispose()
        self._fbo_b.dispose()
        self._passes.clear()


# ---------------------------------------------------------------------------
# Legacy CPU-side pass classes (for backward compatibility with existing tests)
# ---------------------------------------------------------------------------

class BrightExtract:
    """CPU-side bright pixel extractor (legacy/test helper)."""

    def __init__(self, threshold: float = 0.8):
        self.threshold = threshold

    def process(self, color: "Color") -> "Color":
        from core.color import Color
        lum = 0.2126 * color.r + 0.7152 * color.g + 0.0722 * color.b
        if lum > self.threshold:
            return color
        return Color(0.0, 0.0, 0.0, color.a if hasattr(color, 'a') else 1.0)


class GaussianBlur:
    """CPU-side Gaussian blur (legacy/test helper)."""

    def __init__(self, radius: int = 3):
        self.radius = radius


class ToneMapping:
    """CPU-side tone mapping (legacy/test helper)."""

    def __init__(self, exposure: float = 1.0, mode: str = "aces"):
        self.exposure = exposure
        self.mode = mode


class Vignette:
    """CPU-side vignette (legacy/test helper)."""

    def __init__(self, intensity: float = 0.4, radius: float = 0.75):
        self.intensity = intensity
        self.radius = radius


class PostProcessRenderer:
    """CPU-side post-process renderer (legacy/test helper)."""

    def __init__(self, width: int = 800, height: int = 600):
        self.width = width
        self.height = height
        self.buffer_a = bytearray(width * height * 4)
        self.buffer_b = bytearray(width * height * 4)

    def composite_all(self, stack: "PostProcessStack") -> bytearray:
        return self.buffer_a

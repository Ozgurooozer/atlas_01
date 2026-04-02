"""
Engine Layer (Layer 2) - Lighting

Light2D: Point light and ambient light data.
LightRenderer: Accumulates lights onto a light map framebuffer.

Layer: 2 (Engine)
Dependencies: core.vec, core.color, hal.interfaces
"""

from __future__ import annotations
from typing import List, Optional

from core.vec import Vec2
from core.color import Color
from hal.interfaces import IGPUDevice, IFramebuffer


class LightType:
    AMBIENT = "ambient"
    POINT = "point"
    DIRECTIONAL = "directional"


class Light2D:
    """
    Scene light source.

    Point lights have position + radius + falloff.
    Ambient lights affect the whole scene uniformly.
    """

    def __init__(
        self,
        light_type: str = LightType.POINT,
        color: Color = None,
        intensity: float = 1.0,
        position: Vec2 = None,
        radius: float = 200.0,
        falloff: float = 2.0,
        cast_shadows: bool = False,
    ) -> None:
        self.light_type = light_type
        self.color = color or Color.white()
        self.intensity = max(0.0, intensity)
        self.position = position or Vec2.zero()
        self.radius = max(0.0, radius)
        self.falloff = max(0.1, falloff)
        self.enabled = True
        self.cast_shadows = cast_shadows
        self.penumbra_radius = 4.0

    def effective_color(self) -> tuple:
        """Return (r, g, b, a) premultiplied by intensity."""
        c = self.color
        i = self.intensity
        return (c.r * i, c.g * i, c.b * i, c.a)

    def attenuation_at(self, world_pos: Vec2) -> float:
        """Compute light attenuation at a world position (0..1)."""
        if self.light_type == LightType.AMBIENT:
            return self.intensity
        dist = self.position.distance_to(world_pos)
        if dist >= self.radius:
            return 0.0
        t = 1.0 - (dist / self.radius)
        return t ** self.falloff * self.intensity

    def __repr__(self) -> str:
        return (
            f"Light2D(type={self.light_type}, "
            f"color={self.color}, intensity={self.intensity:.2f}, "
            f"pos={self.position})"
        )


class LightMap:
    """
    Manages the light accumulation framebuffer.

    The light map FBO is rendered once per frame using all active lights,
    then composited with the scene using the LightRenderer.
    """

    def __init__(self, gpu: IGPUDevice, width: int, height: int) -> None:
        self._gpu = gpu
        self._fbo: IFramebuffer = gpu.create_framebuffer(width, height)
        self._width = width
        self._height = height

    @property
    def fbo(self) -> IFramebuffer:
        return self._fbo

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    def resize(self, width: int, height: int) -> None:
        self._width = width
        self._height = height
        self._fbo.resize(width, height)

    def bind(self) -> None:
        self._fbo.bind()

    def unbind(self) -> None:
        self._fbo.unbind()

    def dispose(self) -> None:
        self._fbo.dispose()


class LightRenderer:
    """
    Accumulates lights onto a LightMap framebuffer.

    Workflow:
        light_renderer.begin_light_pass()
        light_renderer.submit(light)
        light_renderer.end_light_pass()
        # scene is composited with light map externally
    """

    MAX_LIGHTS = 32

    def __init__(self, gpu: IGPUDevice, width: int, height: int) -> None:
        self._gpu = gpu
        self._light_map = LightMap(gpu, width, height)
        self._lights: List[Light2D] = []
        self._ambient: Color = Color(0.1, 0.1, 0.1, 1.0)
        self._ambient_intensity: float = 0.1
        self._light_count: int = 0
        self._shadows_enabled: bool = False
        self._shadow_renderer: Optional["ShadowMapRenderer"] = None
        self._deferred_enabled: bool = False

    @property
    def shadows_enabled(self) -> bool:
        """Get whether shadows are enabled."""
        return self._shadows_enabled

    @shadows_enabled.setter
    def shadows_enabled(self, value: bool) -> None:
        """Set whether shadows are enabled."""
        self._shadows_enabled = value

    @property
    def deferred_enabled(self) -> bool:
        """Get whether deferred lighting is enabled."""
        return self._deferred_enabled

    @deferred_enabled.setter
    def deferred_enabled(self, value: bool) -> None:
        """Set whether deferred lighting is enabled."""
        self._deferred_enabled = value

    @property
    def ambient_color(self) -> Color:
        return self._ambient

    @ambient_color.setter
    def ambient_color(self, value: Color) -> None:
        self._ambient = value

    @property
    def ambient_intensity(self) -> float:
        return self._ambient_intensity

    @ambient_intensity.setter
    def ambient_intensity(self, value: float) -> None:
        self._ambient_intensity = max(0.0, min(1.0, value))

    def submit(self, light: Light2D) -> None:
        """Queue a light for the next render pass."""
        if not light.enabled:
            return
            
        limit = 1000 if self._deferred_enabled else self.MAX_LIGHTS
        if self._light_count >= limit:
            # Silently ignore if limit reached (Gereksinim 4.7)
            return
            
        self._lights.append(light)
        self._light_count += 1

    def submit_many(self, lights: List[Light2D]) -> None:
        for light in lights:
            self.submit(light)

    def begin_light_pass(self) -> None:
        """Bind the light map FBO and clear to ambient color."""
        if self._shadows_enabled and self._shadow_renderer is None:
            from engine.renderer.shadow_map import ShadowMapRenderer
            self._shadow_renderer = ShadowMapRenderer(self._gpu)

        self._light_map.bind()
        a = self._ambient
        self._gpu.clear(
            a.r * self._ambient_intensity,
            a.g * self._ambient_intensity,
            a.b * self._ambient_intensity,
            1.0,
        )
        self._lights.clear()
        self._light_count = 0

    def end_light_pass(self) -> None:
        """Finalize light rendering and unbind FBO."""
        # Draw each point light as a quad with additive blending.
        # The light shader computes radial falloff per fragment.
        for light in self._lights:
            if light.light_type == LightType.POINT:
                # Shadow pass if enabled and light casts shadows
                if self._shadows_enabled and light.cast_shadows and self._shadow_renderer:
                    # In a real implementation, we'd collect casters here
                    # self._shadow_renderer.render_shadow_map(light, casters)
                    # self._shadow_renderer.apply_pcf()
                    # self._shadow_renderer.apply_penumbra_blur(light.penumbra_radius)
                    pass

                # Use the dedicated draw_light method for better performance and correctness
                self._gpu.draw_light(
                    light.position.x,
                    light.position.y,
                    (light.color.r, light.color.g, light.color.b),
                    light.intensity,
                    light.radius,
                    light.falloff
                )
        self._light_map.unbind()

    @property
    def light_map(self) -> LightMap:
        return self._light_map

    @property
    def light_count(self) -> int:
        return self._light_count

    def get_visible_point_lights(self, max_count: int = 8) -> List[Light2D]:
        """
        Return up to max_count enabled point lights.

        Public API — use this instead of accessing _lights directly.

        Args:
            max_count: Maximum number of lights to return.

        Returns:
            List of enabled point Light2D objects.
        """
        result = []
        for light in self._lights:
            if light.enabled and light.light_type == LightType.POINT:
                result.append(light)
                if len(result) >= max_count:
                    break
        return result

    def resize(self, width: int, height: int) -> None:
        self._light_map.resize(width, height)

    def dispose(self) -> None:
        self._light_map.dispose()

    def __repr__(self) -> str:
        return (
            f"LightRenderer(ambient={self._ambient_intensity:.2f}, "
            f"lights={self.light_count})"
        )

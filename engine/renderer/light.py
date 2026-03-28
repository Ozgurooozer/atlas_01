"""
Engine Layer (Layer 2) - Lighting

Light2D: Point light and ambient light data.
LightRenderer: Accumulates lights onto a light map framebuffer.

Layer: 2 (Engine)
Dependencies: core.vec, core.color, hal.interfaces
"""

from __future__ import annotations
import math
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
    ) -> None:
        self.light_type = light_type
        self.color = color or Color.white()
        self.intensity = max(0.0, intensity)
        self.position = position or Vec2.zero()
        self.radius = max(0.0, radius)
        self.falloff = max(0.1, falloff)
        self.enabled = True
        self.cast_shadows = False

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

    def __init__(self, gpu: IGPUDevice, width: int, height: int) -> None:
        self._gpu = gpu
        self._light_map = LightMap(gpu, width, height)
        self._lights: List[Light2D] = []
        self._ambient: Color = Color(0.1, 0.1, 0.1, 1.0)
        self._ambient_intensity: float = 0.1

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
        if light.enabled:
            self._lights.append(light)

    def submit_many(self, lights: List[Light2D]) -> None:
        for light in lights:
            self.submit(light)

    def begin_light_pass(self) -> None:
        """Bind the light map FBO and clear to ambient color."""
        self._light_map.bind()
        a = self._ambient
        self._gpu.clear(
            a.r * self._ambient_intensity,
            a.g * self._ambient_intensity,
            a.b * self._ambient_intensity,
            1.0,
        )
        self._lights.clear()

    def end_light_pass(self) -> None:
        """Finalize light rendering and unbind FBO."""
        self._light_map.unbind()

    @property
    def light_map(self) -> LightMap:
        return self._light_map

    @property
    def light_count(self) -> int:
        return len(self._lights)

    def resize(self, width: int, height: int) -> None:
        self._light_map.resize(width, height)

    def dispose(self) -> None:
        self._light_map.dispose()

    def __repr__(self) -> str:
        return (
            f"LightRenderer(ambient={self._ambient_intensity:.2f}, "
            f"lights={self.light_count})"
        )

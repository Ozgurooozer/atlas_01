"""Tests for light system.

Layer: 2 (Engine)
"""

from __future__ import annotations

import pytest

from core.color import Color
from core.vec import Vec2


class TestLight2D:
    """Test Light2D class."""

    def test_light_creation(self):
        """Test basic light creation."""
        from engine.renderer.light import Light2D, LightType

        light = Light2D(
            light_type=LightType.POINT,
            color=Color.red(),
            intensity=1.0,
            position=Vec2(100, 100),
            radius=200.0,
        )

        assert light.light_type == LightType.POINT
        assert light.intensity == 1.0
        assert light.radius == 200.0
        assert light.enabled

    def test_light_effective_color(self):
        """Test effective color calculation."""
        from engine.renderer.light import Light2D, LightType

        light = Light2D(
            light_type=LightType.POINT,
            color=Color(1.0, 0.5, 0.0, 1.0),
            intensity=0.5,
        )

        r, g, b, a = light.effective_color()

        assert r == 0.5
        assert g == 0.25
        assert b == 0.0

    def test_light_attenuation(self):
        """Test light attenuation at distance."""
        from engine.renderer.light import Light2D, LightType

        light = Light2D(
            light_type=LightType.POINT,
            position=Vec2(0, 0),
            radius=100.0,
            intensity=1.0,
        )

        # At center, full intensity
        att_center = light.attenuation_at(Vec2(0, 0))
        assert att_center == 1.0

        # At radius, zero intensity
        att_edge = light.attenuation_at(Vec2(100, 0))
        assert att_edge == 0.0

        # Beyond radius, zero intensity
        att_beyond = light.attenuation_at(Vec2(150, 0))
        assert att_beyond == 0.0

    def test_ambient_light_no_attenuation(self):
        """Test ambient light has no attenuation."""
        from engine.renderer.light import Light2D, LightType

        light = Light2D(
            light_type=LightType.AMBIENT,
            intensity=0.5,
        )

        att = light.attenuation_at(Vec2(1000, 1000))
        assert att == 0.5


class TestLightRenderer:
    """Test LightRenderer class."""

    def test_renderer_creation(self):
        """Test basic renderer creation."""
        from engine.renderer.light import LightRenderer
        from hal.headless import HeadlessGPU

        gpu = HeadlessGPU()
        renderer = LightRenderer(gpu, 800, 600)

        assert renderer.light_map.width == 800
        assert renderer.light_map.height == 600

    def test_submit_light(self):
        """Test submitting lights."""
        from engine.renderer.light import LightRenderer, Light2D, LightType
        from hal.headless import HeadlessGPU

        gpu = HeadlessGPU()
        renderer = LightRenderer(gpu, 800, 600)

        light = Light2D(light_type=LightType.POINT)
        renderer.submit(light)

        assert renderer.light_count == 1

    def test_submit_disabled_light(self):
        """Test disabled lights are not submitted."""
        from engine.renderer.light import LightRenderer, Light2D, LightType
        from hal.headless import HeadlessGPU

        gpu = HeadlessGPU()
        renderer = LightRenderer(gpu, 800, 600)

        light = Light2D(light_type=LightType.POINT)
        light.enabled = False
        renderer.submit(light)

        assert renderer.light_count == 0

    def test_ambient_settings(self):
        """Test ambient color and intensity."""
        from engine.renderer.light import LightRenderer
        from hal.headless import HeadlessGPU
        from core.color import Color

        gpu = HeadlessGPU()
        renderer = LightRenderer(gpu, 800, 600)

        renderer.ambient_color = Color(0.2, 0.3, 0.4, 1.0)
        renderer.ambient_intensity = 0.5

        assert renderer.ambient_color.to_tuple() == (0.2, 0.3, 0.4, 1.0)
        assert renderer.ambient_intensity == 0.5

    def test_light_pass(self):
        """Test light pass workflow."""
        from engine.renderer.light import LightRenderer, Light2D, LightType
        from hal.headless import HeadlessGPU

        gpu = HeadlessGPU()
        renderer = LightRenderer(gpu, 800, 600)

        renderer.begin_light_pass()

        light = Light2D(light_type=LightType.POINT)
        renderer.submit(light)

        renderer.end_light_pass()

        assert renderer.light_count == 1

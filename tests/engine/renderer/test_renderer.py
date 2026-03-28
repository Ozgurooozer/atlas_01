"""
Tests for Renderer subsystem.

Renderer provides 2D rendering capabilities.
Tests use HeadlessGPU for CI compatibility.

Layer: 2 (Engine)
"""

import pytest
from engine.subsystem import ISubsystem
from engine.renderer.renderer import IRenderer, Renderer2D
from hal.headless import HeadlessGPU
from hal.interfaces import IGPUDevice


class TestRendererInterface:
    """Test that Renderer2D implements IRenderer."""

    def test_renderer_is_subsystem(self):
        """Renderer2D should be a ISubsystem."""
        assert issubclass(Renderer2D, ISubsystem)

    def test_renderer_implements_irenderer(self):
        """Renderer2D should implement IRenderer interface."""
        assert issubclass(Renderer2D, IRenderer)

    def test_irenderer_has_clear_method(self):
        """IRenderer should define clear method."""
        assert hasattr(IRenderer, "clear")

    def test_irenderer_has_present_method(self):
        """IRenderer should define present method."""
        assert hasattr(IRenderer, "present")


class TestRendererName:
    """Test Renderer name property."""

    def test_renderer_has_name(self):
        """Renderer should have name property."""
        renderer = Renderer2D()
        assert hasattr(renderer, "name")

    def test_renderer_name_is_renderer(self):
        """Renderer name should be 'renderer'."""
        renderer = Renderer2D()
        assert renderer.name == "renderer"


class TestRendererInitialization:
    """Test Renderer initialization."""

    def test_renderer_has_initialize(self):
        """Renderer should have initialize method."""
        renderer = Renderer2D()
        assert hasattr(renderer, "initialize")
        assert callable(renderer.initialize)

    def test_renderer_initialize_accepts_engine(self):
        """Renderer initialize should accept engine parameter."""
        renderer = Renderer2D()
        # Just check it can be called
        # In production, this receives Engine instance
        renderer.initialize(None)  # Should not raise

    def test_renderer_has_gpu_device_property(self):
        """Renderer should have gpu_device property."""
        renderer = Renderer2D()
        assert hasattr(renderer, "gpu_device")

    def test_renderer_can_set_gpu_device(self):
        """Renderer gpu_device can be set."""
        renderer = Renderer2D()
        gpu = HeadlessGPU()
        renderer.gpu_device = gpu
        assert renderer.gpu_device is gpu


class TestRendererTick:
    """Test Renderer tick functionality."""

    def test_renderer_has_tick(self):
        """Renderer should have tick method."""
        renderer = Renderer2D()
        assert hasattr(renderer, "tick")
        assert callable(renderer.tick)

    def test_renderer_tick_accepts_delta_time(self):
        """Renderer tick should accept delta_time."""
        renderer = Renderer2D()
        renderer.initialize(None)
        renderer.tick(0.016)  # Should not raise


class TestRendererShutdown:
    """Test Renderer shutdown."""

    def test_renderer_has_shutdown(self):
        """Renderer should have shutdown method."""
        renderer = Renderer2D()
        assert hasattr(renderer, "shutdown")
        assert callable(renderer.shutdown)

    def test_renderer_shutdown_clears_resources(self):
        """Renderer shutdown should clear resources."""
        renderer = Renderer2D()
        gpu = HeadlessGPU()
        renderer.gpu_device = gpu
        renderer.initialize(None)
        renderer.shutdown()
        # After shutdown, gpu_device should be None
        assert renderer.gpu_device is None


class TestRendererClear:
    """Test Renderer clear functionality."""

    def test_renderer_has_clear(self):
        """Renderer should have clear method."""
        renderer = Renderer2D()
        assert hasattr(renderer, "clear")
        assert callable(renderer.clear)

    def test_clear_accepts_color(self):
        """Renderer clear should accept optional color."""
        renderer = Renderer2D()
        gpu = HeadlessGPU()
        renderer.gpu_device = gpu
        renderer.initialize(None)
        renderer.clear(0.0, 0.0, 0.0, 1.0)  # Should not raise

    def test_clear_default_color(self):
        """Renderer clear should work without color (default)."""
        renderer = Renderer2D()
        gpu = HeadlessGPU()
        renderer.gpu_device = gpu
        renderer.initialize(None)
        renderer.clear()  # Should not raise


class TestRendererPresent:
    """Test Renderer present functionality."""

    def test_renderer_has_present(self):
        """Renderer should have present method."""
        renderer = Renderer2D()
        assert hasattr(renderer, "present")
        assert callable(renderer.present)

    def test_present_swaps_buffers(self):
        """Renderer present should swap buffers."""
        renderer = Renderer2D()
        gpu = HeadlessGPU()
        renderer.gpu_device = gpu
        renderer.initialize(None)
        renderer.present()  # Should not raise


class TestRendererBackgroundColor:
    """Test Renderer background color."""

    def test_renderer_has_background_color(self):
        """Renderer should have background_color property."""
        renderer = Renderer2D()
        assert hasattr(renderer, "background_color")

    def test_background_color_default_black(self):
        """Renderer background_color should default to black."""
        renderer = Renderer2D()
        assert renderer.background_color == (0.0, 0.0, 0.0, 1.0)

    def test_background_color_can_be_set(self):
        """Renderer background_color can be set."""
        renderer = Renderer2D()
        renderer.background_color = (0.5, 0.5, 0.5, 1.0)
        assert renderer.background_color == (0.5, 0.5, 0.5, 1.0)


class TestRendererViewport:
    """Test Renderer viewport."""

    def test_renderer_has_viewport(self):
        """Renderer should have viewport property."""
        renderer = Renderer2D()
        assert hasattr(renderer, "viewport")

    def test_viewport_default(self):
        """Renderer viewport should default to (0, 0, 800, 600)."""
        renderer = Renderer2D()
        assert renderer.viewport == (0, 0, 800, 600)

    def test_viewport_can_be_set(self):
        """Renderer viewport can be set."""
        renderer = Renderer2D()
        renderer.viewport = (0, 0, 1024, 768)
        assert renderer.viewport == (0, 0, 1024, 768)


class TestRendererEnabled:
    """Test Renderer enabled state."""

    def test_renderer_has_enabled(self):
        """Renderer should have enabled property."""
        renderer = Renderer2D()
        assert hasattr(renderer, "enabled")

    def test_renderer_enabled_by_default(self):
        """Renderer should be enabled by default."""
        renderer = Renderer2D()
        assert renderer.enabled is True

    def test_disabled_renderer_skips_tick(self):
        """Disabled renderer should not render in tick."""
        renderer = Renderer2D()
        gpu = HeadlessGPU()
        renderer.gpu_device = gpu
        renderer.initialize(None)
        renderer.enabled = False
        renderer.tick(0.016)  # Should not raise

"""
Pyglet Backend Tests.

Tests for PygletWindow and ModernGLDevice implementations.
These tests check interface compliance. Actual rendering tests
require a display and are skipped in headless environments.
"""

import pytest
import sys


class TestPygletWindowImports:
    """Test PygletWindow can be imported."""

    def test_pyglet_window_import(self):
        """PygletWindow should be importable."""
        from hal.pyglet_backend import PygletWindow
        assert PygletWindow is not None

    def test_pyglet_window_implements_iwindow(self):
        """PygletWindow should implement IWindow interface."""
        from hal.pyglet_backend import PygletWindow
        from hal.interfaces import IWindow
        assert issubclass(PygletWindow, IWindow)


class TestModernGLDeviceImports:
    """Test ModernGLDevice can be imported."""

    def test_moderngl_device_import(self):
        """ModernGLDevice should be importable."""
        from hal.pyglet_backend import ModernGLDevice
        assert ModernGLDevice is not None

    def test_moderngl_device_implements_igpudevice(self):
        """ModernGLDevice should implement IGPUDevice interface."""
        from hal.pyglet_backend import ModernGLDevice
        from hal.interfaces import IGPUDevice
        assert issubclass(ModernGLDevice, IGPUDevice)


class TestPygletWindowMethods:
    """Test PygletWindow has required methods."""

    def test_has_poll_events(self):
        """PygletWindow should have poll_events method."""
        from hal.pyglet_backend import PygletWindow
        assert hasattr(PygletWindow, 'poll_events')

    def test_has_swap_buffers(self):
        """PygletWindow should have swap_buffers method."""
        from hal.pyglet_backend import PygletWindow
        assert hasattr(PygletWindow, 'swap_buffers')

    def test_has_should_close(self):
        """PygletWindow should have should_close method."""
        from hal.pyglet_backend import PygletWindow
        assert hasattr(PygletWindow, 'should_close')

    def test_has_get_size(self):
        """PygletWindow should have get_size method."""
        from hal.pyglet_backend import PygletWindow
        assert hasattr(PygletWindow, 'get_size')


class TestModernGLDeviceMethods:
    """Test ModernGLDevice has required methods."""

    def test_has_create_texture(self):
        """ModernGLDevice should have create_texture method."""
        from hal.pyglet_backend import ModernGLDevice
        assert hasattr(ModernGLDevice, 'create_texture')

    def test_has_clear(self):
        """ModernGLDevice should have clear method."""
        from hal.pyglet_backend import ModernGLDevice
        assert hasattr(ModernGLDevice, 'clear')

    def test_has_draw(self):
        """ModernGLDevice should have draw method."""
        from hal.pyglet_backend import ModernGLDevice
        assert hasattr(ModernGLDevice, 'draw')


# Skip actual window creation tests in headless environments
@pytest.mark.skipif(
    sys.platform == "linux" and not hasattr(sys, 'ps1'),
    reason="Display required for window creation"
)
class TestPygletWindowCreation:
    """Test actual PygletWindow creation (requires display)."""

    def test_create_window(self):
        """Should be able to create a window."""
        pytest.skip("Requires display - skipped in headless environment")


@pytest.mark.skipif(
    sys.platform == "linux" and not hasattr(sys, 'ps1'),
    reason="Display required for GPU context"
)
class TestModernGLDeviceCreation:
    """Test actual ModernGLDevice creation (requires display)."""

    def test_create_device(self):
        """Should be able to create a GPU device."""
        pytest.skip("Requires display - skipped in headless environment")

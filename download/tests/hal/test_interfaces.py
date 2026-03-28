"""
Platform Interface Tests.

Tests for IWindow, IGPUDevice, IFilesystem, IClock interfaces.
These are abstract interfaces - tests verify the interface contract.
"""

import pytest
from abc import ABC, abstractmethod


class TestIWindowInterface:
    """Test IWindow interface contract."""

    def test_iwindow_is_abstract(self):
        """IWindow must be an abstract class."""
        from hal.interfaces import IWindow
        assert issubclass(IWindow, ABC)

    def test_iwindow_has_poll_events_method(self):
        """IWindow must have poll_events abstract method."""
        from hal.interfaces import IWindow
        # Check method exists and is abstract
        assert hasattr(IWindow, 'poll_events')
        method = getattr(IWindow, 'poll_events')
        assert getattr(method, '__isabstractmethod__', False)

    def test_iwindow_has_swap_buffers_method(self):
        """IWindow must have swap_buffers abstract method."""
        from hal.interfaces import IWindow
        assert hasattr(IWindow, 'swap_buffers')
        method = getattr(IWindow, 'swap_buffers')
        assert getattr(method, '__isabstractmethod__', False)

    def test_iwindow_has_should_close_method(self):
        """IWindow must have should_close abstract method."""
        from hal.interfaces import IWindow
        assert hasattr(IWindow, 'should_close')
        method = getattr(IWindow, 'should_close')
        assert getattr(method, '__isabstractmethod__', False)

    def test_iwindow_has_get_size_method(self):
        """IWindow must have get_size abstract method."""
        from hal.interfaces import IWindow
        assert hasattr(IWindow, 'get_size')
        method = getattr(IWindow, 'get_size')
        assert getattr(method, '__isabstractmethod__', False)

    def test_iwindow_cannot_be_instantiated(self):
        """IWindow cannot be instantiated directly."""
        from hal.interfaces import IWindow
        with pytest.raises(TypeError):
            IWindow()


class TestIGPUDeviceInterface:
    """Test IGPUDevice interface contract."""

    def test_igpu_device_is_abstract(self):
        """IGPUDevice must be an abstract class."""
        from hal.interfaces import IGPUDevice
        assert issubclass(IGPUDevice, ABC)

    def test_igpu_device_has_create_texture_method(self):
        """IGPUDevice must have create_texture abstract method."""
        from hal.interfaces import IGPUDevice
        assert hasattr(IGPUDevice, 'create_texture')
        method = getattr(IGPUDevice, 'create_texture')
        assert getattr(method, '__isabstractmethod__', False)

    def test_igpu_device_has_clear_method(self):
        """IGPUDevice must have clear abstract method."""
        from hal.interfaces import IGPUDevice
        assert hasattr(IGPUDevice, 'clear')
        method = getattr(IGPUDevice, 'clear')
        assert getattr(method, '__isabstractmethod__', False)

    def test_igpu_device_has_draw_method(self):
        """IGPUDevice must have draw abstract method."""
        from hal.interfaces import IGPUDevice
        assert hasattr(IGPUDevice, 'draw')
        method = getattr(IGPUDevice, 'draw')
        assert getattr(method, '__isabstractmethod__', False)

    def test_igpu_device_cannot_be_instantiated(self):
        """IGPUDevice cannot be instantiated directly."""
        from hal.interfaces import IGPUDevice
        with pytest.raises(TypeError):
            IGPUDevice()


class TestIFilesystemInterface:
    """Test IFilesystem interface contract."""

    def test_ifilesystem_is_abstract(self):
        """IFilesystem must be an abstract class."""
        from hal.interfaces import IFilesystem
        assert issubclass(IFilesystem, ABC)

    def test_ifilesystem_has_read_file_method(self):
        """IFilesystem must have read_file abstract method."""
        from hal.interfaces import IFilesystem
        assert hasattr(IFilesystem, 'read_file')
        method = getattr(IFilesystem, 'read_file')
        assert getattr(method, '__isabstractmethod__', False)

    def test_ifilesystem_has_write_file_method(self):
        """IFilesystem must have write_file abstract method."""
        from hal.interfaces import IFilesystem
        assert hasattr(IFilesystem, 'write_file')
        method = getattr(IFilesystem, 'write_file')
        assert getattr(method, '__isabstractmethod__', False)

    def test_ifilesystem_has_file_exists_method(self):
        """IFilesystem must have file_exists abstract method."""
        from hal.interfaces import IFilesystem
        assert hasattr(IFilesystem, 'file_exists')
        method = getattr(IFilesystem, 'file_exists')
        assert getattr(method, '__isabstractmethod__', False)

    def test_ifilesystem_cannot_be_instantiated(self):
        """IFilesystem cannot be instantiated directly."""
        from hal.interfaces import IFilesystem
        with pytest.raises(TypeError):
            IFilesystem()


class TestIClockInterface:
    """Test IClock interface contract."""

    def test_iclock_is_abstract(self):
        """IClock must be an abstract class."""
        from hal.interfaces import IClock
        assert issubclass(IClock, ABC)

    def test_iclock_has_get_time_method(self):
        """IClock must have get_time abstract method."""
        from hal.interfaces import IClock
        assert hasattr(IClock, 'get_time')
        method = getattr(IClock, 'get_time')
        assert getattr(method, '__isabstractmethod__', False)

    def test_iclock_has_get_delta_time_method(self):
        """IClock must have get_delta_time abstract method."""
        from hal.interfaces import IClock
        assert hasattr(IClock, 'get_delta_time')
        method = getattr(IClock, 'get_delta_time')
        assert getattr(method, '__isabstractmethod__', False)

    def test_iclock_cannot_be_instantiated(self):
        """IClock cannot be instantiated directly."""
        from hal.interfaces import IClock
        with pytest.raises(TypeError):
            IClock()

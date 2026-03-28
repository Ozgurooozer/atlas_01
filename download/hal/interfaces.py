"""
Platform Hardware Abstraction Layer Interfaces.

These interfaces abstract the underlying platform (window, GPU, filesystem, clock).
Engine components depend on these interfaces, not on concrete implementations.

Layer: 0 (Platform/HAL)
Dependencies: None
"""

from abc import ABC, abstractmethod
from typing import Tuple


class IWindow(ABC):
    """
    Window interface for platform abstraction.

    Provides window management, event polling, and buffer swapping.
    Implementations: PygletWindow, GlfwWindow, HeadlessWindow.
    """

    @abstractmethod
    def poll_events(self) -> list:
        """
        Poll and return pending window events.

        Returns:
            List of Event objects (keyboard, mouse, resize, etc.)
        """
        pass

    @abstractmethod
    def swap_buffers(self) -> None:
        """Swap front and back buffers."""
        pass

    @abstractmethod
    def should_close(self) -> bool:
        """
        Check if window should close.

        Returns:
            True if window should close (user clicked X, etc.)
        """
        pass

    @abstractmethod
    def get_size(self) -> Tuple[int, int]:
        """
        Get window size in pixels.

        Returns:
            Tuple of (width, height)
        """
        pass


class IGPUDevice(ABC):
    """
    GPU device interface for rendering abstraction.

    Provides texture creation, clearing, and drawing operations.
    Implementations: ModernGLDevice, HeadlessGPU.
    """

    @abstractmethod
    def create_texture(self, width: int, height: int, data: bytes | None = None) -> int:
        """
        Create a texture on the GPU.

        Args:
            width: Texture width in pixels
            height: Texture height in pixels
            data: Optional initial pixel data (RGBA)

        Returns:
            Texture handle/ID
        """
        pass

    @abstractmethod
    def clear(self, r: float = 0.0, g: float = 0.0, b: float = 0.0, a: float = 1.0) -> None:
        """
        Clear the screen with specified color.

        Args:
            r: Red component (0.0 - 1.0)
            g: Green component (0.0 - 1.0)
            b: Blue component (0.0 - 1.0)
            a: Alpha component (0.0 - 1.0)
        """
        pass

    @abstractmethod
    def draw(self, texture_id: int, x: float, y: float, width: float | None = None, height: float | None = None) -> None:
        """
        Draw a texture at specified position.

        Args:
            texture_id: Texture handle from create_texture
            x: X position in screen coordinates
            y: Y position in screen coordinates
            width: Optional width (defaults to texture width)
            height: Optional height (defaults to texture height)
        """
        pass

    @abstractmethod
    def flush(self) -> None:
        """
        Flush pending GPU commands.

        Ensures all draw commands are executed.
        Call at end of frame before swap_buffers.
        """
        pass

    @abstractmethod
    def create_framebuffer(self, width: int, height: int) -> "IFramebuffer":
        """
        Create an off-screen framebuffer.

        Args:
            width: Framebuffer width in pixels
            height: Framebuffer height in pixels

        Returns:
            Framebuffer interface
        """
        pass


class IFramebuffer(ABC):
    """
    Framebuffer interface for off-screen rendering.

    Provides render-to-texture capability.
    """

    @abstractmethod
    def bind(self) -> None:
        """Bind framebuffer for rendering."""
        pass

    @abstractmethod
    def unbind(self) -> None:
        """Unbind framebuffer (restore default)."""
        pass

    @abstractmethod
    def resize(self, width: int, height: int) -> None:
        """Resize framebuffer."""
        pass

    @abstractmethod
    def dispose(self) -> None:
        """Release framebuffer resources."""
        pass

    @property
    @abstractmethod
    def width(self) -> int:
        """Framebuffer width."""
        pass

    @property
    @abstractmethod
    def height(self) -> int:
        """Framebuffer height."""
        pass


class IFilesystem(ABC):
    """
    Filesystem interface for I/O abstraction.

    Provides file read/write operations.
    Implementations: OSFilesystem, MemoryFilesystem.
    """

    @abstractmethod
    def read_file(self, path: str) -> bytes:
        """
        Read file contents as bytes.

        Args:
            path: File path (relative or absolute)

        Returns:
            File contents as bytes

        Raises:
            FileNotFoundError: If file does not exist
        """
        pass

    @abstractmethod
    def write_file(self, path: str, data: bytes) -> None:
        """
        Write bytes to file.

        Args:
            path: File path (relative or absolute)
            data: Data to write
        """
        pass

    @abstractmethod
    def file_exists(self, path: str) -> bool:
        """
        Check if file exists.

        Args:
            path: File path to check

        Returns:
            True if file exists
        """
        pass


class IClock(ABC):
    """
    Clock interface for time abstraction.

    Provides time and delta time for game loop.
    Implementations: SystemClock, FixedClock (for tests).
    """

    @abstractmethod
    def get_time(self) -> float:
        """
        Get current time in seconds.

        Returns:
            Time in seconds since some fixed point
        """
        pass

    @abstractmethod
    def get_delta_time(self) -> float:
        """
        Get time elapsed since last frame.

        Returns:
            Delta time in seconds
        """
        pass

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
    def draw(
        self,
        texture_id: int,
        x: float,
        y: float,
        width: float | None = None,
        height: float | None = None,
        rotation: float = 0.0,
        color: Tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0),
        flip_x: bool = False,
        flip_y: bool = False,
        anchor_x: float = 0.5,
        anchor_y: float = 0.5,
        view_matrix: Tuple[float, ...] | None = None,
        projection_matrix: Tuple[float, ...] | None = None,
    ) -> None:
        """
        Draw a texture at specified position with transform and color.

        Args:
            texture_id: Texture handle from create_texture
            x: X position in screen coordinates
            y: Y position in screen coordinates
            width: Optional width (defaults to texture width)
            height: Optional height (defaults to texture height)
            rotation: Rotation in degrees
            color: RGBA color (0.0 - 1.0)
            flip_x: Flip texture horizontally
            flip_y: Flip texture vertically
            anchor_x: Horizontal anchor point (0.0 - 1.0)
            anchor_y: Vertical anchor point (0.0 - 1.0)
            view_matrix: Optional 4x4 view matrix
            projection_matrix: Optional 4x4 projection matrix
        """
        pass

    @abstractmethod
    def draw_with_normal_map(
        self,
        texture_id: int,
        normal_map_id: int,
        x: float,
        y: float,
        width: float | None = None,
        height: float | None = None,
        rotation: float = 0.0,
        color: Tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0),
        flip_x: bool = False,
        flip_y: bool = False,
        anchor_x: float = 0.5,
        anchor_y: float = 0.5,
        view_matrix: Tuple[float, ...] | None = None,
        projection_matrix: Tuple[float, ...] | None = None,
        lights: list | None = None,
        ambient: Tuple[float, float, float] = (0.1, 0.1, 0.1),
    ) -> None:
        """Draw a quad with normal mapping and point lights."""
        pass

    @abstractmethod
    def draw_light(
        self,
        x: float,
        y: float,
        color: Tuple[float, float, float],
        intensity: float,
        radius: float,
        falloff: float,
        projection_matrix: Tuple[float, ...] | None = None,
    ) -> None:
        """Draw a light pass quad (additive)."""
        pass

    @abstractmethod
    def draw_instanced(
        self,
        texture_id: int,
        instance_data: bytes,
        instance_count: int,
        view_matrix: Tuple[float, ...] | None = None,
        projection_matrix: Tuple[float, ...] | None = None,
    ) -> None:
        """Draw multiple instances of a quad with per-instance data."""
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
        Create a new GPU framebuffer.

        Args:
            width: Framebuffer width in pixels
            height: Framebuffer height in pixels

        Returns:
            A new IFramebuffer instance
        """
        pass

    @abstractmethod
    def create_mrt_framebuffer(self, width: int, height: int, attachments: int) -> "IFramebuffer":
        """
        Create a Multiple Render Target (MRT) framebuffer.

        Args:
            width: Framebuffer width in pixels
            height: Framebuffer height in pixels
            attachments: Number of color attachments

        Returns:
            A new IFramebuffer instance with multiple color targets
        """
        pass

    @abstractmethod
    def create_depth_framebuffer(self, width: int, height: int) -> "IFramebuffer":
        """
        Create a depth-only framebuffer.

        Args:
            width: Framebuffer width in pixels
            height: Framebuffer height in pixels

        Returns:
            A new IFramebuffer instance with only a depth target
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

    @property
    @abstractmethod
    def is_bound(self) -> bool:
        """Check if framebuffer is currently bound."""
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

    @abstractmethod
    def delete_file(self, path: str) -> None:
        """
        Delete a file.

        Args:
            path: File path to delete

        Raises:
            FileNotFoundError: If file does not exist
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

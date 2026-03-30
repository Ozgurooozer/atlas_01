"""
Headless Implementations for Testing.

These implementations work without real hardware (GPU, window, filesystem).
Useful for CI/CD pipelines and unit tests.

Layer: 0 (Platform/HAL)
Dependencies: hal.interfaces
"""

from typing import Tuple

from hal.interfaces import IWindow, IGPUDevice, IFilesystem, IClock, IFramebuffer


class HeadlessWindow(IWindow):
    """
    Headless window implementation for testing.

    No actual window is created. All operations are no-ops.
    Useful for testing game logic without display.
    """

    def __init__(self, width: int = 800, height: int = 600):
        """
        Initialize headless window.

        Args:
            width: Window width in pixels
            height: Window height in pixels
        """
        self._width = width
        self._height = height
        self._should_close = False

    def poll_events(self) -> list:
        """Return empty event list (no input in headless mode)."""
        return []

    def swap_buffers(self) -> None:
        """No-op in headless mode."""
        pass

    def should_close(self) -> bool:
        """Return whether window should close."""
        return self._should_close

    def get_size(self) -> Tuple[int, int]:
        """Return window size."""
        return (self._width, self._height)

    def close(self) -> None:
        """Set window to close."""
        self._should_close = True


class HeadlessGPU(IGPUDevice):
    """
    Headless GPU implementation for testing.

    No actual GPU operations. Texture IDs are simulated.
    Useful for testing rendering logic without GPU.
    """

    def __init__(self):
        """Initialize headless GPU."""
        self._next_texture_id = 1
        self._textures = {}  # id -> (width, height, data)

    def create_texture(self, width: int, height: int, data: bytes | None = None) -> int:
        """
        Create a simulated texture.

        Args:
            width: Texture width
            height: Texture height
            data: Optional pixel data (ignored)

        Returns:
            Unique texture ID
        """
        tex_id = self._next_texture_id
        self._next_texture_id += 1
        self._textures[tex_id] = (width, height, data)
        return tex_id

    def clear(self, r: float = 0.0, g: float = 0.0, b: float = 0.0, a: float = 1.0) -> None:
        """No-op in headless mode."""
        pass

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
        """No-op in headless mode."""
        pass

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
        """No-op in headless mode."""
        pass

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
        """No-op in headless mode."""
        pass

    def draw_instanced(
        self,
        texture_id: int,
        instance_data: bytes,
        instance_count: int,
        view_matrix: Tuple[float, ...] | None = None,
        projection_matrix: Tuple[float, ...] | None = None,
    ) -> None:
        """No-op in headless mode."""
        pass

    def flush(self) -> None:
        """No-op in headless mode."""
        pass

    def create_framebuffer(self, width: int, height: int) -> IFramebuffer:
        """Create headless framebuffer."""
        return HeadlessFramebuffer(width, height)

    def create_mrt_framebuffer(self, width: int, height: int, attachments: int) -> IFramebuffer:
        """Create headless MRT framebuffer."""
        return HeadlessFramebuffer(width, height)

    def create_depth_framebuffer(self, width: int, height: int) -> IFramebuffer:
        """Create headless depth framebuffer."""
        return HeadlessFramebuffer(width, height)


class HeadlessFramebuffer(IFramebuffer):
    """Headless framebuffer for testing."""

    def __init__(self, width: int, height: int):
        self._width = width
        self._height = height
        self._bound = False

    def bind(self) -> None:
        self._bound = True

    def unbind(self) -> None:
        self._bound = False

    def resize(self, width: int, height: int) -> None:
        self._width = width
        self._height = height

    def dispose(self) -> None:
        pass

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    @property
    def is_bound(self) -> bool:
        return self._bound


class MemoryFilesystem(IFilesystem):
    """
    In-memory filesystem implementation for testing.

    Files are stored in a dictionary, not on disk.
    Useful for testing asset loading without real files.
    """

    def __init__(self):
        """Initialize empty memory filesystem."""
        self._files = {}  # path -> bytes

    def read_file(self, path: str) -> bytes:
        """
        Read file from memory.

        Args:
            path: File path

        Returns:
            File contents

        Raises:
            FileNotFoundError: If file does not exist
        """
        if path not in self._files:
            raise FileNotFoundError(f"File not found: {path}")
        return self._files[path]

    def write_file(self, path: str, data: bytes) -> None:
        """
        Write file to memory.

        Args:
            path: File path
            data: Data to write
        """
        self._files[path] = data

    def file_exists(self, path: str) -> bool:
        """
        Check if file exists in memory.

        Args:
            path: File path

        Returns:
            True if file exists
        """
        return path in self._files

    def delete_file(self, path: str) -> None:
        """
        Delete file from memory.

        Args:
            path: File path

        Raises:
            FileNotFoundError: If file does not exist
        """
        if path not in self._files:
            raise FileNotFoundError(f"File not found: {path}")
        del self._files[path]


class FixedClock(IClock):
    """
    Fixed clock implementation for deterministic testing.

    Time advances by fixed delta each frame.
    Useful for predictable test results.
    """

    def __init__(self, initial_time: float = 0.0, delta_time: float = 1.0 / 60.0):
        """
        Initialize fixed clock.

        Args:
            initial_time: Starting time in seconds
            delta_time: Time step per frame in seconds
        """
        self._time = initial_time
        self._delta_time = delta_time

    def get_time(self) -> float:
        """Get current time."""
        return self._time

    def get_delta_time(self) -> float:
        """Get delta time."""
        return self._delta_time

    def advance(self) -> None:
        """Advance time by delta (for testing)."""
        self._time += self._delta_time

"""
Texture class for GPU textures.

Provides texture data management for the renderer.
Supports Pillow-based loading and GPU upload tracking.

Layer: 2 (Engine)
Dependencies: core.object
"""

from __future__ import annotations

import io
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, TYPE_CHECKING

from core.object import Object

if TYPE_CHECKING:
    pass


class UVRegion:
    """
    Normalized UV coordinates for a sub-region of a texture.

    u0, v0 = top-left; u1, v1 = bottom-right (in 0..1 space)
    """

    __slots__ = ("u0", "v0", "u1", "v1")

    def __init__(
        self,
        u0: float = 0.0,
        v0: float = 0.0,
        u1: float = 1.0,
        v1: float = 1.0,
    ) -> None:
        self.u0 = u0
        self.v0 = v0
        self.u1 = u1
        self.v1 = v1

    @property
    def width(self) -> float:
        return self.u1 - self.u0

    @property
    def height(self) -> float:
        return self.v1 - self.v0

    def to_tuple(self) -> Tuple[float, float, float, float]:
        return (self.u0, self.v0, self.u1, self.v1)

    @classmethod
    def full(cls) -> "UVRegion":
        return cls(0.0, 0.0, 1.0, 1.0)

    def __repr__(self) -> str:
        return f"UVRegion({self.u0:.3f}, {self.v0:.3f}, {self.u1:.3f}, {self.v1:.3f})"


class Texture(Object):
    """
    GPU texture representation.

    Stores texture data and tracks GPU upload state.
    Supports pixel manipulation and region extraction.

    Attributes:
        width: Texture width in pixels.
        height: Texture height in pixels.
        data: Raw RGBA pixel data (bytes).
        gpu_id: GPU texture ID after upload.
        is_uploaded: Whether texture is uploaded to GPU.
    """

    def __init__(
        self,
        width: int = 0,
        height: int = 0,
        data: Optional[bytes] = None,
        name: Optional[str] = None
    ) -> None:
        """
        Create a texture.

        Args:
            width: Texture width in pixels.
            height: Texture height in pixels.
            data: Optional RGBA pixel data.
            name: Optional texture name.
        """
        super().__init__(name=name or "Texture")
        self._width = max(0, width)
        self._height = max(0, height)
        self._data: Optional[bytes] = data
        self._gpu_id: Optional[int] = None
        self._is_uploaded: bool = False

    @property
    def width(self) -> int:
        """Get texture width."""
        return self._width

    @property
    def height(self) -> int:
        """Get texture height."""
        return self._height

    @property
    def data(self) -> Optional[bytes]:
        """Get texture data."""
        return self._data

    @data.setter
    def data(self, value: Optional[bytes]) -> None:
        """Set texture data."""
        self._data = value
        self._is_uploaded = False  # Data changed, needs re-upload

    @property
    def gpu_id(self) -> Optional[int]:
        """Get GPU texture ID."""
        return self._gpu_id

    @property
    def is_uploaded(self) -> bool:
        """Check if texture is uploaded to GPU."""
        return self._is_uploaded

    @property
    def pixel_count(self) -> int:
        """Get total pixel count."""
        return self._width * self._height

    @property
    def bytes_per_pixel(self) -> int:
        """Get bytes per pixel (4 for RGBA)."""
        return 4

    @property
    def data_size(self) -> int:
        """Get total data size in bytes."""
        return self._width * self._height * 4

    @property
    def is_valid(self) -> bool:
        """Check if texture has valid dimensions."""
        return self._width > 0 and self._height > 0

    @property
    def has_transparency(self) -> bool:
        """Check if texture has any transparent pixels."""
        if self._data is None:
            return False

        # Check alpha channel (every 4th byte)
        for i in range(3, len(self._data), 4):
            if self._data[i] < 255:
                return True
        return False

    def get_pixel(self, x: int, y: int) -> Tuple[int, int, int, int]:
        """
        Get pixel color at position.

        Args:
            x: X coordinate.
            y: Y coordinate.

        Returns:
            (r, g, b, a) tuple.
        """
        if self._data is None:
            return (0, 0, 0, 0)

        if x < 0 or x >= self._width or y < 0 or y >= self._height:
            return (0, 0, 0, 0)

        # Calculate index (top-left origin)
        index = (y * self._width + x) * 4

        return (
            self._data[index],
            self._data[index + 1],
            self._data[index + 2],
            self._data[index + 3]
        )

    def set_pixel(self, x: int, y: int, color: Tuple[int, int, int, int]) -> None:
        """
        Set pixel color at position.

        Args:
            x: X coordinate.
            y: Y coordinate.
            color: (r, g, b, a) tuple.
        """
        if self._data is None:
            # Create empty data
            self._data = bytes(self.data_size)

        if x < 0 or x >= self._width or y < 0 or y >= self._height:
            return

        # Convert to mutable bytearray
        data = bytearray(self._data)
        index = (y * self._width + x) * 4

        data[index] = color[0]
        data[index + 1] = color[1]
        data[index + 2] = color[2]
        data[index + 3] = color[3]

        self._data = bytes(data)
        self._is_uploaded = False

    def fill(self, color: Tuple[int, int, int, int]) -> None:
        """
        Fill texture with a color.

        Args:
            color: (r, g, b, a) tuple.
        """
        data = bytearray(self.data_size)
        r, g, b, a = color

        for i in range(0, len(data), 4):
            data[i] = r
            data[i + 1] = g
            data[i + 2] = b
            data[i + 3] = a

        self._data = bytes(data)
        self._is_uploaded = False

    def get_region(
        self,
        x: int,
        y: int,
        width: int,
        height: int
    ) -> Dict[str, Any]:
        """
        Get a region of the texture.

        Args:
            x: Region X offset.
            y: Region Y offset.
            width: Region width.
            height: Region height.

        Returns:
            Region dictionary with coordinates and texture reference.
        """
        return {
            'x': x,
            'y': y,
            'width': width,
            'height': height,
            'texture': self
        }

    def get_uv_coords(self, region: Dict[str, Any]) -> Dict[str, float]:
        """
        Get normalized UV coordinates for a region.

        Args:
            region: Region dictionary from get_region().

        Returns:
            Dictionary with u1, v1, u2, v2 coordinates.
        """
        return {
            'u1': region['x'] / self._width,
            'v1': region['y'] / self._height,
            'u2': (region['x'] + region['width']) / self._width,
            'v2': (region['y'] + region['height']) / self._height
        }

    def sub_region(self, x: int, y: int, w: int, h: int) -> UVRegion:
        """
        Get UVRegion for a sub-region of the texture.

        Args:
            x: X offset in pixels.
            y: Y offset in pixels.
            w: Width in pixels.
            h: Height in pixels.

        Returns:
            UVRegion with normalized coordinates.
        """
        u0 = x / self._width
        v0 = y / self._height
        u1 = (x + w) / self._width
        v1 = (y + h) / self._height
        return UVRegion(u0, v0, u1, v1)

    def mark_uploaded(self, gpu_id: int) -> None:
        """
        Mark texture as uploaded to GPU.

        Args:
            gpu_id: GPU texture ID.
        """
        self._gpu_id = gpu_id
        self._is_uploaded = True

    def clone(self) -> Texture:
        """
        Create a copy of this texture.

        Returns:
            New Texture with copied data.
        """
        # Copy data if it exists (deep copy)
        data_copy = bytes(bytearray(self._data)) if self._data else None

        return Texture(
            width=self._width,
            height=self._height,
            data=data_copy,
            name=f"{self.name}_clone"
        )

    @classmethod
    def placeholder(cls, width: int = 32, height: int = 32) -> "Texture":
        """
        Magenta placeholder texture — eksik asset durumunda kullanılır.

        Sessiz hata yerine görsel sinyal: magenta (255, 0, 255) renk.

        Args:
            width: Placeholder genişliği.
            height: Placeholder yüksekliği.

        Returns:
            Magenta dolu Texture.
        """
        return cls.from_color(width, height, (255, 0, 255, 255))

    @classmethod
    def from_data(
        cls,
        width: int,
        height: int,
        data: bytes
    ) -> Texture:
        """
        Create texture from raw RGBA data.

        Args:
            width: Texture width.
            height: Texture height.
            data: RGBA pixel data.

        Returns:
            New Texture instance.
        """
        return cls(width=width, height=height, data=data)

    @classmethod
    def from_color(
        cls,
        width: int,
        height: int,
        color: Tuple[int, int, int, int]
    ) -> Texture:
        """
        Create a solid color texture.

        Args:
            width: Texture width.
            height: Texture height.
            color: (r, g, b, a) tuple.

        Returns:
            New Texture instance.
        """
        texture = cls(width=width, height=height)
        texture.fill(color)
        return texture

    @classmethod
    def from_file(cls, path: str) -> Texture:
        """
        Load texture from image file.

        Supports PNG, JPEG, BMP, and other formats via Pillow.

        Args:
            path: Path to image file.

        Returns:
            New Texture instance.

        Raises:
            FileNotFoundError: If file does not exist.
        """
        from PIL import Image

        # Check file exists
        if not Path(path).exists():
            raise FileNotFoundError(f"Texture file not found: {path}")

        # Load image with Pillow
        img = Image.open(path)

        # Convert to RGBA if needed
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        width = img.width
        height = img.height

        # Get raw pixel data
        data = img.tobytes()

        return cls(width=width, height=height, data=data, name=Path(path).stem)

    @classmethod
    def from_bytes(cls, data: bytes, format: str = 'PNG') -> Texture:
        """
        Load texture from bytes data.

        Args:
            data: Raw image file data (PNG, JPEG, etc.).
            format: Image format hint (PNG, JPEG, etc.).

        Returns:
            New Texture instance.
        """
        from PIL import Image

        buffer = io.BytesIO(data)
        img = Image.open(buffer)

        # Convert to RGBA if needed
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        width = img.width
        height = img.height
        pixel_data = img.tobytes()

        return cls(width=width, height=height, data=pixel_data)

    def save(self, path: str) -> None:
        """
        Save texture to image file.

        Format is determined by file extension.

        Args:
            path: Output file path (.png, .jpg, etc.).
        """
        from PIL import Image

        if self._data is None:
            # Create empty data
            self.fill((0, 0, 0, 255))

        # Create image from data
        img = Image.frombytes('RGBA', (self._width, self._height), self._data)

        # Save to file
        img.save(path)

    def serialize(self) -> Dict[str, Any]:
        """Serialize texture metadata (not pixel data)."""
        data = super().serialize()
        data['width'] = self._width
        data['height'] = self._height
        # Don't serialize pixel data - too large
        return data

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"Texture(width={self._width}, height={self._height}, "
            f"uploaded={self._is_uploaded})"
        )


class TextureLoader:
    """
    Texture loader with caching support.

    Loads textures from files and caches them for reuse.
    Useful for asset management in games.

    Example:
        >>> loader = TextureLoader()
        >>> texture = loader.load("assets/player.png")
        >>> same_texture = loader.load("assets/player.png")  # Returns cached
    """

    def __init__(self) -> None:
        """Create a new TextureLoader with empty cache."""
        self._cache: Dict[str, Texture] = {}

    def load(self, path: str) -> Texture:
        """
        Load texture from file with caching.

        If texture was loaded before, returns cached instance.

        Args:
            path: Path to image file.

        Returns:
            Texture instance.
        """
        # Check cache
        if path in self._cache:
            return self._cache[path]

        # Load new texture
        texture = Texture.from_file(path)
        self._cache[path] = texture
        return texture

    def clear_cache(self) -> None:
        """Clear all cached textures."""
        self._cache.clear()

    def get_cached(self, path: str) -> Optional[Texture]:
        """
        Get cached texture without loading.

        Args:
            path: Path to check.

        Returns:
            Cached Texture or None if not cached.
        """
        return self._cache.get(path)

    def is_cached(self, path: str) -> bool:
        """
        Check if path is cached.

        Args:
            path: Path to check.

        Returns:
            True if texture is cached.
        """
        return path in self._cache

    def unload(self, path: str) -> bool:
        """
        Remove texture from cache.

        Args:
            path: Path to unload.

        Returns:
            True if texture was in cache and removed.
        """
        if path in self._cache:
            del self._cache[path]
            return True
        return False

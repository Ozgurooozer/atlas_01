"""
Asset Subsystem.

Provides asset loading and caching.
Uses IFilesystem abstraction for file operations.

Layer: 2 (Engine)
Dependencies: engine.subsystem, hal.interfaces
"""

from __future__ import annotations
from abc import abstractmethod
from typing import Any, Dict, Optional, TYPE_CHECKING

from engine.subsystem import ISubsystem

if TYPE_CHECKING:
    from engine.engine import Engine
    from hal.interfaces import IFilesystem


class IAssetManager(ISubsystem):
    """
    Interface for asset management subsystems.

    Extends ISubsystem with asset-specific methods.
    """

    @abstractmethod
    def load_text(self, path: str) -> str:
        """Load a text file."""
        pass

    @abstractmethod
    def load_bytes(self, path: str) -> bytes:
        """Load a binary file."""
        pass

    @abstractmethod
    def unload(self, path: str) -> None:
        """Unload an asset from cache."""
        pass

    @abstractmethod
    def has_asset(self, path: str) -> bool:
        """Check if asset is in cache."""
        pass


class AssetManager(IAssetManager):
    """
    Asset manager implementation.

    Provides asset loading and caching:
    - Text file loading
    - Binary file loading
    - In-memory caching

    Example:
        >>> manager = AssetManager()
        >>> fs = MemoryFilesystem()
        >>> fs.write_file("config.txt", b"settings")
        >>> manager.filesystem = fs
        >>> manager.initialize(engine)
        >>> content = manager.load_text("config.txt")

    Attributes:
        filesystem: The filesystem to use for loading
        enabled: Whether asset manager is active
        asset_count: Number of cached assets
    """

    def __init__(self):
        """Create a new AssetManager."""
        self._filesystem: Optional["IFilesystem"] = None
        self._enabled: bool = True
        self._cache: Dict[str, Any] = {}

    @property
    def name(self) -> str:
        """Get subsystem name."""
        return "asset"

    @property
    def filesystem(self) -> Optional["IFilesystem"]:
        """Get the filesystem."""
        return self._filesystem

    @filesystem.setter
    def filesystem(self, value: Optional["IFilesystem"]) -> None:
        """Set the filesystem."""
        self._filesystem = value

    @property
    def enabled(self) -> bool:
        """Get whether asset manager is enabled."""
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """Set whether asset manager is enabled."""
        self._enabled = value

    @property
    def asset_count(self) -> int:
        """Get number of cached assets."""
        return len(self._cache)

    def initialize(self, engine: Optional["Engine"]) -> None:
        """
        Initialize the asset manager.

        Args:
            engine: Reference to the Engine (can be None for testing)
        """
        pass

    def tick(self, dt: float) -> None:
        """
        Update the asset manager.

        Args:
            dt: Delta time in seconds
        """
        pass

    def shutdown(self) -> None:
        """Clean up asset manager resources."""
        self._cache.clear()

    def load_text(self, path: str) -> str:
        """
        Load a text file.

        Caches the result for future access.

        Args:
            path: File path

        Returns:
            File content as string
        """
        if path in self._cache:
            return self._cache[path]

        if self._filesystem is None:
            raise RuntimeError("No filesystem set")

        data = self._filesystem.read_file(path)
        content = data.decode("utf-8")
        self._cache[path] = content
        return content

    def load_bytes(self, path: str) -> bytes:
        """
        Load a binary file.

        Caches the result for future access.

        Args:
            path: File path

        Returns:
            File content as bytes
        """
        if path in self._cache:
            return self._cache[path]

        if self._filesystem is None:
            raise RuntimeError("No filesystem set")

        data = self._filesystem.read_file(path)
        self._cache[path] = data
        return data

    def unload(self, path: str) -> None:
        """
        Unload an asset from cache.

        Args:
            path: File path to unload
        """
        if path in self._cache:
            del self._cache[path]

    def has_asset(self, path: str) -> bool:
        """
        Check if asset is in cache.

        Args:
            path: File path

        Returns:
            True if asset is cached
        """
        return path in self._cache

    def clear_cache(self) -> None:
        """Clear all cached assets."""
        self._cache.clear()

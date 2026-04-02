"""
OSFilesystem - Real filesystem implementation.

This module provides a real implementation of IFilesystem
using Python's standard library for actual file I/O.

Layer: 0 (HAL)
Dependencies: hal.interfaces
"""

from __future__ import annotations
from pathlib import Path
from typing import List, Optional

from hal.interfaces import IFilesystem


class OSFilesystem(IFilesystem):
    """
    Real filesystem implementation using Python stdlib.

    Reads and writes actual files on disk. Can operate with
    a base path (for sandboxed access) or with absolute paths.

    Example:
        >>> fs = OSFilesystem(base_path="/game/assets")
        >>> data = fs.read_file("sprites/player.png")
        >>> fs.write_file("save/game1.sav", save_data)

        >>> # Or without base path (absolute paths only)
        >>> fs = OSFilesystem()
        >>> data = fs.read_file("/absolute/path/to/file.txt")
    """

    def __init__(self, base_path: str | None = None):
        """
        Create an OSFilesystem.

        Args:
            base_path: Optional base path for relative paths.
                      If None, only absolute paths work.
        """
        self._base_path = Path(base_path) if base_path else None

    def _resolve_path(self, path: str) -> Path:
        """
        Resolve a path to an absolute path.

        Args:
            path: Relative or absolute path

        Returns:
            Absolute Path object
        """
        path_obj = Path(path)

        # If path is absolute, use it directly
        if path_obj.is_absolute():
            return path_obj

        # If we have a base path, resolve relative to it
        if self._base_path:
            return self._base_path / path

        # No base path and relative path - error
        raise ValueError(
            f"Relative path '{path}' requires a base_path. "
            "Either set base_path or use absolute paths."
        )

    def read_file(self, path: str) -> bytes:
        """
        Read file contents as bytes.

        Args:
            path: File path (relative to base_path or absolute)

        Returns:
            File contents as bytes

        Raises:
            FileNotFoundError: If file does not exist
        """
        resolved = self._resolve_path(path)

        if not resolved.exists():
            raise FileNotFoundError(f"File not found: {path}")

        with open(resolved, "rb") as f:
            return f.read()

    def write_file(self, path: str, data: bytes) -> None:
        """
        Write bytes to file.

        Creates parent directories if they don't exist.

        Args:
            path: File path (relative to base_path or absolute)
            data: Data to write
        """
        resolved = self._resolve_path(path)

        # Create parent directories if needed
        resolved.parent.mkdir(parents=True, exist_ok=True)

        with open(resolved, "wb") as f:
            f.write(data)

    def file_exists(self, path: str) -> bool:
        """
        Check if file exists.

        Args:
            path: File path to check

        Returns:
            True if file exists
        """
        try:
            resolved = self._resolve_path(path)
            return resolved.exists() and resolved.is_file()
        except ValueError:
            return False

    def delete_file(self, path: str) -> None:
        """
        Delete a file.

        Args:
            path: File path to delete

        Raises:
            FileNotFoundError: If file does not exist
        """
        try:
            resolved = self._resolve_path(path)
        except ValueError:
            raise FileNotFoundError(f"File not found: {path}")
        if not resolved.exists() or not resolved.is_file():
            raise FileNotFoundError(f"File not found: {path}")
        resolved.unlink()

    def list_files(self, directory: str = "") -> List[str]:
        """
        List files in a directory.

        Args:
            directory: Directory path (relative to base_path or absolute)

        Returns:
            List of file names in the directory
        """
        try:
            resolved = self._resolve_path(directory)
        except ValueError:
            return []

        if not resolved.exists() or not resolved.is_dir():
            return []

        return [f.name for f in resolved.iterdir() if f.is_file()]

    def list_directories(self, directory: str = "") -> List[str]:
        """
        List subdirectories in a directory.

        Args:
            directory: Directory path

        Returns:
            List of directory names
        """
        try:
            resolved = self._resolve_path(directory)
        except ValueError:
            return []

        if not resolved.exists() or not resolved.is_dir():
            return []

        return [d.name for d in resolved.iterdir() if d.is_dir()]

    def create_directory(self, path: str) -> None:
        """
        Create a directory and all parent directories.

        Args:
            path: Directory path to create
        """
        resolved = self._resolve_path(path)
        resolved.mkdir(parents=True, exist_ok=True)

    def get_file_size(self, path: str) -> Optional[int]:
        """
        Get file size in bytes.

        Args:
            path: File path

        Returns:
            File size in bytes, or None if file doesn't exist
        """
        try:
            resolved = self._resolve_path(path)
            if resolved.exists() and resolved.is_file():
                return resolved.stat().st_size
            return None
        except ValueError:
            return None

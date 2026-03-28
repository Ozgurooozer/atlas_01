"""
OSFilesystem Tests.

Tests for real filesystem implementation using Python stdlib.
OSFilesystem reads/writes actual files on disk.
"""

import pytest
import tempfile
import os


class TestOSFilesystemImports:
    """Test OSFilesystem can be imported."""

    def test_os_filesystem_import(self):
        """OSFilesystem should be importable."""
        from hal.os_filesystem import OSFilesystem
        assert OSFilesystem is not None

    def test_os_filesystem_implements_ifilesystem(self):
        """OSFilesystem should implement IFilesystem interface."""
        from hal.os_filesystem import OSFilesystem
        from hal.interfaces import IFilesystem
        assert issubclass(OSFilesystem, IFilesystem)


class TestOSFilesystemMethods:
    """Test OSFilesystem has required methods."""

    def test_has_read_file(self):
        """OSFilesystem should have read_file method."""
        from hal.os_filesystem import OSFilesystem
        assert hasattr(OSFilesystem, 'read_file')

    def test_has_write_file(self):
        """OSFilesystem should have write_file method."""
        from hal.os_filesystem import OSFilesystem
        assert hasattr(OSFilesystem, 'write_file')

    def test_has_file_exists(self):
        """OSFilesystem should have file_exists method."""
        from hal.os_filesystem import OSFilesystem
        assert hasattr(OSFilesystem, 'file_exists')


class TestOSFilesystemOperations:
    """Test OSFilesystem operations with real files."""

    def test_write_and_read_file(self):
        """Should write and read a file."""
        from hal.os_filesystem import OSFilesystem

        with tempfile.TemporaryDirectory() as tmpdir:
            fs = OSFilesystem(base_path=tmpdir)
            test_path = "test.txt"
            test_data = b"Hello, World!"

            fs.write_file(test_path, test_data)
            assert fs.file_exists(test_path)

            read_data = fs.read_file(test_path)
            assert read_data == test_data

    def test_read_nonexistent_file_raises(self):
        """Reading nonexistent file should raise FileNotFoundError."""
        from hal.os_filesystem import OSFilesystem

        with tempfile.TemporaryDirectory() as tmpdir:
            fs = OSFilesystem(base_path=tmpdir)

            with pytest.raises(FileNotFoundError):
                fs.read_file("nonexistent.txt")

    def test_file_exists_returns_false_for_nonexistent(self):
        """file_exists should return False for nonexistent file."""
        from hal.os_filesystem import OSFilesystem

        with tempfile.TemporaryDirectory() as tmpdir:
            fs = OSFilesystem(base_path=tmpdir)
            assert fs.file_exists("nonexistent.txt") is False

    def test_file_exists_returns_true_for_existing(self):
        """file_exists should return True for existing file."""
        from hal.os_filesystem import OSFilesystem

        with tempfile.TemporaryDirectory() as tmpdir:
            fs = OSFilesystem(base_path=tmpdir)
            fs.write_file("exists.txt", b"data")
            assert fs.file_exists("exists.txt") is True

    def test_write_creates_subdirectories(self):
        """write_file should create subdirectories if needed."""
        from hal.os_filesystem import OSFilesystem

        with tempfile.TemporaryDirectory() as tmpdir:
            fs = OSFilesystem(base_path=tmpdir)
            test_path = "subdir/nested/file.txt"
            test_data = b"nested content"

            fs.write_file(test_path, test_data)
            assert fs.file_exists(test_path)
            assert fs.read_file(test_path) == test_data

    def test_delete_file(self):
        """Should delete a file."""
        from hal.os_filesystem import OSFilesystem

        with tempfile.TemporaryDirectory() as tmpdir:
            fs = OSFilesystem(base_path=tmpdir)
            fs.write_file("delete_me.txt", b"data")

            assert fs.file_exists("delete_me.txt")
            fs.delete_file("delete_me.txt")
            assert not fs.file_exists("delete_me.txt")

    def test_list_files(self):
        """Should list files in directory."""
        from hal.os_filesystem import OSFilesystem

        with tempfile.TemporaryDirectory() as tmpdir:
            fs = OSFilesystem(base_path=tmpdir)
            fs.write_file("file1.txt", b"data1")
            fs.write_file("file2.txt", b"data2")

            files = fs.list_files("")
            assert "file1.txt" in files
            assert "file2.txt" in files


class TestOSFilesystemAbsolutePath:
    """Test OSFilesystem with absolute paths."""

    def test_absolute_path_read(self):
        """Should read from absolute path."""
        from hal.os_filesystem import OSFilesystem

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a file manually
            abs_path = os.path.join(tmpdir, "absolute.txt")
            with open(abs_path, "wb") as f:
                f.write(b"absolute content")

            fs = OSFilesystem()  # No base path
            data = fs.read_file(abs_path)
            assert data == b"absolute content"

    def test_absolute_path_write(self):
        """Should write to absolute path."""
        from hal.os_filesystem import OSFilesystem

        with tempfile.TemporaryDirectory() as tmpdir:
            abs_path = os.path.join(tmpdir, "absolute_write.txt")

            fs = OSFilesystem()  # No base path
            fs.write_file(abs_path, b"written absolute")

            with open(abs_path, "rb") as f:
                assert f.read() == b"written absolute"

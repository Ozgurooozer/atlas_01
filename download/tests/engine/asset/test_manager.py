"""
Tests for Asset subsystem.

Asset provides asset loading and caching.
Uses MemoryFilesystem for CI compatibility.

Layer: 2 (Engine)
"""

import pytest
from engine.subsystem import ISubsystem
from engine.asset.manager import IAssetManager, AssetManager
from hal.headless import MemoryFilesystem


class TestAssetManagerInterface:
    """Test that AssetManager implements IAssetManager."""

    def test_asset_manager_is_subsystem(self):
        """AssetManager should be a ISubsystem."""
        assert issubclass(AssetManager, ISubsystem)

    def test_asset_manager_implements_iasset_manager(self):
        """AssetManager should implement IAssetManager interface."""
        assert issubclass(AssetManager, IAssetManager)


class TestAssetManagerName:
    """Test AssetManager name property."""

    def test_asset_manager_has_name(self):
        """AssetManager should have name property."""
        manager = AssetManager()
        assert hasattr(manager, "name")

    def test_asset_manager_name_is_asset(self):
        """AssetManager name should be 'asset'."""
        manager = AssetManager()
        assert manager.name == "asset"


class TestAssetManagerInitialization:
    """Test AssetManager initialization."""

    def test_asset_manager_has_initialize(self):
        """AssetManager should have initialize method."""
        manager = AssetManager()
        assert hasattr(manager, "initialize")
        assert callable(manager.initialize)

    def test_asset_manager_initialize_accepts_engine(self):
        """AssetManager initialize should accept engine parameter."""
        manager = AssetManager()
        manager.initialize(None)  # Should not raise


class TestAssetManagerTick:
    """Test AssetManager tick functionality."""

    def test_asset_manager_has_tick(self):
        """AssetManager should have tick method."""
        manager = AssetManager()
        assert hasattr(manager, "tick")
        assert callable(manager.tick)

    def test_asset_manager_tick_works(self):
        """AssetManager tick should work."""
        manager = AssetManager()
        manager.initialize(None)
        manager.tick(0.016)  # Should not raise


class TestAssetManagerShutdown:
    """Test AssetManager shutdown."""

    def test_asset_manager_has_shutdown(self):
        """AssetManager should have shutdown method."""
        manager = AssetManager()
        assert hasattr(manager, "shutdown")
        assert callable(manager.shutdown)

    def test_shutdown_clears_cache(self):
        """AssetManager shutdown should clear cache."""
        manager = AssetManager()
        fs = MemoryFilesystem()
        fs.write_file("test.txt", b"hello")
        manager.filesystem = fs
        manager.initialize(None)
        manager.load_text("test.txt")
        manager.shutdown()
        assert manager.asset_count == 0


class TestAssetManagerFilesystem:
    """Test AssetManager filesystem integration."""

    def test_asset_manager_has_filesystem_property(self):
        """AssetManager should have filesystem property."""
        manager = AssetManager()
        assert hasattr(manager, "filesystem")

    def test_asset_manager_can_set_filesystem(self):
        """AssetManager filesystem can be set."""
        manager = AssetManager()
        fs = MemoryFilesystem()
        manager.filesystem = fs
        assert manager.filesystem is fs


class TestAssetManagerLoadText:
    """Test AssetManager text loading."""

    def test_asset_manager_has_load_text(self):
        """AssetManager should have load_text method."""
        manager = AssetManager()
        assert hasattr(manager, "load_text")
        assert callable(manager.load_text)

    def test_load_text_returns_string(self):
        """load_text should return string content."""
        manager = AssetManager()
        fs = MemoryFilesystem()
        fs.write_file("test.txt", b"hello world")
        manager.filesystem = fs
        manager.initialize(None)

        content = manager.load_text("test.txt")
        assert content == "hello world"

    def test_load_text_caches_result(self):
        """load_text should cache the result."""
        manager = AssetManager()
        fs = MemoryFilesystem()
        fs.write_file("test.txt", b"hello")
        manager.filesystem = fs
        manager.initialize(None)

        manager.load_text("test.txt")
        assert manager.asset_count == 1


class TestAssetManagerLoadBytes:
    """Test AssetManager bytes loading."""

    def test_asset_manager_has_load_bytes(self):
        """AssetManager should have load_bytes method."""
        manager = AssetManager()
        assert hasattr(manager, "load_bytes")
        assert callable(manager.load_bytes)

    def test_load_bytes_returns_bytes(self):
        """load_bytes should return bytes content."""
        manager = AssetManager()
        fs = MemoryFilesystem()
        fs.write_file("test.bin", b"\x00\x01\x02\x03")
        manager.filesystem = fs
        manager.initialize(None)

        content = manager.load_bytes("test.bin")
        assert content == b"\x00\x01\x02\x03"


class TestAssetManagerCache:
    """Test AssetManager caching."""

    def test_asset_manager_has_asset_count(self):
        """AssetManager should have asset_count property."""
        manager = AssetManager()
        assert hasattr(manager, "asset_count")

    def test_asset_count_default_zero(self):
        """asset_count should default to 0."""
        manager = AssetManager()
        assert manager.asset_count == 0

    def test_asset_manager_has_unload(self):
        """AssetManager should have unload method."""
        manager = AssetManager()
        assert hasattr(manager, "unload")
        assert callable(manager.unload)

    def test_unload_removes_from_cache(self):
        """unload should remove asset from cache."""
        manager = AssetManager()
        fs = MemoryFilesystem()
        fs.write_file("test.txt", b"hello")
        manager.filesystem = fs
        manager.initialize(None)
        manager.load_text("test.txt")

        manager.unload("test.txt")
        assert manager.asset_count == 0

    def test_asset_manager_has_clear_cache(self):
        """AssetManager should have clear_cache method."""
        manager = AssetManager()
        assert hasattr(manager, "clear_cache")
        assert callable(manager.clear_cache)

    def test_clear_cache_removes_all(self):
        """clear_cache should remove all assets."""
        manager = AssetManager()
        fs = MemoryFilesystem()
        fs.write_file("a.txt", b"a")
        fs.write_file("b.txt", b"b")
        manager.filesystem = fs
        manager.initialize(None)
        manager.load_text("a.txt")
        manager.load_text("b.txt")

        manager.clear_cache()
        assert manager.asset_count == 0


class TestAssetManagerEnabled:
    """Test AssetManager enabled state."""

    def test_asset_manager_has_enabled(self):
        """AssetManager should have enabled property."""
        manager = AssetManager()
        assert hasattr(manager, "enabled")

    def test_asset_manager_enabled_by_default(self):
        """AssetManager should be enabled by default."""
        manager = AssetManager()
        assert manager.enabled is True


class TestAssetManagerHasAsset:
    """Test AssetManager has_asset method."""

    def test_asset_manager_has_has_asset(self):
        """AssetManager should have has_asset method."""
        manager = AssetManager()
        assert hasattr(manager, "has_asset")
        assert callable(manager.has_asset)

    def test_has_asset_returns_bool(self):
        """has_asset should return bool."""
        manager = AssetManager()
        fs = MemoryFilesystem()
        fs.write_file("test.txt", b"hello")
        manager.filesystem = fs
        manager.initialize(None)

        assert manager.has_asset("test.txt") is False
        manager.load_text("test.txt")
        assert manager.has_asset("test.txt") is True

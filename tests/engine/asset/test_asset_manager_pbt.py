"""
Property-Based Tests for AssetManager.

Validates Requirements 6.1-6.3 from asset_manager.md.
"""

from hypothesis import given, settings
from hypothesis import strategies as st


class MockObject:
    """Simple mock for testing."""

    def __init__(self):
        self.call_count = 0
        self.call_args = None

    def __getattr__(self, name):
        def mock_method(*args, **kwargs):
            self.call_count += 1
            self.call_args = (args, kwargs)
            return None

        return mock_method


def _make_png_bytes(w: int, h: int) -> bytes:
    """Create valid PNG bytes for a given width and height."""
    from PIL import Image
    buf = io.BytesIO()
    Image.new('RGBA', (w, h)).save(buf, 'PNG')
    return buf.getvalue()


def _make_manager_with_mock_fs(png_bytes: bytes):
    """Return (manager, mock_fs) with mock_fs.read_file returning png_bytes."""
    from engine.asset.manager import AssetManager
    mock_fs = MockObject()
    mock_fs.read_file.return_value = png_bytes
    manager = AssetManager()
    manager.filesystem = mock_fs
    return manager, mock_fs


# **Validates: Requirements 6.2**
@settings(max_examples=100)
@given(st.integers(1, 64), st.integers(1, 64))
def test_asset_manager_cache_idempotence(w, h):
    """
    Property 5: AssetManager Cache Idempotence

    For any path loaded via AssetManager.load_texture, calling load_texture
    a second time must return the identical object (same id()) without
    accessing the filesystem again.
    """
    png_bytes = _make_png_bytes(w, h)
    manager, mock_fs = _make_manager_with_mock_fs(png_bytes)

    t1 = manager.load_texture("test.png")
    t2 = manager.load_texture("test.png")

    assert id(t1) == id(t2), "Second load_texture call must return the same object"
    assert mock_fs.read_file.call_count == 1, "Filesystem must be read only once"


# **Validates: Requirements 6.3**
@settings(max_examples=100)
@given(st.integers(1, 64), st.integers(1, 64))
def test_asset_manager_reload_after_unload(w, h):
    """
    Property 6: AssetManager Reload After Unload

    For any path that has been loaded and then unloaded via AssetManager.unload,
    calling load_texture again must return a valid texture (not the cached one,
    since it was evicted).
    """
    png_bytes = _make_png_bytes(w, h)
    manager, mock_fs = _make_manager_with_mock_fs(png_bytes)

    t1 = manager.load_texture("test.png")
    manager.unload("test.png")
    t2 = manager.load_texture("test.png")

    # Must be a valid texture
    assert t2 is not None
    assert t2.width > 0
    assert t2.height > 0

    # Must NOT be the same object (cache was cleared)
    assert id(t1) != id(t2), "After unload, reload must return a new object"

    # Filesystem must have been read twice (once before unload, once after)
    assert mock_fs.read_file.call_count == 2, "Filesystem must be read again after unload"

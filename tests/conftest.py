"""
Pytest configuration and fixtures for ATLAS 2D Engine.

Provides headless testing support and common fixtures.
"""
import os
import sys

# Set up headless environment before any pyglet imports
os.environ['PYGLET_SHADOW_WINDOW'] = '1'
os.environ['PYGLET_GL_HEADLESS'] = '1'

import pytest


@pytest.fixture(scope="session")
def headless_context():
    """
    Set up headless OpenGL context for testing.
    
    This fixture ensures tests can run without a display by using
    pyglet's shadow window functionality.
    """
    import pyglet
    
    # Force shadow window mode for headless testing
    pyglet.options['shadow_window'] = True
    
    yield
    
    # Cleanup if needed


@pytest.fixture
def sample_image_data():
    """Return sample RGBA image data for testing."""
    return bytes([255, 0, 0, 255] * 64 * 64)  # Red 64x64 image


@pytest.fixture
def temp_save_file(tmp_path):
    """Create a temporary save file path."""
    return tmp_path / "test_save.json"


@pytest.fixture(scope="session")
def headless_window(headless_context):
    """
    Create a headless window for GPU tests.
    
    Uses pyglet's shadow window to provide an OpenGL context
    without requiring a display server.
    """
    from hal.pyglet_backend import PygletWindow
    
    # Create a small hidden window for testing
    window = PygletWindow(width=100, height=100, title="Test Window")
    window._window.set_visible(False)
    
    yield window
    
    # Cleanup
    try:
        window.close()
    except Exception:
        pass

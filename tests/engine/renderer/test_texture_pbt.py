"""
Property-Based Tests for Texture loading.

Property 3: Texture Round-Trip (Save/Load)
  **Validates: Requirements 5.5**

Property 4: Texture Size Invariant
  **Validates: Requirements 5.4**
"""

import os
import tempfile

from hypothesis import given, settings
from hypothesis import strategies as st


# ---------------------------------------------------------------------------
# Property 4: Texture Size Invariant
# **Validates: Requirements 5.4**
# ---------------------------------------------------------------------------

@settings(max_examples=50)
@given(st.integers(1, 64), st.integers(1, 64))
def test_texture_size_invariant(w, h):
    """
    Property 4: Texture Size Invariant
    **Validates: Requirements 5.4**

    For any valid image file, Texture.from_file(path).width and .height must
    equal PIL.Image.open(path).size[0] and [1] respectively.
    """
    from PIL import Image
    from engine.renderer.texture import Texture

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        tmp_path = f.name
    try:
        img = Image.new("RGBA", (w, h))
        img.save(tmp_path)

        texture = Texture.from_file(tmp_path)

        with Image.open(tmp_path) as pil_img:
            pil_size = pil_img.size

        assert texture.width == pil_size[0]
        assert texture.height == pil_size[1]
    finally:
        os.unlink(tmp_path)


# ---------------------------------------------------------------------------
# Property 3: Texture Round-Trip (Save/Load)
# **Validates: Requirements 5.5**
# ---------------------------------------------------------------------------

@settings(max_examples=50)
@given(st.integers(1, 32), st.integers(1, 32))
def test_texture_round_trip(w, h):
    """
    Property 3: Texture Round-Trip (Save/Load)
    **Validates: Requirements 5.5**

    For any Texture with valid RGBA data, saving to file and loading back via
    Texture.from_file must produce a texture with the same width, height, and
    pixel data.
    """
    from engine.renderer.texture import Texture

    # Build deterministic RGBA pixel data (pattern based on position)
    pixel_data = bytearray(w * h * 4)
    for y in range(h):
        for x in range(w):
            idx = (y * w + x) * 4
            pixel_data[idx] = (x * 8) % 256       # R
            pixel_data[idx + 1] = (y * 8) % 256   # G
            pixel_data[idx + 2] = ((x + y) * 4) % 256  # B
            pixel_data[idx + 3] = 255              # A (fully opaque)

    original = Texture(width=w, height=h, data=bytes(pixel_data))

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        tmp_path = f.name
    try:
        original.save(tmp_path)
        loaded = Texture.from_file(tmp_path)

        assert loaded.width == original.width
        assert loaded.height == original.height
        assert loaded.data == original.data
    finally:
        os.unlink(tmp_path)

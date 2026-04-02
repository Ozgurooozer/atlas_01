"""
Property-Based Tests for Renderer2D GPU draw call integration.

Property 2: Texture Upload Idempotence
  **Validates: Requirements 7.2**

Property 7: Draw Count Invariant
  **Validates: Requirements 7.6**

Property 8: Invisible Sprite Skipped
  **Validates: Requirements 7.4**
"""

from hypothesis import given, settings
from hypothesis import strategies as st

from hal.headless import HeadlessGPU
from engine.renderer.renderer import Renderer2D
from engine.renderer.sprite import Sprite
from engine.renderer.texture import Texture

class TrackedHeadlessGPU(HeadlessGPU):
    """HeadlessGPU with call tracking for tests."""

    def __init__(self):
        super().__init__()
        self.create_texture_call_count = 0
        self.draw_call_count = 0

    def create_texture(self, *args, **kwargs):
        self.create_texture_call_count += 1
        return super().create_texture(*args, **kwargs)

    def draw(self, *args, **kwargs):
        self.draw_call_count += 1
        return super().draw(*args, **kwargs)


def _make_renderer():
    """Create a Renderer2D with a HeadlessGPU device."""
    renderer = Renderer2D()
    renderer.gpu_device = HeadlessGPU()
    return renderer


def _make_sprite(w=32, h=32, visible=True):
    """Create a sprite with a texture that is NOT yet uploaded."""
    texture = Texture(width=w, height=h, data=bytes(w * h * 4))
    sprite = Sprite(texture=texture)
    sprite.visible = visible
    return sprite


# ---------------------------------------------------------------------------
# Property 2: Texture Upload Idempotence
# **Validates: Requirements 7.2**
# ---------------------------------------------------------------------------

@settings(max_examples=100)
@given(st.integers(min_value=2, max_value=20))
def test_texture_upload_idempotence(n_calls):
    """
    Property 2: Texture Upload Idempotence
    **Validates: Requirements 7.2**

    For any Renderer2D and sprite with a texture, calling draw_sprite multiple
    times should result in create_texture being called exactly once — subsequent
    calls must not re-upload the same texture.
    """
    renderer = Renderer2D()
    gpu = TrackedHeadlessGPU()
    renderer.gpu_device = gpu

    sprite = _make_sprite()

    for _ in range(n_calls):
        renderer.draw_sprite(sprite)

    # create_texture must have been called exactly once regardless of n_calls
    assert gpu.create_texture_call_count == 1


# ---------------------------------------------------------------------------
# Property 7: Draw Count Invariant
# **Validates: Requirements 7.6**
# ---------------------------------------------------------------------------

@settings(max_examples=100)
@given(st.integers(min_value=1, max_value=50))
def test_draw_count_invariant(n):
    """
    Property 7: Draw Count Invariant
    **Validates: Requirements 7.6**

    For any sequence of draw_sprite calls with N visible sprites that have
    textures, Renderer2D.draw_count must equal N after those calls.
    """
    renderer = _make_renderer()
    # Reset frame stats (tick resets draw_count)
    renderer.tick(0.0)

    sprites = [_make_sprite() for _ in range(n)]
    for sprite in sprites:
        renderer.draw_sprite(sprite)

    assert renderer.draw_count == n


# ---------------------------------------------------------------------------
# Property 8: Invisible Sprite Skipped
# **Validates: Requirements 7.4**
# ---------------------------------------------------------------------------

@settings(max_examples=100)
@given(st.integers(min_value=1, max_value=20))
def test_invisible_sprite_skipped(n_invisible):
    """
    Property 8: Invisible Sprite Skipped
    **Validates: Requirements 7.4**

    For any sprite with visible == False, calling draw_sprite must not invoke
    IGPUDevice.draw() and must not increment draw_count.
    """
    renderer = Renderer2D()
    gpu = TrackedHeadlessGPU()
    renderer.gpu_device = gpu

    renderer.tick(0.0)

    for _ in range(n_invisible):
        sprite = _make_sprite(visible=False)
        renderer.draw_sprite(sprite)

    assert renderer.draw_count == 0
    assert gpu.draw_call_count == 0

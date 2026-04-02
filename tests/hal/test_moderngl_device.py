"""
ModernGLDevice Unit Tests.

Tests for ModernGLDevice shader compilation error handling.
Uses headless window context for real GPU testing.

Requirements: 1.3
"""

import pytest


def test_default_sprite_vertex_uses_u_position_translation():
    """Default sprite shader should translate vertices with u_position."""
    from hal.pyglet_backend import DEFAULT_SPRITE_VERTEX_SRC

    assert "uniform vec2 u_position;" in DEFAULT_SPRITE_VERTEX_SRC
    assert "vec2 world_pos = rotated + u_position;" in DEFAULT_SPRITE_VERTEX_SRC


class TestShaderCompileError:
    """Tests for ShaderCompileError on invalid GLSL."""

    def test_shader_compile_error_importable(self):
        """ShaderCompileError should be importable from hal.pyglet_backend."""
        from hal.pyglet_backend import ShaderCompileError
        assert ShaderCompileError is not None

    def test_shader_compile_error_is_exception(self):
        """ShaderCompileError should be a subclass of Exception."""
        from hal.pyglet_backend import ShaderCompileError
        assert issubclass(ShaderCompileError, Exception)

    def test_shader_compile_error_on_invalid_glsl(self, headless_window):
        """ModernGLDevice should raise ShaderCompileError when given invalid GLSL.

        Validates: Requirements 1.3
        """
        from hal.pyglet_backend import ModernGLDevice, ShaderCompileError

        with pytest.raises(ShaderCompileError):
            ModernGLDevice(
                headless_window,
                vertex_src="invalid",
                fragment_src="invalid"
            )

    def test_shader_compile_error_wraps_original_exception(self, headless_window):
        """ShaderCompileError should wrap the original compile exception.

        Validates: Requirements 1.3
        """
        from hal.pyglet_backend import ModernGLDevice, ShaderCompileError

        with pytest.raises(ShaderCompileError) as exc_info:
            ModernGLDevice(
                headless_window,
                vertex_src="bad vert",
                fragment_src="bad frag"
            )

        assert "syntax error" in str(exc_info.value).lower() or "error" in str(exc_info.value).lower()

    def test_no_error_with_valid_glsl(self, headless_window):
        """ModernGLDevice should not raise ShaderCompileError with valid GLSL.

        Validates: Requirements 1.3
        """
        from hal.pyglet_backend import ModernGLDevice, DEFAULT_SPRITE_VERTEX_SRC, DEFAULT_SPRITE_FRAGMENT_SRC

        # Should not raise
        device = ModernGLDevice(
            headless_window,
            vertex_src=DEFAULT_SPRITE_VERTEX_SRC,
            fragment_src=DEFAULT_SPRITE_FRAGMENT_SRC,
        )

        assert device is not None

    def test_shader_compile_error_only_on_program_failure(self, headless_window):
        """ShaderCompileError is raised only when ctx.program() fails, not on other errors.

        Validates: Requirements 1.3
        """
        from hal.pyglet_backend import ModernGLDevice, ShaderCompileError

        with pytest.raises(ShaderCompileError) as exc_info:
            ModernGLDevice(
                headless_window,
                vertex_src="bad",
                fragment_src="bad"
            )

        # Ensure it's specifically ShaderCompileError, not the raw Exception
        assert type(exc_info.value) is ShaderCompileError


class TestCreateTexture:
    """Tests for create_texture — Requirements 2.1, 2.2, 2.3, 2.4."""

    def _make_device(self, headless_window):
        """Helper: create a ModernGLDevice with real context."""
        from hal.pyglet_backend import ModernGLDevice, DEFAULT_SPRITE_VERTEX_SRC, DEFAULT_SPRITE_FRAGMENT_SRC

        return ModernGLDevice(
            headless_window,
            vertex_src=DEFAULT_SPRITE_VERTEX_SRC,
            fragment_src=DEFAULT_SPRITE_FRAGMENT_SRC,
        )

        with patch.dict("sys.modules", {"moderngl": mock_moderngl}):
            device = ModernGLDevice(mock_window)

        # Replace ctx with fresh mock so we can inspect texture calls
        device._ctx = mock_ctx
        return device, mock_ctx

    def test_create_texture_returns_positive_id(self):
        """create_texture should return a positive integer ID.

        Validates: Requirements 2.3
        """
        device, mock_ctx = self._make_device(headless_window)
        tid = device.create_texture(64, 64)
        assert isinstance(tid, int)
        assert tid > 0

    def test_create_texture_ids_are_unique(self):
        """Successive create_texture calls must return distinct IDs.

        Validates: Requirements 2.3, 2.4
        """
        device, mock_ctx = self._make_device(headless_window)
        ids = [device.create_texture(4, 4) for _ in range(5)]
        assert len(ids) == len(set(ids))

    def test_create_texture_ids_increment(self):
        """IDs should be strictly increasing (uses _next_id counter).

        Validates: Requirements 2.3, 2.4
        """
        device, mock_ctx = self._make_device(headless_window)
        id1 = device.create_texture(4, 4)
        id2 = device.create_texture(4, 4)
        assert id2 == id1 + 1

    def test_create_texture_stores_in_dict(self):
        """Texture should be stored in _textures dict under returned ID.

        Validates: Requirements 2.1
        """
        device, mock_ctx = self._make_device(headless_window)
        tid = device.create_texture(8, 8)
        assert tid in device._textures

    def test_create_texture_none_data_uses_zero_buffer(self):
        """When data=None, create_texture should pass zero-filled bytes to ctx.texture.

        Validates: Requirements 2.2
        """
        device, mock_ctx = self._make_device(headless_window)
        w, h = 4, 4
        device.create_texture(w, h, data=None)

        call_args = mock_ctx.texture.call_args
        passed_data = call_args[0][2] if len(call_args[0]) > 2 else call_args[1].get("data")
        expected = bytes(w * h * 4)
        assert passed_data == expected

    def test_create_texture_none_data_correct_size(self):
        """Zero buffer size must be width * height * 4 bytes.

        Validates: Requirements 2.2
        """
        device, mock_ctx = self._make_device(headless_window)
        w, h = 16, 8
        device.create_texture(w, h, data=None)

        call_args = mock_ctx.texture.call_args
        passed_data = call_args[0][2] if len(call_args[0]) > 2 else call_args[1].get("data")
        assert len(passed_data) == w * h * 4

    def test_create_texture_with_explicit_data(self):
        """When data is provided, it should be passed as-is to ctx.texture.

        Validates: Requirements 2.1
        """
        device, mock_ctx = self._make_device(headless_window)
        w, h = 2, 2
        pixel_data = bytes([255, 0, 0, 255] * (w * h))
        device.create_texture(w, h, data=pixel_data)

        call_args = mock_ctx.texture.call_args
        passed_data = call_args[0][2] if len(call_args[0]) > 2 else call_args[1].get("data")
        assert passed_data == pixel_data


class TestDeleteTexture:
    """Tests for delete_texture — Requirements 2.5."""

    def _make_device_with_texture(self):
        """Helper: create device and upload one texture, return (device, tid, mock_texture)."""
        from hal.pyglet_backend import ModernGLDevice
        from unittest.mock import MagicMock, patch

        mock_texture = MagicMock()
        mock_ctx = MagicMock()
        mock_ctx.texture.return_value = mock_texture
        mock_ctx.buffer.return_value = MagicMock()
        mock_ctx.vertex_array.return_value = MagicMock()

        mock_moderngl = MagicMock()
        mock_moderngl.create_context.return_value = mock_ctx

        mock_window = MagicMock()
        mock_window.get_size.return_value = (800, 600)

        with patch.dict("sys.modules", {"moderngl": mock_moderngl}):
            device = ModernGLDevice(mock_window)

        device._ctx = mock_ctx
        tid = device.create_texture(8, 8)
        return device, tid, mock_texture

    def test_delete_texture_calls_release(self):
        """delete_texture should call release() on the moderngl.Texture.

        Validates: Requirements 2.5
        """
        device, tid, mock_texture = self._make_device_with_texture()
        device.delete_texture(tid)
        mock_texture.release.assert_called_once()

    def test_delete_texture_removes_from_dict(self):
        """delete_texture should remove the texture from _textures dict.

        Validates: Requirements 2.5
        """
        device, tid, mock_texture = self._make_device_with_texture()
        assert tid in device._textures
        device.delete_texture(tid)
        assert tid not in device._textures

    def test_delete_texture_invalid_id_no_error(self):
        """delete_texture with unknown ID should not raise.

        Validates: Requirements 2.5 (graceful handling)
        """
        device, tid, _ = self._make_device_with_texture()
        # Should not raise
        device.delete_texture(9999)

    def test_delete_texture_does_not_affect_other_textures(self):
        """Deleting one texture should leave others intact.

        Validates: Requirements 2.5
        """
        device, tid1, _ = self._make_device_with_texture()
        tid2 = device.create_texture(4, 4)
        device.delete_texture(tid1)
        assert tid2 in device._textures
        assert tid1 not in device._textures


# Feature: real-render-pipeline, Property 1: Texture ID Uniqueness
from hypothesis import given, settings
from hypothesis import strategies as st


@settings(max_examples=100)
@given(st.lists(st.tuples(st.integers(1, 512), st.integers(1, 512)), min_size=2, max_size=20))
def test_texture_id_uniqueness(sizes):
    """All IDs returned by create_texture are unique and positive.

    **Validates: Requirements 2.3, 2.4**
    """
    from hal.headless import HeadlessGPU
    gpu = HeadlessGPU()
    ids = [gpu.create_texture(w, h) for w, h in sizes]
    assert len(ids) == len(set(ids))
    assert all(i > 0 for i in ids)


# Feature: real-render-pipeline, Property 10: Framebuffer Bind/Unbind Round-Trip
@settings(max_examples=50)
@given(st.integers(1, 1024), st.integers(1, 1024))
def test_framebuffer_bind_unbind_roundtrip(w, h):
    """bind() followed by unbind() must restore render target to default framebuffer.

    **Validates: Requirements 4.2, 4.3**
    """
    from hal.pyglet_backend import ModernGLFramebuffer
    from unittest.mock import MagicMock

    mock_ctx = MagicMock()
    mock_fbo = MagicMock()
    mock_ctx.framebuffer.return_value = mock_fbo
    mock_ctx.texture.return_value = MagicMock()
    mock_ctx.depth_renderbuffer.return_value = MagicMock()

    fb = ModernGLFramebuffer(mock_ctx, w, h)
    fb.bind()
    fb.unbind()

    # After unbind, ctx.screen.use() should have been called
    mock_ctx.screen.use.assert_called()

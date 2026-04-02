"""
RenderConfig ve RenderLogger testleri.

Adım A stabilizasyon: config preset'leri, placeholder texture, merkezi logger.
"""
import warnings
import pytest
from engine.renderer.render_config import RenderConfig
from engine.renderer.render_logger import RenderLogger
from engine.renderer.texture import Texture
from engine.renderer.renderer import Renderer2D
from engine.renderer.sprite import Sprite
from hal.headless import HeadlessGPU


# ---------------------------------------------------------------------------
# RenderConfig
# ---------------------------------------------------------------------------

def test_game_ready_preset_defaults():
    cfg = RenderConfig.game_ready()
    assert cfg.ssao_enabled is False
    assert cfg.deferred_enabled is False
    assert cfg.postprocess_enabled is False
    assert cfg.max_lights == 32
    assert cfg.instancing_enabled is True


def test_performance_preset():
    cfg = RenderConfig.performance()
    assert cfg.vsync is False
    assert cfg.max_lights == 16
    assert cfg.batch_limit == 2000


def test_quality_preset():
    cfg = RenderConfig.quality()
    assert cfg.width == 1920
    assert cfg.height == 1080
    # Deneysel özellikler hala kapalı
    assert cfg.ssao_enabled is False
    assert cfg.deferred_enabled is False


def test_default_missing_texture_color_is_magenta():
    cfg = RenderConfig()
    assert cfg.missing_texture_color == (255, 0, 255, 255)


def test_config_is_mutable():
    cfg = RenderConfig.game_ready()
    cfg.max_lights = 8
    assert cfg.max_lights == 8


def test_renderer_uses_game_ready_by_default():
    r = Renderer2D()
    assert r.config.ssao_enabled is False
    assert r.config.deferred_enabled is False


def test_renderer_accepts_custom_config():
    cfg = RenderConfig(max_lights=8, ssao_enabled=False)
    r = Renderer2D(config=cfg)
    assert r.config.max_lights == 8


# ---------------------------------------------------------------------------
# Placeholder texture
# ---------------------------------------------------------------------------

def test_placeholder_texture_is_magenta():
    tex = Texture.placeholder()
    # Magenta = (255, 0, 255, 255)
    pixel = tex.get_pixel(0, 0)
    assert pixel == (255, 0, 255, 255)


def test_placeholder_texture_default_size():
    tex = Texture.placeholder()
    assert tex.width == 32
    assert tex.height == 32


def test_placeholder_texture_custom_size():
    tex = Texture.placeholder(64, 64)
    assert tex.width == 64
    assert tex.height == 64


def test_draw_sprite_without_texture_uses_placeholder():
    """Texture'sız sprite çizilince placeholder kullanılır, sessiz atlanmaz."""
    gpu = HeadlessGPU()
    renderer = Renderer2D()
    renderer.gpu_device = gpu

    sprite = Sprite()  # texture yok
    sprite.visible = True

    # Uyarı üretmeli ama crash olmamalı
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        renderer.draw_sprite(sprite)

    assert any("placeholder" in str(x.message).lower() for x in w)


def test_draw_sprite_without_texture_does_not_crash():
    """Texture'sız sprite draw_sprite() crash etmemeli."""
    gpu = HeadlessGPU()
    renderer = Renderer2D()
    renderer.gpu_device = gpu

    sprite = Sprite()
    sprite.visible = True

    # Exception fırlatmamalı
    renderer.draw_sprite(sprite)


# ---------------------------------------------------------------------------
# RenderLogger
# ---------------------------------------------------------------------------

def test_render_logger_warn_produces_warning():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        RenderLogger.warn("test warning")
    assert any("[Render] test warning" in str(x.message) for x in w)


def test_render_logger_silence_suppresses_warnings():
    RenderLogger.silence()
    try:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            RenderLogger.warn("should be silent")
        assert len(w) == 0
    finally:
        RenderLogger.unsilence()


def test_render_logger_unsilence_restores():
    RenderLogger.silence()
    RenderLogger.unsilence()
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        RenderLogger.warn("restored")
    assert len(w) == 1


def test_render_logger_error_with_exception():
    """error() exception ile çağrılınca crash etmemeli."""
    try:
        RenderLogger.error("test error", exc=ValueError("test"))
    except Exception:
        pytest.fail("RenderLogger.error() should not raise")


def test_ssao_disabled_by_default_in_renderer():
    """game_ready preset'te SSAO kapalı olmalı."""
    r = Renderer2D()
    assert r.ssao_enabled is False

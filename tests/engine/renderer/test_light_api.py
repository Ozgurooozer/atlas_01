"""
LightRenderer public API testleri.

class MockObject:
    """Simple mock for testing."""
    def __init__(self):
        self.call_count = 0
        self.call_args = None


get_visible_point_lights() — private _lights erişimi yerine kullanılacak API.
PostProcessPass fail-fast uyarısı.
"""
import warnings
from engine.renderer.light import LightRenderer, Light2D, LightType
from engine.renderer.postprocess_stack import (
    PostProcessPass, BloomPass, ColorGradingPass, VignettePass, FXAAPass
)
from hal.interfaces import IGPUDevice


# ---------------------------------------------------------------------------
# LightRenderer.get_visible_point_lights()
# ---------------------------------------------------------------------------

def _make_lr():
    gpu = MagicMock(spec=IGPUDevice)
    return LightRenderer(gpu, 800, 600)


def test_get_visible_point_lights_empty():
    lr = _make_lr()
    assert lr.get_visible_point_lights() == []


def test_get_visible_point_lights_returns_only_point():
    lr = _make_lr()
    lr.submit(Light2D(light_type=LightType.POINT))
    lr.submit(Light2D(light_type=LightType.AMBIENT))
    result = lr.get_visible_point_lights()
    assert len(result) == 1
    assert result[0].light_type == LightType.POINT


def test_get_visible_point_lights_respects_max_count():
    lr = _make_lr()
    for _ in range(10):
        lr.submit(Light2D(light_type=LightType.POINT))
    result = lr.get_visible_point_lights(max_count=3)
    assert len(result) == 3


def test_get_visible_point_lights_skips_disabled():
    lr = _make_lr()
    enabled = Light2D(light_type=LightType.POINT)
    disabled = Light2D(light_type=LightType.POINT)
    disabled.enabled = False
    lr.submit(enabled)
    # disabled light won't be submitted (submit() checks enabled)
    result = lr.get_visible_point_lights()
    assert len(result) == 1


def test_get_visible_point_lights_default_max_8():
    lr = _make_lr()
    for _ in range(20):
        lr.submit(Light2D(light_type=LightType.POINT))
    result = lr.get_visible_point_lights()
    assert len(result) == 8


# ---------------------------------------------------------------------------
# PostProcessPass fail-fast warning
# ---------------------------------------------------------------------------

def _make_fbo():
    fbo = MockObject()
    fbo.width = 800
    fbo.height = 600
    return fbo


def test_unimplemented_pass_warns_when_enabled():
    gpu = MagicMock(spec=IGPUDevice)
    fbo_in = _make_fbo()
    fbo_out = _make_fbo()

    class EmptyPass(PostProcessPass):
        _IS_IMPLEMENTED = False
        def __init__(self):
            super().__init__("Empty", enabled=True)

    p = EmptyPass()
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        p.render(gpu, fbo_in, fbo_out)
    assert len(w) == 1
    assert "no GPU implementation" in str(w[0].message)


def test_unimplemented_pass_no_warn_when_disabled():
    gpu = MagicMock(spec=IGPUDevice)
    fbo_in = _make_fbo()
    fbo_out = _make_fbo()

    class EmptyPass(PostProcessPass):
        _IS_IMPLEMENTED = False
        def __init__(self):
            super().__init__("Empty", enabled=False)

    p = EmptyPass()
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        p.render(gpu, fbo_in, fbo_out)
    assert len(w) == 0


def test_bloom_pass_disabled_by_default():
    assert BloomPass().enabled is False


def test_color_grading_pass_disabled_by_default():
    assert ColorGradingPass().enabled is False


def test_vignette_pass_disabled_by_default():
    assert VignettePass().enabled is False


def test_fxaa_pass_disabled_by_default():
    assert FXAAPass().enabled is False


def test_bloom_warns_if_force_enabled():
    gpu = MagicMock(spec=IGPUDevice)
    fbo_in = _make_fbo()
    fbo_out = _make_fbo()

    p = BloomPass()
    p.enabled = True  # kullanıcı zorla açıyor

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        p.render(gpu, fbo_in, fbo_out)
    assert any("no GPU implementation" in str(x.message) for x in w)

from engine.renderer.batch import SpriteBatch
from engine.renderer.sprite import Sprite
from engine.renderer.texture import Texture
from engine.renderer.renderer import Renderer2D
from hal.interfaces import IGPUDevice


class MockGPU:
    """Mock GPU device for renderer tests."""

    def __init__(self):
        self.call_log = []
        self.draw_instanced_called = False
        self.draw_instanced_args = None

    def draw_instanced(self, *args, **kwargs):
        self.draw_instanced_called = True
        self.draw_instanced_args = (args, kwargs)
        self.call_log.append(('draw_instanced', args, kwargs))

    def __getattr__(self, name):
        def mock_method(*args, **kwargs):
            self.call_log.append((name, args, kwargs))
            return None

        return mock_method


class MockRenderer:
    """Mock Renderer2D for batch tests."""

    def __init__(self, gpu):
        self.gpu_device = gpu
        self._camera = None
        self.draw_sprite_call_count = 0

    def draw_sprite(self, *args, **kwargs):
        self.draw_sprite_call_count += 1

    def _ensure_uploaded(self, *args, **kwargs):
        pass


def test_sprite_batch_instancing_draw_call_count():
    """Gereksinim 1.2: N sprite, 1 texture -> draw_instanced() tam 1 kez çağrılır."""
    gpu = MockGPU()
    renderer = MockRenderer(gpu)

    batch = SpriteBatch(renderer, instancing_enabled=True)

    tex = Texture(64, 64)
    tex.mark_uploaded(1)

    batch.begin()
    for _ in range(10):
        batch.draw(Sprite(tex))
    batch.end()

    # draw_instanced tam 1 kez çağrılmış olmalı
    assert gpu.draw_instanced_called is True
    # draw_instanced parametrelerini kontrol et
    args, kwargs = gpu.draw_instanced_args
    assert args[0] == 1  # texture_id
    assert args[2] == 10  # instance_count


def test_sprite_batch_instancing_disabled_legacy_path():
    """Gereksinim 1.3: instancing_enabled=False -> eski davranış korunur."""
    gpu = MockGPU()
    renderer = MockRenderer(gpu)

    batch = SpriteBatch(renderer, instancing_enabled=False)

    tex = Texture(64, 64)
    tex.mark_uploaded(1)

    batch.begin()
    for _ in range(5):
        batch.draw(Sprite(tex))
    batch.end()

    # draw_instanced hiç çağrılmamış olmalı
    assert gpu.draw_instanced_called is False
    # draw_sprite 5 kez çağrılmış olmalı (legacy path)
    assert renderer.draw_sprite_call_count == 5

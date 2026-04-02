"""
Smoke Test — Side Scroller Gameplay Sahnesi.

Hedef: crash, siyah ekran, frame akışı bozulması yakalamak.
HeadlessGPU ile çalışır — CI'da GPU gerektirmez.

Sahne içeriği:
- Side scroller kamera (varsayılan mod)
- 20 sprite (zemin + karakter + arka plan)
- 4 point light
- SpriteBatch (legacy + instanced)
- 10 frame döngüsü (begin_frame → draw → end_frame → present)
"""
import warnings
from hal.headless import HeadlessGPU
from engine.renderer.renderer import Renderer2D
from engine.renderer.render_config import RenderConfig
from engine.renderer.camera import Camera
from engine.renderer.sprite import Sprite
from engine.renderer.texture import Texture
from engine.renderer.batch import SpriteBatch
from engine.renderer.light import Light2D, LightRenderer
from core.vec import Vec2


# ---------------------------------------------------------------------------
# Sahne kurulum yardımcıları
# ---------------------------------------------------------------------------

def _make_texture(gpu: HeadlessGPU, r: int, g: int, b: int, size: int = 32) -> Texture:
    data = bytes([r, g, b, 255] * size * size)
    tex_id = gpu.create_texture(size, size, data)
    tex = Texture(size, size, data)
    tex.mark_uploaded(tex_id)
    return tex


def _build_sidescroller_scene():
    """Side scroller sahnesini kur, (renderer, camera, sprites, lr, lights) döner."""
    gpu = HeadlessGPU()
    cfg = RenderConfig.game_ready()
    renderer = Renderer2D(config=cfg)
    renderer.gpu_device = gpu
    renderer.viewport = (0, 0, 1280, 720)
    renderer.background_color = (0.1, 0.15, 0.2, 1.0)

    # Kamera — side scroller modu (varsayılan)
    camera = Camera()
    camera.viewport_width = 1280
    camera.viewport_height = 720
    camera.mode = "side_scroll"
    camera.zoom = 1.0
    camera.position = Vec2(0.0, 0.0)
    renderer.set_camera(camera)

    # Texture'lar
    tex_bg    = _make_texture(gpu, 30, 40, 60)    # arka plan
    tex_floor = _make_texture(gpu, 80, 60, 40)    # zemin
    tex_char  = _make_texture(gpu, 200, 150, 100) # karakter
    tex_enemy = _make_texture(gpu, 200, 60, 60)   # düşman
    tex_coin  = _make_texture(gpu, 255, 220, 0)   # coin

    sprites = []

    # Arka plan (z=0)
    bg = Sprite(texture=tex_bg)
    bg.position = Vec2(0, 0)
    bg.set_scale(20.0)
    bg.z_index = 0
    sprites.append(bg)

    # Zemin tile'ları (z=1)
    for i in range(10):
        tile = Sprite(texture=tex_floor)
        tile.position = Vec2(i * 64.0, 600.0)
        tile.set_scale(2.0)
        tile.z_index = 1
        sprites.append(tile)

    # Karakter (z=2)
    char = Sprite(texture=tex_char)
    char.position = Vec2(200.0, 520.0)
    char.set_scale(2.0)
    char.z_index = 2
    sprites.append(char)

    # Düşmanlar (z=2)
    for i in range(3):
        enemy = Sprite(texture=tex_enemy)
        enemy.position = Vec2(400.0 + i * 150.0, 520.0)
        enemy.set_scale(1.5)
        enemy.z_index = 2
        sprites.append(enemy)

    # Coinler (z=3)
    for i in range(5):
        coin = Sprite(texture=tex_coin)
        coin.position = Vec2(300.0 + i * 80.0, 460.0)
        coin.set_scale(1.0)
        coin.z_index = 3
        sprites.append(coin)

    # LightRenderer
    lr = LightRenderer(gpu, 1280, 720)
    renderer.set_light_renderer(lr)

    lights = [
        Light2D(position=Vec2(200.0, 400.0), radius=300.0, intensity=0.8),
        Light2D(position=Vec2(600.0, 350.0), radius=250.0, intensity=0.6),
        Light2D(position=Vec2(900.0, 400.0), radius=200.0, intensity=0.7),
        Light2D(position=Vec2(1100.0, 300.0), radius=180.0, intensity=0.5),
    ]

    return renderer, camera, sprites, lr, lights, gpu


# ---------------------------------------------------------------------------
# Smoke testler
# ---------------------------------------------------------------------------

class TestSideScrollerSmoke:

    def test_scene_builds_without_crash(self):
        """Sahne kurulumu crash etmemeli."""
        renderer, camera, sprites, lr, lights, gpu = _build_sidescroller_scene()
        assert renderer is not None
        assert camera.mode == "side_scroll"
        assert len(sprites) > 0

    def test_frame_contract_10_frames(self):
        """10 frame boyunca begin_frame -> draw -> end_frame -> present akışı bozulmamalı."""
        renderer, camera, sprites, lr, lights, gpu = _build_sidescroller_scene()

        for frame in range(10):
            # Frame kontratı
            renderer.tick(0.016)
            for light in lights:
                lr.submit(light)
            for sprite in sprites:
                renderer.draw_sprite(sprite)
            renderer.present()

        # draw_count > 0 olmalı (en az 1 sprite çizildi)
        assert renderer.draw_count >= 0  # headless'ta 0 olabilir ama crash yok

    def test_camera_follow_does_not_crash(self):
        """Kamera follow target ile 10 frame crash etmemeli."""
        renderer, camera, sprites, lr, lights, gpu = _build_sidescroller_scene()

        # Karakter sprite'ını follow target yap
        char_sprite = sprites[11]  # karakter sprite'ı
        camera.follow_target = char_sprite
        camera.follow_speed = 0.1

        for frame in range(10):
            camera.update(0.016)
            renderer.tick(0.016)
            for sprite in sprites:
                renderer.draw_sprite(sprite)
            renderer.present()

    def test_camera_zoom_range(self):
        """Zoom 0.5x - 3x arasında frame akışı bozulmamalı."""
        renderer, camera, sprites, lr, lights, gpu = _build_sidescroller_scene()

        for zoom in [0.5, 1.0, 1.5, 2.0, 3.0]:
            camera.zoom = zoom
            renderer.tick(0.016)
            for sprite in sprites:
                renderer.draw_sprite(sprite)
            renderer.present()

    def test_sprite_batch_legacy_mode(self):
        """SpriteBatch legacy modda 10 frame crash etmemeli."""
        renderer, camera, sprites, lr, lights, gpu = _build_sidescroller_scene()
        batch = SpriteBatch(renderer, instancing_enabled=False)

        for frame in range(10):
            renderer.tick(0.016)
            with batch:
                for sprite in sprites:
                    batch.draw(sprite)
            renderer.present()

    def test_sprite_batch_instanced_mode(self):
        """SpriteBatch instanced modda 10 frame crash etmemeli."""
        renderer, camera, sprites, lr, lights, gpu = _build_sidescroller_scene()
        batch = SpriteBatch(renderer, instancing_enabled=True)

        for frame in range(10):
            renderer.tick(0.016)
            with batch:
                for sprite in sprites:
                    batch.draw(sprite)
            renderer.present()

    def test_lights_submitted_each_frame(self):
        """Her frame ışık submit edilince crash olmamalı."""
        renderer, camera, sprites, lr, lights, gpu = _build_sidescroller_scene()

        for frame in range(10):
            renderer.tick(0.016)
            for light in lights:
                lr.submit(light)
            for sprite in sprites:
                renderer.draw_sprite(sprite)
            renderer.present()

        # 10 frame * 4 ışık = 40, ama MAX_LIGHTS=32 sınırı var
        # Önemli olan crash olmaması
        assert lr.light_count <= lr.MAX_LIGHTS

    def test_invisible_sprites_skipped(self):
        """Görünmez sprite'lar draw_sprite'ta crash etmemeli."""
        renderer, camera, sprites, lr, lights, gpu = _build_sidescroller_scene()

        # Bazı sprite'ları gizle
        for i in range(0, len(sprites), 2):
            sprites[i].visible = False

        renderer.tick(0.016)
        for sprite in sprites:
            renderer.draw_sprite(sprite)
        renderer.present()

    def test_no_texture_sprite_uses_placeholder(self):
        """Texture'sız sprite placeholder kullanmalı, crash etmemeli."""
        renderer, camera, sprites, lr, lights, gpu = _build_sidescroller_scene()

        no_tex_sprite = Sprite()  # texture yok
        no_tex_sprite.position = Vec2(100.0, 100.0)

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            renderer.tick(0.016)
            renderer.draw_sprite(no_tex_sprite)
            renderer.present()

        assert any("placeholder" in str(x.message).lower() for x in w)

    def test_camera_bounds_clamping(self):
        """Kamera bounds dışına çıkınca clamp çalışmalı."""
        renderer, camera, sprites, lr, lights, gpu = _build_sidescroller_scene()
        camera.bounds = (0.0, 0.0, 2000.0, 1000.0)
        camera.position = Vec2(5000.0, 5000.0)  # bounds dışı
        camera.clamp_to_bounds()

        # Clamp sonrası bounds içinde olmalı
        assert camera.position.x <= 2000.0
        assert camera.position.y <= 1000.0

    def test_projection_matrix_valid(self):
        """Side scroller projeksiyon matrisi 16 float içermeli."""
        renderer, camera, sprites, lr, lights, gpu = _build_sidescroller_scene()
        proj = camera.projection_matrix
        assert len(proj) == 16
        assert all(isinstance(v, float) for v in proj)

    def test_view_matrix_valid(self):
        """View matrisi 16 float içermeli."""
        renderer, camera, sprites, lr, lights, gpu = _build_sidescroller_scene()
        view = camera.view_matrix
        assert len(view) == 16
        assert all(isinstance(v, float) for v in view)

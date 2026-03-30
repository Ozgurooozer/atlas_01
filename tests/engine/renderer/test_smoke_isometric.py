"""
Smoke Test — Isometric Gameplay Sahnesi.

Hedef: crash, siyah ekran, frame akışı bozulması yakalamak.
HeadlessGPU ile çalışır — CI'da GPU gerektirmez.

Sahne içeriği:
- Isometric kamera modu
- 25 sprite (zemin tile'ları + karakterler + objeler)
- 3 point light
- Depth sort (z_index ile)
- 10 frame döngüsü
"""
import pytest
from hal.headless import HeadlessGPU
from engine.renderer.renderer import Renderer2D
from engine.renderer.render_config import RenderConfig
from engine.renderer.camera import Camera
from engine.renderer.sprite import Sprite
from engine.renderer.texture import Texture
from engine.renderer.batch import SpriteBatch
from engine.renderer.light import Light2D, LightRenderer, LightType
from engine.renderer.isometric import IsometricProjection
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


def _build_isometric_scene():
    """Isometric sahnesini kur, (renderer, camera, sprites, lr, lights, iso, gpu) döner."""
    gpu = HeadlessGPU()
    cfg = RenderConfig.game_ready()
    renderer = Renderer2D(config=cfg)
    renderer.gpu_device = gpu
    renderer.viewport = (0, 0, 1280, 720)
    renderer.background_color = (0.05, 0.08, 0.12, 1.0)

    # Kamera — isometric modu
    camera = Camera()
    camera.viewport_width = 1280
    camera.viewport_height = 720
    camera.mode = "isometric"
    camera.zoom = 1.0
    camera.position = Vec2(0.0, 0.0)
    renderer.set_camera(camera)

    # IsometricProjection yardımcısı
    iso = IsometricProjection(screen_width=1280, screen_height=720, tile_size=64)

    # Texture'lar
    tex_grass  = _make_texture(gpu, 60, 120, 50)   # çimen
    tex_stone  = _make_texture(gpu, 100, 90, 80)   # taş
    tex_water  = _make_texture(gpu, 40, 80, 160)   # su
    tex_char   = _make_texture(gpu, 200, 160, 100) # karakter
    tex_tree   = _make_texture(gpu, 40, 100, 40)   # ağaç
    tex_chest  = _make_texture(gpu, 180, 140, 60)  # sandık

    sprites = []

    # 5x5 zemin grid (isometric koordinatlardan screen'e çevir)
    tile_textures = [tex_grass, tex_stone, tex_water]
    for row in range(5):
        for col in range(5):
            world_pos = Vec2(float(col), float(row))
            screen_pos = iso.world_to_screen(world_pos)
            tex = tile_textures[(row + col) % len(tile_textures)]
            tile = Sprite(texture=tex)
            tile.position = screen_pos
            tile.set_scale(1.0)
            # Depth sort: isometric'te row+col ile sırala
            tile.z_index = row + col
            sprites.append(tile)

    # Karakterler
    for i in range(3):
        world_pos = Vec2(float(i + 1), float(i + 1))
        screen_pos = iso.world_to_screen(world_pos)
        char = Sprite(texture=tex_char)
        char.position = screen_pos
        char.set_scale(1.5)
        char.z_index = (i + 1) * 2 + 10  # zemin üstünde
        sprites.append(char)

    # Ağaçlar
    for i in range(4):
        world_pos = Vec2(float(i), 4.0)
        screen_pos = iso.world_to_screen(world_pos)
        tree = Sprite(texture=tex_tree)
        tree.position = screen_pos
        tree.set_scale(2.0)
        tree.z_index = 4 + i + 10
        sprites.append(tree)

    # Sandıklar
    for i in range(2):
        world_pos = Vec2(3.0, float(i + 1))
        screen_pos = iso.world_to_screen(world_pos)
        chest = Sprite(texture=tex_chest)
        chest.position = screen_pos
        chest.set_scale(1.2)
        chest.z_index = (i + 1) + 20
        sprites.append(chest)

    # LightRenderer
    lr = LightRenderer(gpu, 1280, 720)
    renderer.set_light_renderer(lr)

    lights = [
        Light2D(position=Vec2(400.0, 300.0), radius=350.0, intensity=0.9),
        Light2D(position=Vec2(700.0, 400.0), radius=280.0, intensity=0.7),
        Light2D(position=Vec2(1000.0, 250.0), radius=200.0, intensity=0.6),
    ]

    return renderer, camera, sprites, lr, lights, iso, gpu


# ---------------------------------------------------------------------------
# Smoke testler
# ---------------------------------------------------------------------------

class TestIsometricSmoke:

    def test_scene_builds_without_crash(self):
        """Isometric sahne kurulumu crash etmemeli."""
        renderer, camera, sprites, lr, lights, iso, gpu = _build_isometric_scene()
        assert renderer is not None
        assert camera.mode == "isometric"
        assert len(sprites) > 0

    def test_frame_contract_10_frames(self):
        """10 frame boyunca frame kontratı bozulmamalı."""
        renderer, camera, sprites, lr, lights, iso, gpu = _build_isometric_scene()

        for frame in range(10):
            renderer.tick(0.016)
            for light in lights:
                lr.submit(light)
            for sprite in sprites:
                renderer.draw_sprite(sprite)
            renderer.present()

    def test_isometric_projection_matrix_valid(self):
        """Isometric projeksiyon matrisi 16 float içermeli."""
        renderer, camera, sprites, lr, lights, iso, gpu = _build_isometric_scene()
        proj = camera.projection_matrix
        assert len(proj) == 16
        assert all(isinstance(v, float) for v in proj)

    def test_isometric_projection_differs_from_sidescroll(self):
        """Isometric ve side scroller projeksiyon matrisleri farklı olmalı."""
        camera_iso = Camera()
        camera_iso.viewport_width = 1280
        camera_iso.viewport_height = 720
        camera_iso.mode = "isometric"

        camera_ss = Camera()
        camera_ss.viewport_width = 1280
        camera_ss.viewport_height = 720
        camera_ss.mode = "side_scroll"

        assert camera_iso.projection_matrix != camera_ss.projection_matrix

    def test_world_to_screen_conversion(self):
        """World -> screen koordinat dönüşümü tutarlı olmalı."""
        iso = IsometricProjection(screen_width=1280, screen_height=720, tile_size=64)

        # Origin (0,0) ekran merkezine yakın olmalı
        screen = iso.world_to_screen(Vec2(0.0, 0.0))
        assert isinstance(screen.x, float)
        assert isinstance(screen.y, float)

        # Farklı world pozisyonları farklı screen pozisyonları vermeli
        s1 = iso.world_to_screen(Vec2(0.0, 0.0))
        s2 = iso.world_to_screen(Vec2(1.0, 0.0))
        assert s1.x != s2.x or s1.y != s2.y

    def test_depth_sort_order(self):
        """Isometric sprite'lar z_index'e göre sıralanmalı."""
        renderer, camera, sprites, lr, lights, iso, gpu = _build_isometric_scene()
        batch = SpriteBatch(renderer, instancing_enabled=False)

        renderer.tick(0.016)
        with batch:
            for sprite in sprites:
                batch.draw(sprite)
        renderer.present()

        # Sorted sprites z_index'e göre artan sırada olmalı
        sorted_sprites = batch.sorted_sprites
        if len(sorted_sprites) > 1:
            for i in range(len(sorted_sprites) - 1):
                assert sorted_sprites[i].z_index <= sorted_sprites[i + 1].z_index

    def test_sprite_batch_legacy_10_frames(self):
        """SpriteBatch legacy modda 10 frame crash etmemeli."""
        renderer, camera, sprites, lr, lights, iso, gpu = _build_isometric_scene()
        batch = SpriteBatch(renderer, instancing_enabled=False)

        for frame in range(10):
            renderer.tick(0.016)
            with batch:
                for sprite in sprites:
                    batch.draw(sprite)
            renderer.present()

    def test_sprite_batch_instanced_10_frames(self):
        """SpriteBatch instanced modda 10 frame crash etmemeli."""
        renderer, camera, sprites, lr, lights, iso, gpu = _build_isometric_scene()
        batch = SpriteBatch(renderer, instancing_enabled=True)

        for frame in range(10):
            renderer.tick(0.016)
            with batch:
                for sprite in sprites:
                    batch.draw(sprite)
            renderer.present()

    def test_camera_mode_switch_raises_on_invalid(self):
        """Geçersiz kamera modu ValueError fırlatmalı."""
        camera = Camera()
        with pytest.raises(ValueError):
            camera.mode = "invalid_mode"

    def test_camera_zoom_in_isometric(self):
        """Isometric modda zoom değişimi crash etmemeli."""
        renderer, camera, sprites, lr, lights, iso, gpu = _build_isometric_scene()

        for zoom in [0.5, 1.0, 2.0]:
            camera.zoom = zoom
            renderer.tick(0.016)
            for sprite in sprites:
                renderer.draw_sprite(sprite)
            renderer.present()

    def test_lights_in_isometric_scene(self):
        """Isometric sahnede ışık submit crash etmemeli."""
        renderer, camera, sprites, lr, lights, iso, gpu = _build_isometric_scene()

        for frame in range(5):
            renderer.tick(0.016)
            for light in lights:
                lr.submit(light)
            for sprite in sprites:
                renderer.draw_sprite(sprite)
            renderer.present()

    def test_screen_to_world_roundtrip(self):
        """World -> screen -> world dönüşümü yaklaşık tutarlı olmalı."""
        iso = IsometricProjection(screen_width=1280, screen_height=720, tile_size=64)

        original = Vec2(2.0, 3.0)
        screen = iso.world_to_screen(original)
        recovered = iso.screen_to_world(screen)

        assert abs(recovered.x - original.x) < 0.01
        assert abs(recovered.y - original.y) < 0.01

    def test_many_sprites_no_crash(self):
        """100 sprite ile 5 frame crash etmemeli."""
        gpu = HeadlessGPU()
        renderer = Renderer2D()
        renderer.gpu_device = gpu
        renderer.viewport = (0, 0, 1280, 720)

        camera = Camera()
        camera.mode = "isometric"
        camera.viewport_width = 1280
        camera.viewport_height = 720
        renderer.set_camera(camera)

        iso = IsometricProjection(1280, 720, 64)
        tex_data = bytes([100, 150, 80, 255] * 32 * 32)
        tex_id = gpu.create_texture(32, 32, tex_data)
        tex = Texture(32, 32, tex_data)
        tex.mark_uploaded(tex_id)

        sprites = []
        for i in range(100):
            s = Sprite(texture=tex)
            s.position = iso.world_to_screen(Vec2(float(i % 10), float(i // 10)))
            s.z_index = i
            sprites.append(s)

        for frame in range(5):
            renderer.tick(0.016)
            for sprite in sprites:
                renderer.draw_sprite(sprite)
            renderer.present()

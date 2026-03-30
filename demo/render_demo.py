"""
Render Demo — Gerçek GPU render testi.

ModernGLDevice + PygletWindow + Texture ile ekranda sprite gösterir.
ESC veya pencereyi kapatarak çıkılır.

Çalıştır: python demo/render_demo.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hal.pyglet_backend import PygletWindow, ModernGLDevice
from engine.renderer.texture import Texture
from engine.renderer.sprite import Sprite
from engine.renderer.renderer import Renderer2D
from core.vec import Vec2


def solid_texture(r: int, g: int, b: int, size: int = 64) -> Texture:
    return Texture.from_color(size, size, (r, g, b, 255))


def checkerboard_texture(size: int = 64) -> Texture:
    data = bytearray(size * size * 4)
    for y in range(size):
        for x in range(size):
            idx = (y * size + x) * 4
            if (x // 8 + y // 8) % 2 == 0:
                data[idx:idx+4] = [240, 240, 240, 255]
            else:
                data[idx:idx+4] = [40, 40, 40, 255]
    return Texture(size, size, bytes(data))


def gradient_texture(size: int = 64) -> Texture:
    data = bytearray(size * size * 4)
    for y in range(size):
        for x in range(size):
            idx = (y * size + x) * 4
            data[idx]   = int(x / size * 255)
            data[idx+1] = int(y / size * 255)
            data[idx+2] = 180
            data[idx+3] = 255
    return Texture(size, size, bytes(data))


def circle_texture(size: int = 64) -> Texture:
    """Daire şeklinde texture."""
    data = bytearray(size * size * 4)
    cx, cy, r = size / 2, size / 2, size / 2 - 2
    for y in range(size):
        for x in range(size):
            idx = (y * size + x) * 4
            dist = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            if dist <= r:
                t = dist / r
                data[idx]   = int(255 * (1 - t))
                data[idx+1] = int(180 * t)
                data[idx+2] = 255
                data[idx+3] = 255
            else:
                data[idx:idx+4] = [0, 0, 0, 0]
    return Texture(size, size, bytes(data))


def make_sprite(tex: Texture, x: float, y: float, scale: float = 1.0) -> Sprite:
    s = Sprite(texture=tex, position=Vec2(x, y))
    s.set_scale(scale)
    return s


def run():
    WIDTH, HEIGHT = 800, 600

    window = PygletWindow(WIDTH, HEIGHT, "Atlas Engine — Render Demo")
    gpu = ModernGLDevice(window)

    renderer = Renderer2D()
    renderer.gpu_device = gpu
    renderer.viewport = (0, 0, WIDTH, HEIGHT)
    renderer.background_color = (0.08, 0.08, 0.12, 1.0)

    # Texture'lar
    tex_bg    = solid_texture(20, 20, 30, 1)
    tex_red   = solid_texture(220, 60, 60)
    tex_green = solid_texture(60, 200, 80)
    tex_blue  = solid_texture(60, 120, 220)
    tex_check = checkerboard_texture(64)
    tex_grad  = gradient_texture(64)
    tex_circ  = circle_texture(64)

    # Sprite listesi — pozisyonlar top-left origin (x, y)
    sprites = [
        make_sprite(tex_bg,    0,   0,   max(WIDTH, HEIGHT) / 1.0),  # arka plan
        make_sprite(tex_red,   60,  250, 1.2),
        make_sprite(tex_green, 210, 250, 1.2),
        make_sprite(tex_blue,  360, 250, 1.2),
        make_sprite(tex_check, 510, 230, 1.5),
        make_sprite(tex_grad,  660, 230, 1.5),
        make_sprite(tex_circ,  360,  80, 1.8),   # daire — üstte, mavi karenin üzerinde değil
    ]

    print("=" * 40)
    print("  Atlas Engine — Render Demo")
    print("=" * 40)
    print(f"  Pencere  : {WIDTH}x{HEIGHT}")
    print(f"  Sprite   : {len(sprites)}")
    print(f"  Backend  : ModernGL {__import__('moderngl').__version__}")
    print("  ESC ile çıkın.")
    print("=" * 40)

    import pyglet

    @window.pyglet_window.event
    def on_key_press(symbol, modifiers):
        if symbol == pyglet.window.key.ESCAPE:
            window.close()

    @window.pyglet_window.event
    def on_draw():
        renderer.tick(0.016)
        for sprite in sprites:
            renderer.draw_sprite(sprite)
        renderer.present()

    pyglet.app.run()
    print(f"Çıkıldı. Son frame draw count: {renderer.draw_count}")


if __name__ == "__main__":
    run()

"""
Benchmark Demo -- Sprite x Isik x Cozunurluk matrisli FPS tablosu.

Calistir:
  python demo/benchmark.py              # GPU (ModernGL)
  python demo/benchmark.py --headless   # CPU-only (no GPU)
  python demo/benchmark.py --sprites 100 1000 --lights 0 8 --res 800x600 1920x1080
"""
import sys
import os
import time
import argparse
import itertools

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ---------------------------------------------------------------------------
# Konfigürasyon
# ---------------------------------------------------------------------------

SPRITE_COUNTS  = [100, 500, 1000, 5000]
LIGHT_COUNTS   = [0, 4, 8, 16]
RESOLUTIONS    = [(800, 600), (1280, 720), (1920, 1080)]
FRAMES_PER_RUN = 60
WARMUP_FRAMES  = 10


# ---------------------------------------------------------------------------
# Yardımcılar
# ---------------------------------------------------------------------------

def _make_textures(gpu, n: int):
    ids = []
    for i in range(min(n, 8)):
        r = (i * 37 + 80) % 256
        g = (i * 71 + 120) % 256
        b = (i * 113 + 60) % 256
        data = bytes([r, g, b, 255] * 32 * 32)
        ids.append(gpu.create_texture(32, 32, data))
    return ids


def _build_scene(gpu, width, height, sprite_count, light_count):
    from engine.renderer.renderer import Renderer2D
    from engine.renderer.texture import Texture
    from engine.renderer.sprite import Sprite
    from engine.renderer.light import Light2D, LightRenderer
    from core.vec import Vec2

    renderer = Renderer2D()
    renderer.gpu_device = gpu
    renderer.viewport = (0, 0, width, height)
    renderer.background_color = (0.05, 0.05, 0.08, 1.0)

    tex_ids = _make_textures(gpu, sprite_count)
    sprites = []
    for i in range(sprite_count):
        tex = Texture(32, 32)
        tex.mark_uploaded(tex_ids[i % len(tex_ids)])
        s = Sprite(texture=tex)
        s.position = Vec2((i % 60) * (width / 60.0), (i // 60) * 20.0)
        sprites.append(s)

    lr = LightRenderer(gpu, width, height)
    renderer.set_light_renderer(lr)
    lights = [
        Light2D(
            position=Vec2(width * (j + 1) / (light_count + 1), height / 2),
            radius=250.0,
            intensity=0.9,
        )
        for j in range(light_count)
    ]

    return renderer, sprites, lr, lights


def _print_table(results: list):
    print("\n" + "=" * 72)
    print("  BENCHMARK SONUCLARI")
    print("=" * 72)
    print(f"{'Cozunurluk':<14} {'Sprite':>7} {'Isik':>5} {'FPS':>8} {'ms/frame':>10}")
    print("-" * 72)

    prev_res = None
    for r in results:
        if prev_res and r["res"] != prev_res:
            print()
        fps = r["fps"]
        fps_str = f"{fps:8.1f}"
        if fps >= 60:
            fps_colored = f"\033[92m{fps_str}\033[0m"
        elif fps >= 30:
            fps_colored = f"\033[93m{fps_str}\033[0m"
        else:
            fps_colored = f"\033[91m{fps_str}\033[0m"
        print(f"{r['res']:<14} {r['sprites']:>7} {r['lights']:>5} {fps_colored} {r['ms']:>9.2f}ms")
        prev_res = r["res"]

    print("=" * 72)
    if results:
        best  = max(results, key=lambda x: x["fps"])
        worst = min(results, key=lambda x: x["fps"])
        print(f"\n  En iyi : {best['res']} | {best['sprites']} sprite | {best['lights']} isik -> {best['fps']:.1f} FPS")
        print(f"  En kotu: {worst['res']} | {worst['sprites']} sprite | {worst['lights']} isik -> {worst['fps']:.1f} FPS\n")


# ---------------------------------------------------------------------------
# Headless benchmark
# ---------------------------------------------------------------------------

def run_headless_benchmark():
    from hal.headless import HeadlessGPU

    print("\n" + "=" * 72)
    print("  HEADLESS BENCHMARK  (CPU zamanlama, GPU no-op)")
    print("=" * 72)

    results = []
    combinations = list(itertools.product(RESOLUTIONS, SPRITE_COUNTS, LIGHT_COUNTS))
    total = len(combinations)

    for idx, ((width, height), sprite_count, light_count) in enumerate(combinations):
        gpu = HeadlessGPU()
        renderer, sprites, lr, lights = _build_scene(gpu, width, height, sprite_count, light_count)

        # Warmup
        for _ in range(WARMUP_FRAMES):
            renderer.tick(0.016)
            for l in lights:
                lr.submit(l)
            for s in sprites:
                renderer.draw_sprite(s)
            renderer.present()

        # Measure
        t0 = time.perf_counter()
        for _ in range(FRAMES_PER_RUN):
            renderer.tick(0.016)
            for l in lights:
                lr.submit(l)
            for s in sprites:
                renderer.draw_sprite(s)
            renderer.present()
        elapsed = time.perf_counter() - t0

        fps = FRAMES_PER_RUN / elapsed
        ms  = elapsed / FRAMES_PER_RUN * 1000
        results.append({"res": f"{width}x{height}", "sprites": sprite_count,
                         "lights": light_count, "fps": fps, "ms": ms})

        label = f"{width}x{height} | {sprite_count:>5} sprite | {light_count:>2} isik"
        print(f"  [{idx+1:>3}/{total}] {label}  ->  {fps:6.1f} FPS  ({ms:.2f} ms)")

    _print_table(results)
    return results


# ---------------------------------------------------------------------------
# GPU benchmark — tek pencere, sıralı kombinasyonlar
# ---------------------------------------------------------------------------

def run_gpu_benchmark():
    try:
        import pyglet
        from hal.pyglet_backend import PygletWindow, ModernGLDevice
    except ImportError as e:
        print(f"GPU benchmark icin pyglet/moderngl gerekli: {e}")
        return run_headless_benchmark()

    print("\n" + "=" * 72)
    print("  GPU BENCHMARK  (ModernGL + Pyglet)")
    print("=" * 72)

    max_w = max(r[0] for r in RESOLUTIONS)
    max_h = max(r[1] for r in RESOLUTIONS)

    window = PygletWindow(max_w, max_h, "Engine Benchmark")
    gpu    = ModernGLDevice(window)

    combinations = list(itertools.product(RESOLUTIONS, SPRITE_COUNTS, LIGHT_COUNTS))
    total        = len(combinations)
    results      = []

    # Tüm kombinasyonları sırayla işleyecek state machine
    state = {
        "idx":         0,
        "frame":       0,
        "frame_times": [],
        "renderer":    None,
        "sprites":     [],
        "lr":          None,
        "lights":      [],
        "abort":       False,
    }

    def load_next():
        idx = state["idx"]
        if idx >= total:
            pyglet.app.exit()
            return

        (width, height), sprite_count, light_count = combinations[idx]
        label = f"{width}x{height} | {sprite_count:>5} sprite | {light_count:>2} isik"
        print(f"  [{idx+1:>3}/{total}] {label} ...", end="", flush=True)

        renderer, sprites, lr, lights = _build_scene(gpu, width, height, sprite_count, light_count)
        state["renderer"]    = renderer
        state["sprites"]     = sprites
        state["lr"]          = lr
        state["lights"]      = lights
        state["frame"]       = 0
        state["frame_times"] = []

    load_next()

    @window.pyglet_window.event
    def on_key_press(symbol, modifiers):
        if symbol == pyglet.window.key.ESCAPE:
            state["abort"] = True
            pyglet.app.exit()

    @window.pyglet_window.event
    def on_draw():
        if state["abort"] or state["idx"] >= total:
            return

        renderer = state["renderer"]
        sprites  = state["sprites"]
        lr       = state["lr"]
        lights   = state["lights"]

        t0 = time.perf_counter()

        renderer.tick(0.016)
        for l in lights:
            lr.submit(l)
        for s in sprites:
            renderer.draw_sprite(s)
        renderer.present()
        window.pyglet_window.flip()

        elapsed_ms = (time.perf_counter() - t0) * 1000
        state["frame"] += 1

        if state["frame"] > WARMUP_FRAMES:
            state["frame_times"].append(elapsed_ms)

        if state["frame"] >= WARMUP_FRAMES + FRAMES_PER_RUN:
            # Kombinasyon bitti — sonucu kaydet
            ft = state["frame_times"]
            avg_ms = sum(ft) / len(ft) if ft else 0.0
            fps    = 1000.0 / avg_ms if avg_ms > 0 else 0.0
            min_ms = min(ft) if ft else 0.0
            max_ms = max(ft) if ft else 0.0

            (width, height), sprite_count, light_count = combinations[state["idx"]]
            results.append({
                "res":     f"{width}x{height}",
                "sprites": sprite_count,
                "lights":  light_count,
                "fps":     fps,
                "ms":      avg_ms,
                "min_ms":  min_ms,
                "max_ms":  max_ms,
            })
            print(f"  {fps:6.1f} FPS  ({avg_ms:.2f} ms avg)")

            state["idx"] += 1
            if state["idx"] < total:
                load_next()
            else:
                pyglet.app.exit()

    pyglet.app.run()

    try:
        window.pyglet_window.close()
    except Exception:
        pass

    _print_table(results)
    return results


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Engine Benchmark")
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--sprites", nargs="+", type=int, default=None)
    parser.add_argument("--lights",  nargs="+", type=int, default=None)
    parser.add_argument("--res",     nargs="+", type=str, default=None)
    parser.add_argument("--frames",  type=int,  default=FRAMES_PER_RUN)
    args = parser.parse_args()

    if args.sprites: SPRITE_COUNTS[:]  = args.sprites
    if args.lights:  LIGHT_COUNTS[:]   = args.lights
    if args.res:     RESOLUTIONS[:]    = [tuple(int(v) for v in r.split("x")) for r in args.res]
    FRAMES_PER_RUN = args.frames

    if args.headless:
        run_headless_benchmark()
    else:
        run_gpu_benchmark()

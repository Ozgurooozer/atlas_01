# 2D Game Engine

Unreal Engine felsefesiyle 2D oyun motoru — Python'da modüler, test edilebilir, genişletilebilir.

## Özellikler

- **Her şey Object** — Actor, Component, Widget hepsi Object'ten türetilir
- **Reflection sistemi** — Editor otomatik çalışır, ek kod gerektirmez
- **Subsystem pattern** — Modüler genişleme, yeni subsystem eklemek kolay
- **1638 test, 0 fail** — Headless GPU ile CI'da çalışır
- **GPU Instancing** — SpriteBatch, tek draw call ile N sprite
- **Normal Map Lighting** — Lambertian + Blinn-Phong, max 8 point light per sprite
- **Deferred / Forward mutex** — Renderer2D'de runtime geçiş koruması
- **SSAO** — 64-sample hemisphere kernel, 4x4 noise texture, box blur
- **Soft Shadows** — Depth pass + PCF + Gaussian penumbra
- **TileMap** — Frustum culling + UV atlas lookup
- **Particle System** — Ring buffer pool, SpriteBatch entegrasyonu
- **2.5D Isometric** — IsometricProjection, HeightSprite, LayerManager

## Bağımlılıklar

| Paket | Amaç |
|-------|------|
| pyglet >= 2.0 | Window/GL context |
| moderngl >= 5.10 | Modern OpenGL |
| pymunk >= 7.2 | 2D Physics |
| Pillow >= 10.0 | Texture loading |
| msgspec >= 0.18 | Fast serialization |
| watchdog >= 4.0 | Hot reload |
| dearpygui >= 1.13 | Editor UI |

## Kurulum

```bash
pip install -r requirements.txt
pytest tests/ -v
```

## Proje Yapısı

```
hal/                        # Layer 0: Hardware Abstraction
├── interfaces.py           # IWindow, IGPUDevice, IFilesystem, IClock, IFramebuffer
├── headless.py             # HeadlessGPU, HeadlessFramebuffer, MemoryFilesystem
├── pyglet_backend.py       # PygletWindow, ModernGLDevice
└── os_filesystem.py

core/                       # Layer 1: Foundation
├── object.py, guid.py, reflection.py
├── eventbus.py, serializer.py
├── vec.py, color.py, scheduler.py

engine/                     # Layer 2: Subsystems
├── renderer/
│   ├── renderer.py         # Renderer2D (deferred/forward mutex, SSAO pipeline)
│   ├── sprite.py           # Sprite (uv_offset, uv_size, normal_map)
│   ├── batch.py            # SpriteBatch (instanced + legacy)
│   ├── instance_data.py    # InstanceData (17 float GPU struct)
│   ├── gbuffer.py          # GBuffer (albedo/normal/depth FBO)
│   ├── ssao.py             # SSAOPass (64 kernel, noise, blur)
│   ├── shadow_map.py       # ShadowMapRenderer (depth, PCF, penumbra)
│   ├── soft_shadows.py     # ShadowCaster, ShadowMap, SoftShadowKernel
│   ├── normal_lighting.py  # NormalMapShader, Light3D, LightManager
│   ├── light.py            # Light2D, LightRenderer, LightMap
│   ├── tilemap.py          # TileMapRenderer (frustum culling, UV atlas)
│   ├── particle.py         # ParticleEmitter (ring buffer)
│   ├── texture.py, camera.py, material.py
│   ├── animation.py, spritesheet.py, shader.py
│   ├── isometric.py, height_sprite.py, layer_manager.py
│   ├── directional_sprite.py, sdf_font.py
│   ├── postprocess_stack.py, volumetric.py, optimization.py
│   └── particle3d.py
├── physics/                # AABB, OverlapDetector, SpatialHash
├── input/, audio/, asset/

world/                      # Layer 3: Actor/Component/ECS
game/                       # Layer 4: Inventory, Quest, Save, Dialogue
scripting/                  # Layer 5: StateMachine, BehaviourTree, EventGraph
ui/                         # Layer 6: Widget, Canvas, Layout, Theme
editor/                     # Layer 7: Viewport, Hierarchy, Properties
```

## Hızlı Kullanım

```python
from hal.headless import HeadlessGPU
from engine.renderer.renderer import Renderer2D
from engine.renderer.sprite import Sprite
from engine.renderer.texture import Texture
from engine.renderer.batch import SpriteBatch

gpu = HeadlessGPU()
renderer = Renderer2D()
renderer.gpu_device = gpu

# Normal map sprite
sprite = Sprite(texture)
sprite.normal_map = normal_texture  # otomatik draw_with_normal_map kullanır

# GPU instancing
batch = SpriteBatch(renderer, instancing_enabled=True)
with batch:
    for s in sprites:
        batch.draw(s)  # tek draw_instanced() çağrısı

# SSAO
renderer.ssao_enabled = True
renderer.begin_frame()
# ... çizim ...
renderer.end_frame()

# Tilemap
tilemap = TileMapRenderer(tileset, tile_size=32)
tilemap.set_tiles(width, height, tile_indices)
tilemap.draw(batch, camera_pos, viewport_size)
```

## Test

```bash
pytest tests/ -v
pytest tests/ --cov=. --cov-report=html
```

## Durum

| Faz | Açıklama | Test |
|-----|----------|------|
| 1-12 | Foundation → 2.5D Isometric | 1569 |
| 13 | GPU Instancing + Normal Map + Advanced Lighting | 69 |
| **Toplam** | | **1638** ✅ |

## Dokümantasyon

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — Mimari tasarım ve sistem detayları
- [docs/CODE_REVIEW_NOTES.md](docs/CODE_REVIEW_NOTES.md) — Kod inceleme bulguları

## Lisans

MIT

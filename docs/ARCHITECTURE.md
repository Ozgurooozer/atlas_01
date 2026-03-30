# 2D GAME ENGINE MİMARİSİ

## Vizyon

Unreal Engine'in "her şey Object, her şey düzenlenebilir" felsefesini 2D için Python'da gerçekleştirmek. Modüler, test edilebilir, genişletilebilir bir core yapı.

---

## Bağımlılıklar

| Paket | Versiyon | Amaç | Katman |
|-------|----------|------|--------|
| pyglet | >=2.0 | Window/GL context | 0 - HAL |
| moderngl | >=5.10 | Modern OpenGL | 0 - HAL |
| pymunk | >=7.2 | 2D Physics | 2 - Engine |
| Pillow | >=10.0 | Texture loading | 2 - Engine |
| msgspec | >=0.18 | Fast serialization | 1 - Core |
| watchdog | >=4.0 | Hot reload | 2 - Engine |
| dearpygui | >=1.13 | Editor UI | 7 - Editor |

---

## Katman Mimarisi

```
┌─────────────────────────────────────────────────────────────┐
│                        EDITOR (7)                           │
│  DearPyGui → Viewport • Hierarchy • Properties              │
│  (Engine API'ını tüketir, runtime kodu YOK)                 │
├─────────────────────────────────────────────────────────────┤
│                         UI (6)                              │
│  Widget • Canvas • HUD • Dialogue • Layout • Theme          │
├─────────────────────────────────────────────────────────────┤
│                     SCRIPTING (5)                           │
│  StateMachine • BehaviourTree • EventGraph • Blackboard     │
├─────────────────────────────────────────────────────────────┤
│                      GAME (4)                               │
│  GameMode • Controller • Inventory • Quest • Save • Dialogue│
├─────────────────────────────────────────────────────────────┤
│                       WORLD (3)                             │
│  World • Level • Actor • Component • System • Prefab        │
│  (ECS + Composition)                                         │
├─────────────────────────────────────────────────────────────┤
│                      ENGINE (2)                             │
│  Renderer (ModernGL) • Physics (Pymunk) • Audio • Input     │
│  Asset (Pillow) • HotReload (Watchdog)                      │
│  (Her biri ISubsystem implemente eder)                       │
├─────────────────────────────────────────────────────────────┤
│                        CORE (1)                             │
│  Object • Reflection • EventBus • Serializer (msgspec)      │
│  (Her şeyin temeli)                                          │
├─────────────────────────────────────────────────────────────┤
│                         HAL (0)                             │
│  IWindow → PygletWindow • HeadlessWindow                    │
│  IGPUDevice → ModernGLDevice • HeadlessGPU                  │
│  IFilesystem → OSFilesystem • MemoryFilesystem              │
│  IClock → SystemClock • FixedClock                          │
└─────────────────────────────────────────────────────────────┘

BAĞIMLILIK YÖNÜ: ↓ SADECE AŞAĞI
```

---

## Katman Detayları

### Katman 0: HAL (Hardware Abstraction Layer)

**Sorumluluk:** Donanım ve OS soyutlaması. Engine'in geri kalanı pyglet bilmez.

```
hal/
├── __init__.py
├── interfaces.py      # IWindow, IGPUDevice, IFilesystem, IClock, IFramebuffer
├── headless.py        # HeadlessWindow, HeadlessGPU, HeadlessFramebuffer,
│                      # MemoryFilesystem, FixedClock
├── pyglet_backend.py  # PygletWindow, ModernGLDevice
└── os_filesystem.py   # OSFilesystem (gerçek dosya sistemi)
```

**IGPUDevice arayüzü (tam):**

| Metot | Açıklama |
|-------|----------|
| `create_texture(w, h, data)` | GPU texture oluştur, ID döner |
| `clear(r, g, b, a)` | Ekranı temizle |
| `draw(...)` | Standart sprite çiz |
| `draw_with_normal_map(...)` | Normal map + point lights ile çiz |
| `draw_light(...)` | Additive light pass quad çiz |
| `draw_instanced(...)` | GPU instancing ile N sprite çiz |
| `flush()` | GPU komutlarını flush et |
| `create_framebuffer(w, h)` | Standart FBO oluştur |
| `create_mrt_framebuffer(w, h, n)` | Multiple Render Target FBO |
| `create_depth_framebuffer(w, h)` | Depth-only FBO |

---

### Katman 1: CORE

**Sorumluluk:** Tüm sistemlerin üzerinde durduğu temel yapı taşları.

```
core/
├── __init__.py
├── guid.py            # GUID - Unique identifier (UUID4)
├── object.py          # Object base class
├── reflection.py      # @reflect decorator + PropertyMeta
├── eventbus.py        # Pub/sub event system
├── serializer.py      # JSON + msgspec serialization
├── vec.py             # Vec2, Vec3
├── color.py           # Color (r, g, b, a)
└── scheduler.py       # Delayed/Repeated callbacks
```

---

### Katman 2: ENGINE

**Sorumluluk:** Runtime subsystem'leri. Her biri ISubsystem implemente eder.

```
engine/
├── __init__.py
├── engine.py          # Engine class (subsystem manager)
├── subsystem.py       # ISubsystem interface
├── loop.py            # Game loop
├── settings.py        # Engine settings
└── renderer/
    ├── renderer.py        # IRenderer + Renderer2D (deferred/forward mutex, SSAO)
    ├── camera.py          # Camera (free/iso/topdown)
    ├── sprite.py          # Sprite (uv_offset, uv_size, normal_map)
    ├── texture.py         # Texture + UVRegion + TextureLoader
    ├── batch.py           # SpriteBatch (instanced + legacy flush)
    ├── instance_data.py   # InstanceData (17 float, 68 byte GPU struct)
    ├── material.py        # Material
    ├── shader.py          # Shader sistemi
    ├── animation.py       # Sprite animasyon
    ├── spritesheet.py     # Spritesheet yönetimi
    ├── light.py           # Light2D + LightRenderer + LightMap
    ├── normal_lighting.py # NormalMapShader + Light3D + LightManager
    ├── gbuffer.py         # GBuffer (albedo/normal/depth FBO'lar)
    ├── ssao.py            # SSAOPass (64-sample kernel, 4x4 noise)
    ├── shadow_map.py      # ShadowMapRenderer (depth pass, PCF, penumbra)
    ├── soft_shadows.py    # ShadowCaster + ShadowMap + SoftShadowKernel
    ├── particle.py        # ParticleEmitter (ring buffer pool)
    ├── particle3d.py      # 3D particle sistemi
    ├── tilemap.py         # TileMapRenderer (frustum culling, UV atlas)
    ├── isometric.py       # IsometricProjection
    ├── height_sprite.py   # HeightSprite
    ├── layer_manager.py   # LayerManager
    ├── directional_sprite.py # DirectionalSprite
    ├── sdf_font.py        # SDF font rendering
    ├── postprocess_stack.py  # PostProcessStack
    ├── volumetric.py      # Volumetric effects
    └── optimization.py    # OptimizationManager
```

#### Renderer2D — Önemli Özellikler

**Deferred / Forward mutex:**
```python
renderer.deferred_enabled = True   # forward otomatik kapanır
renderer.forward_enabled = True    # deferred açıkken ValueError fırlatır
```

**SSAO pipeline:**
```python
renderer.ssao_enabled = True
renderer.begin_frame()   # GBuffer + SSAOPass lazy init
# ... sprite çizimi ...
renderer.end_frame()     # SSAO render → blur → composite
```

**Normal map sprite:**
```python
sprite.normal_map = normal_texture  # Texture objesi
# draw_sprite() otomatik draw_with_normal_map() kullanır
# LightRenderer'dan max 8 point light toplanır
```

#### GBuffer

Üç bağımsız FBO:
- `albedo_fbo` — renk attachment
- `normal_fbo` — yüzey normalleri (SSAO input)
- `depth_fbo` — derinlik (SSAO input)

#### SSAOPass

```python
ssao = SSAOPass(gpu, width, height)
# 64 hemisphere kernel sample (quadratic clustering)
# 4x4 RGBA noise texture (tangent space rotation)
ssao_fbo = ssao.render(gbuffer)   # normal + depth input
blurred  = ssao.blur(ssao_fbo)    # 4x4 box blur
```

#### ShadowMapRenderer

```python
smr = ShadowMapRenderer(gpu, resolution=512)
smr.render_shadow_map(light, casters)  # depth pass, gpu.draw() çağrılır
pcf_fbo = smr.apply_pcf()             # PCF soft edges
final   = smr.apply_penumbra_blur(4.0) # Gaussian penumbra
```

#### TileMapRenderer

```python
tilemap = TileMapRenderer(tileset, tile_size=32)
tilemap.set_tiles(width, height, tile_indices)
tilemap.draw(batch, camera_pos, viewport_size)
# Her tile için UV offset = (col * uv_w, row * uv_h)
# Frustum culling: sadece görünen tile'lar çizilir
```

#### InstanceData (GPU struct)

```
17 float = 68 byte per instance
pos(2) | size(2) | rot(1) | color(4) | anchor(2) | flip(2) | uv_off(2) | uv_size(2)
```

`SpriteBatch` instancing modunda `sprite.uv_offset` / `sprite.uv_size`'ı okur.

#### ParticleEmitter

- Ring buffer pool (`max_particles` sabit boyut)
- `emit(count, **kwargs)` — pool'dan particle al
- `update(dt)` — fizik + yaşam döngüsü
- `draw(batch)` — tek temp sprite ile batch'e gönder

---

### Katman 3: WORLD

```
world/
├── world.py           # World container (GUID-based O(1) lookup)
├── level.py           # Level + LevelManager
├── actor.py           # Actor
├── component.py       # Component base
├── transform.py       # TransformComponent
├── prefab.py          # Prefab system
└── tag.py             # Tag system
```

---

### Katman 4: GAME

```
game/
├── gamemode.py
├── controller.py
├── inventory/inventory.py
├── quest/quest.py
├── save/save.py
└── dialogue/dialogue.py
```

---

### Katman 5: SCRIPTING

```
scripting/
├── statemachine.py
├── behaviour_tree.py
├── event_graph.py
├── blackboard.py
└── timeline.py
```

---

### Katman 6: UI

```
ui/
├── widget.py
├── canvas.py
├── label.py
├── button.py
├── panel.py
├── layout.py
└── theme.py
```

---

### Katman 7: EDITOR

```
editor/
├── main.py
├── viewport.py
├── hierarchy.py
├── properties.py
├── asset_browser.py
├── graph_editor.py
└── animation_editor.py
```

---

## Test Stratejisi

- HAL katmanı `HeadlessGPU` / `HeadlessFramebuffer` sağlar — CI'da GPU olmadan çalışır
- `MagicMock(spec=IGPUDevice)` sadece pipeline state testlerinde kullanılır
- Gerçek GPU davranışı (shader output, pixel correctness) headless ortamda test edilemez

---

## Geliştirme Fazları

| Faz | Açıklama | Test | Durum |
|-----|----------|------|-------|
| 1 | Foundation (HAL + Core) | 117 | ✅ |
| 2 | Engine Skeleton | 90 | ✅ |
| 3 | World/ECS | 215 | ✅ |
| 4 | Subsystems (Renderer, Physics, Input, Asset) | 320 | ✅ |
| 5 | Game & UI | 180 | ✅ |
| 6 | Editor | 136 | ✅ |
| 7 | Demo Games | 113 | ✅ |
| 8 | Collision Detection | 20 | ✅ |
| 9 | Timer/Scheduler | 33 | ✅ |
| 10 | Quality Gate (CI + pre-commit) | 98 | ✅ |
| 11 | Advanced Renderer (Shader, Animation, Light, Spritesheet) | 44 | ✅ |
| 12 | 2.5D Isometric Rendering | 184 | ✅ |
| 13 | GPU Instancing + Normal Map Lighting + Advanced Lighting | 69 | ✅ |
| **TOPLAM** | | **1638** | ✅ |

### Faz 13 Detayı

**GPU Instancing (spec: gpu-instancing)**
- `InstanceData` — 17 float GPU struct, `to_bytes()` / `from_bytes()`
- `SpriteBatch` — `instancing_enabled` flag, `_flush_instanced()` texture gruplama
- `uv_offset` / `uv_size` sprite'tan okunur (atlas desteği)

**Normal Map Lighting (spec: normal-map-lighting)**
- `NormalMapShader` — Lambertian + Blinn-Phong specular
- `Light3D` + `LightAttenuation` + `LightManager` (max 50, cull by distance)
- `Renderer2D.draw_sprite()` — normal_map varsa `draw_with_normal_map()` kullanır

**Advanced Lighting (spec: advanced-lighting)**
- `GBuffer` — albedo/normal/depth ayrı FBO'lar
- `SSAOPass` — 64 kernel, 4x4 noise, render + blur
- `ShadowMapRenderer` — depth pass + PCF + penumbra blur
- `TileMapRenderer` — frustum culling + UV atlas lookup
- `ParticleEmitter` — ring buffer pool
- Deferred/Forward mutex — `Renderer2D` setter'larında `ValueError`

---

## Temel Prensipler

1. **Her şey Object** → Actor, Component, Widget hepsi Object'ten
2. **Reflection sistemi** → Editor otomatik çalışır
3. **Subsystem pattern** → Modüler genişleme
4. **Yukarı bağımlılık yok** → Sadece alt katmanları bil
5. **Interface'e bağımlılık** → Somut değil, soyuta bağlan
6. **Headless test** → CI'da GPU olmadan çalışır
7. **Pre-commit + CI Gate** → Otomatik kalite koruması

# Kod İnceleme Notları

> Kiro tarafından yapılan kod incelemesinin bulguları ve düzeltmeleri.
> Kural: Testlere güvenme, kodu oku.

---

## HAL (Layer 0) ✅

**Durum:** Temiz.

- `interfaces.py` — `IGPUDevice` tam: `draw`, `draw_with_normal_map`, `draw_light`, `draw_instanced`, `create_framebuffer`, `create_mrt_framebuffer`, `create_depth_framebuffer`.
- `headless.py` — `HeadlessGPU` tüm interface metodlarını implemente ediyor. `HeadlessFramebuffer` `is_bound` state'ini doğru takip ediyor.
- 2 test skipped: gerçek GPU/pencere gerektiren testler, headless ortamda normal.

---

## Core (Layer 1) ✅

**Durum:** Temiz.

### Geçmiş Düzeltmeler
- `vec.py` — `Vec2.__hash__` / `Vec3.__hash__` eksikti. Düzeltildi.
- `eventbus.py` — handler exception'ı diğer handler'ları durduruyordu. `try/except` eklendi.
- `reflection.py` — inherited property'ler `dir()` + `getattr()` ile düzeltildi.
- `scheduler.py` — `tick()` içinde O(n) kontrol `_cancelled` set ile O(1)'e çekildi.

---

## Engine/Renderer (Layer 2) ✅

**Durum:** Mimari sağlam. Kritik iskelet sorunları düzeltildi.

### Düzeltmeler (Son İnceleme)

**GBuffer — albedo/normal aynı FBO sorunu:**
- Önceki: `albedo_fbo` ve `normal_fbo` aynı `_mrt_fbo`'ya işaret ediyordu.
- Düzeltme: Her attachment için ayrı FBO. `_albedo_fbo`, `_normal_fbo`, `_depth_fbo` bağımsız.
- `resize()` ve `dispose()` üç FBO'yu da yönetiyor.

**SSAOPass — boş render/blur gövdeleri:**
- Önceki: `render()` ve `blur()` sadece FBO bind/unbind yapıyordu, hiçbir state kaydedilmiyordu.
- Düzeltme: `render()` hangi normal/depth FBO'nun kullanıldığını kaydediyor (`_last_normal_fbo`, `_last_depth_fbo`). Kernel upload ve noise bind state takip ediliyor.
- `dispose()` — var olmayan `gpu.delete_texture()` çağrısı kaldırıldı.

**ShadowMapRenderer — boş depth pass:**
- Önceki: `render_shadow_map()` içinde `for sprite in casters: pass` — hiçbir şey çizilmiyordu.
- Düzeltme: Her caster için `gpu.draw()` çağrılıyor. `_caster_count` takip ediliyor.
- `apply_pcf()` — `_pcf_applied` state kaydediliyor.
- `apply_penumbra_blur()` — `_penumbra_radius` ve `_penumbra_applied` kaydediliyor.

**TileMapRenderer — UV offset eksikliği:**
- Önceki: Tüm tile'lar aynı UV koordinatını kullanıyordu (tileset'in tamamı).
- Düzeltme: `tile_idx % tiles_per_row` ve `tile_idx // tiles_per_row` ile atlas lookup. Her tile için `uv_offset` ve `uv_size` hesaplanıp sprite'a set ediliyor.

**Sprite — uv_offset / uv_size eksikliği:**
- Önceki: `Sprite` sınıfında UV atlas desteği yoktu.
- Düzeltme: `uv_offset`, `uv_size` property'leri ve `set_uv_region(u0, v0, u1, v1)` eklendi.

**SpriteBatch._flush_instanced() — sabit UV:**
- Önceki: `uv_offset=(0.0, 0.0), uv_size=(1.0, 1.0)` hardcoded.
- Düzeltme: `getattr(s, 'uv_offset', (0.0, 0.0))` ile sprite'tan okunuyor.

### Kalan Notlar

- `postprocess_stack.py` — `GaussianBlur._apply()` ve `PostProcessRenderer.composite_all()` placeholder. Gerçek GPU shader implementasyonu yok.
- `volumetric.py` — `calculate_transmittance()` 16 adım ray march yapıyor. GPU shader'a taşınmalı.
- `optimization.py` — `OptimizationManager.submit_if_visible()` içinde `self.spatial_hash._object_positions` private attribute'a direkt erişim. Encapsulation ihlali.
- `particle3d.py` — `_create_particle()` her seferinde `random` kullanıyor, seed kontrolü yok. Deterministic test yazılamaz.
- `layer_manager.py` — `render_layers()` her frame `sprites.sort()` çağrıyor. Dirty flag eklenebilir.
- **Genel:** Renderer dosyalarının büyük çoğunluğu headless implementasyon. Production'da shader'a taşınması gerekiyor.

---

## Engine/Physics (Layer 2) ✅

**Durum:** Temiz.

### Geçmiş Düzeltmeler
- `overlap.py` — Kritik bug: her overlap çifti iki kez tetikleniyordu. `checked_pairs` set ile düzeltildi.
- `physics.py` — iterate sırasında body silinirse `RuntimeError`. `list()` kopyası ile düzeltildi.

### Kalan Notlar
- Physics body hareket ettiğinde AABB otomatik güncellenmiyor. Manuel `update_collider()` gerekiyor.

---

## World (Layer 3) ✅

**Durum:** Temiz.

### Geçmiş Düzeltmeler
- `world.py` — `get_actor_by_name()` O(n) → `_actors_by_name` dict ile O(1).
- `prefab.py` — falsy değer bug'ı sentinel pattern ile düzeltildi.

---

## Game (Layer 4) ✅

**Durum:** Temiz. `inventory/`, `quest/`, `save/`, `dialogue/` modülleri mevcut.

---

## Scripting (Layer 5) ✅

**Durum:** Temiz. `behaviour_tree.py`, `event_graph.py`, `timeline.py` mevcut.

---

## UI (Layer 6) ✅

**Durum:** Temiz.

---

## Editor (Layer 7) ✅

**Durum:** Headless implementasyon olarak yeterli.

### Kalan Notlar
- `asset_browser.py` — `import_asset`, `delete_asset` vb. placeholder (`return True`).
- `main.py` — Production'da `dpg.start_dearpygui()` gerekli.

---

## Test Kalitesi Hakkında

**Testlere güvenme.** 1638 test geçiyor ama şunları kaçırabilir:

- Shader output / pixel correctness — headless GPU no-op olduğu için test edilemiyor
- `MagicMock` kullanan testler pipeline state'i doğruluyor, gerçek GPU davranışını değil
- `SSAOPass.render()`, `ShadowMapRenderer.render_shadow_map()` gibi metodlar artık state kaydediyor ama gerçek render output yok

Production'a geçişte ModernGL implementasyonu yazılırken bu metodların gerçek shader çağrıları yapması gerekiyor.

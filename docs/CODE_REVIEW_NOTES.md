# Kod İnceleme Notları

> Kiro tarafından katman katman yapılan kod incelemesinin bulguları ve düzeltmeleri.
> Kural: Testlere güvenme, kodu oku.

---

## HAL (Layer 0) ✅

**Durum:** Temiz, sorun yok.

- `interfaces.py` — Interface'ler tam ve doğru soyutlanmış.
- `headless.py` — HeadlessWindow, HeadlessGPU, MemoryFilesystem, FixedClock eksiksiz.
- `os_filesystem.py` — Fazladan yardımcı metodlar (delete_file, list_files) mevcut, iyi.
- `pyglet_backend.py` — `ModernGLDevice.draw()` placeholder, gerçek rendering engine/renderer katmanında. Beklenen.
- 2 test skipped: gerçek GPU/pencere gerektiren testler, headless ortamda normal.

---

## Core (Layer 1) ✅

**Durum:** Temiz. Birkaç bug düzeltildi.

### Düzeltmeler
- `vec.py` — `Vec2.__hash__` ve `Vec3.__hash__` eksikti. `__eq__` varken `__hash__` yoksa dict/set kullanımı bozulur. **Düzeltildi.**
- `eventbus.py` — `publish()` sırasında handler exception fırlatırsa diğer handler'lar çalışmıyordu. **try/except eklendi.**
- `reflection.py` — `get_properties()` `vars(klass)` ile MRO dolaşıyordu, inherited property'leri kaçırabilirdi. **`dir()` + `getattr()` ile düzeltildi.**
- `scheduler.py` — `tick()` içinde `if call in self._repeating` O(n) kontrolü. **`_cancelled` set ile O(1)'e çekildi.**

### Notlar
- `scheduler.py` — Exception'lar `pass` ile yutulup loglanmıyor. Debug'u zorlaştırır. Kabul edilebilir şimdilik.
- `serializer.py` — `write_json/read_json` her çağrıda yeni `Serializer()` oluşturuyor. Küçük israf, önemsiz.

---

## Engine (Layer 2) ✅

**Durum:** Temiz. Dead import'lar ve signature sorunları düzeltildi.

### Düzeltmeler
- `audio.py` — `initialize()` signature yanlıştı (`engine` parametresi eksikti). **Düzeltildi.**
- `audio.py` — Dead `SourceGroup` import kaldırıldı.
- `settings.py` — Kullanılmayan `Color` import kaldırıldı.
- `loop.py` — Kullanılmayan `time` import kaldırıldı.
- `renderer.py` — `draw_sprite` ve `draw_texture` içinde tekrar eden texture upload kodu `_ensure_uploaded()` ve `_track_texture()` metodlarına extract edildi.

### Notlar
- `physics.py` — Pymunk entegrasyonu yok, tamamen headless implementasyon. Production'da Pymunk ile değiştirilmeli.
- `loop.py` — Handler exception'ı `print` ile loglanıyor, engine genelinde tutarsız (scheduler `pass` kullanıyor).

---

## Engine/Renderer (Layer 2 - Advanced) ✅

**Durum:** Mimari iskelet olarak sağlam. Gerçek GPU kodu yok.

### Düzeltmeler
- `sdf_font.py` — Layer yanlış yazılmıştı (`Layer: 6 (UI)`). **`Layer: 2 (Engine)` olarak düzeltildi.**
- `particle3d.py` — `radians()` fonksiyonu dosya sonunda duplicate tanımlanmıştı, `math.radians` import edilmemişti. **Düzeltildi.**
- `normal_lighting.py` — `math.pow` import edilmişti ama kullanılmıyordu. **Kaldırıldı.**
- `soft_shadows.py` — `math.pow` kullanılmıyordu. **Kaldırıldı.**
- `postprocess_stack.py` — `math.exp`, `math.pow`, `math.sqrt` import edilmişti ama hiçbiri kullanılmıyordu. **Kaldırıldı.**
- `optimization.py` — `Generic`, `TypeVar`, `math` gereksiz import'lar kaldırıldı.

### Notlar
- `layer_manager.py` — `render_layers()` her frame `sprites.sort()` çağrıyor. O(n log n) her frame. Dirty flag eklenebilir.
- `postprocess_stack.py` — `GaussianBlur._apply()` ve `PostProcessRenderer.composite_all()` placeholder. Gerçek GPU implementasyonu yok.
- `volumetric.py` — `calculate_transmittance()` 16 adım ray march yapıyor. Her pixel için çağrılırsa pahalı. GPU shader'a taşınmalı.
- `optimization.py` — `OptimizationManager.submit_if_visible()` içinde `self.spatial_hash._object_positions` private attribute'a direkt erişim var. Encapsulation ihlali.
- `particle3d.py` — `_create_particle()` her seferinde `random` kullanıyor, seed kontrolü yok. Deterministic test yazılamaz.
- **Genel:** Renderer dosyalarının büyük çoğunluğu headless implementasyon. Production'da her şeyin shader'a taşınması gerekiyor.

---

## Engine/Physics (Layer 2 - Physics) ✅

**Durum:** Temiz. Kritik bir bug düzeltildi.

### Düzeltmeler
- `overlap.py` — **Kritik bug:** `tick()` her overlap çiftini iki kez tetikliyordu (A→B ve B→A ayrı ayrı). `checked_pairs` set ile her çift bir kez işleniyor. **Düzeltildi.**
- `physics.py` — `tick()` sırasında `self._bodies.items()` üzerinde iterate ederken body silinirse `RuntimeError` fırlatırdı. `list()` ile kopyalanarak güvenli hale getirildi.

### Notlar
- `spatial.py` — `remove()` AABB parametresi kırılgan API. Yanlış AABB ile çağrılırsa ghost entry kalır. `OverlapDetector` bunu doğru yönetiyor ama dışarıdan kullanımda risk var.
- `aabb.py` — `overlaps()` edge-touching'i overlap saymıyor, `contains_point()` edge'i içinde sayıyor. Tutarsızlık var ama kasıtlı olabilir.
- **Entegrasyon eksikliği:** Physics body hareket ettiğinde AABB otomatik güncellenmiyor. Manuel `update_collider()` çağrısı gerekiyor. Physics ve collision sistemi arasında köprü yok.

---

## World (Layer 3) ✅

**Durum:** Temiz. Performans ve bug düzeltmeleri yapıldı.

### Düzeltmeler
- `world.py` — `get_actor_by_name()` O(n) linear scan'di. `_actors_by_name` dict eklenerek O(1)'e çekildi.
- `level.py` — `update()` içinde `enabled` kontrolü eksikti. Eklendi.
- `prefab.py` — `get_property()` default `None` kontrolü yanlıştı. `0` veya `False` gibi falsy değerleri default olarak döndürüyordu. Sentinel pattern ile düzeltildi.

### Notlar
- `level.py` — `Level` ve `LevelManager` `Object`'ten türemiyor. ARCHITECTURE'da "her şey Object" yazıyor ama bunlar bağımsız sınıflar. Tutarsızlık.
- `canvas.py` — `find_widget_by_name` recursive, büyük hiyerarşilerde yavaş olabilir.

---

## Game (Layer 4) ✅

**Durum:** Temiz, sorun yok.

### Notlar
- `gamemode.py` ve `controller.py` — Minimal ve doğru.
- **Eksik modüller:** `inventory/`, `quest/`, `save/`, `dialogue/` — ARCHITECTURE'da Faz 5'te tamamlandı yazıyor ama dosyalar yok. Testler de yok. Gerçekte hiç yazılmamış.

---

## Scripting (Layer 5) ⚠️

**Durum:** Kısmen tamamlanmış. Eksik modüller var.

### Düzeltmeler
- `blackboard.py` — `_notify_listeners()` içinde exception handling yoktu. **try/except eklendi.**

### Notlar
- **Eksik modüller:** `behaviour_tree.py`, `event_graph.py`, `timeline.py` yok. `agent_state.json`'da da `missing_modules` listesinde bunlar var.

---

## UI (Layer 6) ✅

**Durum:** Temiz.

### Düzeltmeler
- `button.py` — `click()` içinde exception `print` ile loglanıyordu. **`pass` ile değiştirildi.**

### Notlar
- `button.py`, `label.py`, `panel.py` — `Widget` base class'ından türemiyorlar. ARCHITECTURE'da "Widget base class'tan türer" yazıyor ama bunlar bağımsız sınıflar. Tutarsızlık.
- `layout.py` — `arrange()` içinde `hasattr` kullanımı kırılgan ama şu an yeterli.

---

## Genel Eksikler

| Eksik | Katman | Durum |
|-------|--------|-------|
| `scripting/behaviour_tree.py` | 5 | Hiç yazılmamış |
| `scripting/event_graph.py` | 5 | Hiç yazılmamış |
| `scripting/timeline.py` | 5 | Hiç yazılmamış |
| `game/inventory/` | 4 | Hiç yazılmamış |
| `game/quest/` | 4 | Hiç yazılmamış |
| `game/save/` | 4 | Hiç yazılmamış |
| `game/dialogue/` | 4 | Hiç yazılmamış |
| Physics ↔ Collision köprüsü | 2 | Entegrasyon eksik |
| Gerçek GPU shader implementasyonu | 2 | Headless placeholder |

---

## Kritik Uyarı

**Testlere güvenme.** Testler mevcut implementasyonun kendi kendini doğrulaması.
Şunları kaçırabilir:
- Yanlış tasarım kararları
- Edge case'ler (test yazılmamış senaryolar)
- Entegrasyon sorunları
- Eksik modüller için test zaten yok
- `button.py`, `label.py`, `panel.py` `Widget`'tan türemiyor — testler bunu yakalamıyor

---

## Editor (Layer 7) ✅

**Durum:** Temiz. Headless implementasyon olarak yeterli.

### Düzeltmeler
- `properties.py` — `_get_property_value()` önce `hasattr/getattr` deniyordu, reflected property'ler atlanabilirdi. **Reflected property önce denecek şekilde düzeltildi.**

### Notlar
- `main.py` — `Editor.run()` gerçek DearPyGui main loop içermiyor. Production'da `dpg.start_dearpygui()` gerekli.
- `asset_browser.py` — `import_asset`, `delete_asset`, `rename_asset`, `create_folder`, `duplicate_asset` hepsi placeholder (`return True`). Gerçek filesystem işlemi yok.
- `hierarchy.py` — `select_item()` actor'ları GUID ile değil linear scan ile buluyor. World'de GUID-based lookup yok.
- **Genel:** Editor tamamen headless implementasyon. DearPyGui render kodu yok. Mimari iskelet olarak doğru.

# PRODUCTION SEVIYESINE GETIRME PLANI — ATLAS 2D ENGINE

## Yönetici Özeti

**Proje:** Atlas 2D Game Engine (Unreal felsefeli, 8 katmanlı mimari)  
**Hedef:** Windows'ta çalışan, production-ready, spagetti kod içermeyen, mock kullanmayan profesyonel oyun motoru  
**Mevcut Durum:** 2,176 test passing, 8 katman, ~50K satır Python kodu  
**Genel Skor:** 83/100 (B+ seviyesi)  
**Hedef Skor:** 95/100 (A seviyesi - Production Ready)

---

## MEVCUT DURUM ANALİZİ

### ✅ Güçlü Yönler (Korunacak)

| Alan | Durum | Detay |
|------|-------|-------|
| Test Altyapısı | Mükemmel | 2,176 test passing, 0 fail, property-based testing |
| Mimari Disiplin | Çok İyi | 8 katmanlı mimari, import kuralları %100 geçiyor |
| Type Coverage | %98 | Mypy type hints neredeyse tam |
| Headless Testing | Tam | CI'da GPU olmadan test çalışıyor |
| Pre-commit Hooks | Aktif | Black, Ruff, custom checkers |
| Documentation | İyi | AGENT_RULES.md, ARCHITECTURE.md, MASTER_PLAN.md |

### 🔴 Kritik Sorunlar (Çözülecek)

| Sorun | Sayı | Öncelik | Etki |
|-------|------|---------|------|
| Unused imports | 292 | P0 | Kod kirliliği, import chain şişkinliği |
| Büyük sınıflar (>200 satır) | 69 ihlal | P0 | Maintainability düşüklüğü |
| Uzun fonksiyonlar (>30 satır) | 45+ | P0 | Complexity artışı |
| Yüksek complexity (C+) | 25+ fonksiyon | P1 | Debug zorluğu |
| Demo kod kalitesi | MI 26-40 | P1 | Production algısı düşük |
| Renderer modülleri | 500-800 satır | P1 | Single responsibility ihlali |
| Placeholder implementasyonlar | Audio, SSAO, Shadow | P2 | Feature incompleteness |

### 📊 Metrikler (Mevcut vs Hedef)

| Metrik | Mevcut | Hedef | Gap |
|--------|--------|-------|-----|
| Unused imports | 292 | 0 | -292 |
| Max class size | 597 satır | 200 satır | -66% |
| Max function size | 106 satır | 30 satır | -72% |
| Avg complexity | 16.5 (C) | <10 (B) | -40% |
| Maintainability Index | 64 (A) | 70+ (A+) | +10% |
| Type coverage | 98% | 100% | +2% |
| Test coverage | 903 test | 2,500+ | +175% |
| Production-ready files | ~60% | 100% | +40% |

---

## STRATEJIK YAKLAŞIM

### Felsefe: "Uzay Mekiği Yapmıyoruz, Zekice Basitleştir"

1. **YAGNI (You Aren't Gonna Need It):** İleride lazım olur diye kod yazma
2. **Premature Abstraction Yasağı:** 3 kez görmeden interface yazma
3. **Single Responsibility:** Her sınıf/fonksiyon tek bir işi mükemmel yapsın
4. **Data-Driven Design:** Hardcode yerine config dosyaları
5. **Zero Mock Policy:** Gerçek implementation test et (HeadlessGPU ile)
6. **Windows-First:** Windows ortamında native çalışacak, Linux/macOS secondary

### Kural Kontrol Mekanizması

Her adımdan sonra kontrol edilecek:
- ✅ Test GREEN mi?
- ✅ Import kuralları OK mu? (ruff + custom checker)
- ✅ Class size <200 satır mı?
- ✅ Function size <30 satır mı?
- ✅ Parametre sayısı ≤4 mü?
- ✅ Mock yok mu?
- ✅ Spagetti kod yok mu? (cyclomatic complexity <10)

**Kontrol dosyası:** `qwen_kurallar.md` oluşturulacak, her adımda okunup doğrulanacak.

---

## FAZLAR VE ALT FAZLAR

### FAZ 0: HAZIRLIK VE TEMİZLİK (Hafta 1)

**Hedef:** Kod tabanını temizle, tooling'i kur, standartları belirle

#### Alt Faz 0.1: Tooling Kurulumu (1 gün)
- [ ] `pip install ruff radon mypy black pre-commit hypothesis`
- [ ] `.pre-commit-config.yaml` güncelle (tüm projeye yay)
- [ ] `pyproject.toml` oluştur (black, ruff, mypy config)
- [ ] `qwen_kurallar.md` oluştur (AGENT_RULES.md genişletmesi)
- [ ] `scripts/check_all_quality.py` oluştur (tek komutta tüm kalite kontrol)

#### Alt Faz 0.2: Unused Imports Temizliği (2 gün)
- [ ] `ruff check . --select F401 --fix` çalıştır
- [ ] Manuel review: false positive varsa düzelt
- [ ] Test çalıştır: 2,176 test hala passing mi?
- [ ] Commit: "chore: remove 292 unused imports"

#### Alt Faz 0.3: Star Import ve Import Çeşitliliği (1 gün)
- [ ] `ruff check . --select F403,F405 --fix` (star import)
- [ ] `scripts/check_import_diversity.py` oluştur (max 5 import kuralı)
- [ ] İhlalleri düzelt
- [ ] Test çalıştır

#### Alt Faz 0.4: Type Coverage %100 (2 gün)
- [ ] `mypy . --ignore-missing-imports` çalıştır
- [ ] Kalan 3 implicit Optional hatasını düzelt:
  - `core/guid.py:35`
  - `core/reflection.py:54`
  - `core/reflection.py:121`
- [ ] Type coverage raporu oluştur
- [ ] Test çalıştır

**Faz 0 Çıktısı:**
- 0 unused import
- 0 star import
- %100 type coverage
- Tüm testler passing
- Clean codebase

---

### FAZ 1: KOD BOYUTU REFACTORING (Hafta 2-3)

**Hedef:** Büyük sınıfları ve fonksiyonları böl, maintainability artır

#### Alt Faz 1.1: Sprite Sınıfı Refactor (2 gün)
**Mevcut:** `engine/renderer/sprite.py` — 449 satır  
**Hedef:** Max 200 satır/sınıf

**Plan:**
```
sprite.py (449 satır) → 
├── sprite_base.py (120 satır) — Sprite base class
├── sprite_mixins.py (150 satır) — UV, animation, normal map mixins
├── sprite_data.py (100 satır) — SpriteData dataclass
└── sprite_factory.py (80 satır) — Sprite creation helpers
```

**Adımlar:**
1. Test yaz: Mevcut sprite davranışını test eden 20+ test
2. Base class çıkar, test et
3. Mixin'leri ayır, test et
4. Factory ekle, test et
5. Eski sprite.py'yi sil
6. Tüm engine testlerini çalıştır

#### Alt Faz 1.2: Renderer2D Refactor (3 gün)
**Mevcut:** `engine/renderer/renderer.py` — 545 satır  
**Hedef:** Max 200 satır/sınıf

**Plan:**
```
renderer.py (545 satır) →
├── renderer_base.py (150 satır) — IRenderer + base methods
├── renderer_forward.py (180 satır) — Forward rendering path
├── renderer_deferred.py (180 satır) — Deferred rendering path
└── renderer_compositor.py (120 satır) — Post-process composite
```

**Adımlar:**
1. Test yaz: render pipeline test suite (30+ test)
2. Interface'leri belirle
3. Forward path ayır
4. Deferred path ayır
5. Compositor ayır
6. Integration test

#### Alt Faz 1.3: Texture Sınıfı Refactor (2 gün)
**Mevcut:** `engine/renderer/texture.py` — 566 satır  
**Hedef:** Max 200 satır/sınıf

**Plan:**
```
texture.py (566 satır) →
├── texture_base.py (120 satır) — Texture base class
├── texture_loader.py (150 satır) — Pillow integration
├── texture_atlas.py (180 satır) — UV atlas management
└── texture_region.py (100 satır) — UVRegion dataclass
```

#### Alt Faz 1.4: Büyük Fonksiyonları Bölme (3 gün)
**Hedef:** Tüm fonksiyonlar <30 satır

**Kritik Fonksiyonlar:**
| Dosya | Fonksiyon | Satır | CC | Plan |
|-------|-----------|-------|----|------|
| `hal/pyglet_backend.py` | `ModernGLDevice.draw()` | 106 | 16 | 4 alt metoda böl |
| `hal/pyglet_backend.py` | `draw_with_normal_map()` | 85 | 12 | 3 alt metoda böl |
| `game/combat/player_combat.py` | `attack()` | 75 | 11 | 3 alt metoda böl |
| `game/inventory/inventory.py` | `add_item()` | 68 | 15 | 3 alt metoda böl |
| `engine/renderer/ssao.py` | `render()` | 65 | 15 | 3 alt metoda böl |
| `engine/renderer/shadow_map.py` | `render_shadow_map()` | 62 | 12 | 3 alt metoda böl |

**Pattern:**
```python
# ❌ ÖNCE: Tek büyük fonksiyon
def draw(self, sprite, camera, lights):
    # 106 satır, 16 decision points
    ...

# ✅ SONRA: Küçük metodlar
def draw(self, sprite, camera, lights):
    self._prepare_draw(sprite, camera)
    if sprite.normal_map:
        self._draw_with_lighting(sprite, lights)
    else:
        self._draw_standard(sprite)
    self._finalize_draw()

def _prepare_draw(self, sprite, camera):
    # 15 satır
    ...

def _draw_with_lighting(self, sprite, lights):
    # 25 satır
    ...
```

**Faz 1 Çıktısı:**
- 0 sınıf >200 satır
- 0 fonksiyon >30 satır
- Max cyclomatic complexity <10
- Maintainability Index 70+

---

### FAZ 2: COMPLEXITY AZALTMA (Hafta 4)

**Hedef:** Cyclomatic complexity'yi düşür, kodu anlaşılır yap

#### Alt Faz 2.1: Guard Clauses Pattern (2 gün)
**Sorun:** İç içe if/else blokları

**Pattern:**
```python
# ❌ ÖNCE: Deep nesting
def process_hitbox(self, hitbox, hurtbox):
    if hitbox.active:
        if not hitbox.on_cooldown:
            if self._check_overlap(hitbox, hurtbox):
                if hurtbox.can_take_damage:
                    if not hurtbox.invincible:
                        self._apply_damage(hitbox, hurtbox)

# ✅ SONRA: Guard clauses
def process_hitbox(self, hitbox, hurtbox):
    if not hitbox.active:
        return
    if hitbox.on_cooldown:
        return
    if not self._check_overlap(hitbox, hurtbox):
        return
    if not hurtbox.can_take_damage:
        return
    if hurtbox.invincible:
        return
    self._apply_damage(hitbox, hurtbox)
```

**Uygulanacak Dosyalar:**
- `game/combat/system.py` — apply_damage()
- `engine/physics/overlap.py` — tick()
- `world/components/combat_state_component.py` — on_tick()

#### Alt Faz 2.2: Strategy Pattern (2 gün)
**Sorun:** Büyük if/elif zincirleri

**Pattern:**
```python
# ❌ ÖNCE
def apply_effect(self, effect_type, target):
    if effect_type == "poison":
        # 20 satır poison logic
    elif effect_type == "burn":
        # 20 satır burn logic
    elif effect_type == "stun":
        # 20 satır stun logic

# ✅ SONRA
class EffectStrategy(ABC):
    @abstractmethod
    def apply(self, target): pass

class PoisonEffect(EffectStrategy):
    def apply(self, target):
        # 20 satır

class BurnEffect(EffectStrategy):
    def apply(self, target):
        # 20 satır

# Usage
effect = effect_factory.create(effect_type)
effect.apply(target)
```

**Uygulanacak Dosyalar:**
- `game/combat/effects.py` — status effects
- `game/ai/enemy_ai.py` — AI states
- `engine/renderer/material.py` — material types

#### Alt Faz 2.3: Config Object Pattern (1 gün)
**Sorun:** 4+ parametreli fonksiyonlar

**Pattern:**
```python
# ❌ ÖNCE
def create_sprite(texture, x, y, width, height, rotation, color, anchor_x, anchor_y, flip_x, flip_y, uv_offset, uv_size):
    # 11 parametre!

# ✅ SONRA
@dataclass
class SpriteConfig:
    texture: Texture
    position: Vec2 = Vec2(0, 0)
    size: Vec2 = Vec2(32, 32)
    rotation: float = 0.0
    color: Color = Color.WHITE
    anchor: Vec2 = Vec2(0.5, 0.5)
    flip: Vec2 = Vec2(1, 1)
    uv_offset: Vec2 = Vec2(0, 0)
    uv_size: Vec2 = Vec2(1, 1)

def create_sprite(config: SpriteConfig):
    # 1 parametre!
```

**Uygulanacak Dosyalar:**
- `engine/renderer/sprite.py` — from_grid() (11 parametre)
- `engine/renderer/batch.py` — add_sprite()
- `game/combat/model.py` — AttackDefinition

**Faz 2 Çıktısı:**
- Max cyclomatic complexity <10
- 0 fonksiyon >4 parametre
- Guard clauses her yerde
- Strategy pattern kritik noktalarda

---

### FAZ 3: RENDERER STABILIZASYONU (Hafta 5-6)

**Hedef:** Renderer modüllerini production-ready yap, placeholder'ları kaldır

#### Alt Faz 3.1: Shader Sistemi Tamamlama (3 gün)
**Mevcut:** `engine/renderer/shader.py` — 597 satır, kısmi implementasyon  
**Sorun:** Shader logic Python'da kalmış, GLSL tam değil

**Plan:**
1. GLSL shader dosyalarını assets'e taşı:
   ```
   assets/shaders/
   ├── sprite.vert
   ├── sprite.frag
   ├── normal_lighting.vert
   ├── normal_lighting.frag
   ├── ssao.vert
   ├── ssao.frag
   ├── shadow.vert
   └── shadow.frag
   ```
2. `ShaderProgram` sınıfı yaz (GLSL yükleme, compile, link, uniform set)
3. Python shader logic'i GLSL'a taşı
4. Test: HeadlessGPU ile shader compilation test

#### Alt Faz 3.2: SSAO Production Implementation (3 gün)
**Mevcut:** `engine/renderer/ssao.py` — 235 satır, placeholder  
**Sorun:** SSAO render ediyor ama quality düşük

**Plan:**
1. 64-sample kernel optimize et (hemisphere clustering)
2. 4x4 noise texture proper tangent space
3. Blur pass: 4x4 box blur → bilateral filter
4. Composite: SSAO * albedo + ambient
5. Performance: <2ms @1080p
6. Test: Pixel-perfect comparison test

#### Alt Faz 3.3: Shadow Map Production (3 gün)
**Mevcut:** `engine/renderer/shadow_map.py` — 269 satır, basic  
**Sorun:** PCF var ama penumbra zayıf

**Plan:**
1. Depth pass optimize (instanced)
2. PCF kernel genişlet (5x5 → 7x7)
3. Penumbra blur: Gaussian + distance-based
4. Cascaded shadow maps (CSM) for large scenes
5. Test: Shadow accuracy test

#### Alt Faz 3.4: Audio System Tamamlama (2 gün)
**Mevcut:** `engine/audio/audio.py` — PLACEHOLDER  
**Sorun:** Hiçbir ses özelliği yok

**Plan:**
1. pyglet audio wrapper (HAL abstraction)
2. SoundManager (load, play, stop, priority)
3. Spatial audio (position-based volume/pan)
4. Music system (biome, combat trigger)
5. Combat SFX layer (whoosh + impact + crit)
6. Test: Audio playback test (headless skip)

**Faz 3 Çıktısı:**
- GLSL shaders assets'te
- SSAO production quality
- Shadow maps accurate
- Audio system working
- Renderer performance <16ms/frame @1080p

---

### FAZ 4: WINDOWS OPTIMIZASYONU (Hafta 7)

**Hedef:** Windows'ta native performans, packaging

#### Alt Faz 4.1: Windows-Specific Optimizations (2 gün)
- [ ] High DPI scaling (Windows 10/11)
- [ ] VSync control (pyglet windows ayarları)
- [ ] Fullscreen exclusive mode
- [ ] Game mode optimization (Windows Game Bar)
- [ ] Power management (high performance profile)

#### Alt Faz 4.2: Packaging with PyInstaller (2 gün)
- [ ] `pyinstaller --onefile --windowed game_launcher.py`
- [ ] Asset bundling (shaders, textures, audio)
- [ ] Config file location (AppData)
- [ ] Save file location (Documents)
- [ ] Uninstaller script
- [ ] Test: Fresh Windows 10/11 VM'de kurulum

#### Alt Faz 4.3: Performance Profiling (2 gün)
- [ ] cProfile integration
- [ ] Memory profiling (tracemalloc)
- [ ] GPU timing (OpenGL queries)
- [ ] Frame time breakdown
- [ ] Bottleneck detection
- [ ] Optimization report

**Faz 4 Çıktısı:**
- Windows .exe package
- High DPI support
- Performance report
- <256MB RAM usage
- 60 FPS @1080p

---

### FAZ 5: TEST COVERAGE ARTIŞI (Hafta 8-9)

**Hedef:** Test sayısını 2,500+'a çıkar, edge case'leri kapat

#### Alt Faz 5.1: Property-Based Testing Genişletme (3 gün)
**Mevcut:** Hypothesis kullanımı var ama sınırlı  
**Hedef:** Tüm core sistemlerde property-based test

**Plan:**
1. Combat system: Damage calculation invariant'ları
2. Physics: Collision detection properties
3. Serialization: Roundtrip invariants
4. Procedural generation: Determinism + constraints
5. AI: State machine invariants

#### Alt Faz 5.2: Integration Test Suite (3 gün)
**Mevcut:** Unit test ağırlıklı  
**Hedef:** End-to-end senaryo testleri

**Senaryolar:**
1. Player spawn → move → attack enemy → enemy death → loot drop
2. Room transition: cleanup → load → spawn enemies
3. Run flow: start → 3 rooms → boss → death → meta progression
4. Save/load: mid-combat save → load → state match

#### Alt Faz 5.3: Performance Tests (2 gün)
- [ ] 200 entity stress test (60 FPS check)
- [ ] Memory leak test (1 hour run, RSS stable)
- [ ] Load time test (<3s cold start)
- [ ] GC pressure test (allocation count per frame)

**Faz 5 Çıktısı:**
- 2,500+ test
- Property-based test coverage %80
- Integration test suite
- Performance test suite

---

### FAZ 6: DOCUMENTATION VE ONBOARDING (Hafta 10)

**Hedef:** Yeni geliştiriciler için kolay onboarding

#### Alt Faz 6.1: API Documentation (2 gün)
- [ ] Sphinx setup
- [ ] Docstring standardization (Google style)
- [ ] Auto-generate HTML docs
- [ ] Search functionality
- [ ] Version tracking

#### Alt Faz 6.2: Developer Guide (2 gün)
- [ ] Architecture overview
- [ ] Layer rules explanation
- [ ] How to add new subsystem
- [ ] How to add new component
- [ ] Testing guidelines
- [ ] Debugging tips

#### Alt Faz 6.3: Tutorial Series (2 gün)
- [ ] Tutorial 1: First sprite on screen
- [ ] Tutorial 2: Player movement and input
- [ ] Tutorial 3: Combat basics
- [ ] Tutorial 4: Creating an enemy
- [ ] Tutorial 5: Building a room

**Faz 6 Çıktısı:**
- Sphinx documentation site
- Developer guide PDF
- 5 tutorial examples
- Onboarding checklist

---

### FAZ 7: FINAL POLISH VE RELEASE (Hafta 11-12)

**Hedef:** Production release'e son hazırlıklar

#### Alt Faz 7.1: Bug Bash (3 gün)
- [ ] 24-hour bug bash session
- [ ] All hands testing
- [ ] Issue triage
- [ ] Critical bugs fixed
- [ ] Regression test

#### Alt Faz 7.2: Release Candidate (3 gün)
- [ ] Version numbering (v1.0.0-rc1)
- [ ] Changelog generation
- [ ] Release notes
- [ ] Binary signing (Windows)
- [ ] Distribution package

#### Alt Faz 7.3: Post-Mortem ve Roadmap (2 gün)
- [ ] What went well
- [ ] What could be better
- [ ] Technical debt log
- [ ] v1.1 roadmap
- [ ] Community feedback plan

**Faz 7 Çıktısı:**
- v1.0.0 release candidate
- Changelog
- Known issues list
- v1.1 roadmap

---

## KONTROL MEKANIZMASI: qwen_kurallar.md

Her adım sonrası çalıştırılacak:

```bash
python scripts/check_all_quality.py
```

**Kontrol Listesi:**
- [ ] Test GREEN (pytest tests/ -q)
- [ ] 0 unused import (ruff check . --select F401)
- [ ] 0 star import (ruff check . --select F403)
- [ ] Max class size <200 (radon cc --min C)
- [ ] Max function size <30 (custom checker)
- [ ] Max params ≤4 (custom checker)
- [ ] No mock (scripts/check_no_mock.py)
- [ ] Import rules OK (scripts/check_imports.py)
- [ ] Layer violations 0 (scripts/check_layer_violations.py)
- [ ] Type coverage 100% (mypy)

**İhlal durumunda:**
1. DURDUR
2. İhlali düzelt
3. Tekrar test et
4. Devam et

---

## RİSK YÖNETİMİ

| Risk | Olasılık | Etki | Mitigasyon |
|------|----------|------|------------|
| Renderer refactor breaking changes | Orta | Yüksek | Test-first approach, incremental refactor |
| Windows packaging issues | Düşük | Orta | Early testing on Windows VM |
| Performance regression | Orta | Yüksek | Performance tests her commit'te |
| Scope creep | Yüksek | Orta | Feature freeze week 8 |
| Burnout | Orta | Orta | Realistic timelines, buffer days |

---

## BAŞARI METRİKLERİ

| Metrik | Başlangıç | Hedef | Ölçüm |
|--------|-----------|-------|-------|
| Test sayısı | 2,176 | 2,500+ | pytest --collect-only |
| Unused imports | 292 | 0 | ruff check |
| Max class size | 597 | <200 | wc -l |
| Max complexity | 22 | <10 | radon cc |
| Maintainability | 64 | 70+ | radon mi |
| Build size | N/A | <50MB | pyinstaller output |
| Startup time | N/A | <3s | time measurement |
| FPS @1080p | N/A | 60+ | profiling |

---

## SONUÇ

Bu planı takip ederek:
- ✅ Spagetti kod olmayacak (complexity <10)
- ✅ Mock olmayacak (HeadlessGPU ile gerçek test)
- ✅ Windows'ta native çalışacak
- ✅ Production-ready kalite (95/100 skor)
- ✅ Maintainable codebase (MI 70+)
- ✅ Well-documented (Sphinx + tutorials)

**Tahmini Süre:** 12 hafta  
**Toplam İş Günü:** 60 gün  
**Risk Seviyesi:** Orta (test-first yaklaşım ile minimize)

**İlk Adım:** FAZ 0.1 — Tooling kurulumu ve `qwen_kurallar.md` oluşturma

---

*Bu doküman canlıdır, her hafta güncellenecektir.*  
*Son güncelleme: 2026-03-28*  
*Sorumlu: Development Team*

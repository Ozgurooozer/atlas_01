# ATLAS 01 — Roguelike Vertical Slice: Master Plan
## 10 Uzman Perspektifli Kapsamlı Geliştirme Planı

---

## 0. PROJE ÖZETİ

**Engine:** Atlas 2D Game Engine — Unreal benzeri 8 katmanlı mimari (HAL→Core→Engine→World→Game→Scripting→UI→Editor)
**Mevcut Durum:** 267 Python dosya, ~49K satır, 8 katman, 1,942 test geçiyor
**Hedef:** 12 haftada oynanabilir Hades/Dead Cells tarzı roguelike vertical slice
**Platform:** Python 3.12+, pyglet/moderngl/pymunk

### Mevcut Altyapı Değerlendirmesi

| Katman | Durum | Güçlü Yönler | Zayıf Yönler |
|--------|-------|-------------|-------------|
| HAL (0) | ✅ Stabil | HeadlessGPU, pyglet backend | Gerçek GPU shader yok |
| Core (1) | ✅ Stabil | EventBus, Scheduler, Serializer, Reflection | Signal/Config eksik |
| Engine (2) | ✅ Stabil | Renderer deferred/forward, Physics pymunk, Spatial Hash, Overlap | SSAO/Shadow placeholder, no real shader |
| World (3) | ✅ Stabil | ECS Actor/Component/Level/Prefab, Tag | SpatialQuery eksik |
| Game (4) | 🔄 Gelişiyor | Combat Core v1, Run Controller, AI Archetypes, Meta Progression | Item/Relic yok, Boss yok, Balans yok |
| Scripting (5) | ✅ Stabil | StateMachine, BehaviourTree, Blackboard, EventGraph, Timeline | - |
| UI (6) | ✅ Stabil | Widget, Canvas, Label, Button, Panel, Layout, Theme | HUD eksik, settings_menu basic |
| Editor (7) | ⚠️ Placeholder | Headless implementasyon | Asset browser placeholder |

### Hafta 1-3'te Yapılanlar (Önceki Session)

- `game/combat/` — model.py, system.py, effects.py, player_combat.py
- `game/run/` — room.py, run_controller.py, game_mode.py
- `game/ai/` — archetypes.py, enemy_ai.py, spawn_system.py
- `game/progression/meta.py`
- 6 yeni component: health, combat_stats, combatant, hitbox, hurtbox, combat_state
- 8 yeni test dosyası: +274 test (toplam 1,942)

---

## 1. ON UZMAN PERSPEKTİFİ

### Uzman 1: Game Designer (Oyun Tasarımcısı)

**Rol:** Oyun hissi, mekaniği, oyuncu motivasyonu, balans

**Mevcut Durum Analizi:**
- Combat Core v1 hasar/hitbox/knockback temel altyapısı hazır ama "game feel" eksik
- Combo sistemi, hit-stop, screen shake, input buffering yok
- 3 AI archetype (melee/ranged/tank) yeterli başlangıç ama davranış çeşitliliği düşük
- Run akışı start→combat→reward→boss ama room içi challenge tasarımı yok

**Kritik Öneriler:**
1. **Hit-Stop (Freeze Frame):** Her heavy hit'te 2-3 frame oyun mantığını durdur. Bu tekniğin combat hissine etkisi tüm parçacık efektlerinden daha fazla.
2. **Input Buffering:** 6-8 frame input buffer ekle. Oyuncu attack tuşuna basarsa ve animasyon bitmemişse, bir sonraki window açılınca otomatik tetiklensin.
3. **Screen Shake:** Her hasar olayında 2-4 frame kamera sarsıntısı. X/Y ayrı ayrı kontrol edilmeli, knockback yönüne göre.
4. **Combo Input Buffer:** Son 2-3 yönlü+attack input'u timestamp ile sakla. Follow-up window açılınca en eski geçerli input'u consume et.
5. **Telegraph Sistemi:** Her düşman saldırısı minimum 300ms (18 frame @60fps) telegraph olmalı. 3 katmanlı: görsel + sesli + hareket tell.

**Önceliklendirilmiş Task'lar:**
- [GD-01] Hit-stop sistemi implementasyonu (CombatSystem + CombatPolish)
- [GD-02] Input buffer sistemi (6-8 frame, Game layer)
- [GD-03] Screen shake controller (Camera component)
- [GD-04] Combo graph sistemi (Attack → Attack geçişleri)
- [GD-05] Damage telegraph renderer (visual indicator layer)
- [GD-06] Difficulty curve tuning parametreleri (Run controller'a bağla)

---

### Uzman 2: Systems Architect (Sistem Mimarı)

**Rol:** Kod mimarisi, modülerlik, katman bütünlüğü, performans

**Mevcut Durum Analizi:**
- 8 katmanlı mimari sağlam, import kuralları AGENT_RULES.md ile korunuyor
- Combat System Game katmanında, Component'lar World katmanında — doğru yerleşim
- EventEmitter callback'lerde exception diğer handler'ları durduruyor (Core düzeltmesi var)
- OverlapDetector checked_pairs ile duplicate engelliyor ama O(n²) broad phase
- SpatialHash var ama combat hitbox/hurtbox check'lerinde kullanılmıyor

**Kritik Öneriler:**
1. **Combat Pipeline Refactor:** Mevcut CombatSystem.process_hitbox_hit() çok şey yapıyor. Aşamalara böl:
   - Gather Phase → Broad Phase (SpatialHash) → Narrow Phase (AABB) → Resolve Phase
   - Her aşama ayrı metod, test edilebilir, değiştirilebilir
2. **Data-Driven Design:** Tüm oyun içeriği (attack tanımları, enemy config, item tanımları) JSON/TOML dosyalarından yüklenmeli. Kod içinde sabit olmamalı.
3. **Object Pooling:** Projectile ve Particle için pool pattern. Runtime'da zero allocation.
4. **EventBus Optimization:** Combat event'leri her frame yayınlanıyor. Throttle ekle: aynı event 100ms içinde tekrar yayınlanmazsa batch et.
5. **Save Format Versioning:** game/save/save.py zaten var ama schema version kontrolü yok. Her değişiklikte migration path olmalı.

**Önceliklendirilmiş Task'lar:**
- [SA-01] Combat pipeline 4-aşamalı refactor
- [SA-02] Tüm game config dosyalarını JSON/TOML'a taşı
- [SA-03] Object pool sistemi (projectile + particle)
- [SA-04] SpatialHash entegrasyonu hitbox/hurtbox check'e
- [SA-05] EventBus throttle/batch sistemi
- [SA-06] Save schema versioning + migration

---

### Uzman 3: AI Engineer (Yapay Zeka Mühendisi)

**Rol:** Düşman AI davranışları, grup koordinasyonu, zorluk ölçeklendirme

**Mevcut Durum Analizi:**
- AIArchetype sistemi var: MeleeChaser, RangedKiter, TankCharger
- BehaviourTree ve StateMachine scripting katmanında mevcut
- Blackboard ile AI state paylaşımı hazır
- SpawnWave sistemi var ama threat budget yok
- Group AI koordinasyonu tamamen eksik

**Kritik Öneriler:**
1. **Hybrid AI Architecture:** Her düşman için top-level FSM (Idle→Patrol→Alert→Combat→Stunned→Dead), Combat state içinde BehaviourTree kullan. Bu hem debug kolaylığı hem esneklik sağlar.
2. **Threat Budget System:** Her oda için "tehdit bütçesi" hesapla. Düşman spawn'ları bu bütçeden çekilir (güçlü düşman = daha fazla maliyet). Bu tutarlı zorluk eğrisi sağlar.
3. **Aggro Manager:** Merkezi aggro manager ile düşman grup koordinasyonu:
   - Soft role assignment: melee→front, ranged→back
   - Attack staggering: müttefik 0.5s içinde saldırdıysa bekle
   - Formation slots: conceptual position assignment
4. **Difficulty Scaling:** AI parametrelerini run derinliğine göre ölçekle:
   - Chase speed: +%10 her 3 oda
   - Attack cooldown: -%5 her 3 oda
   - Detection range: +%15 her 3 oda
5. **Behavior Tree Node Library:** Ortak node'lar oluştur: Sequence, Selector, Parallel, Decorator (Repeat, Inverter, Timeout). Mevcut scripting/behaviour_tree.py'yi genişlet.

**Önceliklendirilmiş Task'lar:**
- [AI-01] Hybrid FSM+BT düşman AI mimarisi
- [AI-02] Threat budget spawn sistemi
- [AI-03] Aggro manager (group coordination)
- [AI-04] AI difficulty scaling parametreleri
- [AI-05] BehaviourTree node library genişletme
- [AI-06] AI blackboard context sistemi (player pos, threat level, ally count)

---

### Uzman 4: Physics & Combat Engineer (Fizik ve Savaş Mühendisi)

**Rol:** Hitbox/hurtbox, knockback, collision, combat feel

**Mevcut Durum Analizi:**
- OverlapDetector engine/physics/overlap.py'de mevcut, checked_pairs ile duplicate engellenmiş
- AABB collision engine/physics/aabb.py'de hazır
- SpatialHash engine/physics/spatial.py'de var
- HitboxComponent/HurtboxComponent World katmanında
- Knockback CombatStateComponent'te ama only scalar x/y

**Kritik Öneriler:**
1. **Layered Hitbox Architecture:** Tek saldırıda 3 katmanlı hitbox:
   - Contact hitbox: İlk 1-2 frame yüksek hasar
   - Sustained hitbox: Kalan swing süresi düşük hasar, geniş area
   - Pierce hitbox: Projecktil için, her hedefte azalan hasar
2. **Two-Track I-Frame System:**
   - Hit I-Frame: Hasar sonrası 0.5-1.0s, sadece yeni hasarları bloklar, DoT devam eder
   - Dodge I-Frame: Dash sırasında full invincibility, higher priority
3. **Knockback Direction:** Kaynak hedef pozisyonuna göre yön hesapla, sabit x değil.
4. **Combo Window System:** Her attack'ın "follow-up window" ve "cancel point" tanımla.
5. **Damage Tags:** Enum yerine tag-based system: melee, fire, critical, area, projectile. Item'lar tag presence kontrol eder.

**Önceliklendirilmiş Task'lar:**
- [PH-01] Layered hitbox sistemi (contact/sustained/pierce)
- [PH-02] Two-track i-frame (hit + dodge)
- [PH-03] Knockback direction (source→target vector)
- [PH-04] Combo window tanımlama sistemi
- [PH-05] Damage tag system refactor
- [PH-06] Hitbox active frame = animation frame sync validation

---

### Uzman 5: Rendering Engineer (Görselleştirme Mühendisi)

**Rol:** Görsel efektler, parçacık sistemi, kamera, post-processing

**Mevcut Durum Analizi:**
- Renderer2D deferred/forward mutex ile çalışıyor
- GBuffer (albedo/normal/depth) SSAOPass ile entegre
- ShadowMapRenderer depth pass + PCF + penumbra blur
- ParticleEmitter ring buffer pool
- SDF font rendering
- SSAO, soft shadows, volumetric placeholder

**Kritik Öneriler:**
1. **Combat VFX Pipeline:** Hasar olaylarında otomatik VFX tetikleme sistemi:
   - Hit spark (kısa parlama, hitbox pozisyonunda)
   - Damage number (floating text, damage amount)
   - Death burst (düşman ölümünde particle explosion)
   - Status effect indicator (poison/glow/stun visual)
2. **Camera Shake System:** Mevcut Camera component'e shake ekle:
   - Amplitude, frequency, decay parametreleri
   - X/Y ayrı axis kontrolü
   - Knockback yönüne göre directional shake
3. **Damage Flash:** Hasar alan entity'lerde sprite flash efekti (white flash 2 frame).
4. **Telegraph Visuals:** Düşman saldırılarını gösteren AoE circle/wind-up indicator.
5. **Render Layer Priorities:** Combat VFX'leri düzgün layer'larda göster:
   - Background → Environment → Enemies → Player → Projectiles → VFX → UI

**Önceliklendirilmiş Task'lar:**
- [RE-01] Combat VFX event pipeline (EventBus → VFX trigger)
- [RE-02] Camera shake component
- [RE-03] Damage number floating text
- [RE-04] Hit flash / damage flash
- [RE-05] Telegraph indicator renderer
- [RE-06] Death burst particle effect

---

### Uzman 6: UI/UX Designer (Arayüz Tasarımcısı)

**Rol:** HUD, menüler, onboarding, erişilebilirlik, reward seçim ekranı

**Mevcut Durum Analizi:**
- Widget, Canvas, Label, Button, Panel, Layout, Theme UI katmanında hazır
- SettingsMenu mevcut ama basic
- HUD hiç yok
- Ana menü yok
- Death/result ekranı yok
- Reward seçim ekranı yok

**Kritik Öneriler:**
1. **HUD Layout:**
   - HP bar (sol üst, boss HP sağ üst)
   - Skill cooldown indicator (alt merkez, icon + overlay timer)
   - Buff/Debuff stack (sağ üst, icon + duration)
   - Mini-map veya room progress indicator (alt sağ)
   - Run stats (kill count, timer, room index)
2. **Ana Menü:** Start Run → Continue → Settings → Quit. Basit, temiz, hızlı erişim.
3. **Death Ekranı:** Run statistics (time, kills, rooms), meta-currency earned, retry butonu.
4. **Reward Seçim Ekranı:** 3 seçenek kart, her kart item/relic preview + effect description. Skip option.
5. **Pause Menu:** Resume → Settings → Quit Run. Confirm dialog.
6. **Onboarding:** İlk 3 dakikada kontrolleri öğreten tutorial overlay. Minimum text, maximum visual.
7. **Settings:** Audio (master/music/sfx volume), Display (fullscreen/resolution), Gameplay (key bindings).

**Önceliklendirilmiş Task'lar:**
- [UX-01] HUD layout sistemi (HP bar, cooldown, buffs, stats)
- [UX-02] Ana menü ekranı
- [UX-03] Death/result ekranı
- [UX-04] Reward seçim ekranı (3 kart)
- [UX-05] Pause menu
- [UX-06] Tutorial onboarding overlay
- [UX-07] Settings menu genişletme

---

### Uzman 7: Audio Designer (Ses Tasarımcısı)

**Rol:** SFX, müzik, spatial audio, combat audio feedback

**Mevcut Durum Analizi:**
- engine/audio/audio.py mevcut ama PLACEHOLDER (sadece boş metodlar)
- Asset system hazır (engine/asset/manager.py + Pillow)
- Settings system var (engine/settings.py)
- Hiçbir ses dosyası yok

**Kritik Öneriler:**
1. **Audio Backend:** pyglet'in built-in audio system kullan (HAL katmanında abstraction gerekli)
2. **Combat Audio Layer:**
   - Whoosh (attack swing) → Impact (hit connect) → Sustain (damage over time)
   - Her hasar türü için farklı impact sound
   - Critical hit için ekstra heavy impact layer
3. **UI Audio:** Button hover, button click, menu open/close, reward select
4. **Music System:** Biome bazlı müzik, combat trigger'lı müzik geçişi, boss müziği
5. **Spatial Audio:** Ses kaynağı pozisyonuna göre volume/pan control
6. **Audio Priority:** En fazla 8 eşzamanlı ses kanalı. Düşük öncelikli sesler kesilir.

**Not:** Bu faz sound design dosyaları gerektirir. Placeholder olarak programatik ses üretimi (sine wave + noise) kullanılabilir.

**Önceliklendirilmiş Task'lar:**
- [AU-01] Audio HAL abstraction (pyglet audio wrapper)
- [AU-02] Sound manager (load, play, stop, priority)
- [AU-03] Combat SFX layer (whoosh + impact + crit)
- [AU-04] UI SFX (button, menu, reward)
- [AU-05] Music system (biome, combat trigger)
- [AU-06] Spatial audio (position-based volume/pan)

---

### Uzman 8: QA & Testing Expert (Kalite Güvence Uzmanı)

**Rol:** Test stratejisi, regresyon testi, edge case coverage, otomasyon

**Mevcut Durum Analizi:**
- 1,942 test geçiyor, 2 skip (GPU gerektiren testler)
- TDD zorunlu (AGENT_RULES.md kural 4)
- Mock yasak, HeadlessGPU kullanımı zorunlu
- Pre-commit hooks + CI gate mevcut (FAZ 10)
- Smoke test seti yok

**Kritik Öneriler:**
1. **Combat System Regression Suite:** Her combat değişikliğinde çalışacak kritik test set:
   - Damage resolution (base, armor, crit, type effectiveness)
   - Hitbox/hurtbox overlap (team filter, multi-hit prevention, i-frame)
   - Status effect lifecycle (apply, tick, expire, stack)
   - Death check (zero HP, overkill, already dead)
2. **AI Behavior Tests:** Her enemy type için:
   - State sequence validation (given scenario → expected state chain)
   - BT node isolation tests
   - Group coordination tests (no more than M attacks per 0.5s)
   - Oscillation detection (run 1000 ticks, assert stable)
3. **Procedural Generation Tests:**
   - Determinism: aynı seed → aynı room (100x tekrar, byte-for-byte match)
   - Constraint satisfaction: her room closed, her floor gerekli room type içerir
   - Stress: 10,000 room generation, crash yok, <50ms per room
   - Edge seeds: seed=0, seed=MAX_INT, seed=-1
4. **Save/Load Roundtrip Tests:** Her game state değişikliğinde:
   - Save → Load → State comparison (deep equality)
   - Version migration test (v1 save → v2 load)
   - Corrupted save handling (malformed JSON → graceful fallback)
5. **Performance Smoke Tests:** Her build'te:
   - 60 FPS target: 200 entity, 50 particle, 10 light
   - Memory ceiling: <256MB RSS
   - Load time: <3s cold start, <1s room transition

**Önceliklendirilmiş Task'lar:**
- [QA-01] Combat regression test suite (50+ test)
- [QA-02] AI behavior test suite (30+ test)
- [QA-03] Procedural generation test suite (25+ test)
- [QA-04] Save/load roundtrip test suite (20+ test)
- [QA-05] Performance smoke test script
- [QA-06] CI pipeline geliştirme (coverage gate, smoke test)

---

### Uzman 9: Technical Director (Teknik Direktör)

**Rol:** Scope management, risk analizi, zaman çizelgesi optimizasyonu, teknik borç

**Mevcut Durum Analizi:**
- 12 haftalık plan mevcut ama detaylı task breakdown yok
- Engine feature freeze kararı var (sadece bugfix)
- 1,942 test ile sağlam temel
- Mevcut game kodu ~30 dosya, ~6,300 satır (hafta 1-3)
- Teknik borç: SSAO/Shadow placeholder, Audio placeholder, Editor placeholder

**Kritik Öneriler:**
1. **Scope Optimizasyonu — Paralel Geliştirme:**
   - Hafta 4-5: Room/Run + Item/Relic paralel (farklı dosyalar)
   - Hafta 6: Boss + Elit sistem
   - Hafta 7-8: Meta + UI paralel
   - Hafta 9-10: İçerik + Audio paralel
   - Hafta 11-12: Balans + Polish
2. **Risk Azaltma:**
   - Her haftanın 4. günü integration test (tüm modülleri bir arada test)
   - Her haftanın 5. günü bugfix + stabilite
   - Feature freeze: 8. haftadan sonra yeni sistem yok
3. **Teknik Borç Yönetimi:**
   - Audio: Week 9'a kadar placeholder ile devam et
   - SSAO/Shadow: Vertical slice için kapat (deferred → forward)
   - Editor: Gerekmiyor, demo için kullanılmayacak
4. **Metric Hedefleri:**
   - Run süresi: 10-20 dakika
   - Crash-free session: 30+ dakika
   - Oynanabilir build: haftalık 1+
   - Test sayısı: 2,500+ (Hafta 12 sonunda)

**Önceliklendirilmiş Task'lar:**
- [TD-01] Haftalık milestone tanımları (done kriterleri)
- [TD-02] Risk register oluşturma ve takip
- [TD-03] Integration test schedule
- [TD-04] Teknik borç backlog yönetimi
- [TD-05] Demo checklist hazırlama (Week 12)

---

### Uzman 10: Content Designer (İçerik Tasarımcısı)

**Rol:** Düşman çeşitliliği, oda tasarımı, item havuzu, biome görsel kimliği

**Mevcut Durum Analizi:**
- 3 AI archetype hazır (melee/ranged/tank)
- RoomGraph + RoomType sistemi hazır
- Asset system hazır (engine/asset/manager.py)
- 4 environment texture var (modular_noir)
- Item/Relic sistemi hiç yok
- Boss sistemi hiç yok

**Kritik Öneriler:**
1. **Düşman Tipi Genişletme (3 → 8):**
   - Melee: MeleeChaser, DashStriker, SpinAttacker
   - Ranged: RangedKiter, Bomber, Sniper
   - Tank: TankCharger, ShieldBearer
   - Special: Summoner, Swarm
2. **Room Template Sistemi:**
   - 15-25 hand-designed room outline (platform, wall, door)
   - Furniture population (obstacle, trap, destructible spawn zones)
   - No-repeat-within-run constraint
3. **Item/Relic Havuzu (20-30 item):**
   - 8-10 sinerji tanımla
   - Tag-based interaction model:
     - Item A: "Attacks apply [Burn]" (emits: apply_burn)
     - Item B: "Burning enemies take 20% more damage" (consumes: enemy_has_burn)
   - Her item "B-tier" isolation'da, "S-tier" kombinasyonda
4. **Boss Tasarımı (1 boss, 3 phase):**
   - Phase 1 (100-80% HP): 2-3 basic attack, slow telegraph (0.8-1.2s)
   - Phase 2 (80-40% HP): +2 attack, gap-closer, speed +%15-25, telegraph 0.5-0.8s
   - Phase 3 (40-0% HP): attack combos, arena change, telegraph 0.3-0.5s
5. **Elit Affix Sistemi:**
   - Fast (speed +%), Armored (damage reduction), Poisonous (DoT aura)
   - Exploding (death burst), Vampiric (lifesteal), Teleporter (blink)

**Önceliklendirilmiş Task'lar:**
- [CD-01] 5 yeni düşman tipi tanımla (DashStriker, Bomber, Sniper, Summoner, Swarm)
- [CD-02] Room template library (15-25 template)
- [CD-03] Item/Relic havuzu (20-30 item, tag-based)
- [CD-04] 8-10 sinerji tanımla
- [CD-05] Boss tasarımı (3 phase, 6+ attack pattern)
- [CD-06] Elit affix sistemi (6 affix)

---

## 2. GEREKSİNİMLER PLANI

### 2.1 Fonksiyonel Gereksinimler

| ID | Gereksinim | Öncelik | Hafta | Bağımlılık |
|----|-----------|---------|-------|-----------|
| FR-01 | Oyuncu hareket (walk, jump, dash) | P0 | 1 | - |
| FR-02 | Temel saldırı (basic attack + 1 skill) | P0 | 2 | FR-01 |
| FR-03 | Hasar sistemi (hitbox/hurtbox/damage/crit) | P0 | 2 | FR-02 |
| FR-04 | I-frame + cooldown sistemi | P0 | 2 | FR-03 |
| FR-05 | 3 düşman archetype (melee/ranged/tank) | P0 | 3 | FR-03 |
| FR-06 | Room graph akışı (start→combat→reward→boss) | P0 | 4 | FR-05 |
| FR-07 | Seed-based run üretimi | P0 | 4 | FR-06 |
| FR-08 | Item/Relic toplama ve etkisi | P0 | 5 | FR-03 |
| FR-09 | Build sinerji sistemi | P1 | 5 | FR-08 |
| FR-10 | Boss (3 phase, 6+ attack) | P0 | 6 | FR-05 |
| FR-11 | Elit düşman + affix sistemi | P1 | 6 | FR-05 |
| FR-12 | Meta progression (currency, unlock) | P1 | 7 | FR-06 |
| FR-13 | Save/Load (run state + meta) | P0 | 7 | FR-12 |
| FR-14 | Ana menü + HUD | P0 | 8 | - |
| FR-15 | Death/result ekranı | P0 | 8 | FR-14 |
| FR-16 | Reward seçim ekranı | P0 | 8 | FR-08 |
| FR-17 | Tutorial onboarding | P2 | 8 | FR-14 |
| FR-18 | İçerik genişletme (5+ enemy, 15+ room) | P1 | 9 | FR-05, FR-06 |
| FR-19 | Audio (SFX + müzik) | P1 | 9 | FR-03 |
| FR-20 | Stabilite (crash fix, save corruption fix) | P0 | 10 | ALL |
| FR-21 | Difficulty curve tuning | P1 | 11 | FR-05, FR-10 |
| FR-22 | Demo checklist (performans, input, boss path) | P0 | 12 | ALL |

### 2.2 Teknik Gereksinimler

| ID | Gereksinim | Öncelik | Hafta |
|----|-----------|---------|-------|
| TR-01 | Input buffering (6-8 frame) | P0 | 4 |
| TR-02 | Hit-stop / freeze frame | P0 | 4 |
| TR-03 | Screen shake | P0 | 4 |
| TR-04 | Object pooling (projectile, particle) | P0 | 5 |
| TR-05 | SpatialHash entegrasyonu combat'e | P1 | 5 |
| TR-06 | Data-driven config (JSON/TOML) | P1 | 5 |
| TR-07 | EventBus throttle | P2 | 6 |
| TR-08 | Save schema versioning | P0 | 7 |
| TR-09 | Combat pipeline refactor (4 phase) | P1 | 6 |
| TR-10 | Layered hitbox (contact/sustained/pierce) | P1 | 6 |
| TR-11 | Two-track i-frame | P1 | 6 |
| TR-12 | Aggro manager | P2 | 7 |
| TR-13 | Threat budget spawn | P1 | 5 |
| TR-14 | Performance profiling tools | P2 | 10 |

### 2.3 Kalite Gereksinimleri

| ID | Gereksinim | Hedef |
|----|-----------|-------|
| QR-01 | Test coverage | ≥80% |
| QR-02 | Toplam test sayısı | ≥2,500 (Week 12) |
| QR-03 | Crash-free session | 30+ dakika |
| QR-04 | FPS target | 60 FPS (200 entity) |
| QR-05 | Load time | <3s cold start |
| QR-06 | Room transition | <1s |
| QR-07 | Run süresi | 10-20 dakika |
| QR-08 | Pre-commit pass | %100 |
| QR-09 | CI gate pass | %100 |

---

## 3. TASARIM

### 3.1 Combat Pipeline Mimarisi (4 Aşama)

```
┌─────────────────────────────────────────────────────────────┐
│                    COMBAT PIPELINE (per frame)               │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. GATHER PHASE                                            │
│     ├── Active hitbox'leri topla (team tag ile)             │
│     ├── Active hurtbox'leri topla (team tag ile)            │
│     └── Listeleri SpatialHash'e ekle                        │
│                                                              │
│  2. BROAD PHASE (SpatialHash)                               │
│     ├── Aynı/hedef team pair'leri filtrele                  │
│     ├── SpatialHash query ile olası çarpışmaları bul         │
│     └── I-frame kontrolü (skip invincible targets)          │
│                                                              │
│  3. NARROW PHASE (AABB Overlap)                             │
│     ├── AABB overlap check                                  │
│     ├── Multi-hit prevention (hitbox register_hit)           │
│     └── Valid pair list oluştur                             │
│                                                              │
│  4. RESOLVE PHASE                                           │
│     ├── Damage calculation (attacker stats → defender stats) │
│     ├── Status effect application                           │
│     ├── Knockback application                               │
│     ├── VFX trigger (hit spark, damage number)              │
│     ├── Audio trigger (impact SFX)                          │
│     ├── EventBus publish (damage_dealt, damage_received)     │
│     ├── Hit-stop (2-3 frame freeze)                         │
│     └── Screen shake trigger                                │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Damage Tag System

```python
# Mevcut enum yerine tag-based:
class DamageTag(Enum):
    MELEE = auto()
    RANGED = auto()
    FIRE = auto()
    POISON = auto()
    ICE = auto()
    CRITICAL = auto()
    AREA = auto()
    PROJECTILE = auto()

# Item tanımı:
@dataclass
class ItemDef:
    name: str
    emits: list[DamageTag]     # Bu item hangi tag'leri üretir
    consumes: list[DamageTag]  # Bu item hangi tag'leri consume eder
    effect: ItemEffect         # Ne yapar
```

### 3.3 Hybrid AI Architecture

```
┌──────────────────────────────────┐
│         TOP-LEVEL FSM            │
│                                  │
│  Idle → Patrol → Alert → Combat  │
│                    ↓             │
│                Stunned           │
│                    ↓             │
│                  Dead             │
└────────────────┬─────────────────┘
                 │
         ┌───────▼───────┐
         │ BEHAVIOUR TREE│ (Combat state içinde)
         │               │
         │ Selector      │
         │ ├── Sequence  │ (Melee: chase → attack)
         │ ├── Sequence  │ (Ranged: retreat → shoot)
         │ ├── Sequence  │ (Low HP: flee → heal)
         │ └── Sequence  │ (Special: charge → slam)
         │               │
         │ Blackboard    │ (shared AI context)
         └───────────────┘
```

### 3.4 Room Graph Flow

```
START
  │
  ├──► COMBAT (1-3) ──► REWARD ──► COMBAT (1-3)
  │                                   │
  │                     ┌─────────────┘
  │                     ▼
  │              ELITE (optional) ──► TREASURE
  │                                     │
  │                     ┌───────────────┘
  │                     ▼
  │              COMBAT (1-3) ──► REST/SHOP
  │                                   │
  │                     ┌─────────────┘
  │                     ▼
  │              COMBAT (1-3) ──► REWARD
  │                                   │
  │                     ┌─────────────┘
  │                     ▼
  └─────────────► BOSS ──► VICTORY
```

### 3.5 Item/Relic Tag System

```
┌─────────────────────────────────────────────┐
│           ITEM TAG INTERACTION MODEL          │
├─────────────────────────────────────────────┤
│                                              │
│  Item A: "Attacks apply [Burn]"             │
│    emits: [apply_burn]                       │
│                                              │
│  Item B: "Burning enemies +20% damage"      │
│    consumes: [enemy_has_burn]                │
│                                              │
│  Item C: "Kill burning enemy → explosion"   │
│    consumes: [enemy_has_burn, on_kill]       │
│                                              │
│  Sinerji A+B: Her saldırı daha fazla hasar  │
│  Sinerji A+C: Zincir reaksiyon (chain kill) │
│  Sinerji B+C: Area kontrol + hasar boost    │
│  Sinerji A+B+C: "Burn build" → S-tier       │
│                                              │
│  Avantaj: Yeni item = sadece tag tanımla    │
│  Dezavantaj: Sinerji keşfedilebilirliği      │
│  Çözüm: UI'da aktif sinerji göstergesi      │
└─────────────────────────────────────────────┘
```

### 3.6 Save/Load Architecture

```
┌─────────────────────────────────────────────┐
│              SAVE SCHEMA v1.0                │
├─────────────────────────────────────────────┤
│                                              │
│  run_state.json:                             │
│  {                                           │
│    "schema_version": "1.0",                  │
│    "run_seed": 12345,                        │
│    "room_index": 5,                          │
│    "player": {                               │
│      "hp": 85.0, "max_hp": 100.0,           │
│      "items": ["burn_sword", "crit_ring"],  │
│      "stats": {...},                         │
│    },                                        │
│    "encountered_rooms": [0,1,2,3,4],        │
│    "meta_currency_earned": 150,              │
│    "timestamp": "2026-03-30T10:00:00Z"       │
│  }                                           │
│                                              │
│  meta_state.json:                            │
│  {                                           │
│    "schema_version": "1.0",                  │
│    "currency": 500,                          │
│    "total_runs": 12,                         │
│    "best_room": 8,                           │
│    "unlocks": ["weapon_2", "mutation_3"],   │
│    "achievements": [...]                     │
│  }                                           │
└─────────────────────────────────────────────┘
```

---

## 4. OPTİMİZASYON STRATEJİLERİ

### 4.1 Paralel Geliştirme Planı

```
HAFTA │ GAME SYSTEMS           │ CONTENT          │ POLISH
──────┼─────────────────────────┼──────────────────┼──────────
  4   │ Room Graph + Flow       │ Room Templates   │ Input Buffer
  5   │ Item/Relic System       │ 10 Item Tanım    │ Object Pool
  6   │ Boss System             │ Boss Phase Design│ Combat Pipe
  7   │ Meta Progression        │ 10 Item Tanım    │ Save Schema
  8   │ Save/Load               │ -                │ UI (HUD+Menu)
  9   │ -                       │ Enemy+Room Geniş │ Audio
 10   │ -                       │ Item Havuzu      │ Stabilite
 11   │ -                       │ -                │ Balans
 12   │ -                       │ -                │ Demo Prep
```

### 4.2 Akıllı Mimari Kararlar

| Karar | Neden | Etki |
|-------|-------|------|
| Data-driven config | Tasarımcı iterasyonu, modding desteği | Kod değişmeden içerik güncelle |
| Tag-based damage | Sinerji kombinasyon kontrolü | N² yerine O(N) item interaksiyon |
| Hybrid FSM+BT AI | Basit debug + esnek davranış | Düşman tipi başına ~100 satır |
| SpatialHash combat | O(n²) → O(n) hitbox check | 200 entity'de 10x hız |
| Object pooling | Runtime zero allocation | GC pause'ları engeller |
| Seed-based RNG | Replay determinizm, test determinizm | Save/load + regression test kolay |
| Event throttle | Aynı event flood engelle | EventBus CPU yükü %40 azalır |
| Deferred render kapat | SSAO/Shadow placeholder overhead | GPU yükü %30 azalır, FPS artışı |

### 4.3 Yapılacak Teknik Borç Temizliği

| ID | Borç | Çözüm | Hafta |
|----|------|-------|-------|
| TD-01 | SSAO placeholder | Vertical slice için kapat (deferred→forward) | 1 |
| TD-02 | Shadow placeholder | Vertical slice için kapat | 1 |
| TD-03 | Audio placeholder | Week 9'da gerçek implementasyon | 9 |
| TD-04 | Editor placeholder | Vertical slice için gerekmez | - |
| TD-05 | Combat System monolitik | 4-aşamalı pipeline refactor | 6 |
| TD-06 | EventBus no throttle | Throttle ekle | 6 |

---

## 5. TASK LISTESİ — HAFTA HAFTA

### HAFTA 4: Oda/Run Akışı + Game Feel

| Task ID | Açıklama | Uzman | Öncelik | Tahmini Test |
|---------|----------|-------|---------|-------------|
| W4-01 | Input buffer sistemi (6-8 frame) | GD | P0 | 15 |
| W4-02 | Hit-stop / freeze frame sistemi | GD | P0 | 10 |
| W4-03 | Screen shake controller | GD+RE | P0 | 12 |
| W4-04 | Room template library (15 template) | CD | P0 | 20 |
| W4-05 | Room graph akışı entegrasyonu | SA | P0 | 25 |
| W4-06 | Room encounter scripting (spawn trigger) | AI | P0 | 15 |
| W4-07 | Room transition manager | SA | P0 | 10 |
| W4-08 | Seed-based deterministic room gen | SA | P0 | 15 |
| **Toplam** | | | | **122** |

### HAFTA 5: Item/Relic ve Build Çeşitliliği

| Task ID | Açıklama | Uzman | Öncelik | Tahmini Test |
|---------|----------|-------|---------|-------------|
| W5-01 | Item definition data model (JSON config) | CD | P0 | 15 |
| W5-02 | Tag-based item effect system | CD+SA | P0 | 20 |
| W5-03 | Sinerji detection engine | CD | P0 | 15 |
| W5-04 | Item reward generator (weighted random) | CD | P0 | 12 |
| W5-05 | Player inventory integration | SA | P0 | 15 |
| W5-06 | Object pool sistemi (projectile+particle) | SA | P0 | 15 |
| W5-07 | SpatialHash entegrasyonu combat'e | SA | P1 | 10 |
| W5-08 | 10 item tanımla (data-driven) | CD | P0 | 10 |
| W5-09 | 4 sinerji tanımla | CD | P0 | 8 |
| **Toplam** | | | | **120** |

### HAFTA 6: Boss ve Encounter Tasarımı

| Task ID | Açıklama | Uzman | Öncelik | Tahmini Test |
|---------|----------|-------|---------|-------------|
| W6-01 | Combat pipeline 4-aşama refactor | SA | P0 | 25 |
| W6-02 | Layered hitbox (contact/sustained/pierce) | PH | P0 | 15 |
| W6-03 | Two-track i-frame (hit + dodge) | PH | P0 | 12 |
| W6-04 | Damage tag system refactor | PH | P1 | 15 |
| W6-05 | Boss phase state machine | CD+AI | P0 | 20 |
| W6-06 | Boss attack pattern library (6+ pattern) | CD | P0 | 15 |
| W6-07 | Boss telegraph visual system | RE | P0 | 10 |
| W6-08 | Elit affix sistemi (6 affix) | CD | P1 | 12 |
| W6-09 | Threat budget spawn sistemi | AI | P1 | 12 |
| **Toplam** | | | | **136** |

### HAFTA 7: Meta Progression ve Save

| Task ID | Açıklama | Uzman | Öncelik | Tahmini Test |
|---------|----------|-------|---------|-------------|
| W7-01 | Meta currency + unlock flow entegrasyonu | TD | P0 | 15 |
| W7-02 | 3 unlock hattı tanımla (weapon/mutation/starter) | CD | P0 | 10 |
| W7-03 | Save schema versioning system | SA | P0 | 15 |
| W7-04 | Run state save/load (full roundtrip) | SA | P0 | 20 |
| W7-05 | Meta state save/load | SA | P0 | 12 |
| W7-06 | Save corruption handling + fallback | QA | P0 | 10 |
| W7-07 | Aggro manager (group coordination) | AI | P2 | 12 |
| W7-08 | 10 ek item tanımla (toplam 20) | CD | P1 | 8 |
| W7-09 | 4 ek sinerji tanımla (toplam 8) | CD | P1 | 8 |
| **Toplam** | | | | **110** |

### HAFTA 8: UI/UX ve Onboarding

| Task ID | Açıklama | Uzman | Öncelik | Tahmini Test |
|---------|----------|-------|---------|-------------|
| W8-01 | HUD layout sistemi (HP/cooldown/buffs/stats) | UX | P0 | 20 |
| W8-02 | Ana menü ekranı | UX | P0 | 10 |
| W8-03 | Death/result ekranı | UX | P0 | 12 |
| W8-04 | Reward seçim ekranı (3 kart) | UX | P0 | 12 |
| W8-05 | Pause menu | UX | P0 | 8 |
| W8-06 | Tutorial onboarding overlay | UX | P2 | 10 |
| W8-07 | Settings menu genişletme | UX | P1 | 8 |
| **Toplam** | | | | **80** |

### HAFTA 9: İçerik Derinliği + Audio

| Task ID | Açıklama | Uzman | Öncelik | Tahmini Test |
|---------|----------|-------|---------|-------------|
| W9-01 | 5 yeni düşman tipi (DashStriker, Bomber, Sniper, Summoner, Swarm) | CD | P1 | 25 |
| W9-02 | 10 ek room template (toplam 25) | CD | P1 | 15 |
| W9-03 | 10 ek item tanımla (toplam 30) | CD | P1 | 8 |
| W9-04 | Audio HAL abstraction | AU | P1 | 10 |
| W9-05 | Combat SFX layer | AU | P1 | 12 |
| W9-06 | UI SFX | AU | P2 | 8 |
| W9-07 | Music system | AU | P2 | 8 |
| **Toplam** | | | | **86** |

### HAFTA 10: Stabilite ve Teknik Borç

| Task ID | Açıklama | Uzman | Öncelik | Tahmini Test |
|---------|----------|-------|---------|-------------|
| W10-01 | Combat regression test suite (50+ test) | QA | P0 | 50 |
| W10-02 | AI behavior test suite (30+ test) | QA | P0 | 30 |
| W10-03 | Procedural gen test suite (25+ test) | QA | P0 | 25 |
| W10-04 | Save/load roundtrip test suite (20+ test) | QA | P0 | 20 |
| W10-05 | Performance smoke test script | QA | P0 | 5 |
| W10-06 | Crash fix (session-based testing) | TD | P0 | 10 |
| W10-07 | CI pipeline geliştirme | QA | P1 | 10 |
| W10-08 | EventBus throttle implementasyonu | SA | P2 | 8 |
| **Toplam** | | | | **158** |

### HAFTA 11: Balans ve Oyun Hissi

| Task ID | Açıklama | Uzman | Öncelik | Tahmini Test |
|---------|----------|-------|---------|-------------|
| W11-01 | Difficulty curve tuning (erken/orta/son) | GD+TD | P1 | 15 |
| W11-02 | Drop rate + reward weight balancing | CD | P1 | 10 |
| W11-03 | Boss tuning (HP/damage/phase threshold) | GD+CD | P1 | 12 |
| W11-04 | Item balance pass | CD | P1 | 10 |
| W11-05 | Enemy stat scaling verification | AI | P1 | 10 |
| W11-06 | Combat feel polish (timing, feedback) | GD | P1 | 8 |
| **Toplam** | | | | **65** |

### HAFTA 12: Release Candidate Demo

| Task ID | Açıklama | Uzman | Öncelik | Tahmini Test |
|---------|----------|-------|---------|-------------|
| W12-01 | Build kilidi (sadece blocker fix) | TD | P0 | - |
| W12-02 | Demo checklist: performans (60fps, 200 entity) | TD | P0 | 10 |
| W12-03 | Demo checklist: save/load full path | TD | P0 | 10 |
| W12-04 | Demo checklist: input responsiveness | TD | P0 | 8 |
| W12-05 | Demo checklist: boss clear path (start→finish) | TD | P0 | 12 |
| W12-06 | Trailer/screenshot sahneleri | TD | P2 | - |
| W12-07 | Final regression test run | QA | P0 | 15 |
| **Toplam** | | | | **55** |

---

## 6. TOPLAM PROJE ÖZETİ

### Test Tahmini

| Hafta | Yeni Test | Toplam Test |
|-------|----------|------------|
| Mevcut | - | 1,942 |
| W4 | 122 | 2,064 |
| W5 | 120 | 2,184 |
| W6 | 136 | 2,320 |
| W7 | 110 | 2,430 |
| W8 | 80 | 2,510 |
| W9 | 86 | 2,596 |
| W10 | 158 | 2,754 |
| W11 | 65 | 2,819 |
| W12 | 55 | 2,874 |

### Task Dağılımı (Uzman Bazlı)

| Uzman | Toplam Task | Toplam Test |
|-------|-----------|------------|
| Game Designer (GD) | 10 | 93 |
| Systems Architect (SA) | 14 | 186 |
| AI Engineer (AI) | 8 | 81 |
| Physics Engineer (PH) | 4 | 42 |
| Rendering Engineer (RE) | 3 | 32 |
| UI/UX Designer (UX) | 7 | 80 |
| Audio Designer (AU) | 4 | 38 |
| QA Expert (QA) | 7 | 158 |
| Technical Director (TD) | 9 | 82 |
| Content Designer (CD) | 18 | 189 |

### Risk Matrisi

| Risk | Olasılık | Etki | Azaltma |
|------|---------|------|---------|
| Scope kayması | Yüksek | Yüksek | Feature freeze W8+ |
| Engine'e geri dönme | Orta | Orta | Sadece blocker bugfix |
| İçerik yetişmeme | Orta | Orta | Data-driven, template system |
| Performans sorunları | Düşük | Yüksek | W10 stabilite haftası |
| Test regressyonu | Düşük | Orta | CI gate + regression suite |

---

## 7. HAFTALIK DONE KRİTERLERİ

### Week 4 Done:
- [ ] Input buffer aktif (6-8 frame)
- [ ] Hit-stop çalışıyor (combat hissi belirgin)
- [ ] Screen shake aktif
- [ ] Room graph: start→combat→reward→boss akışı çalışıyor
- [ ] 15 room template tanımlı
- [ ] Seed-based deterministik room üretimi
- [ ] 1 oynanabilir build

### Week 5 Done:
- [ ] Item data model + JSON config sistemi
- [ ] Tag-based item effect sistemi
- [ ] 10 item tanımlı ve çalışıyor
- [ ] 4 sinerji çalışıyor
- [ ] Object pool aktif (projectile+particle)
- [ ] SpatialHash combat entegre
- [ ] Farklı build'ler oynanabiliyor

### Week 6 Done:
- [ ] Combat pipeline 4-aşamalı
- [ ] Layered hitbox (contact/sustained/pierce)
- [ ] Two-track i-frame
- [ ] 1 boss (3 phase, 6+ attack)
- [ ] Elit affix sistemi (6 affix)
- [ ] Threat budget spawn
- [ ] Boss encounter oynanabilir

### Week 7 Done:
- [ ] Meta progression aktif (currency + unlock)
- [ ] 3 unlock hattı
- [ ] Save/load çalışıyor (run + meta)
- [ ] Save corruption handling
- [ ] 20 item + 8 sinerji
- [ ] Aggro manager

### Week 8 Done:
- [ ] HUD aktif (HP, cooldown, buffs, stats)
- [ ] Ana menü
- [ ] Death/result ekranı
- [ ] Reward seçim ekranı
- [ ] Pause menu
- [ ] Dış testçiye anlatmadan oynatılabilir

### Week 9 Done:
- [ ] 8 düşman tipi (3 mevcut + 5 yeni)
- [ ] 25 room template
- [ ] 30 item + 8 sinerji
- [ ] Audio backend aktif
- [ ] Combat SFX

### Week 10 Done:
- [ ] Regression test suite (150+ test)
- [ ] Performance smoke test
- [ ] 30+ dakika crash-free session
- [ ] CI pipeline geliştirilmiş
- [ ] EventBus throttle

### Week 11 Done:
- [ ] Difficulty curve balanced
- [ ] Drop rates tuned
- [ ] Boss HP/damage tuned
- [ ] Item balance pass
- [ ] Combat feel polished

### Week 12 Done:
- [ ] Build kilidi
- [ ] Demo checklist geçiyor (%100)
- [ ] 60 FPS (200 entity)
- [ ] Boss clear path çalışıyor
- [ ] Paylaşılabilir vertical slice demo

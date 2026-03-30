# VERTICAL SLICE GELİŞTİRME KURALLARI
> Bu dosya AI agent tarafından Vertical Slice geliştirmesinde SIKI SIKIYA uyulacaktır.
> İhlal = DURDUR ve düzelt. Devam etme.

---

## 0. GENEL İLKELER

### 0.1 Engine Feature Freeze
```
ENGINE DOSYALARINA DOKUNMA.
Yeni render/engine özelliği eklenmez, sadece blocker bugfix.
Engine katmanı (hal/, core/, engine/) SABİT.
Sadece game/, scripting/, ui/ katmanlarında geliştirme yapılır.
world/ katmanına sadece YENİ component eklenebilir, mevcut dosyalar değişmez.
```

### 0.2 Haftalık Ritim
```
4 gün üretim + 1 gün stabilite/test/balans.
Her hafta oynanabilir build hedefi.
Kritik bug sayısı artmıyor (trend aşağı).
Bir sonraki haftaya devreden iş en fazla %20.
```

### 0.3 TDD Zorunluluğu (AGENT_RULES.md Kural 4)
```
1. ÖNCE test yaz (RED)
2. SONRA implementation yaz (GREEN)
3. EN SON refactor yap (REFACTOR)
Test yoksa kod yazılamaz.
Mock YASAK — HeadlessGPU/gerçek implementation kullan.
```

---

## 1. HAFTA 4 KURALLARI — Oda/Run Akışı + Game Feel

### 1.1 Task Sırası (KESİN SIRAYLA)
```
W4-01: Input buffer sistemi
W4-02: Hit-stop / freeze frame sistemi
W4-03: Screen shake controller
W4-04: Room template library (JSON config)
W4-05: Room graph akışı entegrasyonu
W4-06: Room encounter scripting
W4-07: Room transition manager
W4-08: Seed-based deterministik room gen
```

### 1.2 Input Buffer (W4-01)
```
Dosya: game/input/input_buffer.py (Layer 4)
Katman: game/ → core/, world/ bağımlılığı olabilir
Spesifikasyon:
  - Frame-based input buffer (6-8 frame = 100-133ms @60fps)
  - Buffer: [(input_type, timestamp), ...] max 4 giriş sakla
  - consume(input_type): en eski eşleşen input'u döndür, buffer'dan sil
  - push(input_type, timestamp): buffer'a ekle, 4'ten fazlaysa en eskisini sil
  - clear(): tüm buffer'ı temizle
  - tick(dt): timeout'lu girişleri temizle (>200ms)
```

### 1.3 Hit-Stop (W4-02)
```
Dosya: game/combat/hit_stop.py (Layer 4)
Katman: game/ → core/ bağımlılığı
Spesifikasyon:
  - HitStopController sınıfı (Object'dan inherit)
  - request(frames: int): N frame freeze talep et
  - is_active: bool — freeze aktif mi
  - remaining_frames: int — kalan freeze frame
  - tick(): her frame remaining azalt, 0 olunca deaktif
  - Heavy hit: 3 frame, Light hit: 1 frame, Critical: 4 frame
  - Sadece game logic durur, render devam eder (delta time = 0)
```

### 1.4 Screen Shake (W4-03)
```
Dosya: game/camera/screen_shake.py (Layer 4)
Katman: game/ → core/ bağımlılığı (Vec2)
Spesifikasyon:
  - ScreenShake sınıfı (Object'dan inherit)
  - trigger(amplitude: float, frequency: float, duration: float, direction: Vec2)
  - tick(dt): perlin-noise benzeri shake hesapla, decay uygula
  - offset: Vec2 — mevcut frame offset (camera'ya ekle)
  - is_active: bool
  - Hit shake: amplitude=3, duration=0.1s
  - Heavy shake: amplitude=6, duration=0.2s
  - X/Y ayrı axis kontrolü
```

### 1.5 Room Template (W4-04)
```
Dosya: game/run/room_templates.py (Layer 4)
Config: game/config/rooms/ (JSON dosyaları)
Spesifikasyon:
  - RoomTemplate dataclass: name, width, height, platforms[], spawn_zones[], door_locations[]
  - RoomTemplateLibrary: load_from_config(path), get_template(name), get_random(rng)
  - 15 hand-designed template (JSON):
    - 5 combat small (2-3 platform)
    - 5 combat medium (4-5 platform)
    - 3 combat large (5+ platform)
    - 1 boss arena
    - 1 treasure room
  - No-repeat-within-run constraint tracking
```

### 1.6 Room Graph Entegrasyonu (W4-05)
```
Dosya: game/run/room.py (MEVCUT — güncelle)
Katman: game/ → game/run/room_templates.py
Spesifikasyon:
  - Mevcut RoomGraph.generate()'i RoomTemplateLibrary ile entegre et
  - Room sınıfına template alanı ekle
  - Room 생성ında template'den platform/spawn/door verisini kullan
  - Graph akışı: START → COMBAT(1-3) → REWARD → COMBAT(1-3) → ELITE → TREASURE → COMBAT(1-3) → BOSS
```

### 1.7 Room Encounter Scripting (W4-06)
```
Dosya: game/run/encounter.py (Layer 4)
Spesifikasyon:
  - Encounter sınıfı: enemy_spawns[], trigger_type (on_enter/on_clear/on_timer)
  - ThreatBudget: float — oda için toplama düşman bütçesi
  - EncounterGenerator: budget + template → enemy composition üret
  - spawn_trigger: "on_room_enter" | "on_wave_clear" | "on_timer"
  - wave_system: bir dalgayı temizle → sonraki dalgayı tetikle
```

### 1.8 Room Transition Manager (W4-07)
```
Dosya: game/run/transition.py (Layer 4)
Spesifikasyon:
  - RoomTransitionManager sınıfı
  - transition_to(room: Room, direction: str): geçiş başlat
  - is_transitioning: bool
  - transition_progress: float (0.0-1.0)
  - fade_duration: float (default 0.5s)
  - Callback'ler: on_transition_start, on_transition_complete
```

### 1.9 Seed-Based Room Gen (W4-08)
```
Dosya: game/run/game_rng.py (Layer 4)
Spesifikasyon:
  - GameRNG sınıfı — seeded pseudo-random number generator wrapper
  - Python random.Random(seed) kullan, global state'e DOKUNMA
  - room_seed(run_seed, room_index): int = hash(run_seed, room_index)
  - all_random_calls GO THROUGH GameRNG, never random module directly
  - Serializable: current state kaydedilebilir (save/load için)
  - Reproducible: aynı seed → aynı room composition
```

---

## 2. DONE KRİTERLERİ — HAFTA 4

```
[ ] Input buffer aktif (6-8 frame, consume/push/clear/tick)
[ ] Hit-stop çalışıyor (combat hissi belirgin: heavy=3f, light=1f, crit=4f)
[ ] Screen shake aktif (hit/heavy parametreleri, X/Y ayrı)
[ ] 15 room template JSON dosyası tanımlı
[ ] Room graph: start→combat→reward→boss akışı çalışıyor
[ ] Encounter scripting: threat budget + spawn trigger
[ ] Room transition: fade in/out çalışıyor
[ ] Seed-based deterministik room üretimi (aynı seed = aynı room)
[ ] Mevcut 1942 test REGRESSYON YOK (hepsi geçiyor)
[ ] Yeni test sayısı: ~122 (toplam hedef: ~2064)
[ ] 1 oynanabilir build
```

---

## 3. YASAKLAR

| Yasak | Açıklama |
|-------|----------|
| Engine dokunmak | hal/, core/, engine/ dosyalarını değiştirme (blocker bugfix hariç) |
| Mock kullanmak | HeadlessGPU/gerçek implementation kullan |
| Test'siz kod | Her dosyanın test karşılığı zorunlu |
| Global random | random.seed() YASAK, GameRNG kullan |
| Star import | from module import * YASAK |
| Üst katman import | Game katmanı UI/Editor import edemez |
| Premature abstraction | 3 kez görmeden interface yazma |
| Magic number | Sabit tanımla (MAX_INPUT_BUFFER = 4 gibi) |

---

## 4. ADIM PROSEDÜRÜ

```
Her task için:
1. agent_state.json OKU → task sırasını ve durumu anla
2. Test DOSYASINI yaz (henüz implementation yok) → RED
3. Test'i ÇALIŞTIR → RED olduğunu gör
4. Implementation YAZ → GREEN
5. TÜM TESTLERİ ÇALIŞTIR → regresyon yok
6. agent_state.json GÜNCELLE
7. Sonraki task'a geç

İHLAL DURUMUNDA:
1. DURDUR
2. İhlali düzelt
3. Tekrar test et
4. Devam et
```

---

## 5. KALİTE KONTROL

```
Her task sonrası:
- [ ] Import kuralları OK mu? (AGENT_RULES.md kural 1)
- [ ] Katman bütünlüğü OK mu? (Game → Core/World, üst yok)
- [ ] Test coverage OK mu? (Yeni kod ≥80%)
- [ ] Regresyon yok mu? (1942 mevcut test geçiyor)
- [ ] Over-engineer yok mu? (YAGNI)
- [ ] Class ≤200 satır, Func ≤30 satır, Param ≤4
```

---

**BU KURALLAR TARTIŞILAMAZ. İHLAL = DURDUR.**

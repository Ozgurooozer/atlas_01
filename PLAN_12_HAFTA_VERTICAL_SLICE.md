# 12 Haftalık Vertical Slice Planı

## Hedef Çıktı (Hafta 12 Sonu)

- Tek biome, 1 boss, 6-8 düşman tipi, 20-30 item/relic ile baştan sona oynanabilir run.
- Side scroller + isometric destekli tek stabil render preset.
- Demo kalitesinde menü/HUD, save/load, onboarding, temel balans ve bugfix turu.

## Çalışma Prensibi

- Engine feature freeze: yeni render/engine özelliği eklenmez, sadece bugfix.
- Haftalık ritim: 4 gün üretim + 1 gün stabilite/test/balans.
- Her hafta oynanabilir build alınır.

## Haftalara Bölünmüş Yol Haritası

### Hafta 1 - Freeze ve Oyun Çatısı

- Render stabilizasyon dokümanını uygulamaya bağla: `docs/RENDER_STABILIZATION_PLAN.md`.
- Oyun çekirdeği klasör yapısını netleştir (`game/` altında `combat`, `run`, `ai`, `progression` alt modülleri).
- Tek game loop sözleşmesi oluştur (start-run, tick, death, reward, next-room).
- Çıktı: boş ama uçtan uca çalışan run shell build.

### Hafta 2 - Combat Core v1

- Hasar modeli, cooldown, i-frame, hit/hurtbox kuralları.
- Oyuncu aksiyonları: basic attack, dash, 1 aktif skill.
- Combat eventlerini EventBus üzerinden merkezileştir: `core/eventbus.py`.
- Çıktı: tek odada tatmin edici combat loop.

### Hafta 3 - Düşman AI Paketleri

- 3 archetype: melee chaser, ranged kiter, tank/charger.
- AI davranışlarını state machine + behaviour tree ile standardize et: `scripting/statemachine.py`, `scripting/behaviour_tree.py`.
- Spawn-wave akışı ekle (room clear koşulu).
- Çıktı: 5-7 dakikalık combat test arenası.

### Hafta 4 - Oda/Run Akışı

- Oda graph akışı (start -> combat -> reward -> combat -> mini/boss).
- Seed tabanlı run üretimi (aynı seed aynı layout).
- Level/room geçişlerini `world/level.py` üzerinde sade bir flow ile bağla.
- Çıktı: baştan sona 1 run (ham içerik).

### Hafta 5 - Item/Relic ve Build Çeşitliliği

- 20-30 item/relic havuzu (saldırı hızı, crit, DoT, dash modları vb.).
- Stack ve inventory kullanımını oyuna bağla: `game/inventory/inventory.py`.
- 8-10 belirgin sinerji tanımla.
- Çıktı: farklı oynanışa zorlayan build seçimleri.

### Hafta 6 - Boss ve Encounter Tasarımı

- 1 boss phase yapısı (en az 2 phase).
- Elit düşman ve affix sistemi (hızlı, zırhlı, zehirli vb.).
- Risk/ödül dengesi (boss öncesi güçlenme penceresi).
- Çıktı: run finali hissi veren karşılaşma.

### Hafta 7 - Meta Progression ve Save

- Run içi ve run dışı progression ayrımı.
- Save schema sürümü ve fallback stratejisi: `game/save/save.py`.
- Unlock akışı (2-3 kalıcı ilerleme hattı).
- Çıktı: ölünce tekrar oynamayı teşvik eden meta döngü.

### Hafta 8 - UI/UX ve Onboarding

- Ana menü, pause, death/result ekranı, settings.
- HUD sadeleştirme (HP, cooldown, buff/debuff, reward seçim ekranı).
- İlk 3 dakikada öğretici onboarding.
- Çıktı: dış testçiye anlatmadan oynatılabilir sürüm.

### Hafta 9 - İçerik Derinliği Sprinti

- Düşman, oda varyasyonu, item havuzu genişletme.
- Biome görsel kimliği (asset entegrasyonu, tematik tutarlılık).
- Audio pass (SFX + müzik geçişleri): `engine/audio/audio.py`.
- Çıktı: tekrar oynanabilirlikte görünür artış.

### Hafta 10 - Stabilite ve Teknik Borç Temizliği

- Crash, soft-lock, save bozulması, frame stutter odaklı bugfix haftası.
- Kritik gameplay path smoke test seti oluştur.
- Sessiz yutulan exception noktalarını logla (özellikle oyun katmanı).
- Çıktı: uzun oturumda dayanıklı build.

### Hafta 11 - Balans ve Oyun Hissi

- Difficulty curve (erken/orta/son) tuning.
- Drop rate, reward weight, boss tuning.
- Combat polish'i kontrollü bağla: `engine/game/combat_polish.py`.
- Çıktı: adil ama zorlayıcı hissi.

### Hafta 12 - Release Candidate Demo Haftası

- Build kilidi: yalnızca blocker bug fix.
- Demo checklist: performans, save/load, input, boss clear path.
- Trailer/screenshot için stabil içerik sahneleri hazırlanır.
- Çıktı: paylaşılabilir vertical slice demo.

## Haftalık Done Kriteri

- O hafta tanımlı içerik + en az 1 oynanabilir build.
- Kritik bug sayısı artmıyor (trend aşağı).
- Bir sonraki haftaya devreden iş en fazla %20.

## Riskler ve Karşı Önlem

- Scope kayması: her hafta yeni feature ekleme isteğini backlog'a at, sprint içine alma.
- Engine'e geri dönme refleksi: yalnızca blocker bugfix için engine dosyalarına dokun.
- İçerik yetişmeme riski: 8. haftadan sonra yeni sistem değil sadece içerik+balans.

## Ölçüm Metrikleri (Basit ama Etkili)

- Haftalık oynanabilir build sayısı: hedef 1+
- Ortalama run süresi: hedef 10-20 dk
- Crash-free session: hedef 30+ dk
- Testçi geri bildirimi: anlaşılırlık, akış, tekrar oynama isteği 1-5 puan

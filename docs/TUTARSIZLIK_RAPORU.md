# Dökümantasyon vs Proje Tutarsızlık Raporu

**Tarih:** 29 Mart 2026
**İnceleyen:** AI Agent

---

## Özet

Dökümantasyon (README.md, ARCHITECTURE.md) ile gerçek proje yapısı arasında **kritik tutarsızlıklar** tespit edilmiştir.

---

## 1. TEST SAYISI TUTARSIZLIĞI ⚠️ KRİTİK

| Kaynak | Test Sayısı | Açıklama |
|--------|-------------|----------|
| README.md (üst) | 1340 | "%100 coverage hedefi" |
| README.md (alt) | 770 | "Toplam: 770 test geçiyor" |
| ARCHITECTURE.md | ~1477 | "TOPLAM: ~1477 test" |

**Sorun:** 3 farklı sayı var, hangisi doğru?

---

## 2. CORE DİZİNİ TUTARSIZLIĞI ⚠️ KRİTİK

### Dökümantasyonda Listelenen (README.md):
```
core/
├── signal.py          # Signal/Slot
├── config.py          # Config system
├── logger.py          # Logging
└── profiler.py        # Performance profiling
```

### Gerçek core/ Dizini:
```
core/
├── __init__.py
├── color.py           # ← Dökümanda YOK
├── eventbus.py
├── guid.py
├── object.py
├── reflection.py
├── scheduler.py
└── serializer.py
```

**Sorunlar:**
- `signal.py`, `config.py`, `logger.py`, `profiler.py` **YOK** (planlanan ama yazılmamış)
- `color.py` **VAR** ama dökümanda listelenmemiş
- README.md yanıltıcı - bu dosyalar varmış gibi gösteriliyor

---

## 3. ENGINE DİZİNİ TUTARSIZLIĞI ⚠️ KRİTİK

### Dökümantasyonda Listelenen (ARCHITECTURE.md):
```
engine/
├── renderer/
│   ├── renderer.py
│   ├── texture.py
│   ├── sprite.py
│   ├── batch.py
│   └── camera.py
├── physics/
│   ├── physics.py
│   ├── aabb.py
│   ├── overlap.py
│   └── spatial.py
├── audio/
├── input/
└── asset/
```

### Gerçek engine/ Dizini:
```
engine/
├── __init__.py
├── engine.py
├── loop.py
├── settings.py
├── subsystem.py
├── asset/          # Boş
├── audio/          # Boş
├── game/           # Boş
├── input/          # Boş
├── physics/        # Boş
└── renderer/       # Boş
```

**Sorun:** Alt dizinler var ama **içleri boş** - implementasyonlar yapılmamış

---

## 4. FAZ DURUMU TUTARSIZLIĞI ⚠️ ORTA

| Kaynak | Son Tamamlanan Faz |
|--------|-------------------|
| README.md | FAZ 6: EDITOR |
| ARCHITECTURE.md | FAZ 11: SCRIPTING (GELİŞTİRİLİYOR) |

**Sorun:** README.md güncelliğini yitirmiş olabilir

---

## 5. EKSİK DOSYA REFERANSLARI ⚠️ DÜŞÜK

### README.md'de Referans Verilen Ama Olmayan Dosyalar:
- `DEVELOPMENT_PROMPT.md` → docs/ dizininde yok
- `AGENT_RULES.md` → Kök dizinde yok (docs/AGENT_RULES.md var)

---

## 6. DÖKÜMANTASYONDA OLMAYAN DOSYALAR

### Mevcut Ama Dökümante Edilmemiş:
- `core/color.py` - Color utility class
- `core/__init__.py` - Package init
- `engine/settings.py` - Engine settings
- `engine/loop.py` - Game loop

---

## ÖNCELİKLI DÜZELTMELER

### 🔴 Yüksek Öncelik:
1. **Test sayısını doğrula** - Gerçek test sayısını bul ve dökümantasyonu güncelle
2. **README.md core/ bölümünü düzelt** - Olmayan dosyaları kaldır, olanları ekle
3. **Engine alt dizinlerini kontrol et** - Boş dizinler varsa dökümandan kaldır

### 🟡 Orta Öncelik:
4. **Faz durumunu güncelle** - README.md ve ARCHITECTURE.md'yi senkronize et
5. **Eksik dosya referanslarını düzelt** - DEVELOPMENT_PROMPT.md → docs/RENDERER_DEVELOPMENT_PROMPT.md

### 🟢 Düşük Öncelik:
6. **Eksik dökümantasyonu ekle** - color.py, settings.py, loop.py için dokümantasyon

---

## ÖNERİLER

1. **Dökümantasyon Güncelleme Prosedürü Oluştur:**
   - Her yeni dosya eklendiğinde README.md güncellenmeli
   - Faz tamamlandığında hem README hem ARCHITECTURE güncellenmeli

2. **Otomatik Doğrulama:**
   - Dökümanda listelenen dosyaların var olup olmadığını kontrol eden bir script
   - Test sayısını otomatik çekip dökümana yazan bir CI step'i

3. **Tek Kaynak Doğruluğu:**
   - ARCHITECTURE.md teknik detaylar için
   - README.md genel bakış için
   - İkisi senkron tutulmalı

---

## SONUÇ

Dökümantasyon **güncelliğini yitirmiş** ve **yanıltıcı bilgiler** içermektedir. 
Özellikle test sayısı ve core dosyaları konusunda ciddi tutarsızlıklar vardır.
Dökümantasyonun gözden geçirilmesi ve güncellenmesi **acil** gereklidir.
# QWEN GELİŞTİRME KURALLARI — PRODUCTION READY

> **BU DOSYA HER ADIMDAN SONRA KONTROL EDİLECEK**  
> İhlal = DURDUR → Düzelt → Test Et → Devam Et

---

## 0. ALTIN KURALLAR (TARTIŞILAMAZ)

1. **Spagetti Kod YASAK:** Cyclomatic complexity <10
2. **Mock YASAK:** HeadlessGPU ile gerçek test
3. **Windows-First:** Windows'ta native çalışacak
4. **Test-First:** Test olmadan implementation yok
5. **YAGNI:** "İleride lazım" diye kod yazma

---

## 1. KOD KALİTESİ STANDARTLARI

### 1.1 Sınıf Boyutu
```
MAX_SATIR = 200
```
**Kontrol:** `wc -l dosya.py`  
**İhlal örneği:** `engine/renderer/sprite.py` — 449 satır ❌  
**Çözüm:** Base class + mixins pattern ile böl

### 1.2 Fonksiyon Boyutu
```
MAX_SATIR = 30
```
**Kontrol:** Radon veya manuel sayım  
**İhlal örneği:** `ModernGLDevice.draw()` — 106 satır ❌  
**Çözüm:** Guard clauses + private helper methods

### 1.3 Parametre Sayısı
```
MAX_PARAMETRE = 4
```
**Kontrol:** Manuel review  
**İhlal örneği:** `from_grid()` — 11 parametre ❌  
**Çözüm:** Config object pattern (@dataclass)

### 1.4 Cyclomatic Complexity
```
MAX_COMPLEXITY = 10
```
**Kontrol:** `radon cc dosya.py`  
**Seviyeler:**
- 1-5: A ✅
- 6-10: B ✅
- 11-20: C ⚠️ (refactor gerekli)
- 21+: D/E/F ❌ (acil refactor)

---

## 2. IMPORT KURALLARI (AGENT_RULES.md GENİŞLETMESİ)

### 2.1 Yukarı Bağımlılık YASAK
```python
# ❌ YASAK: Katman 1, Katman 2'yi import edemez
# core/object.py
from engine.renderer import Renderer  # İHLAL!

# ✅ DOĞRU: Sadece alt katmanlar
# engine/renderer/sprite.py
from core.object import Object  # OK (Layer 2 → Layer 1)
```

**Kontrol:** `python scripts/check_layer_imports.py`

### 2.2 Import Çeşitliliği
```
MAX_IMPORT_COUNT = 5
```
**Kontrol:** `scripts/check_import_diversity.py`  
**İhlal:** 6+ farklı modülden import → dosya çok büyük, BÖL

### 2.3 Star Import YASAK
```python
from module import *  # ❌ KESİNLİKLE YASAK
```

**Kontrol:** `ruff check . --select F403`

### 2.4 Unused Import YASAK
```python
from typing import List, Dict  # ❌ Dict kullanılmıyor
```

**Kontrol:** `ruff check . --select F401`  
**Hedef:** 0 unused import

---

## 3. TEST ZORUNLULUKLARI

### 3.1 Test-Olmadan-Commit YASAK
```
Her .py dosyası için tests/test_*.py ZORUNLU
```

**Kontrol:** `ls tests/test_*.py`  
**İhlal:** Implementation var ama test yok → DURDUR

### 3.2 Mock YASAK
```python
# ❌ YASAK
@patch('engine.renderer.Renderer')
def test_something(mock_renderer):
    pass

# ✅ DOĞRU
def test_something():
    gpu = HeadlessGPU()  # Gerçek test double
    renderer = Renderer2D(gpu)
```

**Kontrol:** `python scripts/check_no_mock.py`

### 3.3 Headless Backend ZORUNLU
```
HAL katmanı: IWindow, IGPUDevice interfaceleri
Test implementasyonları: HeadlessWindow, HeadlessGPU
```

**Kontrol:** CI'da GPU olmadan test çalışıyor mu?

### 3.4 Test Sırası (TDD)
1. ÖNCE test yaz (RED)
2. SONRA implementation yaz (GREEN)
3. EN SON refactor yap (REFACTOR)

---

## 4. WINDOWS UYUMLULUĞU

### 4.1 Path Handling
```python
# ❌ YASAK: Linux path
path = "assets/textures/player.png"

# ✅ DOĞRU: Cross-platform
from pathlib import Path
path = Path("assets") / "textures" / "player.png"
```

### 4.2 Line Endings
```
Git config: core.autocrlf = true (Windows)
Editor: LF veya CRLF tutarlı olmalı
```

**Kontrol:** `.gitattributes` dosyası

### 4.3 Encoding
```python
# Her dosyanın başında
# -*- coding: utf-8 -*-
```

**Kontrol:** `file *.py` → UTF-8 olmalı

---

## 5. DOKÜMANTASYON STANDARTLARI

### 5.1 Docstring Format (Google Style)
```python
def calculate_damage(base: int, multiplier: float) -> int:
    """
    Hasar hesapla.
    
    Args:
        base: Temel hasar değeri
        multiplier: Çarpan (1.0 = normal)
    
    Returns:
        Nihai hasar değeri
    
    Raises:
        ValueError: multiplier < 0 ise
    """
```

**Kontrol:** `python -m pydocstyle dosya.py`

### 5.2 Type Hints ZORUNLU
```python
# ❌ YASAK
def func(x, y):
    return x + y

# ✅ DOĞRU
def func(x: int, y: int) -> int:
    return x + y
```

**Kontrol:** `mypy . --ignore-missing-imports`  
**Hedef:** %100 type coverage

---

## 6. OVER-ENGINEER YASAKLARI

### 6.1 Premature Abstraction
```
Aynı pattern 3 kez görülmeden interface YAZMA
```

**Örnek:**
```python
# 1. weapon var → interface yazma
class Sword: ...

# 2. weapon geldi → hala yazma
class Bow: ...

# 3. weapon geldi → ŞİMDİ yaz
class Axe: ...
# Artık IWeapon interface olabilir
```

### 6.2 Factory Factory YASAK
```
Maximum 1 seviye factory
AbstractFactoryFactory → ❌
```

### 6.3 Magic Method Sınırı
```
__getattr__, __setattr__ → Sadece Core Object için
Başka yerde → ❌
```

---

## 7. PERFORMANS STANDARTLARI

### 7.1 Frame Time
```
TARGET_FPS = 60
MAX_FRAME_TIME_MS = 16.67
```

**Kontrol:** Profiling ile ölç

### 7.2 Memory
```
MAX_RAM_MB = 256
```

**Kontrol:** `tracemalloc` ile ölç

### 7.3 Allocation
```
MAX_ALLOCATION_PER_FRAME = 100
```

**Kontrol:** GC tracking

---

## 8. KONTROL LİSTESİ (Her Adımdan Sonra)

```bash
# 1. Test GREEN mi?
pytest tests/ -q --tb=no
# Beklenen: 0 failed

# 2. Unused import var mı?
ruff check . --select F401
# Beklenen: 0

# 3. Star import var mı?
ruff check . --select F403
# Beklenen: 0

# 4. Class size >200 var mı?
find . -name "*.py" -exec wc -l {} \; | sort -rn | head -10
# Beklenen: Max <200

# 5. Complexity >10 var mı?
radon cc -s -a --min C .
# Beklenen: 0 dosya

# 6. Mock var mı?
python scripts/check_no_mock.py
# Beklenen: 0 mock

# 7. Import rules OK mi?
python scripts/check_imports.py
# Beklenen: 0 violation

# 8. Layer violations var mı?
python scripts/check_layer_violations.py
# Beklenen: 0 violation

# 9. Type coverage %100 mü?
mypy . --ignore-missing-imports
# Beklenen: 0 error

# 10. Function size >30 var mı?
# Manuel review veya custom script
# Beklenen: 0
```

---

## 9. İHLAL PROSEDÜRÜ

### Adım 1: DURDUR
```
İhlal tespit edildiğinde DERHAL durdur.
Devam etme, commit etme, PR açma.
```

### Adım 2: İHLALİ DÜZELT
```
İhlalin kök nedenini bul.
Minimum değişiklikle düzelt.
Over-fix yapma (YAGNI!).
```

### Adım 3: TEST ET
```
Düzeltmeden sonra TÜM testleri çalıştır.
pytest tests/ -q
Beklenen: 0 failed
```

### Adım 4: TEKRAR KONTROL ET
```
python scripts/check_all_quality.py
Tüm kontroller YEŞİL olmalı.
```

### Adım 5: DEVAM ET
```
Ancak tüm kontroller YEŞİL ise bir sonraki adıma geç.
```

---

## 10. ÖRNEK İHLAL SENARYOLARI

### Senaryo 1: Büyük Sınıf
```
❌ TESPİT: engine/renderer/sprite.py — 449 satır
🛑 DURDUR
✅ DÜZELT: sprite_base.py, sprite_mixins.py, sprite_data.py olarak böl
✅ TEST: pytest tests/engine/renderer/test_sprite.py -v
✅ KONTROL: wc -l engine/renderer/sprite*.py < 200
✅ DEVAM
```

### Senaryo 2: Mock Kullanımı
```
❌ TESPİT: tests/game/combat/test_system.py — @patch kullanılmış
🛑 DURDUR
✅ DÜZELT: HeadlessGPU ile gerçek test yaz
✅ TEST: pytest tests/game/combat/test_system.py -v
✅ KONTROL: python scripts/check_no_mock.py
✅ DEVAM
```

### Senaryo 3: Yüksek Complexity
```
❌ TESPİT: game/combat/system.py:apply_damage() — CC=16
🛑 DURDUR
✅ DÜZELT: Guard clauses + helper methods ile CC<10'a düşür
✅ TEST: pytest tests/game/combat/test_system.py -v
✅ KONTROL: radon cc game/combat/system.py --min C
✅ DEVAM
```

---

## 11. AUTOMATED CHECK SCRIPT

`scripts/check_all_quality.py` şunları çalıştıracak:

```python
#!/usr/bin/env python3
"""
Tüm kalite kontrollerini tek komutta çalıştır.
Çıktı: PASSED veya FAILED + detaylı rapor
"""

import subprocess
import sys

def run_check(name, command):
    print(f"\n{'='*60}")
    print(f"CHECK: {name}")
    print(f"{'='*60}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ FAILED: {name}")
        print(result.stdout)
        print(result.stderr)
        return False
    print(f"✅ PASSED: {name}")
    return True

def main():
    checks = [
        ("Tests GREEN", "pytest tests/ -q --tb=no"),
        ("No unused imports", "ruff check . --select F401"),
        ("No star imports", "ruff check . --select F403"),
        ("No mocks", "python scripts/check_no_mock.py"),
        ("Import rules OK", "python scripts/check_imports.py"),
        ("No layer violations", "python scripts/check_layer_violations.py"),
        ("Type coverage OK", "mypy . --ignore-missing-imports"),
    ]
    
    results = [run_check(name, cmd) for name, cmd in checks]
    
    print(f"\n{'='*60}")
    if all(results):
        print("🎉 ALL CHECKS PASSED!")
        return 0
    else:
        print("❌ SOME CHECKS FAILED!")
        print(f"Passed: {sum(results)}/{len(results)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

---

## 12. VERSİYON GEÇMİŞİ

| Versiyon | Tarih | Değişiklik |
|----------|-------|------------|
| 1.0 | 2026-03-28 | İlk versiyon |
| | | |

---

**BU DOSYA CANLIDIR**  
Gerekirse güncelle, ama kuralları ASLA ihlal etme.

**Son güncelleme:** 2026-03-28  
**Sorumlu:** Development Team

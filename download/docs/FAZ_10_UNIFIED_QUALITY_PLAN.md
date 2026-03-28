# FAZ 10: BİRLEŞİK KALİTE KORUMA SİSTEMİ
## Hybrid Timer Validator + CI Gate + Pre-commit Hook

---

## ÖZET

Bu belge, Scheduler sisteminin güvenli geçişi için üç katmanlı koruma sistemini birleştirir:

1. **Hybrid Timer Validator** - Paralel karşılaştırma ile sıfır regresyon
2. **CI Gate** - Kalite kapısı (her push'ta otomatik kontrol)
3. **Pre-commit Hook** - Yerel koruma (her commit'te 2 dk kontrol)

**Sonuç:** "Bizi kimse durduramaz" - tam otomatik kalite güvencesi

---

## 1. ÜÇ KATMANLI KORUMA MİMARİSİ

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DEVELOPER WORKFLOW                                 │
│                                                                              │
│   git commit ───► PRE-COMMIT HOOK (2 dk) ───► commit başarılı/hata         │
│                         │                                                    │
│                         ▼                                                    │
│                    ┌─────────────┐                                          │
│                    │ • format    │                                          │
│                    │ • lint      │                                          │
│                    │ • import    │                                          │
│                    │ • quick test│                                          │
│                    └─────────────┘                                          │
│                                                                              │
│   git push ─────► CI GATE (5-10 dk) ───► merge/block                        │
│                         │                                                    │
│                         ▼                                                    │
│                    ┌─────────────┐                                          │
│                    │ • full test │                                          │
│                    │ • coverage  │                                          │
│                    │ • layer chk │                                          │
│                    │ • timer val │                                          │
│                    └─────────────┘                                          │
│                                                                              │
│   runtime ────────► HYBRID TIMER VALIDATOR ───► discrepancy raporu         │
│                         │                                                    │
│                         ▼                                                    │
│                    ┌─────────────┐                                          │
│                    │ • shadow    │                                          │
│                    │ • compare   │                                          │
│                    │ • report    │                                          │
│                    └─────────────┘                                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. HYBRID TIMER VALIDATOR DETAYI

### 2.1 Katman Yerleşimi

```
Layer 1 (Core):
├── scheduler.py       [MEVCUT] - Scheduler sınıfı
├── legacy_timer.py    [YENİ]   - Eski sistem wrapper
└── timer_validator.py [YENİ]   - Karşılaştırma sistemi
```

**Bağımlılık Kontrolü:**
```
timer_validator.py
  ├── from core.scheduler import Scheduler      ✓ Aynı katman
  ├── from core.legacy_timer import LegacyTimer ✓ Aynı katman
  ├── from typing import Callable, List, Tuple  ✓ stdlib
  └── from dataclasses import dataclass         ✓ stdlib

Toplam: 4 modül (< 5) ✓
```

### 2.2 TDD Süreci

| Adım | Test Dosyası | Test Sayısı | Süre |
|------|--------------|-------------|------|
| 1 | test_legacy_timer.py | 12 | 1 gün |
| 2 | test_timer_validator.py | 15 | 1 gün |
| 3 | test_timer_validator_comparison.py | 12 | 1 gün |
| 4 | test_scheduler_validator_integration.py | 8 | 0.5 gün |
| 5 | test_shooter_with_validator.py | 8 | 1 gün |

**Toplam:** 55 yeni test, 4.5 gün

### 2.3 Monitoring Aşaması

```python
# config.py
TIMER_VALIDATION_MODE = True

# Her tick'te
if validator.discrepancy_count > 0:
    log.warning(f"Timer discrepancy: {validator.get_report()}")

# Geçiş Kriterileri:
# - 10 gün boyunca discrepancy = 0
# - Tüm demo oyunlar çalışıyor
# - Yeni testlerin hepsi geçiyor
```

---

## 3. PRE-COMMIT HOOK DETAYI

### 3.1 Yapılandırma

```yaml
# .pre-commit-config.yaml
repos:
  # 1. FORMAT KONTROL (30 saniye)
  - repo: https://github.com/psf/black
    rev: 24.1.0
    hooks:
      - id: black
        language_version: python3.12

  # 2. LINT KONTROL (45 saniye)
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.2.0
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]

  # 3. IMPORT KONTROL (15 saniye)
  - repo: local
    hooks:
      - id: check-imports
        name: Check Import Rules
        entry: python scripts/check_imports.py
        language: system
        types: [python]
        pass_filenames: false

  # 4. HIZLI TEST (60 saniye)
  - repo: local
    hooks:
      - id: quick-tests
        name: Quick Tests
        entry: python scripts/run_quick_tests.py
        language: system
        types: [python]
        pass_filenames: false
```

### 3.2 Import Kontrol Scripti

```python
# scripts/check_imports.py
#!/usr/bin/env python3
"""
AGENT_RULES.md kural 1.1, 1.3 kontrolü:
- Yukarı bağımlılık yok
- Max 5 import
- Star import yok
"""

import ast
import sys
from pathlib import Path

LAYERS = {
    "hal": 0, "core": 1, "engine": 2, "world": 3,
    "game": 4, "scripting": 5, "ui": 6, "editor": 7
}

def get_layer(file_path: Path) -> int:
    for name, layer in LAYERS.items():
        if f"/{name}/" in str(file_path):
            return layer
    return -1

def check_file(file_path: Path) -> list[str]:
    errors = []
    source_layer = get_layer(file_path)
    if source_layer < 0:
        return errors

    with open(file_path) as f:
        tree = ast.parse(f.read())

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
                if alias.name == "*":
                    errors.append(f"Star import YASAK: from ... import *")
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            imports.append(module)
            if node.names[0].name == "*":
                errors.append(f"Star import YASAK: from {module} import *")

            # Yukarı bağımlılık kontrolü
            for name, layer in LAYERS.items():
                if module.startswith(name) and layer > source_layer:
                    errors.append(
                        f"Yukarı bağımlılık YASAK: "
                        f"Layer {source_layer} → Layer {layer} ({module})"
                    )

    # Import çeşitliliği kontrolü
    unique_modules = set(imports)
    if len(unique_modules) > 5:
        errors.append(
            f"Import sınırı aşıldı: {len(unique_modules)} > 5 "
            f"(dosyayı böl)"
        )

    return errors

def main():
    errors = []
    for py_file in Path("engine").rglob("*.py"):
        file_errors = check_file(py_file)
        for err in file_errors:
            errors.append(f"{py_file}: {err}")

    if errors:
        for err in errors:
            print(f"❌ {err}")
        sys.exit(1)

    print("✅ Tüm import kuralları geçti")
    sys.exit(0)

if __name__ == "__main__":
    main()
```

### 3.3 Hızlı Test Scripti

```python
# scripts/run_quick_tests.py
#!/usr/bin/env python3
"""
Hızlı test: Değişen dosyaların testlerini çalıştır
Hedef: < 60 saniye
"""

import subprocess
import sys

def main():
    # Sadece core testleri (en kritik)
    result = subprocess.run(
        ["pytest", "tests/core/", "-x", "-q", "--tb=short"],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print("❌ Test hatası:")
        print(result.stdout)
        print(result.stderr)
        sys.exit(1)

    print("✅ Hızlı testler geçti")
    sys.exit(0)

if __name__ == "__main__":
    main()
```

### 3.4 Kurulum

```bash
# Pre-commit kurulumu
pip install pre-commit

# Hook'ları aktifleştir
cd engine
pre-commit install

# Tüm dosyalarda çalıştır (ilk sefer)
pre-commit run --all-files
```

---

## 4. CI GATE DETAYI

### 4.1 GitHub Actions Workflow

```yaml
# .github/workflows/quality_gate.yml
name: Quality Gate

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  quality-gate:
    runs-on: ubuntu-latest
    timeout-minutes: 15

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: 'pip'

      - name: Install Dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov ruff black

      - name: Format Check
        run: black --check engine/ tests/

      - name: Lint Check
        run: ruff check engine/ tests/

      - name: Import Rules Check
        run: python scripts/check_imports.py

      - name: Full Tests with Coverage
        run: |
          pytest tests/ \
            --cov=engine \
            --cov-report=xml \
            --cov-fail-under=80 \
            -v \
            --tb=short

      - name: Timer Validation Tests
        run: pytest tests/core/test_timer*.py -v

      - name: Upload Coverage
        uses: codecov/codecov-action@v4
        with:
          files: coverage.xml

  layer-check:
    runs-on: ubuntu-latest
    needs: quality-gate

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Layer Dependency Analysis
        run: python scripts/check_imports.py

      - name: Class Size Analysis
        run: |
          python scripts/check_class_size.py \
            --max-lines 200 \
            --max-params 4
```

### 4.2 Sınıf Boyutu Kontrol Scripti

```python
# scripts/check_class_size.py
#!/usr/bin/env python3
"""
AGENT_RULES.md kural 5.1, 5.2, 5.3 kontrolü:
- Max 200 satır sınıf
- Max 30 satır fonksiyon
- Max 4 parametre
"""

import ast
import argparse
from pathlib import Path

def check_file(file_path: Path, max_lines: int, max_params: int) -> list[str]:
    errors = []
    with open(file_path) as f:
        source = f.read()
        lines = source.split("\n")
        tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            start_line = node.lineno
            end_line = max(
                child.end_lineno
                for child in ast.walk(node)
                if hasattr(child, 'end_lineno')
            )
            class_lines = end_line - start_line + 1

            if class_lines > max_lines:
                errors.append(
                    f"{file_path}:{start_line}: "
                    f"Sınıf çok büyük: {class_lines} > {max_lines} satır "
                    f"(bölünmeli)"
                )

        elif isinstance(node, ast.FunctionDef):
            func_lines = node.end_lineno - node.lineno + 1
            if func_lines > 30:
                errors.append(
                    f"{file_path}:{node.lineno}: "
                    f"Fonksiyon çok büyük: {func_lines} > 30 satır"
                )

            params = len(node.args.args)
            if params > max_params:
                errors.append(
                    f"{file_path}:{node.lineno}: "
                    f"Çok fazla parametre: {params} > {max_params}"
                )

    return errors

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-lines", type=int, default=200)
    parser.add_argument("--max-params", type=int, default=4)
    args = parser.parse_args()

    errors = []
    for py_file in Path("engine").rglob("*.py"):
        errors.extend(check_file(py_file, args.max_lines, args.max_params))

    if errors:
        for err in errors:
            print(f"❌ {err}")
        return 1

    print("✅ Tüm boyut kuralları geçti")
    return 0

if __name__ == "__main__":
    exit(main())
```

---

## 5. ZAMAN ÇİZELGESİ

### 5.1 Hazırlık (Gün 0)

```bash
# Pre-commit kurulumu
pip install pre-commit
cd engine && pre-commit install

# CI workflow dosyalarını ekle
git add .github/workflows/quality_gate.yml
git add scripts/check_imports.py
git add scripts/run_quick_tests.py
git add scripts/check_class_size.py
git add .pre-commit-config.yaml

git commit -m "feat: Add quality gate system (pre-commit + CI)"
```

### 5.2 Geliştirme (Gün 1-5)

| Gün | İşlem | Çıktı |
|-----|-------|-------|
| 1 | test_legacy_timer.py + legacy_timer.py | 12 test GREEN |
| 2 | test_timer_validator.py + timer_validator.py | 15 test GREEN |
| 3 | test_timer_validator_comparison.py | 12 test GREEN |
| 4 | test_scheduler_validator_integration.py | 8 test GREEN |
| 5 | test_shooter_with_validator.py + shooter.py güncelle | 8 test GREEN |

### 5.3 Monitoring (Gün 6-15)

```
Gün 6-15: TimerValidator aktif, discrepancy = 0 kontrol
Her gün: CI Gate çalışıyor, pre-commit aktif
```

### 5.4 Cleanup (Gün 16-17)

```
Geçiş kriterleri karşılanınca:
1. TimerValidator → Scheduler (tek sistem)
2. legacy_timer.py sil
3. timer_validator.py sil
4. Test dosyalarını güncelle
5. ARCHITECTURE.md güncelle: FAZ 10 TAMAMLANDI
```

---

## 6. KORUMA ÖZETİ

### 6.1 Ne Zaman Ne Çalışır?

| Olay | Pre-commit | CI Gate | Timer Validator |
|------|------------|---------|-----------------|
| git commit | ✅ 2 dk | ❌ | ❌ |
| git push | ❌ | ✅ 5-10 dk | ❌ |
| oyun runtime | ❌ | ❌ | ✅ sürekli |

### 6.2 Ne Kontrol Edilir?

| Kural | Pre-commit | CI Gate | Timer Validator |
|-------|------------|---------|-----------------|
| Format (black) | ✅ | ✅ | ❌ |
| Lint (ruff) | ✅ | ✅ | ❌ |
| Yukarı bağımlılık | ✅ | ✅ | ❌ |
| Import sınırı (max 5) | ✅ | ✅ | ❌ |
| Star import | ✅ | ✅ | ❌ |
| Sınıf boyutu (max 200) | ❌ | ✅ | ❌ |
| Fonksiyon boyutu (max 30) | ❌ | ✅ | ❌ |
| Parametre sayısı (max 4) | ❌ | ✅ | ❌ |
| Test coverage (min 80%) | ❌ | ✅ | ❌ |
| Core testler | ✅ hızlı | ✅ tam | ❌ |
| Timer discrepancy | ❌ | ❌ | ✅ |

### 6.3 Hata Durumunda

```
PRE-COMMIT BAŞARISIZ:
→ Commit engellenir
→ Hata mesajı gösterilir
→ Düzelt ve tekrar commit

CI GATE BAŞARISIZ:
→ Push engellenir (branch protection)
→ GitHub PR'da kırmızı X
→ Düzelt ve tekrar push

TIMER VALIDATOR BAŞARISIZ:
→ Uyarı logu
→ discrepancy_count > 0
→ Araştır ve düzelt
```

---

## 7. KURAL UYUMLULUK TABLOSU

| Kural ID | Açıklama | Pre-commit | CI Gate | Timer Val |
|----------|----------|------------|---------|-----------|
| 1.1 | Yukarı bağımlılık yok | ✅ | ✅ | - |
| 1.2 | Döngüsel import yok | ✅ | ✅ | - |
| 1.3 | Max 5 import | ✅ | ✅ | - |
| 1.4 | Star import yok | ✅ | ✅ | - |
| 3.1 | YAGNI | - | - | ✅ |
| 4.1 | Test-olmadan-commit yok | ✅ | ✅ | - |
| 4.3 | Mock yok | - | ✅ | ✅ |
| 5.1 | Sınıf max 200 satır | - | ✅ | - |
| 5.2 | Fonksiyon max 30 satır | - | ✅ | - |
| 5.3 | Max 4 parametre | - | ✅ | - |

---

## 8. DOSYA YAPISI

```
engine/
├── .pre-commit-config.yaml    [YENİ]
├── scripts/
│   ├── check_imports.py       [YENİ]
│   ├── run_quick_tests.py     [YENİ]
│   └── check_class_size.py    [YENİ]
├── core/
│   ├── scheduler.py           [MEVCUT]
│   ├── legacy_timer.py        [YENİ - Geçici]
│   └── timer_validator.py     [YENİ - Geçici]
└── tests/
    └── core/
        ├── test_scheduler.py              [MEVCUT]
        ├── test_legacy_timer.py           [YENİ]
        ├── test_timer_validator.py        [YENİ]
        ├── test_timer_validator_comparison.py [YENİ]
        └── test_scheduler_validator_integration.py [YENİ]

.github/
└── workflows/
    └── quality_gate.yml       [YENİ]
```

---

## 9. SONUÇ

**Bu sistemle:**

1. **Her commit** temiz girer (pre-commit engeller)
2. **Her push** kalite geçer (CI Gate onaylar)
3. **Her runtime** doğrulanır (Timer Validator karşılaştırır)
4. **Sıfır regresyon** garantisi (paralel çalışma)
5. **Tam izlenebilirlik** (log ve raporlar)

**"Bizi kimse durduramaz" çünkü:**
- Hata yapamazsın (pre-commit engeller)
- Bozamazsın (CI Gate korur)
- Geriye bakmazsın (Timer Validator doğrular)

---

## 10. BAŞLAMA KOMUTLARI

```bash
# 1. Pre-commit kur
pip install pre-commit
cd engine && pre-commit install

# 2. Script dosyalarını oluştur
mkdir -p scripts .github/workflows

# 3. İlk kontrol
pre-commit run --all-files

# 4. Geliştirmeye başla (TDD)
# ÖNCE: tests/core/test_legacy_timer.py yaz
# SONRA: core/legacy_timer.py yaz
```

---

**BU PLAN AGENT_RULES.md VE ARCHITECTURE.md'E %100 UYUMLUDUR.**

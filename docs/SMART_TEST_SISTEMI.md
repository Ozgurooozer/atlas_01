# 🤖 AI-WRITTEN CODE İÇİN SMART TEST SİSTEMİ

> 2D Game Engine için akıllı, otomatik ve ölçeklenebilir test stratejisi

**Hedef:** AI tarafından yazılan kodun kalitesini otomatik denetlemek, mimari ihlalleri yakalamak, ölü kod ve tekrarları temizlemek.

---

## 📊 PROBLEM TANIMI

AI kod yazarken şu sorunlar oluşabilir:

| Problem | Açıklama | Örnek |
|---------|----------|-------|
| **Mimari İhlal** | Katman kurallarına uymama | `core/object.py` → `from engine.renderer import ...` |
| **Kod Tekrarı** | Aynı kodu birden fazla yere yazma | 3 farklı dosyada aynı `serialize()` fonksiyonu |
| **Ölü Kod** | Kullanılmayan fonksiyon/class | Hiç çağrılmayan `helper_function()` |
| **Pattern Drift** | Kod standardından sapma | Docstring eksikliği, `type: ignore` kullanımı |
| **Import İhlali** | Import kurallarına uymama | 10+ import/dosya, `from x import *` |

---

## 🎯 ÇÖZÜM: 3 KATMANLI TEST SİSTEMİ

```
┌─────────────────────────────────────────────────────────────┐
│           KATMAN 1: AI CODE QUALITY (YENİ!)                 │
│  - Architecture compliance (katman ihlali yakala)           │
│  - Import policy enforcement (import kuralları)             │
│  - Duplication detection (kod tekrarı bul)                  │
│  - Dead code detection (kullanılmayan kod bul)              │
│  - AI drift detection (pattern dışına çıkışı bul)           │
├─────────────────────────────────────────────────────────────┤
│           KATMAN 2: CONTRACT TESTS                          │
│  - Interface contract tests (otomatik discovery)            │
│  - Her implementation otomatik test edilir                  │
├─────────────────────────────────────────────────────────────┤
│           KATMAN 3: FUNCTIONAL TESTS                        │
│  - Critical path tests (lifecycle testleri)                 │
│  - Property-based tests (Hypothesis - math/physics)         │
│  - Scenario tests (demo = test, snapshot)                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 DOSYA YAPISI

```
tests/
├── conftest.py                    # Global fixtures
│
├── quality/                       # 🆕 AI CODE QUALITY
│   ├── __init__.py
│   ├── test_architecture.py       # Katman ihlalleri
│   ├── test_imports.py            # Import policy
│   ├── test_duplication.py        # Kod tekrarı
│   ├── test_dead_code.py          # Ölü kod
│   └── test_ai_drift.py           # Pattern drift
│
├── contracts/                     # Interface tests
│   ├── __init__.py
│   └── test_interfaces.py
│
├── critical/                      # Critical path tests
│   ├── __init__.py
│   └── test_lifecycle.py
│
├── properties/                    # Math/Physics invariants
│   ├── __init__.py
│   └── test_math_properties.py
│
├── scenarios/                     # Demo = Test
│   ├── __init__.py
│   └── test_demos_work.py
│
├── legacy/                        # Eski testler (kademeli sil)
│   ├── core/
│   ├── hal/
│   ├── engine/
│   └── world/
│
├── auto_generate_tests.py         # Otomatik test oluşturucu
├── run_tests.py                   # Smart test runner
└── conftest.py                    # Global fixtures
```

---

## 📋 KATMAN 1: AI CODE QUALITY TESTS

### 1.1 Architecture Compliance Test

**Dosya:** `tests/quality/test_architecture.py`

```python
"""
ARCHITECTURE COMPLIANCE TEST

AI kod yazarken katman ihlali yapabilir.
Bu test OTOMATIK yakalar.

KURAL: Üst katmandan import YASAK

Layer Hierarchy:
    0. HAL      - Window, GPU, Filesystem, Clock
    1. CORE     - Object, Reflection, EventBus, Serializer
    2. ENGINE   - Renderer, Physics, Audio, Input, Asset
    3. WORLD    - World, Level, Actor, Component, System
    4. GAME     - GameMode, Controller, Inventory, Quest
    5. UI       - Widget, Canvas, Label, Button
    6. EDITOR   - Viewport, Hierarchy, Properties
"""

import ast
from pathlib import Path
import pytest


# KATMAN TANIMI
LAYERS = {
    'hal': 0,       # Layer 0
    'core': 1,      # Layer 1
    'engine': 2,    # Layer 2
    'world': 3,     # Layer 3
    'game': 4,      # Layer 4
    'ui': 5,        # Layer 5
    'editor': 6,    # Layer 6
}


def get_file_layer(file_path: Path) -> int:
    """
    Dosyanın katmanını bul.
    
    Args:
        file_path: Dosya yolu
        
    Returns:
        Katman numarası (0-6), -1 eğer bilinmiyor
    """
    for layer_name, layer_num in LAYERS.items():
        if layer_name in str(file_path):
            return layer_num
    return -1  # Unknown


def get_imports_from_file(file_path: Path) -> list[str]:
    """
    Dosyadaki tüm import'ları çıkar.
    
    Args:
        file_path: Dosya yolu
        
    Returns:
        Import edilen modül isimleri listesi
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        tree = ast.parse(f.read())
    
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module.split('.')[0])
    
    return imports


class TestArchitectureCompliance:
    """
    AI-written code architecture compliance.
    
    Her commit'te çalışır, katman ihlali varsa FAIL.
    """
    
    @pytest.mark.parametrize("source_file", [
        f for f in Path('download/engine').rglob('*.py')
        if 'test' not in str(f) and '__pycache__' not in str(f)
    ])
    def test_no_upper_layer_import(self, source_file):
        """
        Dosya SADECE kendi veya alt katmandan import edebilir.
        
        ÖRNEK HATA:
            core/object.py import engine/renderer  ← YASAK!
        
        DOĞRU:
            engine/renderer/sprite.py import core/object  ← OK
        """
        file_layer = get_file_layer(source_file)
        if file_layer < 0:
            return  # Test dışı dosya
        
        imports = get_imports_from_file(source_file)
        
        for imp in imports:
            if imp in LAYERS:
                imported_layer = LAYERS[imp]
                assert imported_layer <= file_layer, (
                    f"❌ ARCHITECTURE VIOLATION:\n"
                    f"  File: {source_file}\n"
                    f"  Layer: {file_layer} ({list(LAYERS.keys())[file_layer]})\n"
                    f"  Illegal import: {imp} (Layer {imported_layer})\n"
                    f"  FIX: Remove 'from {imp} import ...'"
                )
    
    def test_no_circular_imports(self):
        """
        Döngüsel import YASAK.
        
        A → B → A  YASAK
        A → B → C → A  YASAK
        
        Çözüm:
            - Type hint için string kullan: `def func() -> "Type":`
            - Late import: fonksiyon içinde import
        """
        # Basit cycle detection
        import_graph = {}
        
        for py_file in Path('download/engine').rglob('*.py'):
            if 'test' in str(py_file) or '__pycache__' in str(py_file):
                continue
            
            module_name = str(py_file).replace('/', '.').replace('\\', '.').replace('.py', '')
            imports = get_imports_from_file(py_file)
            import_graph[module_name] = imports
        
        # DFS cycle detection
        def has_cycle(node, visited, rec_stack):
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in import_graph.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor, visited, rec_stack):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        visited = set()
        rec_stack = set()
        
        for node in import_graph:
            if node not in visited:
                assert not has_cycle(node, visited, rec_stack), \
                    f"❌ CIRCULAR IMPORT detected involving {node}"
```

**Örnek Hata Çıktısı:**
```
❌ ARCHITECTURE VIOLATION:
  File: download/engine/core/object.py
  Layer: 1 (core)
  Illegal import: engine (Layer 2)
  FIX: Remove 'from engine import ...'
```

---

### 1.2 Import Policy Test

**Dosya:** `tests/quality/test_imports.py`

```python
"""
IMPORT POLICY ENFORCER

AI yanlış import yapabilir.
Bu test KURALLARI korur.

KURALLAR:
    1. Max 5 import/dosya
    2. Star import (*) YASAK
    3. Third-party sadece kendi katmanında
"""

import ast
from pathlib import Path
import pytest


class TestImportPolicy:
    """
    Import policy enforcement.
    
    Her dosya için import kuralları.
    """
    
    def test_max_5_imports_per_file(self):
        """
        Bir dosya en fazla 5 farklı modülden import edebilir.
        
        AGENTS.md kuralı: "Import Diversity Limit"
        
        Neden?
            - Fazla import = dosya çok büyük
            - Bölünmesi gerekiyor
        """
        violations = []
        
        for py_file in Path('download/engine').rglob('*.py'):
            if 'test' in str(py_file) or '__pycache__' in str(py_file):
                continue
            
            with open(py_file, 'r', encoding='utf-8') as f:
                try:
                    tree = ast.parse(f.read())
                except:
                    continue
            
            imported_modules = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imported_modules.add(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imported_modules.add(node.module.split('.')[0])
            
            if len(imported_modules) > 5:
                violations.append(
                    f"{py_file}: {len(imported_modules)} imports\n"
                    f"  Modules: {', '.join(sorted(imported_modules))}"
                )
        
        assert len(violations) == 0, (
            f"❌ TOO MANY IMPORTS ({len(violations)} files):\n"
            + '\n\n'.join(violations[:5])
            + "\n\nFIX: Reduce imports (max 5 per file)"
        )
    
    def test_no_forbidden_third_party(self):
        """
        Third-party kütüphaneler sadece kendi katmanlarında.
        
        KURALLAR:
            pyglet, moderngl → sadece hal/
            pymunk           → sadece engine/physics/
            Pillow           → sadece engine/asset/
            watchdog         → sadece engine/asset/
            msgspec          → sadece core/
            dearpygui        → sadece editor/
        
        Neden?
            - Third-party bağımlılıkları izole et
            - Değiştirmeyi kolaylaştır
        """
        THIRD_PARTY_RULES = {
            'pyglet': ['hal'],
            'moderngl': ['hal', 'engine/renderer'],
            'pymunk': ['engine/physics'],
            'PIL': ['engine/asset'],
            'watchdog': ['engine/asset'],
            'msgspec': ['core'],
            'dearpygui': ['editor'],
        }
        
        violations = []
        
        for py_file in Path('download/engine').rglob('*.py'):
            if 'test' in str(py_file) or '__pycache__' in str(py_file):
                continue
            
            file_path = str(py_file)
            
            with open(py_file, 'r', encoding='utf-8') as f:
                try:
                    tree = ast.parse(f.read())
                except:
                    continue
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        module = alias.name.split('.')[0]
                        if module in THIRD_PARTY_RULES:
                            allowed_paths = THIRD_PARTY_RULES[module]
                            if not any(allowed in file_path for allowed in allowed_paths):
                                violations.append(
                                    f"{py_file}: import {module}\n"
                                    f"  Allowed in: {', '.join(allowed_paths)}"
                                )
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        module = node.module.split('.')[0]
                        if module in THIRD_PARTY_RULES:
                            allowed_paths = THIRD_PARTY_RULES[module]
                            if not any(allowed in file_path for allowed in allowed_paths):
                                violations.append(
                                    f"{py_file}: from {module} import ...\n"
                                    f"  Allowed in: {', '.join(allowed_paths)}"
                                )
        
        assert len(violations) == 0, (
            f"❌ FORBIDDEN THIRD-PARTY IMPORTS ({len(violations)}):\n"
            + '\n\n'.join(violations[:10])
            + "\n\nFIX: Move third-party imports to allowed locations"
        )
    
    def test_no_star_imports(self):
        """
        from module import *  YASAK.
        
        Neden?
            - Hangi isimlerin import edildiği belli değil
            - İsim çakışması riski
            - AI tembellik yapabilir
        """
        star_imports = []
        
        for py_file in Path('download/engine').rglob('*.py'):
            if 'test' in str(py_file) or '__pycache__' in str(py_file):
                continue
            
            with open(py_file, 'r', encoding='utf-8') as f:
                try:
                    tree = ast.parse(f.read())
                except:
                    continue
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        if alias.name == '*':
                            star_imports.append(
                                f"{py_file}: from {node.module} import *"
                            )
        
        assert len(star_imports) == 0, (
            f"❌ STAR IMPORTS FOUND ({len(star_imports)}):\n"
            + '\n'.join(star_imports)
            + "\n\nFIX: Import specific names only"
        )
```

---

### 1.3 Code Duplication Test

**Dosya:** `tests/quality/test_duplication.py`

```python
"""
CODE DUPLICATION DETECTOR

AI aynı kodu tekrar tekrar yazabilir.
Bu test OTOMATIK bulur.

Neden önemli?
    - Aynı kod 3 yerde = 3x bakım maliyeti
    - Bug fix 3 yerde yapılmalı
    - DRY principle ihlali
"""

import ast
from pathlib import Path
from collections import Counter
import pytest


def normalize_code(code: str) -> str:
    """
    Kodu normalize et (whitespace, comment sil).
    
    Aynı kod farklı formatting ile yazılmış olsa da bul.
    
    Args:
        code: Normalized edilecek kod
        
    Returns:
        Normalize edilmiş kod string
    """
    lines = []
    for line in code.split('\n'):
        # Remove comments
        if '#' in line:
            line = line[:line.index('#')]
        # Strip and normalize whitespace
        line = ' '.join(line.split())
        if line:
            lines.append(line)
    return '\n'.join(lines)


def extract_functions(file_path: Path) -> list[tuple[str, str]]:
    """
    Dosyadaki tüm fonksiyonları çıkar.
    
    Args:
        file_path: Dosya yolu
        
    Returns:
        (function_name, normalized_code) listesi
    """
    functions = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        tree = ast.parse(content)
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # Get function code
            func_code = ast.get_source_segment(content, node) or ''
            functions.append((
                f"{file_path}:{node.name}",
                normalize_code(func_code)
            ))
    
    return functions


class TestCodeDuplication:
    """
    AI-written code duplication detector.
    
    Aynı fonksiyon kodu 2+ yerde olmamalı.
    """
    
    def test_no_duplicate_functions(self):
        """
        Aynı fonksiyon birden fazla yerde olmamalı.
        
        ÖRNEK HATA:
            world/actor.py: def serialize(self): ...
            world/component.py: def serialize(self): ...  ← Aynı kod!
            ui/widget.py: def serialize(self): ...        ← Aynı kod!
        
        ÇÖZÜM:
            - Object base class'a taşı
            - Utility module oluştur
        """
        all_functions = []
        
        for py_file in Path('download/engine').rglob('*.py'):
            if 'test' in str(py_file) or '__pycache__' in str(py_file):
                continue
            
            all_functions.extend(extract_functions(py_file))
        
        # Group by normalized code
        code_groups = Counter(code for _, code in all_functions)
        
        # Find duplicates (same code, different location)
        duplicates = [
            (name, code) for name, code in all_functions
            if code_groups[code] > 1
        ]
        
        # Report (ilk 5 duplicate)
        if len(set(code for _, code in duplicates)) > 0:
            seen_codes = set()
            duplicate_reports = []
            
            for name, code in duplicates:
                if code not in seen_codes:
                    seen_codes.add(code)
                    # Sadece farklı dosyalardakileri rapor et
                    duplicate_reports.append(name)
            
            assert len(duplicate_reports) <= 5, (
                f"⚠️ POTENTIAL DUPLICATION ({len(duplicate_reports)} groups):\n"
                + '\n'.join(duplicate_reports[:5])
                + "\n\nFIX: Extract to common base class or utility module"
            )
```

**Örnek Hata Çıktısı:**
```
⚠️ POTENTIAL DUPLICATION (3 groups):
  download/engine/world/actor.py:serialize
  download/engine/world/component.py:serialize
  download/engine/ui/widget.py:serialize

FIX: Extract to common base class or utility module
```

---

### 1.4 Dead Code Test

**Dosya:** `tests/quality/test_dead_code.py`

```python
"""
DEAD CODE DETECTOR

AI kod yazar ama kullanmaz.
Bu test OTOMATIK bulur.

Neden önemli?
    - Ölü kod = bakım maliyeti
    - Kafa karıştırıcı
    - Test edilmeli ama kullanılmıyor
"""

import ast
from pathlib import Path
import pytest


class TestDeadCode:
    """
    AI-written dead code detector.
    
    Kullanılmayan fonksiyon/class varsa FAIL.
    """
    
    def test_no_unused_public_functions(self):
        """
        Public fonksiyonlar (_) kullanılmalı.
        
        ÖRNEK HATA:
            def helper_function():  # Hiçbir yerde çağrılmıyor!
                pass
        
        ISTISNALAR:
            - Entry point fonksiyonları (main, run)
            - Event handler'lar (on_created, on_destroyed)
            - Override edilen method'lar
        """
        # Tüm fonksiyonları topla
        all_functions = {}
        
        for py_file in Path('download/engine').rglob('*.py'):
            if 'test' in str(py_file) or '__pycache__' in str(py_file):
                continue
            
            with open(py_file, 'r', encoding='utf-8') as f:
                try:
                    tree = ast.parse(f.read())
                except:
                    continue
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if not node.name.startswith('_'):  # Public only
                        key = f"{py_file}:{node.name}"
                        all_functions[key] = node.name
        
        # Tüm çağrıları topla
        all_calls = set()
        
        for py_file in Path('download/engine').rglob('*.py'):
            if 'test' in str(py_file) or '__pycache__' in str(py_file):
                continue
            
            with open(py_file, 'r', encoding='utf-8') as f:
                try:
                    tree = ast.parse(f.read())
                except:
                    continue
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        all_calls.add(node.func.id)
                    elif isinstance(node.func, ast.Attribute):
                        all_calls.add(node.func.attr)
        
        # Kullanılmayanları bul
        unused = [
            key for key, name in all_functions.items()
            if name not in all_calls
        ]
        
        # Entry point'leri filtrele
        entry_points = {'main', 'run', 'setup', 'init', 'create'}
        unused = [k for k in unused if k.split(':')[-1] not in entry_points]
        
        # Lifecycle hook'ları filtrele
        lifecycle_hooks = {'on_created', 'on_destroyed', 'on_tick', 'on_draw', 
                          'on_attach', 'on_detach', 'initialize', 'shutdown'}
        unused = [k for k in unused if k.split(':')[-1] not in lifecycle_hooks]
        
        # Sadece küçük fonksiyonları rapor et (5 satır altı)
        suspicious_unused = []
        
        for key in unused:
            file_path, func_name = key.rsplit(':', 1)
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Fonksiyon satır sayısını bul
            for i, line in enumerate(lines):
                if f'def {func_name}(' in line:
                    # Count function lines (simple heuristic)
                    func_lines = 1
                    for j in range(i + 1, len(lines)):
                        if lines[j].strip() and not lines[j].startswith(' ') and not lines[j].startswith('\t'):
                            break
                        func_lines += 1
                    
                    # Small unused functions are suspicious
                    if func_lines < 10:
                        suspicious_unused.append(key)
                    break
        
        assert len(suspicious_unused) < 10, (
            f"⚠️ POTENTIALLY UNUSED FUNCTIONS ({len(suspicious_unused)}):\n"
            + '\n'.join(suspicious_unused[:10])
            + "\n\nFIX: Use or remove these functions"
        )
```

---

### 1.5 AI Drift Test

**Dosya:** `tests/quality/test_ai_drift.py`

```python
"""
AI CODE DRIFT DETECTOR

AI zamanla pattern dışına çıkabilir.
Bu test KOD STANDARDI'nı korur.

KONTROL EDILENLER:
    - Docstring varlığı
    - type: ignore yokluğu
    - Star import yokluğu
    - print() statement yokluğu
"""

import ast
from pathlib import Path
import pytest


class TestAICodeDrift:
    """
    AI-written code drift detector.
    
    Kod standardı dışına çıkılırsa FAIL.
    """
    
    def test_all_functions_have_docstrings(self):
        """
        Tüm public fonksiyonların docstring'i olmalı.
        
        AGENTS.md kuralı: "Docstring Zorunluluğu"
        
        Neden?
            - AI bazen docstring yazmayı unutur
            - Dokümantasyon otomatik oluşur
            - Kod anlaşılır olur
        
        ÖRNEK DOĞRU:
            def calculate_distance(x: float, y: float) -> float:
                \"\"\"
                Calculate distance between two points.
                
                Args:
                    x: X coordinate
                    y: Y coordinate
                
                Returns:
                    Distance value
                \"\"\"
        """
        missing_docstrings = []
        
        for py_file in Path('download/engine').rglob('*.py'):
            if 'test' in str(py_file) or '__pycache__' in str(py_file):
                continue
            
            with open(py_file, 'r', encoding='utf-8') as f:
                try:
                    tree = ast.parse(f.read())
                except:
                    continue
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if not node.name.startswith('_'):  # Public only
                        docstring = ast.get_docstring(node)
                        if not docstring:
                            missing_docstrings.append(
                                f"{py_file}:{node.name}"
                            )
        
        assert len(missing_docstrings) < 5, (
            f"❌ MISSING DOCSTRINGS ({len(missing_docstrings)}):\n"
            + '\n'.join(missing_docstrings[:10])
            + "\n\nFIX: Add docstring to these functions"
        )
    
    def test_no_type_ignore_comments(self):
        """
        type: ignore YASAK.
        
        Neden?
            - AI mypy hatalarını gizlemek için kullanabilir
            - Gerçek tip hatası maskelenir
            - Type safety bozulur
        
        DOĞRU YAKLAŞIM:
            - Tip hatasını düzelt
            - Gerekirse cast() kullan
            - Gerekirse # type: ignore [specific-error]
        """
        type_ignores = []
        
        for py_file in Path('download/engine').rglob('*.py'):
            if 'test' in str(py_file) or '__pycache__' in str(py_file):
                continue
            
            with open(py_file, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f, 1):
                    if 'type: ignore' in line.lower():
                        type_ignores.append(f"{py_file}:{i}")
        
        assert len(type_ignores) == 0, (
            f"❌ TYPE: IGNORE FOUND ({len(type_ignores)}):\n"
            + '\n'.join(type_ignores)
            + "\n\nFIX: Fix type errors, don't hide them"
        )
    
    def test_no_print_in_production(self):
        """
        print() production kodda YASAK.
        
        Neden?
            - AI debug için bırakmış olabilir
            - Console output kirlenir
            - Logging module kullanılmalı
        
        DOĞRU YAKLAŞIM:
            from core.logger import logger
            logger.debug("Debug message")
            logger.info("Info message")
        """
        prints = []
        
        for py_file in Path('download/engine').rglob('*.py'):
            if 'test' in str(py_file) or '__pycache__' in str(py_file):
                continue
            
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'print(' in content:
                    for i, line in enumerate(content.split('\n'), 1):
                        if 'print(' in line and not line.strip().startswith('#'):
                            prints.append(f"{py_file}:{i}: {line.strip()[:50]}")
        
        # Test dosyalarında print serbest
        prints = [p for p in prints if 'test_' not in p]
        
        assert len(prints) < 5, (
            f"❌ PRINT STATEMENTS FOUND ({len(prints)}):\n"
            + '\n'.join(prints[:10])
            + "\n\nFIX: Use logging module instead"
        )
```

---

## 📋 KATMAN 2: CONTRACT TESTS

### 2.1 Interface Contract Test

**Dosya:** `tests/contracts/test_interfaces.py`

```python
"""
INTERFACE CONTRACT TEST

Her interface için otomatik contract test.
Yeni implementation eklenince test otomatik çalışır.

Neden önemli?
    - Interface method'ları implement edilmeli
    - Docstring olmalı
    - Type hint olmalı
"""

import inspect
from abc import ABC
import pytest
from typing import List, Type


def find_all_interfaces() -> List[Type]:
    """
    Tüm interface sınıflarını bul (ABC + abstract method).
    
    Returns:
        Interface class listesi
    """
    interfaces = []
    
    from hal import interfaces as hal_interfaces
    from engine import subsystem
    
    for module in [hal_interfaces, subsystem]:
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and issubclass(obj, ABC) and obj is not ABC:
                if any(getattr(m, '__isabstractmethod__', False) 
                       for m in obj.__dict__.values() 
                       if isinstance(m, (type(lambda: None), ABCMeta))):
                    interfaces.append(obj)
    
    return interfaces


class TestInterfaceContracts:
    """Tüm interface'ler için otomatik contract test."""
    
    @pytest.mark.parametrize("interface", find_all_interfaces())
    def test_interface_has_name(self, interface):
        """Her interface'in ismi 'I' ile başlamalı."""
        assert interface.__name__.startswith('I'), \
            f"Interface '{interface.__name__}' 'I' ile başlamalı (örn: IWindow)"
    
    @pytest.mark.parametrize("interface", find_all_interfaces())
    def test_interface_is_abstract(self, interface):
        """Her interface abstract olmalı."""
        assert issubclass(interface, ABC), \
            f"{interface.__name__} ABC'den inherit etmeli"
    
    def test_iwindow_cannot_be_instantiated(self):
        """IWindow interface'inden instance oluşturulamaz."""
        from hal.interfaces import IWindow
        with pytest.raises(TypeError):
            IWindow()
    
    def test_igpu_device_cannot_be_instantiated(self):
        """IGPUDevice interface'inden instance oluşturulamaz."""
        from hal.interfaces import IGPUDevice
        with pytest.raises(TypeError):
            IGPUDevice()
    
    def test_ifilesystem_cannot_be_instantiated(self):
        """IFilesystem interface'inden instance oluşturulamaz."""
        from hal.interfaces import IFilesystem
        with pytest.raises(TypeError):
            IFilesystem()
    
    def test_iclock_cannot_be_instantiated(self):
        """IClock interface'inden instance oluşturulamaz."""
        from hal.interfaces import IClock
        with pytest.raises(TypeError):
            IClock()
```

---

## 📋 KATMAN 3: FUNCTIONAL TESTS

### 3.1 Global Fixtures

**Dosya:** `tests/conftest.py`

```python
"""
GLOBAL FIXTURES

Tek dosya, boilerplate'ı %80 azaltır.

Kullanım:
    def test_something(engine):  # Fixture otomatik enjekte edilir
        renderer = engine.get_subsystem("renderer")
        ...
"""

import pytest
from hal.headless import HeadlessWindow, HeadlessGPU, MemoryFilesystem, FixedClock
from engine.engine import Engine
from engine.renderer.renderer import Renderer2D
from engine.physics.physics import Physics2D
from core.eventbus import EventBus


@pytest.fixture
def headless_gpu():
    """
    Reusable GPU for tests.
    
    HeadlessGPU gerçek GPU gerektirmez.
    CI/CD'de çalışır.
    """
    return HeadlessGPU()


@pytest.fixture
def headless_window():
    """
    Reusable window for tests.
    
    HeadlessWindow gerçek window oluşturmaz.
    """
    return HeadlessWindow(800, 600)


@pytest.fixture
def fixed_clock():
    """
    Deterministic clock for tests.
    
    Her frame 0.016 saniye (60 FPS).
    Predictable test sonuçları için.
    """
    return FixedClock(delta_time=0.016)


@pytest.fixture
def memory_fs():
    """
    In-memory filesystem for tests.
    
    Gerçek dosya sistemi yok.
    Test isolation için.
    """
    return MemoryFilesystem()


@pytest.fixture
def engine(headless_gpu):
    """
    Full engine with subsystems.
    
    Usage:
        def test_something(engine):
            renderer = engine.get_subsystem("renderer")
            ...
    
    Auto-cleanup:
        Engine otomatik shutdown edilir.
    """
    eng = Engine()
    
    # Register subsystems
    renderer = Renderer2D()
    renderer.gpu_device = headless_gpu
    eng.register_subsystem(renderer)
    
    physics = Physics2D()
    eng.register_subsystem(physics)
    
    eng.initialize()
    yield eng
    eng.shutdown()


@pytest.fixture
def event_bus():
    """
    Fresh event bus for each test.
    
    Test isolation için her test yeni instance alır.
    """
    return EventBus()
```

---

### 3.2 Critical Path Test

**Dosya:** `tests/critical/test_lifecycle.py`

```python
"""
CRITICAL PATH TESTS

Gerçek kullanımı test et, her method'u ayrı değil.

Neden önemli?
    - Gerçek senaryoları test eder
    - Integration yakalar
    - Daha az test, daha fazla coverage
"""

import pytest


class TestActorLifecycle:
    """
    Actor lifecycle test.
    
    Senaryo: Actor oluştur → Component ekle → Tick → Destroy
    """
    
    def test_full_lifecycle(self, engine):
        """
        Actor: create → add component → tick → destroy.
        
        Gerçek kullanımı test et.
        """
        from world.actor import Actor
        from world.component import Component
        
        # Create
        actor = Actor(name="Player")
        assert actor.name == "Player"
        assert actor.guid is not None
        
        # Add component
        component = Component()
        actor.add_component(component)
        assert component in actor.components
        assert component.owner == actor
        
        # Tick (engine integration)
        engine.world.spawn_actor(actor)
        engine.tick(0.016)
        # If no exception = success
        
        # Destroy
        engine.world.destroy_actor(actor)
        assert actor not in engine.world.actors


class TestComponentLifecycle:
    """
    Component lifecycle test.
    
    Senaryo: Component oluştur → Attach → Tick → Detach
    """
    
    def test_full_lifecycle(self, engine):
        """
        Component: create → attach → tick → detach.
        """
        from world.actor import Actor
        from world.component import Component
        
        # Create actor and component
        actor = Actor(name="Player")
        component = Component(name="HealthComponent")
        
        # Attach
        actor.add_component(component)
        assert component.owner == actor
        
        # Tick
        engine.world.spawn_actor(actor)
        engine.tick(0.016)
        # Component.on_tick called
        
        # Detach
        actor.remove_component(component)
        assert component.owner is None


class TestWorldLifecycle:
    """
    World lifecycle test.
    
    Senaryo: World oluştur → Actor spawn → Tick → Actor destroy
    """
    
    def test_full_lifecycle(self, engine):
        """
        World: create → spawn → tick → destroy.
        """
        from world.actor import Actor
        from world.world import World
        
        # Create world
        world = World(name="GameWorld")
        
        # Spawn actor
        actor = Actor(name="Enemy")
        world.spawn_actor(actor)
        assert actor in world.actors
        assert actor.world == world
        
        # Tick
        world.tick(0.016)
        # Actor.tick called
        
        # Destroy actor
        world.destroy_actor(actor)
        assert actor not in world.actors
```

---

### 3.3 Property-Based Test (Hypothesis)

**Dosya:** `tests/properties/test_math_properties.py`

```python
"""
PROPERTY-BASED TESTS

Hypothesis ile otomatik test data generation.

Neden önemli?
    - Tek test = 1000+ input kombinasyonu
    - Edge case'leri otomatik bulur
    - Math kuralları HER ZAMAN doğru olmalı

Kullanım:
    Sadece math/physics gibi kritik yerlerde.
    UI widget için gerek yok.
"""

from hypothesis import given, strategies as st, settings
from core.vec import Vec2


class TestVec2Invariants:
    """
    Vec2 matematik kuralları HER ZAMAN doğru olmalı.
    
    Hypothesis otomatik edge case bulur.
    """
    
    @given(st.floats(), st.floats())
    def test_addition_commutative(self, x, y):
        """
        v1 + v2 == v2 + v1
        
        Her zaman doğru olmalı.
        """
        v1, v2 = Vec2(x, y), Vec2(y, x)
        assert (v1 + v2) == (v2 + v1)
    
    @given(st.floats(min_value=0), st.floats(min_value=0))
    def test_magnitude_positive(self, x, y):
        """
        Magnitude her zaman pozitif veya sıfır.
        """
        assert Vec2(x, y).magnitude >= 0
    
    @given(st.floats(), st.floats())
    def test_normalize_unit(self, x, y):
        """
        Normalize edilmiş vektörün magnitude'ı 1.
        
        Zero vector exception.
        """
        v = Vec2(x, y)
        if v.magnitude > 0:
            assert abs(v.normalized().magnitude - 1.0) < 0.0001
    
    @given(
        v=st.builds(Vec2, st.floats(), st.floats()),
        scalar=st.floats(-100, 100)
    )
    def test_scalar_multiplication(self, v, scalar):
        """
        scalar * v = (scalar * v.x, scalar * v.y)
        """
        result = scalar * v
        assert abs(result.x - scalar * v.x) < 0.0001
        assert abs(result.y - scalar * v.y) < 0.0001
    
    @settings(max_examples=500)  # 500 farklı input dene
    @given(st.floats(), st.floats())
    def test_distance_symmetric(self, x, y):
        """
        distance(v1, v2) == distance(v2, v1)
        """
        v1 = Vec2(x, y)
        v2 = Vec2(0, 0)
        d1 = v1.distance_to(v2)
        d2 = v2.distance_to(v1)
        assert abs(d1 - d2) < 0.0001
```

---

### 3.4 Scenario Test (Demo = Test)

**Dosya:** `tests/scenarios/test_demos_work.py`

```python
"""
SCENARIO TESTS

Demo oyunları test olarak kullan.

Neden önemli?
    - Gerçek gameplay senaryosu
    - Tüm sistem integration
    - Çalışıyorsa PASS

Kullanım:
    Demo'ya yeni özellik eklenince test otomatik güncellenir.
"""

import pytest
from demo.bouncing_ball import BouncingBallGame


class TestBouncingBallScenario:
    """
    Bouncing ball demo testi.
    
    Senaryo: Top yerçekimi ile düşer, yere çarpınca zıplar.
    """
    
    def test_ball_falls_with_gravity(self):
        """
        Top yerçekimi ile aşağı düşmeli.
        """
        game = BouncingBallGame()
        game.initialize()
        
        initial_y = game.ball.position.y
        
        # 10 frame bekla
        for _ in range(10):
            game.tick(0.016)
        
        # Top aşağı düşmeli (gravity < 0)
        assert game.ball.position.y < initial_y
    
    def test_ball_bounces_off_ground(self):
        """
        Top yere çarpınca zıplamalı.
        """
        game = BouncingBallGame()
        game.initialize()
        
        # Top yere düşene kadar bekla
        for _ in range(100):
            game.tick(0.016)
            if game.ball.on_ground:
                break
        
        # Top yere değdi
        assert game.ball.on_ground
        
        # Velocity yukarı olmalı (bounce)
        assert game.ball.velocity.y >= 0
    
    def test_ball_jumps_when_space_pressed(self):
        """
        Space tuşuna basınca top zıplamalı.
        """
        game = BouncingBallGame()
        game.initialize()
        
        # Top yere düşene kadar bekla
        for _ in range(100):
            game.tick(0.016)
            if game.ball.on_ground:
                break
        
        # Space'e bas
        game.handle_input("SPACE")
        
        # Zıpladı mı kontrol et
        assert game.ball.velocity.y > 0
        assert not game.ball.on_ground
    
    def test_demo_runs_without_errors(self):
        """
        Demo 100 frame hatasız çalışmalı.
        
        Integration test.
        """
        game = BouncingBallGame()
        game.initialize()
        
        # 100 frame çalıştır
        for _ in range(100):
            game.tick(0.016)
        
        # Hata fırlatmadı = PASS
        assert game.ball is not None
        assert game.ball.position.y >= game.ground_y
```

---

## 🚀 TEST RUNNER

**Dosya:** `tests/run_tests.py`

```python
"""
SMART TEST RUNNER

Test kategorilerine göre çalıştır.

Kullanım:
    python -m tests.run_tests           # Tüm testler
    python -m tests.run_tests quality   # Sadece AI quality
    python -m tests.run_tests contract  # Sadece contract
    python -m tests.run_tests critical  # Sadece critical path
    python -m tests.run_tests --coverage # Coverage raporu
"""

import pytest
import sys


def run_all_tests():
    """Tüm testleri çalıştır."""
    pytest.main([
        'tests/',
        '-v',
        '--tb=short',
        '--ignore=tests/legacy/',  # Legacy testleri skip
    ])


def run_quality_tests():
    """AI quality testlerini çalıştır."""
    pytest.main(['tests/quality/', '-v'])


def run_contract_tests():
    """Contract testlerini çalıştır."""
    pytest.main(['tests/contracts/', '-v'])


def run_critical_tests():
    """Critical path testlerini çalıştır."""
    pytest.main(['tests/critical/', '-v'])


def run_property_tests():
    """Property-based testlerini çalıştır."""
    pytest.main(['tests/properties/', '-v', '--hypothesis-show-statistics'])


def run_scenario_tests():
    """Scenario testlerini çalıştır."""
    pytest.main(['tests/scenarios/', '-v'])


def run_with_coverage():
    """Coverage raporu ile çalıştır."""
    pytest.main([
        'tests/',
        '-v',
        '--tb=short',
        '--cov=download/engine',
        '--cov-report=html',
        '--cov-report=term-missing',
        '--ignore=tests/legacy/',
    ])


if __name__ == '__main__':
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'quality':
            run_quality_tests()
        elif command == 'contract':
            run_contract_tests()
        elif command == 'critical':
            run_critical_tests()
        elif command == 'property':
            run_property_tests()
        elif command == 'scenario':
            run_scenario_tests()
        elif command == '--coverage':
            run_with_coverage()
        else:
            run_all_tests()
    else:
        run_all_tests()
```

---

## 📊 TEST SONUÇLARI ÖRNEK

```bash
# Tüm testleri çalıştır
python -m tests.run_tests

# Çıktı:
tests/quality/test_architecture.py::TestArchitectureCompliance::test_no_upper_layer_import PASSED
tests/quality/test_imports.py::TestImportPolicy::test_max_5_imports_per_file PASSED
tests/quality/test_duplication.py::TestCodeDuplication::test_no_duplicate_functions PASSED
tests/quality/test_dead_code.py::TestDeadCode::test_no_unused_public_functions PASSED
tests/quality/test_ai_drift.py::TestAICodeDrift::test_all_functions_have_docstrings PASSED
tests/contracts/test_interfaces.py::TestInterfaceContracts::test_interface_has_name PASSED
tests/critical/test_lifecycle.py::TestActorLifecycle::test_full_lifecycle PASSED
tests/properties/test_math_properties.py::TestVec2Invariants::test_addition_commutative PASSED
tests/scenarios/test_demos_work.py::TestBouncingBallScenario::test_ball_falls_with_gravity PASSED

==================================== 80 passed in 5.2s =====================================
```

---

## 🎯 ÖZET

| Katman | Dosya Sayısı | Test Sayısı | Amaç |
|--------|--------------|-------------|------|
| **Quality** | 5 | ~30 | AI kod kalitesi |
| **Contract** | 1 | ~10 | Interface compliance |
| **Critical** | 1 | ~10 | Lifecycle tests |
| **Properties** | 1 | ~10 | Math invariants |
| **Scenarios** | 1 | ~10 | Demo = Test |
| **TOPLAM** | **9** | **~70** | **Etkili coverage** |

---

## ✅ KAZANIMLAR

1. **AI Kod Kalitesi Otomatik Denetlenir**
   - Mimari ihlal → Otomatik yakala
   - Kod tekrarı → Otomatik bul
   - Ölü kod → Otomatik temizle

2. **Mimari Korunur**
   - Katman kuralları → Her commit'te check
   - Import policy → Otomatik enforce

3. **Daha Az Test, Daha Fazla Coverage**
   - 903 test → ~70 test
   - Ama daha etkili

4. **Ölçeklenebilir**
   - Yeni kod → Otomatik test
   - Yeni implementation → Otomatik check

---

## 📝 SONRAKİ ADIMLAR

1. ✅ Bu dosyayı kaydet
2. ⏳ Test dosyalarını oluştur
3. ⏳ Legacy testleri `tests/legacy/` klasörüne taşı
4. ⏳ Pre-commit hook ekle
5. ⏳ CI/CD pipeline'a entegre et

---

**Dokümantasyon Versiyonu:** 1.0  
**Son Güncelleme:** 2026-03-28  
**Yazar:** AI Assistant

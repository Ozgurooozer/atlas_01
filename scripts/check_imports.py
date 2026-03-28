#!/usr/bin/env python3
"""
Import Kural Kontrolü
AGENT_RULES.md:
  - 1.1 Yukarı bağımlılık yok
  - 1.3 Max 5 import
  - 1.4 Star import yok
"""

import ast
import sys
from pathlib import Path

# Katman tanımları
LAYERS = {
    "hal": 0,
    "core": 1,
    "engine": 2,
    "world": 3,
    "game": 4,
    "scripting": 5,
    "ui": 6,
    "editor": 7,
}

# stdlib modülleri (katman kontrolü dışı)
STDLIB = {
    "abc", "argparse", "ast", "asyncio", "collections", "contextlib",
    "copy", "dataclasses", "datetime", "enum", "functools", "gc",
    "hashlib", "importlib", "inspect", "io", "itertools", "json",
    "logging", "math", "mmap", "operator", "os", "pathlib", "pickle",
    "platform", "random", "re", "shutil", "signal", "socket", "sqlite3",
    "stat", "string", "struct", "subprocess", "sys", "tempfile", "threading",
    "time", "traceback", "types", "typing", "unittest", "uuid", "warnings",
    "weakref", "xml", "zipfile", "__future__",
}


def get_layer(file_path: Path) -> int:
    """Dosyanın katman numarasını döndür."""
    path_str = str(file_path)
    for name, layer in LAYERS.items():
        if f"/{name}/" in path_str or f"\\{name}\\" in path_str:
            return layer
    return -1


def get_module_layer(module: str) -> int:
    """Import edilen modülün katmanını bul."""
    # stdlib kontrolü
    top_level = module.split(".")[0]
    if top_level in STDLIB:
        return -2  # stdlib işaretçisi

    # third-party kontrolü
    third_party = {"pyglet", "moderngl", "pymunk", "PIL", "msgspec", "watchdog", "dearpygui"}
    if top_level in third_party:
        return -3  # third-party işaretçisi

    # engine modülü kontrolü
    for name, layer in LAYERS.items():
        if module.startswith(name) or module.startswith(f"engine.{name}"):
            return layer

    return -1


def check_file(file_path: Path) -> list[str]:
    """Tek dosyayı kontrol et."""
    errors = []
    source_layer = get_layer(file_path)

    if source_layer < 0:
        return errors  # Katman dışı dosya

    try:
        with open(file_path, encoding="utf-8") as f:
            source = f.read()
        tree = ast.parse(source)
    except (SyntaxError, UnicodeDecodeError) as e:
        return [f"{file_path}: Parse hatası: {e}"]

    imports = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                module = alias.name
                imports.append(module)

                # Star import kontrolü
                if alias.name == "*":
                    errors.append(f"{file_path}: Star import YASAK (Kural 1.4)")

        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            imports.append(module)

            # Star import kontrolü
            for alias in node.names:
                if alias.name == "*":
                    errors.append(
                        f"{file_path}: Star import YASAK: "
                        f"from {module} import * (Kural 1.4)"
                    )

            # Yukarı bağımlılık kontrolü
            target_layer = get_module_layer(module)
            if target_layer >= 0 and target_layer > source_layer:
                errors.append(
                    f"{file_path}: Yukarı bağımlılık YASAK (Kural 1.1): "
                    f"Layer {source_layer} → Layer {target_layer} ({module})"
                )

    # Import çeşitliliği kontrolü
    unique_modules = set()
    for imp in imports:
        top_level = imp.split(".")[0]
        if top_level not in STDLIB:
            unique_modules.add(top_level)

    if len(unique_modules) > 5:
        errors.append(
            f"{file_path}: Import sınırı aşıldı (Kural 1.3): "
            f"{len(unique_modules)} > 5 modül - dosyayı böl"
        )

    return errors


def main():
    """Ana kontrol fonksiyonu."""
    errors = []

    # engine klasörünü kontrol et
    engine_path = Path("engine")
    if not engine_path.exists():
        print("⚠️ engine/ klasörü bulunamadı, kontrol atlanıyor")
        sys.exit(0)

    for py_file in engine_path.rglob("*.py"):
        file_errors = check_file(py_file)
        errors.extend(file_errors)

    if errors:
        print("\n❌ İMPORT KURAL İHLALLERİ:\n")
        for err in errors:
            print(f"  {err}")
        print(f"\nToplam {len(errors)} hata bulundu.")
        print("AGENT_RULES.md'e uygun düzeltme yapın.\n")
        sys.exit(1)

    print("✅ Tüm import kuralları geçti")
    sys.exit(0)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Layer import kontrolü - AGENT_RULES.md Section 1.1

KATMANLAR:
  0 = HAL
  1 = Core
  2 = Engine
  3 = World
  4 = Game
  5 = Scripting
  6 = UI
  7 = Editor

KURAL: Bir dosya SADECE kendi katmanındaki veya ALT katmanlardan import yapabilir.
       Üst katmandan import YASAKTIR.
"""

import ast
import sys
from pathlib import Path
from typing import List, Tuple

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


def get_layer(file_path: Path) -> int:
    """
    Dosyanın katmanını belirle.

    Engine klasör yapısı:
      engine/hal/       → Layer 0
      engine/core/      → Layer 1
      engine/engine/    → Layer 2
      engine/world/     → Layer 3
      engine/game/      → Layer 4
      engine/ui/        → Layer 6
      engine/editor/    → Layer 7

    Args:
        file_path: Dosya yolu

    Returns:
        Katman numarası, katman dışı ise -1
    """
    parts = file_path.parts

    # En yakın (son) layer'ı bul
    found_layer = -1
    for part in parts:
        if part in LAYERS:
            found_layer = LAYERS[part]

    return found_layer


def get_imports(file_path: Path) -> List[str]:
    """
    Dosyadaki tüm import'ları bul.

    Args:
        file_path: Dosya yolu

    Returns:
        Import listesi
    """
    try:
        content = file_path.read_text()
        tree = ast.parse(content)
    except Exception:
        return []

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)

    return imports


def check_file(file_path: Path) -> List[Tuple[str, str]]:
    """
    Tek dosyayı kontrol et.

    Args:
        file_path: Dosya yolu

    Returns:
        Hata listesi [(dosya, hata_mesajı)]
    """
    errors = []
    file_layer = get_layer(file_path)

    if file_layer < 0:
        return errors  # Katman dışı, kontrol etme

    imports = get_imports(file_path)

    for imp in imports:
        # Proje içi import mu?
        imp_layer = -1
        for layer_name, layer_num in LAYERS.items():
            if imp == layer_name or imp.startswith(f"{layer_name}."):
                imp_layer = layer_num
                break

        # Üst katman import'u mu?
        if imp_layer > file_layer:
            errors.append((
                str(file_path),
                f"UPPER LAYER IMPORT: Layer {file_layer} -> Layer {imp_layer} ({imp})"
            ))

    return errors


def main():
    """Tüm Python dosyalarını kontrol et."""
    # Engine klasörünü bul
    engine_path = Path(__file__).parent.parent
    
    if not engine_path.exists():
        print("ERROR: engine/ folder not found")
        sys.exit(1)

    all_errors = []

    for py_file in engine_path.rglob("*.py"):
        # Test, scripts ve demo dosyalarını atla
        # Demo: tüm katmanları serbestçe kullanabilir
        if "tests" in str(py_file) or "scripts" in str(py_file) or "demo" in str(py_file):
            continue
        errors = check_file(py_file)
        all_errors.extend(errors)

    if all_errors:
        print("=" * 60)
        print("LAYER IMPORT VIOLATIONS DETECTED!")
        print("=" * 60)
        for file_path, error in all_errors:
            print(f"\n{file_path}")
            print(f"  {error}")
        print("\n" + "=" * 60)
        print("AGENT_RULES.md Section 1.1: Ust katmandan import YASAK!")
        print("=" * 60)
        sys.exit(1)
    else:
        print("OK: All layer imports valid")
        sys.exit(0)


if __name__ == "__main__":
    main()

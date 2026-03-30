#!/usr/bin/env python3
"""
Star import kontrolü - AGENT_RULES.md Section 1.4

KURAL: from module import * KESİNLİKLE YASAK
"""

import ast
import sys
from pathlib import Path
from typing import List, Tuple


def check_file(file_path: Path) -> List[Tuple[str, int, str]]:
    """
    Dosyada star import var mı kontrol et.

    Args:
        file_path: Dosya yolu

    Returns:
        Hata listesi [(dosya, satır, modül)]
    """
    errors = []

    try:
        content = file_path.read_text()
        tree = ast.parse(content)
    except Exception:
        return errors

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name == "*":
                    module = node.module or "(unknown)"
                    errors.append((str(file_path), node.lineno, module))

    return errors


def main():
    """Tüm Python dosyalarını kontrol et."""
    engine_path = Path(__file__).parent.parent
    all_errors = []

    for py_file in engine_path.rglob("*.py"):
        # __init__.py dosyalarında star import'a izin var (re-export için)
        if py_file.name == "__init__.py":
            continue
        errors = check_file(py_file)
        all_errors.extend(errors)

    if all_errors:
        print("=" * 60)
        print("STAR IMPORT DETECTED (BANNED!)")
        print("=" * 60)
        for file_path, line, module in all_errors:
            print(f"\n{file_path}:{line}")
            print(f"  Found: from {module} import *")
        print("\n" + "=" * 60)
        print("AGENT_RULES.md Section 1.4:")
        print("from module import * KESINLIKLE YASAK")
        print("=" * 60)
        sys.exit(1)
    else:
        print("OK: No star imports found")
        sys.exit(0)


if __name__ == "__main__":
    main()

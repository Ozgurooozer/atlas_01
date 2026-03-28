#!/usr/bin/env python3
"""
Mock kullanım kontrolü - AGENT_RULES.md Section 4.3

KURAL: Mock kullanımı YASAK - gerçek implementation test et.
       Integration test yoluyla gerçek bağımlılıkları kullan.
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple

FORBIDDEN_PATTERNS = [
    (r"from\s+unittest\.mock\s+import", "from unittest.mock import"),
    (r"from\s+mock\s+import", "from mock import"),
    (r"@patch\s*\(", "@patch decorator"),
    (r"@mock\.", "@mock decorator"),
    (r"\bMock\s*\(", "Mock()"),
    (r"\bMagicMock\s*\(", "MagicMock()"),
    (r"patch\.object\s*\(", "patch.object()"),
    (r"\bMock\s*:", "Mock type hint"),
]


def check_file(file_path: Path) -> List[Tuple[str, int, str]]:
    """
    Dosyada mock kullanımı var mı kontrol et.

    Args:
        file_path: Dosya yolu

    Returns:
        Hata listesi [(dosya, satır, pattern)]
    """
    errors = []

    try:
        content = file_path.read_text()
        lines = content.split("\n")
    except Exception:
        return errors

    for pattern, description in FORBIDDEN_PATTERNS:
        for i, line in enumerate(lines, 1):
            if re.search(pattern, line):
                # Yorum satırlarını atla
                stripped = line.strip()
                if stripped.startswith("#"):
                    continue
                errors.append((str(file_path), i, description))

    return errors


def main():
    """Tüm test dosyalarını kontrol et."""
    engine_path = Path(__file__).parent.parent
    all_errors = []

    for py_file in engine_path.rglob("*.py"):
        # Sadece test dosyalarını kontrol et
        if "tests" not in str(py_file):
            continue
        errors = check_file(py_file)
        all_errors.extend(errors)

    if all_errors:
        print("=" * 60)
        print("MOCK USAGE DETECTED (BANNED!)")
        print("=" * 60)
        for file_path, line, pattern in all_errors:
            print(f"\n{file_path}:{line}")
            print(f"  Found: {pattern}")
        print("\n" + "=" * 60)
        print("AGENT_RULES.md Section 4.3:")
        print("Mock YASAK - Gercek test double kullan!")
        print("Ornek: HeadlessGPU() Mock yerine")
        print("=" * 60)
        sys.exit(1)
    else:
        print("OK: No mock usage found")
        sys.exit(0)


if __name__ == "__main__":
    main()

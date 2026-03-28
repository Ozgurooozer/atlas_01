#!/usr/bin/env python3
"""
İlgili testleri çalıştır - AGENT_RULES.md Section 4.1

Değişen dosyalarla ilgili testleri otomatik bul ve çalıştır.
"""

import subprocess
import sys
from pathlib import Path
from typing import List


def get_test_file(source_file: str) -> str:
    """
    Kaynak dosyaya karşılık gelen test dosyasını bul.

    Args:
        source_file: Kaynak dosya yolu

    Returns:
        Test dosyası yolu
    """
    path = Path(source_file)

    # Zaten test dosyası mı?
    if "tests" in str(path):
        return source_file

    # Modül yolunu test yoluna çevir
    # core/scheduler.py -> tests/core/test_scheduler.py
    parts = path.parts

    if "engine" in parts:
        idx = parts.index("engine")
        relative = list(parts[idx + 1:])  # engine sonrası
        test_path = Path("engine") / "tests" / Path(*relative)
        test_path = test_path.parent / f"test_{test_path.name}"
        return str(test_path)

    return ""


def run_tests(test_files: List[str]) -> bool:
    """
    Test dosyalarını çalıştır.

    Args:
        test_files: Test dosyası listesi

    Returns:
        Başarılı mı?
    """
    if not test_files:
        print("No related tests found")
        return True

    print("=" * 60)
    print("RUNNING RELATED TESTS")
    print("=" * 60)

    # Engine klasörüne geç
    engine_path = Path(__file__).parent.parent

    cmd = [
        sys.executable,
        "-m",
        "pytest",
        *test_files,
        "-v",
        "--tb=short",
        "-x",  # İlk hatada dur
    ]

    result = subprocess.run(cmd, cwd=engine_path)

    return result.returncode == 0


def main():
    """Ana fonksiyon."""
    # Pass filenames from pre-commit
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="*", help="Changed files")
    args = parser.parse_args()

    test_files = []
    for file in args.files:
        test_file = get_test_file(file)
        if test_file and Path(test_file).exists():
            test_files.append(test_file)

    if not test_files:
        print("OK: No related tests to run")
        sys.exit(0)

    success = run_tests(test_files)

    if success:
        print("\nOK: All related tests passed")
        sys.exit(0)
    else:
        print("\nFAIL: Some tests failed")
        sys.exit(1)


if __name__ == "__main__":
    main()

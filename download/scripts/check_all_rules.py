#!/usr/bin/env python3
"""
AGENT_RULES.md uyumluluk kontrolü.

Tüm kuralları kontrol eden ana script.
"""

import subprocess
import sys
from pathlib import Path


def run_check(script_name: str, description: str) -> bool:
    """
    Tek bir kontrol script'ini çalıştır.

    Args:
        script_name: Script dosya adı
        description: Açıklama

    Returns:
        Başarılı mı?
    """
    scripts_path = Path(__file__).parent
    script_path = scripts_path / script_name

    print(f"\n{'='*60}")
    print(f"Checking: {description}")
    print('='*60)

    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=scripts_path.parent
    )

    return result.returncode == 0


def main():
    """Tüm kontrolleri çalıştır."""
    print("=" * 60)
    print("AGENT_RULES.md COMPLIANCE CHECK")
    print("=" * 60)

    checks = [
        ("check_layer_imports.py", "Layer Import Rules (Section 1.1)"),
        ("check_class_size.py", "Class Size Rules (Section 5.1)"),
        ("check_no_mock.py", "Mock Ban (Section 4.3)"),
        ("check_no_star_import.py", "Star Import Ban (Section 1.4)"),
    ]

    all_passed = True
    results = []

    for script, desc in checks:
        passed = run_check(script, desc)
        results.append((desc, passed))
        if not passed:
            all_passed = False

    # Özet
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    for desc, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {desc}")

    print("=" * 60)

    if all_passed:
        print("\nALL CHECKS PASSED!")
        sys.exit(0)
    else:
        print("\nSOME CHECKS FAILED!")
        print("Fix errors before commit.")
        sys.exit(1)


if __name__ == "__main__":
    main()

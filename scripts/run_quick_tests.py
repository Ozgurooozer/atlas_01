#!/usr/bin/env python3
"""
Hızlı Test Çalıştırıcı
Pre-commit için optimize edilmiş, sadece core testleri çalıştırır.
Hedef: < 60 saniye
"""

import subprocess
import sys
from pathlib import Path


def run_tests():
    """Core testlerini çalıştır."""
    test_path = Path("engine/tests/core")

    if not test_path.exists():
        print("⚠️ engine/tests/core klasörü bulunamadı")
        return 0

    # pytest komutu
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        str(test_path),
        "-x",           # İlk hatada dur
        "-q",           # Quiet mode
        "--tb=short",   # Kısa traceback
        "--no-header",  # Header'ı atla
    ]

    print("🏃 Core testleri çalışıyor...\n")

    result = subprocess.run(cmd, capture_output=True, text=True)

    # Sonuçları yazdır
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)

    if result.returncode != 0:
        print("\n❌ Test başarısız - commit engellendi")
        print("Testleri düzeltip tekrar deneyin.\n")
        return 1

    print("\n✅ Core testleri geçti\n")
    return 0


def main():
    """Ana fonksiyon."""
    exit_code = run_tests()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Tüm kalite kontrollerini tek komutta çalıştır.
Çıktı: PASSED veya FAILED + detaylı rapor

Kullanım:
    python scripts/check_all_quality.py

Her adımdan sonra çalıştırılacak (qwen_kurallar.md)
"""

import subprocess
import sys
from pathlib import Path

def print_header(text: str) -> None:
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}")

def run_check(name: str, command: str, expected_zero: bool = True) -> tuple[bool, str]:
    """Kalite kontrolü çalıştır, sonucu döndür."""
    print(f"\n▶️  Running: {name}")
    print(f"   Command: {command}")
    
    result = subprocess.run(
        command, 
        shell=True, 
        capture_output=True, 
        text=True,
        cwd=Path(__file__).parent.parent
    )
    
    output = result.stdout + result.stderr
    
    # Check based on expectation
    if expected_zero:
        # Expect return code 0 (no issues found)
        passed = result.returncode == 0
    else:
        # Some commands return non-zero even on success
        passed = "FAILED" not in output.upper() and "ERROR" not in output.upper()
    
    if passed:
        print(f"   ✅ PASSED")
    else:
        print(f"   ❌ FAILED")
        if output.strip():
            # Show first 500 chars of output
            preview = output[:500]
            if len(output) > 500:
                preview += "\n... (output truncated)"
            print(f"   Output:\n{preview}")
    
    return passed, output

def check_class_sizes() -> tuple[bool, str]:
    """Sınıf boyutlarını kontrol et (>200 satır var mı?)."""
    print(f"\n▶️  Checking class sizes (>200 lines)...")
    
    # Find large files
    result = subprocess.run(
        "find . -name '*.py' -not -path './tests/*' -not -path './demo/*' -exec wc -l {} \\; | sort -rn | head -20",
        shell=True,
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent
    )
    
    output = result.stdout
    violations = []
    
    for line in output.strip().split('\n'):
        if line.strip():
            parts = line.split()
            if len(parts) >= 2:
                try:
                    lines = int(parts[0])
                    filepath = parts[-1]
                    if lines > 200:
                        violations.append(f"   {filepath}: {lines} lines")
                except ValueError:
                    pass
    
    if violations:
        print(f"   ❌ FAILED: Found {len(violations)} files >200 lines")
        for v in violations[:10]:  # Show first 10
            print(v)
        if len(violations) > 10:
            print(f"   ... and {len(violations) - 10} more")
        return False, "\n".join(violations)
    else:
        print(f"   ✅ PASSED: All files ≤200 lines")
        return True, ""

def check_complexity() -> tuple[bool, str]:
    """Cyclomatic complexity kontrolü (>10 var mı?)."""
    print(f"\n▶️  Checking cyclomatic complexity (>10)...")
    
    result = subprocess.run(
        "radon cc -s -a --min C . 2>&1",
        shell=True,
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent
    )
    
    output = result.stdout
    
    # Count violations (exclude test files and demo files)
    violations = []
    for line in output.strip().split('\n'):
        if line.strip() and 'tests/' not in line and 'demo/' not in line:
            if any(x in line for x in ['C (', 'D (', 'E (', 'F (']):
                violations.append(f"   {line.strip()}")
    
    if violations:
        print(f"   ❌ FAILED: Found {len(violations)} functions with complexity >10")
        for v in violations[:10]:
            print(v)
        if len(violations) > 10:
            print(f"   ... and {len(violations) - 10} more")
        return False, "\n".join(violations)
    else:
        print(f"   ✅ PASSED: All functions have complexity ≤10")
        return True, ""

def main():
    """Ana kontrol fonksiyonu."""
    print_header("PRODUCTION QUALITY CHECK")
    print("Running all quality checks as per qwen_kurallar.md")
    
    checks = [
        # Test checks
        ("Tests GREEN", "pytest tests/ -q --tb=no 2>&1", True),
        
        # Linting checks
        ("No unused imports", "ruff check . --select F401 2>&1", True),
        ("No star imports", "ruff check . --select F403 2>&1", True),
        
        # Custom checks
        ("No mocks", "python scripts/check_no_mock.py 2>&1", True),
        ("Import rules OK", "python scripts/check_imports.py 2>&1", True),
        ("No layer violations", "python scripts/pre_commit/check_layer_violations.py 2>&1", True),
        
        # Type checking
        ("Type coverage OK", "mypy . --ignore-missing-imports 2>&1", True),
    ]
    
    results = []
    
    # Run standard checks
    for name, command, expected_zero in checks:
        passed, _ = run_check(name, command, expected_zero)
        results.append((name, passed))
    
    # Run custom checks
    class_size_passed, _ = check_class_sizes()
    results.append(("Class sizes <200", class_size_passed))
    
    complexity_passed, _ = check_complexity()
    results.append(("Complexity <10", complexity_passed))
    
    # Summary
    print_header("SUMMARY")
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for name, passed in results:
        status = "✅" if passed else "❌"
        print(f"{status} {name}")
    
    print(f"\n{'='*70}")
    print(f"Total: {passed_count}/{total_count} checks passed")
    print(f"{'='*70}")
    
    if all(passed for _, passed in results):
        print("\n🎉 ALL CHECKS PASSED! Production ready! 🚀")
        return 0
    else:
        failed_count = total_count - passed_count
        print(f"\n❌ {failed_count} check(s) FAILED!")
        print("\n⚠️  İHLAL TESPİT EDİLDİ!")
        print("   1. DURDUR")
        print("   2. İhlali düzelt")
        print("   3. Tekrar test et")
        print("   4. Devam et")
        print("\n   qwen_kurallar.md bölüm 9'u oku.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

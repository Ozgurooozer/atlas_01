"""Pre-commit hook runner - orchestrates all code quality checks."""
import sys
import subprocess
from pathlib import Path


def run_check(script_name: str, description: str) -> bool:
    """Run a single checker script."""
    print(f"\n{'='*60}")
    print(f"[CHECK] {description}")
    print("=" * 60)
    
    script_path = Path(__file__).parent / script_name
    
    if not script_path.exists():
        print(f"  [WARN] Script not found: {script_path}")
        return True
    
    result = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True,
        text=True,
        cwd=str(script_path.parent)
    )
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    
    return result.returncode == 0


def main() -> int:
    """Run all pre-commit checks."""
    print("""
╔══════════════════════════════════════════════════════════╗
║         PRE-COMMIT CODE QUALITY CHECKS                   ║
║  Enforcing: 7-Layer Architecture & Agent Rules          ║
╚══════════════════════════════════════════════════════════╝
""")
    
    checks = [
        ("check_layer_violations.py", "Layer Violation Check"),
        ("check_import_rules.py", "Import Rules Check"),
        ("check_test_coverage.py", "Test Coverage Check"),
    ]
    
    all_passed = True
    
    for script, description in checks:
        if not run_check(script, description):
            all_passed = False
    
    print(f"\n{'='*60}")
    
    if all_passed:
        print("[PASS] ALL CHECKS PASSED - Commit allowed")
        print("=" * 60)
        return 0
    else:
        print("[FAIL] CHECKS FAILED - Fix violations before committing")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())

"""Test coverage checker - ensures every module has a corresponding test file."""
from pathlib import Path

from base_checker import BaseChecker, CheckResult


class TestCoverageChecker(BaseChecker):
    """Checks that every implementation file has a corresponding test."""
    
    def get_name(self) -> str:
        return "Test Coverage Checker"
    
    def get_test_file(self, source_file: Path) -> Path | None:
        """Get the expected test file path for a source file."""
        parts = source_file.parts
        
        # Find the 'engine' directory in path
        if "engine" not in parts:
            return None
        
        engine_idx = parts.index("engine")
        
        # Build test file path: tests/engine/path/test_filename.py
        relative_path = parts[engine_idx + 1:]  # Everything after 'engine'
        test_dir = source_file.parents[-1].parent / "tests" / "engine" / "/".join(relative_path[:-1])
        
        # Source is like engine/core/object.py -> tests/engine/core/test_object.py
        test_filename = f"test_{source_file.stem}.py"
        test_file = test_dir / test_filename
        
        return test_file
    
    def check_file(self, file_path: Path) -> CheckResult:
        """Check if source file has corresponding test file."""
        # Skip __init__.py and test files themselves
        if file_path.name == "__init__.py":
            return CheckResult(True, "", str(file_path))
        
        # Skip files in tests directory
        if "tests" in file_path.parts:
            return CheckResult(True, "", str(file_path))
        
        # Skip scripts directory
        if "scripts" in file_path.parts:
            return CheckResult(True, "", str(file_path))
        
        # Only check files in engine/ directory
        if "engine" not in file_path.parts:
            return CheckResult(True, "", str(file_path))
        
        # Calculate expected test path
        parts = list(file_path.parts)
        
        # Find 'engine' in path
        if "engine" not in parts:
            return CheckResult(True, "", str(file_path))
        
        engine_idx = parts.index("engine")
        
        # Get path after engine (e.g., ['core', 'vec.py'])
        sub_path = parts[engine_idx + 1:]
        
        # Build test path: engine/tests/engine/core/test_vec.py
        if len(sub_path) >= 2:
            # Has subdirectory
            test_dir_parts = parts[:engine_idx + 1] + ["tests", "engine"] + sub_path[:-1]
        else:
            # Directly under engine
            test_dir_parts = parts[:engine_idx + 1] + ["tests", "engine"]
        
        test_dir = Path(*test_dir_parts)
        test_file = test_dir / f"test_{file_path.stem}.py"
        
        if not test_file.exists():
            return CheckResult(
                False,
                f"Missing test file: {test_file}",
                str(file_path)
            )
        
        return CheckResult(True, "", str(file_path))


if __name__ == "__main__":
    checker = TestCoverageChecker()
    success = checker.run()
    exit(0 if success else 1)

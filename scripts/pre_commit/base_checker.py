"""Base checker class for pre-commit hooks."""
from abc import ABC, abstractmethod
from pathlib import Path


class CheckResult:
    """Result of a code check."""
    
    def __init__(self, passed: bool, message: str = "", file: str = ""):
        self.passed = passed
        self.message = message
        self.file = file
    
    def __str__(self) -> str:
        status = "+" if self.passed else "-"
        if self.file:
            return f"[{status}] {self.file}: {self.message}"
        return f"[{status}] {self.message}"


class BaseChecker(ABC):
    """Base class for all pre-commit checkers."""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.errors: list[CheckResult] = []
    
    @abstractmethod
    def check_file(self, file_path: Path) -> CheckResult:
        """Check a single file."""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Return checker name."""
        pass
    
    def run(self, files: list[Path] = None) -> bool:
        """Run checker on all Python files."""
        if files is None:
            files = list(self.project_root.rglob("*.py"))
        
        self.errors = []
        
        print(f"\n[CHECK] {self.get_name()}...")
        
        for file_path in files:
            if "__pycache__" in str(file_path):
                continue
            if "test" in file_path.name and file_path.name.startswith("test_"):
                continue
            
            result = self.check_file(file_path)
            if not result.passed:
                self.errors.append(result)
        
        if self.errors:
            print(f"  [FAIL] {len(self.errors)} violation(s) found:")
            for error in self.errors:
                print(f"    {error}")
            return False
        
        print("  [OK] All checks passed")
        return True

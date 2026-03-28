"""Layer violation checker - enforces 7-layer architecture rules."""
import ast
from pathlib import Path

from base_checker import BaseChecker, CheckResult


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


class LayerViolationChecker(BaseChecker):
    """Checks for 7-layer architecture violations."""
    
    def get_name(self) -> str:
        return "Layer Violation Checker"
    
    def get_file_layer(self, file_path: Path) -> int:
        """Determine which layer a file belongs to."""
        parts = file_path.parts
        
        for i, part in enumerate(parts):
            if part in LAYERS:
                return LAYERS[part]
        
        return -1
    
    def get_import_layer(self, import_path: str) -> int:
        """Determine which layer an import belongs to."""
        parts = import_path.split(".")
        
        for part in parts:
            if part in LAYERS:
                return LAYERS[part]
        
        return -1
    
    def check_file(self, file_path: Path) -> CheckResult:
        """Check a Python file for layer violations."""
        file_layer = self.get_file_layer(file_path)
        
        if file_layer == -1:
            return CheckResult(True, "", str(file_path))
        
        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content)
        except Exception as e:
            return CheckResult(False, f"Parse error: {e}", str(file_path))
        
        violations = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    import_layer = self.get_import_layer(alias.name)
                    if import_layer > file_layer:
                        violations.append(
                            f"Line {node.lineno}: Import '{alias.name}' from layer {import_layer} "
                            f"into layer {file_layer}"
                        )
            
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    import_layer = self.get_import_layer(node.module)
                    if import_layer > file_layer:
                        violations.append(
                            f"Line {node.lineno}: Import '{node.module}' from layer {import_layer} "
                            f"into layer {file_layer}"
                        )
        
        if violations:
            return CheckResult(
                False,
                f"Layer violation(s): {', '.join(violations[:3])}",
                str(file_path)
            )
        
        return CheckResult(True, "", str(file_path))


if __name__ == "__main__":
    checker = LayerViolationChecker()
    success = checker.run()
    exit(0 if success else 1)

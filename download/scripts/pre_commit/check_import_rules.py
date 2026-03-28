"""Import rules checker - enforces star import, diversity limits, third-party rules."""
import ast
from pathlib import Path
from collections import defaultdict

from base_checker import BaseChecker, CheckResult


# Third-party library allowed locations
THIRD_PARTY_RULES = {
    "pyglet": ["hal/"],
    "moderngl": ["hal/", "engine/renderer/"],
    "pymunk": ["engine/physics/"],
    "PIL": ["engine/asset/"],
    "watchdog": ["engine/asset/"],
    "msgspec": ["core/serializer.py"],
    "dearpygui": ["editor/"],
}


class ImportRulesChecker(BaseChecker):
    """Checks for import rule violations."""
    
    def get_name(self) -> str:
        return "Import Rules Checker"
    
    def check_star_imports(self, node: ast.ImportFrom) -> str | None:
        """Check for star imports."""
        if node.names and any(alias.name == "*" for alias in node.names):
            return "Star import (*) detected - FORBIDDEN"
        return None
    
    def check_import_diversity(self, file_path: Path, imports: list) -> str | None:
        """Check if imports exceed 5 different modules."""
        # Count unique module names
        modules = set()
        for node in imports:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    modules.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom) and node.module:
                modules.add(node.module.split(".")[0])
        
        if len(modules) > 5:
            return f"Import diversity limit exceeded: {len(modules)} modules (max 5)"
        return None
    
    def check_third_party(self, file_path: Path, node: ast.AST) -> str | None:
        """Check third-party library placement."""
        module_name = None
        
        if isinstance(node, ast.Import):
            for alias in node.names:
                base = alias.name.split(".")[0]
                if base in THIRD_PARTY_RULES:
                    module_name = base
        elif isinstance(node, ast.ImportFrom) and node.module:
            base = node.module.split(".")[0]
            if base in THIRD_PARTY_RULES:
                module_name = base
        
        if not module_name:
            return None
        
        file_str = str(file_path)
        allowed_paths = THIRD_PARTY_RULES[module_name]
        
        for allowed in allowed_paths:
            if allowed in file_str:
                return None
        
        return f"Third-party library '{module_name}' can only be used in: {', '.join(allowed_paths)}"
    
    def check_file(self, file_path: Path) -> CheckResult:
        """Check a Python file for import violations."""
        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content)
        except Exception as e:
            return CheckResult(False, f"Parse error: {e}", str(file_path))
        
        violations = []
        all_imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                all_imports.append(node)
                
                # Check star imports
                if isinstance(node, ast.ImportFrom):
                    violation = self.check_star_imports(node)
                    if violation:
                        violations.append(f"Line {node.lineno}: {violation}")
                
                # Check third-party placement
                violation = self.check_third_party(file_path, node)
                if violation:
                    violations.append(f"Line {node.lineno}: {violation}")
        
        # Check import diversity
        diversity_violation = self.check_import_diversity(file_path, all_imports)
        if diversity_violation:
            violations.append(diversity_violation)
        
        if violations:
            return CheckResult(
                False,
                f"Import violation(s): {'; '.join(violations[:3])}",
                str(file_path)
            )
        
        return CheckResult(True, "", str(file_path))


if __name__ == "__main__":
    checker = ImportRulesChecker()
    success = checker.run()
    exit(0 if success else 1)

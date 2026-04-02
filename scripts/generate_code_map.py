import json
from pathlib import Path

def generate_code_map(root_path):
    """Generate a comprehensive code map of the project structure."""
    
    code_map = {
        "project_name": "2D Game Engine",
        "version": "0.0.1",
        "total_tests": 1340,
        "architecture": "7-Layer",
        "layers": {},
        "files": {
            "total_python_files": 0,
            "total_test_files": 0,
            "total_documentation_files": 0,
            "total_lines_of_code": 0
        },
        "structure": {}
    }
    
    # Layer mapping
    layer_folders = {
        "layer_0_hal": "hal",
        "layer_1_core": "core", 
        "layer_2_engine": "engine",
        "layer_3_world": "world",
        "layer_4_game": "game",
        "layer_5_scripting": "scripting",
        "layer_6_ui": "ui",
        "layer_7_editor": "editor"
    }
    
    root = Path(root_path)
    
    for item in root.iterdir():
        if item.is_dir() and not item.name.startswith('.') and item.name not in ['__pycache__', '.git', '.mypy_cache', '.pytest_cache', '.ruff_cache']:
            dir_info = {
                "type": "directory",
                "item_count": len(list(item.iterdir())),
                "python_files": [],
                "subdirectories": {},
                "test_files": []
            }
            
            # Scan directory recursively
            for file in item.rglob('*.py'):
                if '__pycache__' not in str(file):
                    relative_path = str(file.relative_to(root))
                    if file.name.startswith('test_'):
                        dir_info["test_files"].append(relative_path)
                        code_map["files"]["total_test_files"] += 1
                    else:
                        dir_info["python_files"].append(relative_path)
                        code_map["files"]["total_python_files"] += 1
                        
                        # Count lines
                        try:
                            with open(file, 'r', encoding='utf-8') as f:
                                lines = len(f.readlines())
                                code_map["files"]["total_lines_of_code"] += lines
                        except:
                            pass
            
            # Find subdirectories
            for subdir in item.iterdir():
                if subdir.is_dir() and not subdir.name.startswith('.') and subdir.name != '__pycache__':
                    py_count = len(list(subdir.rglob('*.py')))
                    dir_info["subdirectories"][subdir.name] = {
                        "python_file_count": py_count
                    }
            
            code_map["structure"][item.name] = dir_info
            
            # Map to layer
            for layer_key, folder in layer_folders.items():
                if item.name == folder:
                    code_map["layers"][layer_key] = {
                        "folder": folder,
                        "python_files": len(dir_info["python_files"]),
                        "test_files": len(dir_info["test_files"])
                    }
    
    # Add documentation
    docs_dir = root / "docs"
    if docs_dir.exists():
        code_map["documentation"] = [f.name for f in docs_dir.iterdir() if f.is_file()]
        code_map["files"]["total_documentation_files"] = len(code_map["documentation"])
    
    # Add root files
    code_map["root_files"] = [f.name for f in root.iterdir() if f.is_file()]
    
    return code_map

if __name__ == "__main__":
    # Generate code map for current directory
    project_root = "."
    code_map = generate_code_map(project_root)
    
    # Save to JSON
    output_file = "code_map.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(code_map, f, indent=2, ensure_ascii=False)
    
    print(f"Code map saved to {output_file}")
    print(f"Total Python files: {code_map['files']['total_python_files']}")
    print(f"Total test files: {code_map['files']['total_test_files']}")
    print(f"Total lines of code: {code_map['files']['total_lines_of_code']}")

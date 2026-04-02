#!/usr/bin/env python3
"""Bulk remove unittest.mock from test files and replace with simple mocks."""

import re
from pathlib import Path

def create_mock_class(name, methods=None):
    """Generate a simple mock class."""
    methods = methods or []
    code = f"""
class {name}:
    \"\"\"Simple mock for testing.\"\"\"
    def __init__(self):
        self.call_count = 0
        self.call_args = None
"""
    for method in methods:
        code += f"""
    def {method}(self, *args, **kwargs):
        self.call_count += 1
        self.call_args = (args, kwargs)
"""
    return code

def process_file(filepath):
    """Remove unittest.mock imports and replace MagicMock() usage."""
    content = filepath.read_text()
    original = content
    
    # Remove import
    content = re.sub(r'^from unittest\.mock import.*\n', '', content, flags=re.MULTILINE)
    
    # Track replacements needed
    replacements = []
    
    # Find all MagicMock() assignments
    for match in re.finditer(r'(\w+)\s*=\s*MagicMock\(\)', content):
        var_name = match.group(1)
        if var_name not in ['callback', 'on_load', 'on_complete']:
            replacements.append((var_name, 'MockObject'))
        else:
            replacements.append((var_name, 'MockCallback'))
    
    # Add mock classes at top after imports
    if replacements:
        # Find end of imports
        import_end = content.find('\n\n')
        if import_end > 0:
            mock_classes = ""
            if any(r[1] == 'MockObject' for r in replacements):
                mock_classes += create_mock_class('MockObject')
            if any(r[1] == 'MockCallback' for r in replacements):
                mock_classes += create_mock_class('MockCallback', ['__call__'])
            
            content = content[:import_end] + '\n' + mock_classes + content[import_end:]
    
    # Replace MagicMock() calls
    for var_name, mock_class in replacements:
        content = re.sub(rf'{re.escape(var_name)}\s*=\s*MagicMock\(\)', 
                        f'{var_name} = {mock_class}()', content)
    
    if content != original:
        filepath.write_text(content)
        return True
    return False

# Process all test files with mocks
test_dir = Path('tests')
mock_files = [
    'ui/test_panel.py',
    'ui/test_button.py', 
    'world/test_level.py',
    'world/test_prefab.py',
    'engine/renderer/test_deferred.py',
    'engine/renderer/test_light_api.py',
    'engine/renderer/test_light_renderer_draw_light.py',
    'engine/renderer/test_normal_map_sprite.py',
    'engine/renderer/test_renderer2d_gpu.py',
    'engine/renderer/test_shadow_map.py',
    'engine/renderer/test_sprite_batch_instancing.py',
    'engine/renderer/test_ssao.py',
    'engine/asset/test_asset_manager_pbt.py',
]

changed = 0
for mock_file in mock_files:
    filepath = test_dir / mock_file
    if filepath.exists():
        if process_file(filepath):
            changed += 1
            print(f"✓ Fixed {mock_file}")
        else:
            print(f"- No changes needed: {mock_file}")
    else:
        print(f"! Not found: {mock_file}")

print(f"\nTotal: {changed}/{len(mock_files)} files updated")

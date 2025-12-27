"""
Fix QAction imports for PyQt5.
In PyQt5, QAction is in QtWidgets, not QtGui.
"""

import os
import re
from pathlib import Path


def fix_qaction_imports(file_path):
    """Fix QAction imports in a file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    changes_made = False
    
    # Pattern 1: from PyQt5.QtGui import ... QAction ...
    pattern1 = r'from PyQt5\.QtGui import(.*?)(QAction)(.*?)\n'
    
    def replace_qtgui_import(match):
        nonlocal changes_made
        imports = match.group(0)
        
        # Extract all imports from QtGui line
        import_part = match.group(1) + match.group(2) + match.group(3)
        imports_list = [imp.strip() for imp in import_part.split(',')]
        
        # Remove QAction from QtGui imports
        if 'QAction' in imports_list:
            imports_list.remove('QAction')
            changes_made = True
            
            # Rebuild QtGui import line
            if imports_list:
                new_qtgui_line = f"from PyQt5.QtGui import {', '.join(imports_list)}\n"
            else:
                new_qtgui_line = ""
            
            # Check if QtWidgets import exists
            if 'from PyQt5.QtWidgets import' in content:
                # Need to add QAction to existing QtWidgets import
                return new_qtgui_line
            else:
                # Add new QtWidgets import for QAction
                return new_qtgui_line + "from PyQt5.QtWidgets import QAction\n"
        
        return imports
    
    content = re.sub(pattern1, replace_qtgui_import, content, flags=re.DOTALL)
    
    # Pattern 2: Check if QAction needs to be added to QtWidgets import
    if 'QAction' in content and 'from PyQt5.QtWidgets import' in content:
        # Find QtWidgets import lines
        qtwidgets_pattern = r'(from PyQt5\.QtWidgets import.*?)\n'
        
        def add_qaction_to_qtwidgets(match):
            nonlocal changes_made
            import_line = match.group(0)
            
            if 'QAction' not in import_line:
                # Add QAction to import
                import_line = import_line.rstrip('\n')
                if import_line.endswith(')'):
                    # Multi-line import
                    import_line = import_line.replace(')', ', QAction)')
                else:
                    # Single line import
                    import_line += ', QAction'
                import_line += '\n'
                changes_made = True
            
            return import_line
        
        content = re.sub(qtwidgets_pattern, add_qaction_to_qtwidgets, content, flags=re.DOTALL)
    
    # Fix the specific warning in tab_manager.py
    if 'tab_manager.py' in str(file_path):
        # Fix the invalid escape sequence
        content = content.replace(r'C:\Projects', r'C:\\Projects')
        changes_made = True
    
    if changes_made:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ Fixed {file_path.name}")
    
    return changes_made


def fix_all_files():
    """Fix all Python files in the project"""
    project_root = Path(__file__).parent
    src_dir = project_root / 'src'
    
    print("Fixing QAction imports for PyQt5...")
    
    files_fixed = 0
    
    # Process all Python files in src
    for py_file in src_dir.rglob('*.py'):
        if fix_qaction_imports(py_file):
            files_fixed += 1
    
    # Also check root directory
    for py_file in project_root.glob('*.py'):
        if py_file.name not in ['fix_qaction_imports.py', 'fix_pyqt5_imports.py']:
            if fix_qaction_imports(py_file):
                files_fixed += 1
    
    print(f"\n✅ Fixed {files_fixed} files")
    return files_fixed


if __name__ == "__main__":
    fix_all_files()
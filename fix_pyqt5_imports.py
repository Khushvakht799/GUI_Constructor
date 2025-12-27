"""
Fix imports for PyQt5 compatibility.
Run this script once to convert all PyQt6 imports to PyQt5.
"""

import os
import re
from pathlib import Path


def convert_file_to_pyqt5(file_path):
    """Convert PyQt6 imports to PyQt5 in a file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Track changes
    changes_made = False
    
    # Replace PyQt6 with PyQt5
    if 'PyQt6' in content:
        content = content.replace('PyQt6', 'PyQt5')
        changes_made = True
        print(f"  Converted PyQt6 → PyQt5 in {os.path.basename(file_path)}")
    
    # Fix QAction import (in PyQt5 it's in QtWidgets)
    if 'from PyQt5.QtGui import QAction' in content:
        # Check if QtWidgets import exists
        if 'from PyQt5.QtWidgets import' in content:
            # Move QAction to QtWidgets import
            content = content.replace('from PyQt5.QtGui import QAction\n', '')
            # Add QAction to QtWidgets import
            content = re.sub(
                r'(from PyQt5\.QtWidgets import.*?)\n',
                r'\1, QAction\n',
                content,
                flags=re.DOTALL
            )
            print(f"  Fixed QAction import in {os.path.basename(file_path)}")
    
    # Fix exec() to exec_() for PyQt5
    if 'app.exec()' in content:
        content = content.replace('app.exec()', 'app.exec_()')
        changes_made = True
    
    if changes_made:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    return changes_made


def fix_all_files():
    """Fix all Python files in the project"""
    project_root = Path(__file__).parent
    src_dir = project_root / 'src'
    
    print("Converting PyQt6 imports to PyQt5...")
    
    files_fixed = 0
    
    # Process all Python files
    for py_file in src_dir.rglob('*.py'):
        if convert_file_to_pyqt5(py_file):
            files_fixed += 1
    
    # Also check root directory
    for py_file in project_root.glob('*.py'):
        if py_file.name != 'fix_pyqt5_imports.py':
            if convert_file_to_pyqt5(py_file):
                files_fixed += 1
    
    print(f"\n✅ Fixed {files_fixed} files for PyQt5 compatibility")
    print("\nNext steps:")
    print("1. Install PyQt5: pip install PyQt5")
    print("2. Run: python app.py")


if __name__ == "__main__":
    fix_all_files()
import sys
import os
import re

def fix_imports_in_file(filepath):
    """Исправляем импорты в файле"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Исправляем относительные импорты
    # from ..core -> from core (когда запускаем из корня)
    # from .module -> из того же пакета
    
    # Для файлов в src/gui
    if 'src\\gui' in filepath:
        content = content.replace('from ..core', 'from core')
        content = content.replace('from ..utils', 'from utils')
        content = content.replace('from .', 'from gui.')
    
    # Для файлов в src/core
    elif 'src\\core' in filepath:
        content = content.replace('from ..gui', 'from gui')
        content = content.replace('from ..utils', 'from utils')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

# Исправляем импорты во всех файлах
for root, dirs, files in os.walk('src'):
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            print(f"Исправление {filepath}")
            fix_imports_in_file(filepath)

print("✅ Импорты исправлены")

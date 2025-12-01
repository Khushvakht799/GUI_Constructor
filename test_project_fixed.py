#!/usr/bin/env python3
"""
Тестовый скрипт для проверки импортов - исправленная версия
"""

import sys
import os

# Добавляем src в путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Проверяем все импорты"""
    print("🔍 Тестирование импортов...")
    
    tests = [
        ("core модули", lambda: __import__('core')),
        ("gui модули", lambda: __import__('gui')),
        ("utils модули", lambda: __import__('utils')),
    ]
    
    for test_name, import_func in tests:
        try:
            module = import_func()
            print(f"✅ {test_name}: OK")
        except Exception as e:
            print(f"❌ {test_name}: FAILED - {e}")
            import traceback
            traceback.print_exc()
            return False
    
    # Тестируем конкретные классы
    print("\n🔍 Тестирование конкретных классов...")
    
    class_tests = [
        ("KnowledgeBaseManager", "from core import KnowledgeBaseManager"),
        ("ProjectAnalyzer", "from core import ProjectAnalyzer"),
        ("CustomButton", "from gui import CustomButton"),
        ("GUIManager", "from gui import GUIManager"),
    ]
    
    for class_name, import_stmt in class_tests:
        try:
            exec(import_stmt)
            print(f"✅ {class_name}: OK")
        except Exception as e:
            print(f"❌ {class_name}: FAILED - {e}")
            return False
    
    return True

def check_files():
    """Проверяем наличие файлов"""
    print("\n📁 Проверка файловой структуры...")
    
    required_files = [
        'src/core/kb_manager.py',
        'src/core/project_analyzer.py',
        'src/gui/gui_main.py',
        'src/utils/utils.py',
        'config/config.json',
        'data/knowledge.json'
    ]
    
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} (отсутствует)")
            all_exist = False
    
    return all_exist

if __name__ == "__main__":
    print("=" * 60)
    print("ПРОВЕРКА СТРУКТУРЫ ПРОЕКТА GUI CONSTRUCTOR")
    print("=" * 60)
    
    files_ok = check_files()
    imports_ok = test_imports()
    
    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТЫ:")
    print(f"Файловая структура: {'✅ OK' if files_ok else '❌ ПРОБЛЕМЫ'}")
    print(f"Импорты Python: {'✅ OK' if imports_ok else '❌ ПРОБЛЕМЫ'}")
    
    if files_ok and imports_ok:
        print("\n🎉 Проект готов к работе!")
        print("\nДоступные команды:")
        print("  python app.py              # Запуск приложения")
        print("  python -m pytest tests/    # Запуск тестов")
    else:
        print("\n⚠️ Требуется исправление проблем")
    
    print("=" * 60)

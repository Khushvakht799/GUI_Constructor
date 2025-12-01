#!/usr/bin/env python3
"""
Тестовый скрипт для проверки импортов
"""

import sys
import os

# Добавляем src в путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def simple_test():
    """Простой тест импортов"""
    print("🔍 Тестирование основных импортов...")
    
    tests = [
        ("core.kb_manager", "from core import kb_manager"),
        ("core.project_analyzer", "from core import project_analyzer"),
        ("gui.gui_main", "from gui import gui_main"),
        ("gui.buttons", "from gui import buttons"),
        ("utils.utils", "from utils import utils"),
    ]
    
    all_passed = True
    for module, import_stmt in tests:
        try:
            exec(import_stmt)
            print(f"✅ {module}: OK")
        except Exception as e:
            print(f"❌ {module}: FAILED - {e}")
            all_passed = False
    
    return all_passed

if __name__ == "__main__":
    print("=" * 50)
    print("Проверка структуры импортов")
    print("=" * 50)
    
    if simple_test():
        print("\n🎉 Все основные импорты работают!")
        print("\nПроверка запуска приложения...")
        try:
            from gui import gui_main
            print("✅ Модуль gui_main загружен успешно")
            print("\nЗапустите приложение командой: python app.py")
        except Exception as e:
            print(f"⚠️ Ошибка при загрузке gui_main: {e}")
    else:
        print("\n⚠️ Есть проблемы с импортами")
    
    print("=" * 50)

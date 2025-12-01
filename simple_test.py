#!/usr/bin/env python3
"""
Простой тест для GUI Constructor
"""

import sys
import os

print("=" * 50)
print("🧪 Простой тест GUI Constructor")
print("=" * 50)

# Устанавливаем пути
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, 'src')

print(f"📂 Базовая директория: {BASE_DIR}")
print(f"📂 SRC директория: {SRC_DIR}")

# Проверяем существование директорий
print("\n📁 Проверка структуры:")
required = ['src', 'src/gui', 'src/core', 'config', 'data']
for dir_name in required:
    dir_path = os.path.join(BASE_DIR, dir_name)
    if os.path.exists(dir_path):
        print(f"  ✅ {dir_name}/")
    else:
        print(f"  ❌ {dir_name}/ (отсутствует)")

# Проверяем основные файлы
print("\n📄 Проверка файлов:")
files_to_check = [
    ('src/gui/gui_main.py', 'Главный GUI модуль'),
    ('src/core/kb_manager.py', 'Менеджер базы знаний'),
    ('config/config.json', 'Конфигурация'),
    ('data/knowledge.json', 'База знаний'),
]

all_files_ok = True
for file_path, description in files_to_check:
    full_path = os.path.join(BASE_DIR, file_path)
    if os.path.exists(full_path):
        print(f"  ✅ {description}")
    else:
        print(f"  ❌ {description}")
        all_files_ok = False

# Проверяем Python и tkinter
print("\n🐍 Проверка Python окружения:")
try:
    import tkinter as tk
    print("  ✅ Tkinter доступен")
    tk_ok = True
except ImportError:
    print("  ❌ Tkinter НЕ доступен")
    tk_ok = False

print(f"  Python версия: {sys.version}")

# Пробуем импортировать модули
print("\n🔧 Пробуем импортировать модули...")
try:
    # Добавляем src в путь
    sys.path.insert(0, SRC_DIR)
    
    # Пробуем импортировать
    print("  1. Импортируем core...")
    from core import KnowledgeBase, ProjectAnalyzer
    print("     ✅ Core модули загружены")
    
    print("  2. Импортируем gui...")
    from gui import CustomButton, GUIManager
    print("     ✅ GUI модули загружены")
    
    print("  3. Создаем объекты...")
    kb = KnowledgeBase("data/knowledge.json")
    analyzer = ProjectAnalyzer()
    print("     ✅ Объекты созданы")
    
    imports_ok = True
    print("\n🎉 Все импорты работают корректно!")
    
except Exception as e:
    print(f"  ❌ Ошибка импорта: {e}")
    imports_ok = False
    import traceback
    traceback.print_exc()

# Итог
print("\n" + "=" * 50)
print("ИТОГОВЫЙ ОТЧЕТ:")
print(f"Файловая структура: {'✅ OK' if all_files_ok else '❌ ПРОБЛЕМЫ'}")
print(f"Tkinter: {'✅ OK' if tk_ok else '❌ ОТСУТСТВУЕТ'}")
print(f"Импорты Python: {'✅ OK' if imports_ok else '❌ ПРОБЛЕМЫ'}")

if all_files_ok and tk_ok and imports_ok:
    print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
    print("\nЗапустите приложение одной из команд:")
    print("  python app.py")
    print("  python run.py")
else:
    print("\n⚠️ Требуются исправления")
    
print("=" * 50)

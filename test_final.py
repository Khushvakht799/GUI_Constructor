#!/usr/bin/env python3
"""
Тестовый скрипт для проверки импортов - окончательная версия
"""

import sys
import os
import json

# Добавляем src в путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_basic_imports():
    """Базовая проверка импортов"""
    print("🔍 Базовая проверка импортов...")
    
    try:
        # Проверяем что модули могут быть импортированы
        import core
        import gui
        import utils
        
        print("✅ Основные модули: OK")
        return True
    except Exception as e:
        print(f"❌ Ошибка импорта: {e}")
        return False

def test_specific_classes():
    """Проверка конкретных классов"""
    print("\n🔍 Проверка конкретных классов...")
    
    tests = [
        ("KnowledgeBase из core", "from core import KnowledgeBase"),
        ("ProjectAnalyzer из core", "from core import ProjectAnalyzer"),
        ("CustomButton из gui", "from gui import CustomButton"),
        ("GUIManager из gui", "from gui import GUIManager"),
        ("GUIConstructor из gui", "from gui import GUIConstructor"),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, import_stmt in tests:
        try:
            exec(import_stmt)
            print(f"✅ {test_name}: OK")
            passed += 1
        except Exception as e:
            print(f"❌ {test_name}: FAILED - {str(e)[:100]}")
    
    return passed == total

def test_config_files():
    """Проверка конфигурационных файлов"""
    print("\n📁 Проверка конфигурационных файлов...")
    
    files = [
        ("config/config.json", "конфигурация приложения"),
        ("data/knowledge.json", "база знаний"),
        ("config/ai_skills_library.json", "AI библиотека"),
        ("config/ai_templates.json", "AI шаблоны"),
    ]
    
    all_valid = True
    for file_path, description in files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if file_path.endswith('.json'):
                        json.loads(content)  # Проверяем валидность JSON
                print(f"✅ {description}: OK ({file_path})")
            except Exception as e:
                print(f"⚠️ {description}: INVALID JSON - {str(e)[:50]} ({file_path})")
                all_valid = False
        else:
            print(f"❌ {description}: ОТСУТСТВУЕТ ({file_path})")
            all_valid = False
    
    return all_valid

def test_directory_structure():
    """Проверка структуры директорий"""
    print("\n🏗️ Проверка структуры директорий...")
    
    required_dirs = [
        "src",
        "src/core",
        "src/gui", 
        "src/utils",
        "config",
        "data",
        "logs",
        "projects",
        "templates",
        "exports",
        "docs",
        "tests"
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ {dir_path}/")
        else:
            print(f"❌ {dir_path}/ (отсутствует)")
            all_exist = False
    
    return all_exist

if __name__ == "__main__":
    print("=" * 60)
    print("КОМПЛЕКСНАЯ ПРОВЕРКА ПРОЕКТА GUI CONSTRUCTOR")
    print("=" * 60)
    
    structure_ok = test_directory_structure()
    config_ok = test_config_files()
    basic_imports_ok = test_basic_imports()
    classes_ok = test_specific_classes()
    
    print("\n" + "=" * 60)
    print("СВОДНЫЙ ОТЧЕТ:")
    print(f"Структура директорий: {'✅ OK' if structure_ok else '❌ ПРОБЛЕМЫ'}")
    print(f"Конфигурационные файлы: {'✅ OK' if config_ok else '❌ ПРОБЛЕМЫ'}")
    print(f"Базовые импорты: {'✅ OK' if basic_imports_ok else '❌ ПРОБЛЕМЫ'}")
    print(f"Конкретные классы: {'✅ OK' if classes_ok else '❌ ПРОБЛЕМЫ'}")
    
    if all([structure_ok, config_ok, basic_imports_ok, classes_ok]):
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("\nДоступные команды:")
        print("  python app.py              # Запуск приложения")
        print("  python main.py             # Альтернативный запуск")
        print("  python -m pytest tests/    # Запуск тестов (когда будут созданы)")
    else:
        print("\n⚠️ НЕОБХОДИМО ИСПРАВИТЬ ОБНАРУЖЕННЫЕ ПРОБЛЕМЫ")
    
    print("=" * 60)

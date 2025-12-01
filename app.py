#!/usr/bin/env python3
"""
Главный модуль GUI Constructor
"""

import sys
import os
import json

# Добавляем src в путь для импортов
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def load_config():
    """Загрузка конфигурации"""
    config_path = "config/config.json"
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Ошибка загрузки конфигурации: {e}")
            return {}
    return {}

def check_dependencies():
    """Проверка зависимостей"""
    try:
        import tkinter
        return True
    except ImportError:
        print("❌ Ошибка: Tkinter не установлен")
        print("   Tkinter обычно входит в состав стандартной библиотеки Python")
        print("   Убедитесь, что Python установлен правильно")
        return False

def main():
    """Точка входа в приложение"""
    print("=" * 50)
    print("🚀 GUI Constructor v1.0")
    print("=" * 50)
    
    # Загружаем конфигурацию
    config = load_config()
    app_name = config.get('app', {}).get('name', 'GUI Constructor')
    version = config.get('app', {}).get('version', '1.0.0')
    
    print(f"Приложение: {app_name} v{version}")
    print(f"Автор: {config.get('app', {}).get('author', 'Khushvakht799')}")
    print(f"Описание: {config.get('app', {}).get('description', 'Visual GUI constructor')}")
    
    # Проверяем зависимости
    if not check_dependencies():
        return 1
    
    try:
        # Импортируем и запускаем GUI
        from gui import gui_main
        
        print("\n✅ Все зависимости проверены")
        print("🚀 Запуск графического интерфейса...")
        
        # Запускаем главное окно
        gui_main.run()
        
        print("\n👋 Приложение завершено")
        return 0
        
    except ImportError as e:
        print(f"\n❌ Критическая ошибка импорта: {e}")
        print("\nВозможные причины:")
        print("1. Повреждена структура проекта")
        print("2. Отсутствуют необходимые модули")
        print("3. Проблемы с путями импорта")
        print("\nПопробуйте:")
        print("1. Запустить тест: python test_final.py")
        print("2. Проверить структуру проекта")
        return 1
    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())

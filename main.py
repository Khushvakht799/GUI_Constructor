#!/usr/bin/env python3
"""
Точка входа в приложение (legacy)
Используйте app.py для нового запуска
"""

import sys
import os

# Для обратной совместимости
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from gui import gui_main
    print("Запуск через main.py...")
    gui_main.run()
except ImportError as e:
    print(f"Ошибка: {e}")
    print("Используйте: python app.py")

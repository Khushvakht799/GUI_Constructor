# step1_init_kb_gui.py
import json; kb = load_kb()
from pathlib import Path
import sys
import tkinter as tk

# Пути
ROOT = Path(__file__).resolve().parent
GUI_DIR = ROOT / "Gui"
KB_FILE = GUI_DIR / "knowledge.json"

# Добавляем Gui в sys.path, чтобы Python видел модули
sys.path.insert(0, str(GUI_DIR))

from gui_manager import GUIManager
from core.kb_manager import KnowledgeBase

# Создаем KB, если нет
if not KB_FILE.exists():
    print("[*] Knowledge Base не найдена, создаем...")
    KB_FILE.write_text(json.dumps({'errors': {}}, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"[+] Knowledge Base создана: {KB_FILE}")
else:
    print(f"[*] Knowledge Base найдена: {KB_FILE}")

# Проверяем GUIManager
try:
    root = tk.Tk()
    app = GUIManager(root)
    print("[+] GUIManager успешно создан")
    root.destroy()
except Exception as e:
    print(f"[!] Ошибка создания GUIManager: {e}")

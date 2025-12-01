"""
Gui/gui_manager.py

Вспомогательные функции для GUI: логика запуска анализатора, работы с KB, утилиты.

Содержит простой интерфейс-обёртку, которым может пользоваться gui_main.py
"""
from pathlib import Path
from core.kb_manager import load_kb

kb = load_kb()import json
import subprocess
import sys
import threading

ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / 'core' / 'project_analyzer.py'
ANALYZER_REPORT = ROOT / 'analyzer_report.json'
KB_FILE = ROOT / 'Gui' / 'knowledge.json'


def run_analyzer(project_path: str, out_path: str, on_line=None):
    cmd = [sys.executable, str(ANALYZER), project_path, '--out', out_path]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    def _reader():
        for line in proc.stdout:
            if on_line:
                on_line(line.rstrip('\n'))
        proc.wait()
        if on_line:
            on_line(f'PROCESS_EXIT_CODE:{proc.returncode}')
    threading.Thread(target=_reader, daemon=True).start()
    return proc


def load_kb():
    if not KB_FILE.exists():
        KB_FILE.write_text(json.dumps({'errors': {}}, indent=2, ensure_ascii=False), encoding='utf-8')
    try:
        return json.loads(KB_FILE.read_text(encoding='utf-8'))
    except Exception:
        return {'errors': {}}
class KnowledgeBase:
    def __init__(self):
        data = load_kb()
        # Приводим структуру к правильному виду
        self.data = {
            "errors": data.get("errors", []) if isinstance(data.get("errors"), list) else []
        }

    def save(self):
        KB_FILE.write_text(json.dumps(self.data, indent=2, ensure_ascii=False), encoding='utf-8')

    def find_fix(self, message):
        """Ищет паттерн, совпадающий с текстом ошибки."""
        import re
        for item in self.data["errors"]:
            if re.search(item["pattern"], message):
                return item
        return None

    def register(self, pattern, description, fix):
        """Добавляет новую запись."""
        self.data["errors"].append({
            "pattern": pattern,
            "description": description,
            "fix": fix
        })
        self.save()


# Глобальный объект БЗ
kb = KnowledgeBase()


def save_kb(kb: dict):
    KB_FILE.write_text(json.dumps(kb, indent=2, ensure_ascii=False), encoding='utf-8')

def analyze_error_message(error_text):
    """Возвращает описание и решение из БЗ."""
    info = kb.find_fix(error_text)
    if info:
        return (
            f"Описание: {info['description']}\n"
            f"Решение: {info['fix']}"
        )
    else:
        return "Ошибка не найдена в базе знаний."
kb.register("ZeroDivisionError", "Деление на ноль", "Проверь значения делителя.")

# Примеры дальнейшего расширения: find_fixes_in_kb, register_error, apply_fix и т.д.

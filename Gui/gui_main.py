"""
Gui/gui_main.py

Главный GUI-каркас для Jarvis GUI_Constructor.
Запускается из main.py (см. инструкция ниже).

Ключевые возможности:
- системная тема (по умолчанию)
- дерево проекта (подгружается из analyzer_report.json)
- кнопки: Анализировать, Открыть KB, Рефакторинг, Тест, Логи
- лог внизу
- запуск project_analyzer в отдельном потоке (subprocess)
- безопасная работа с файлами

Этот файл добавляется в папку Gui/ и не изменяет существующие модули.
"""

import os
import sys
import json
import threading
import queue
import subprocess
import time
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

ROOT = Path(__file__).resolve().parents[1]
ANALYZER_REPORT = ROOT / 'analyzer_report.json'
KB_FILE = ROOT / 'Gui' / 'knowledge.json'
ANALYZER_SCRIPT = ROOT / 'core' / 'project_analyzer.py'

class GUIManager:
    def __init__(self, root_tk):
        self.root = root_tk
        self.root.title('Jarvis GUI Constructor — Управление')
        # системная тема - не форсируем цвета
        self.root.geometry('980x680')
        self.log_q = queue.Queue()
        self._build_ui()
        self.root.after(200, self._flush_log_q)

    def _build_ui(self):
        # Панель инструментов
        toolbar = ttk.Frame(self.root, padding=6)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        btn_analyze = ttk.Button(toolbar, text='🔍 Анализировать', command=self.on_analyze)
        btn_kb = ttk.Button(toolbar, text='📚 Knowledge', command=self.on_open_kb)
        btn_refactor = ttk.Button(toolbar, text='⚙️ Рефакторинг', command=self.on_refactor)
        btn_test = ttk.Button(toolbar, text='🧪 Тестировать', command=self.on_test)
        btn_reload = ttk.Button(toolbar, text='🔄 Обновить дерево', command=self.load_tree_from_report)

        btn_analyze.pack(side=tk.LEFT, padx=4)
        btn_kb.pack(side=tk.LEFT, padx=4)
        btn_refactor.pack(side=tk.LEFT, padx=4)
        btn_test.pack(side=tk.LEFT, padx=4)
        btn_reload.pack(side=tk.LEFT, padx=4)

        # Основной фрейм: дерево слева, центральная панель, лог снизу
        main = ttk.Frame(self.root, padding=6)
        main.pack(fill=tk.BOTH, expand=True)

        main.columnconfigure(1, weight=1)
        main.rowconfigure(0, weight=1)

        # Дерево проекта
        tree_frame = ttk.Frame(main)
        tree_frame.grid(row=0, column=0, sticky='nsw', padx=(0,6))
        ttk.Label(tree_frame, text='Структура проекта').pack(anchor='w')
        self.tree = ttk.Treeview(tree_frame, height=30)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind('<Double-1>', self.on_tree_double)

        # Центральная панель
        center = ttk.Frame(main)
        center.grid(row=0, column=1, sticky='nsew')
        ttk.Label(center, text='Информация').pack(anchor='w')
        self.info_text = tk.Text(center, height=30)
        self.info_text.pack(fill=tk.BOTH, expand=True)

        # Лог
        log_frame = ttk.Frame(self.root)
        log_frame.pack(side=tk.BOTTOM, fill=tk.X)
        ttk.Label(log_frame, text='Журнал:').pack(anchor='w')
        self.log_widget = tk.Text(log_frame, height=10)
        self.log_widget.pack(fill=tk.X)

        # статус бар
        self.status_var = tk.StringVar(value='Готов')
        status = ttk.Label(self.root, textvariable=self.status_var, anchor='w')
        status.pack(side=tk.BOTTOM, fill=tk.X)

        # начальная загрузка
        self.load_tree_from_report()

    # ----------------- UI handlers -----------------
    def log(self, message: str):
        t = time.strftime('%H:%M:%S')
        self.log_q.put(f'[{t}] {message}')

    def _flush_log_q(self):
        try:
            while True:
                msg = self.log_q.get_nowait()
                self.log_widget.insert(tk.END, msg + '\n')
                self.log_widget.see(tk.END)
        except queue.Empty:
            pass
        self.root.after(200, self._flush_log_q)

    def on_analyze(self):
        # Запускаем анализ в отдельном потоке
        project_path = str(ROOT)
        self.log('Запуск анализатора...')
        self.status_var.set('Анализ...')
        threading.Thread(target=self._run_analyzer_subprocess, args=(project_path,), daemon=True).start()

    def _run_analyzer_subprocess(self, project_path: str):
        # Запускам python core/project_analyzer.py --out analyzer_report.json
        cmd = [sys.executable, str(ANALYZER_SCRIPT), project_path, '--out', str(ANALYZER_REPORT)]
        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in proc.stdout:
                self.log(line.rstrip('\n'))
            proc.wait()
            if proc.returncode == 0:
                self.log('Анализ завершён')
                self.status_var.set('Анализ завершён')
                # обновим дерево
                self.load_tree_from_report()
            else:
                self.log(f'Анализ завершён с кодом {proc.returncode}')
                self.status_var.set('Анализ завершился с ошибкой')
        except Exception as e:
            self.log(f'Ошибка запуска анализатора: {e}')
            self.status_var.set('Ошибка')

    def load_tree_from_report(self):
        # загружаем analyzer_report.json
        if not ANALYZER_REPORT.exists():
            self.log('analyzer_report.json не найден — запустите анализ')
            return
        try:
            with open(ANALYZER_REPORT, 'r', encoding='utf-8') as f:
                rep = json.load(f)
        except Exception as e:
            self.log(f'Не удалось прочитать отчет: {e}')
            return
        # очищаем дерево
        for i in self.tree.get_children():
            self.tree.delete(i)
        # добавляем файлы
        files = rep.get('py_files', [])
        root_node = self.tree.insert('', 'end', text=rep.get('root', 'project'))
        for f in files:
            self.tree.insert(root_node, 'end', text=f, values=(f,))
        self.tree.item(root_node, open=True)
        self.log('Дерево загружено из отчёта')

    def on_tree_double(self, event):
        item = self.tree.selection()
        if not item:
            return
        key = item[0]
        text = self.tree.item(key, 'text')
        # если это файл — показать содержимое
        if text.endswith('.py'):
            p = ROOT / text
            if p.exists():
                try:
                    s = p.read_text(encoding='utf-8')
                    self.info_text.delete('1.0', tk.END)
                    self.info_text.insert(tk.END, s)
                except Exception as e:
                    self.log(f'Не удалось открыть файл: {e}')
            else:
                self.log('Файл не найден')

    def on_open_kb(self):
        # откроем knowledge.json в редакторе
        if not KB_FILE.exists():
            # создаём минимальный каркас
            self._create_minimal_kb()
        try:
            s = KB_FILE.read_text(encoding='utf-8')
            # показать в отдельном окне
            wnd = tk.Toplevel(self.root)
            wnd.title('Knowledge Base')
            txt = tk.Text(wnd, width=100, height=40)
            txt.pack(fill=tk.BOTH, expand=True)
            txt.insert(tk.END, s)
            def save_and_close():
                try:
                    txt_content = txt.get('1.0', tk.END)
                    KB_FILE.write_text(txt_content, encoding='utf-8')
                    self.log('Knowledge Base сохранена')
                    wnd.destroy()
                except Exception as e:
                    messagebox.showerror('Ошибка', f'Не удалось сохранить KB: {e}')
            btn = ttk.Button(wnd, text='Сохранить', command=save_and_close)
            btn.pack()
        except Exception as e:
            self.log(f'Не удалось открыть KB: {e}')

    def _create_minimal_kb(self):
        minimal = {'errors': {"SyntaxError": {"description": "Синтаксическая ошибка", "fixes": ["Проверить синтаксис"]}}}
        try:
            KB_FILE.write_text(json.dumps(minimal, ensure_ascii=False, indent=2), encoding='utf-8')
            self.log('Создан минимальный knowledge.json')
        except Exception as e:
            self.log(f'Не удалось создать KB: {e}')

    def on_refactor(self):
        # Заглушка — в будущем вызов рефактор-движка
        messagebox.showinfo('Рефакторинг', 'Запланируй рефакторинг — модуль в разработке')

    def on_test(self):
        # Заглушка для тестирования
        messagebox.showinfo('Тесты', 'Запуск тестов — модуль в разработке')


def main():
    root = tk.Tk()
    GUIManager(root)
    root.mainloop()

# --- GUI launcher (added by assistant) ---
try:
    from Gui import gui_main
    gui_main.main()
except Exception:
    # Если GUI не доступен в этой среде — оставить прежнее поведение
    pass
# --- end GUI launcher ---

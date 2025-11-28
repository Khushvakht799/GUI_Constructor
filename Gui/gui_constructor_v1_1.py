# gui_constructor_v1_1.py - (Версия чатаГпт) - Сохраните и запустите
import os
import sys
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import threading
import queue
import time
from datetime import datetime
import tempfile
import shutil

APP_TITLE = "GUI Constructor v1.1 - БЕЗОПАСНО"

def timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def safe_write_file(path, content, encoding="utf-8"):
    """
    Атомарно записать файл: сначала во временный, затем os.replace.
    Если файл существует - сделаем резервную копию.
    """
    dirpath = os.path.dirname(path) or "."
    os.makedirs(dirpath, exist_ok=True)

    if os.path.exists(path):
        bak = f"{path}.bak.{timestamp()}"
        try:
            shutil.copy2(path, bak)
        except Exception:
            # если копирование провалилось — переименуем
            try:
                os.replace(path, bak)
            except Exception:
                pass

    fd, tmp = tempfile.mkstemp(dir=dirpath, prefix=".tmp_write_")
    os.close(fd)
    try:
        with open(tmp, "w", encoding=encoding) as f:
            f.write(content)
        os.replace(tmp, path)
        return True
    finally:
        if os.path.exists(tmp):
            try:
                os.remove(tmp)
            except Exception:
                pass

class StreamReaderThread(threading.Thread):
    """Читает stdout/stderr процесса и кладёт строки в очередь."""
    def __init__(self, stream, q, tag=""):
        super().__init__(daemon=True)
        self.stream = stream
        self.q = q
        self.tag = tag

    def run(self):
        try:
            for line in iter(self.stream.readline, ""):
                if not line:
                    break
                self.q.put((self.tag, line.rstrip("\n")))
        except Exception as e:
            self.q.put((self.tag, f"<error reading stream: {e}>"))
        finally:
            try:
                self.stream.close()
            except Exception:
                pass

class GUIConstructor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(APP_TITLE)
        self.root.geometry("880x640")
        self.setup_ui()

        self.templates = {
            "python": self.python_template,
            "web": self.web_template,
            "terminal": self.terminal_template,
            "data_processor": self.data_processor_template
        }

        # очередь для потоковой записи в лог (thread -> main)
        self.log_q = queue.Queue()
        self.root.after(200, self._process_log_queue)

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="12")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        title = ttk.Label(main_frame, text="🚀 GUI CONSTRUCTOR v1.1 — сохранно и сразу",
                          font=("Arial", 16, "bold"))
        title.grid(row=0, column=0, columnspan=4, pady=(0, 12), sticky=tk.W)

        ttk.Label(main_frame, text="Папка проекта:").grid(row=1, column=0, sticky=tk.W, pady=4)
        self.path_var = tk.StringVar(value=os.getcwd())
        ttk.Entry(main_frame, textvariable=self.path_var, width=60).grid(row=1, column=1, columnspan=2, pady=4, sticky=(tk.W, tk.E))
        ttk.Button(main_frame, text="Обзор", command=self.browse_folder).grid(row=1, column=3, pady=4, sticky=tk.E)

        ttk.Label(main_frame, text="Имя проекта:").grid(row=2, column=0, sticky=tk.W, pady=4)
        self.name_var = tk.StringVar(value="MyApp")
        ttk.Entry(main_frame, textvariable=self.name_var, width=60).grid(row=2, column=1, columnspan=3, pady=4, sticky=(tk.W, tk.E))

        ttk.Label(main_frame, text="Шаблон GUI:").grid(row=3, column=0, sticky=tk.W, pady=6)
        self.template_var = tk.StringVar(value="python")
        templates = [
            ("Python App (Tkinter)", "python"),
            ("Web Interface (Flask)", "web"),
            ("Terminal/CLI App", "terminal"),
            ("Data Processor (pandas)", "data_processor")
        ]
        for i, (txt, val) in enumerate(templates):
            ttk.Radiobutton(main_frame, text=txt, variable=self.template_var, value=val).grid(row=4+i, column=1, sticky=tk.W, pady=2, columnspan=3)

        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=8, column=0, columnspan=4, pady=12, sticky=tk.W)
        ttk.Button(btn_frame, text="🔍 Сканировать проект", command=self.scan_project).grid(row=0, column=0, padx=6)
        ttk.Button(btn_frame, text="⚡ Создать GUI", command=self.create_gui).grid(row=0, column=1, padx=6)
        ttk.Button(btn_frame, text="🚀 Запустить GUI", command=self.run_gui).grid(row=0, column=2, padx=6)
        ttk.Button(btn_frame, text="🗂 Показать конфиг", command=self.show_config).grid(row=0, column=3, padx=6)

        ttk.Label(main_frame, text="Лог выполнения:").grid(row=9, column=0, sticky=tk.W, pady=(8,0))
        self.log_text = tk.Text(main_frame, height=18, width=100)
        self.log_text.grid(row=10, column=0, columnspan=4, pady=6, sticky=(tk.W, tk.E))

        self.status_var = tk.StringVar(value="Готов к работе...")
        ttk.Label(main_frame, textvariable=self.status_var, foreground="green").grid(row=11, column=0, columnspan=4, pady=4, sticky=tk.W)

    def browse_folder(self):
        path = filedialog.askdirectory(initialdir=self.path_var.get())
        if path:
            self.path_var.set(path)
            # если имя пустое — подставим basename
            if not self.name_var.get() or self.name_var.get().strip() == "":
                self.name_var.set(os.path.basename(path) or "MyApp")

    def _log_put(self, message):
        # добавляем в очередь с таймштампом
        t = datetime.now().strftime("%H:%M:%S")
        self.log_q.put((f"[{t}] {message}"))

    def _process_log_queue(self):
        try:
            while True:
                msg = self.log_q.get_nowait()
                self.log_text.insert(tk.END, msg + "\n")
                self.log_text.see(tk.END)
        except queue.Empty:
            pass
        # повторяем
        self.root.after(200, self._process_log_queue)

    def log(self, message):
        # thread-safe вызов логгера
        self._log_put(message)

    def scan_project(self):
        self.log("🔍 Сканирую проект...")
        project_path = self.path_var.get()
        if not os.path.exists(project_path):
            self.log("❌ Папка не существует!")
            self.status_var.set("Ошибка: папка не найдена")
            return
        files = os.listdir(project_path)
        self.log(f"📁 Найдено файлов/папок: {len(files)}")
        py_files = [f for f in files if f.endswith('.py')]
        js_files = [f for f in files if f.endswith('.js')]
        json_files = [f for f in files if f.endswith('.json')]
        csv_like = [f for f in files if f.endswith('.csv') or f.endswith('.xlsx') or f.endswith('.xls')]
        # более осторожный выбор шаблона
        if any(name in files for name in ("setup.py", "requirements.txt")) or py_files:
            self.log("✅ Вероятно Python-проект")
            self.template_var.set("python")
        elif 'package.json' in files or js_files:
            self.log("✅ Вероятно Web/JavaScript проект")
            self.template_var.set("web")
        elif csv_like:
            self.log("✅ Вероятно проект обработки данных")
            self.template_var.set("data_processor")
        else:
            self.log("⚠️  Не удалось однозначно определить тип — оставлен терминальный шаблон")
            self.template_var.set("terminal")
        self.status_var.set("Сканирование завершено")

    def create_gui(self):
        project_path = os.path.abspath(self.path_var.get())
        project_name = self.name_var.get().strip() or "MyApp"
        template_type = self.template_var.get()
        self.log(f"🛠 Создаю GUI: {project_name} ({template_type}) в {project_path}")

        if not os.path.exists(project_path):
            try:
                os.makedirs(project_path, exist_ok=True)
            except Exception as e:
                self.log(f"❌ Не удалось создать папку проекта: {e}")
                return

        try:
            template_func = self.templates.get(template_type, self.python_template)
            gui_code, extra_files = template_func(project_name)
            # main gui file path
            output_file = os.path.join(project_path, f"{project_name}_gui.py")
            # записываем GUI файл атомарно
            safe_write_file(output_file, gui_code)
            self.log(f"✅ GUI создан: {output_file}")

            # создаём дополнительные файлы, если есть (web_server.py, templates/index.html и т.д.)
            for relpath, content in (extra_files or {}).items():
                target = os.path.join(project_path, relpath)
                safe_write_file(target, content)
                self.log(f"✅ Доп. файл создан: {target}")

            # конфиг
            config = {
                "project": {"name": project_name, "type": template_type, "path": project_path},
                "gui": {"file": output_file, "created": timestamp()}
            }
            config_file = os.path.join(project_path, "gui_config.json")
            safe_write_file(config_file, json.dumps(config, ensure_ascii=False, indent=2))
            self.log("✅ Конфигурация сохранена")
            self.status_var.set("GUI успешно создан!")

        except Exception as e:
            self.log(f"❌ Ошибка при создании GUI: {e}")
            self.status_var.set("Ошибка создания")

    def run_gui(self):
        project_path = os.path.abspath(self.path_var.get())
        project_name = self.name_var.get().strip() or "MyApp"
        gui_file = os.path.join(project_path, f"{project_name}_gui.py")
        if not os.path.exists(gui_file):
            self.log("❌ GUI файл не найден! Создайте его сначала.")
            messagebox.showwarning("Файл не найден", "Сначала создайте GUI (кнопка 'Создать GUI').")
            return

        self.log("🚀 Запускаю GUI (в отдельном процессе)...")
        self.status_var.set("Запуск...")

        def target():
            # запускаем с потоковым чтением stdout/stderr
            try:
                # используем list аргументов, чтобы корректно обрабатывать пробелы в пути
                proc = subprocess.Popen([sys.executable, gui_file],
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        cwd=project_path,
                                        text=True,
                                        bufsize=1,
                                        universal_newlines=True)
                q = queue.Queue()
                out_reader = StreamReaderThread(proc.stdout, q, tag="OUT")
                err_reader = StreamReaderThread(proc.stderr, q, tag="ERR")
                out_reader.start()
                err_reader.start()

                # читаем очередь и отображаем
                while True:
                    try:
                        tag, line = q.get(timeout=0.2)
                        self._log_put(f"[{tag}] {line}")
                    except queue.Empty:
                        pass
                    rc = proc.poll()
                    if rc is not None:
                        # дожидаемся оставшихся сообщений
                        while not q.empty():
                            tag, line = q.get_nowait()
                            self._log_put(f"[{tag}] {line}")
                        break

                if proc.returncode == 0:
                    self.log("✅ GUI процесс завершился успешно")
                else:
                    self.log(f"⚠️ GUI процесс завершился с кодом: {proc.returncode}")

            except Exception as e:
                self.log(f"❌ Ошибка запуска GUI: {e}")
            finally:
                self.status_var.set("Готов к работе")

        threading.Thread(target=target, daemon=True).start()

    def show_config(self):
        project_path = os.path.abspath(self.path_var.get())
        cfg = os.path.join(project_path, "gui_config.json")
        if os.path.exists(cfg):
            try:
                with open(cfg, "r", encoding="utf-8") as f:
                    data = json.load(f)
                pretty = json.dumps(data, ensure_ascii=False, indent=2)
                # показать в отдельном окне
                wnd = tk.Toplevel(self.root)
                wnd.title("Конфигурация GUI")
                txt = tk.Text(wnd, width=80, height=30)
                txt.pack(fill=tk.BOTH, expand=True)
                txt.insert(tk.END, pretty)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось открыть конфиг: {e}")
        else:
            messagebox.showinfo("Конфигурация", "Файл gui_config.json не найден в папке проекта.")

    # ---------- ШАБЛОНЫ (возвращают (main_code, extra_files_dict)) ----------
    def python_template(self, name):
        code = f'''import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys

class {name}GUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("{name} - Auto Generated GUI")
        self.root.geometry("700x500")
        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        header = ttk.Label(main_frame, text="🎉 ВАШ {name} ЗАПУЩЕН!", font=("Arial", 18, "bold"))
        header.pack(pady=20)

        desc = ttk.Label(main_frame, text="Это автоматически сгенерированный интерфейс. GUI Constructor создал его!",
                         justify=tk.CENTER)
        desc.pack(pady=10)

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=30)

        ttk.Button(btn_frame, text="📁 Обзор файлов", command=self.browse_files).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="⚡ Выполнить", command=self.execute).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="❌ Выход", command=self.root.quit).pack(side=tk.LEFT, padx=10)

        ttk.Label(main_frame, text="Журнал:").pack(anchor=tk.W, pady=(20,5))
        self.log_text = tk.Text(main_frame, height=10, width=70)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        self.status_var = tk.StringVar(value="Готов к работе...")
        ttk.Label(main_frame, textvariable=self.status_var, foreground="green").pack(pady=10)

    def browse_files(self):
        filename = filedialog.askopenfilename()
        if filename:
            self.log(f"📂 Выбран файл: {{filename}}")

    def execute(self):
        self.log("⚡ Выполнение операций...")
        self.status_var.set("Выполняется...")
        # Добавьте вашу логику здесь
        self.status_var.set("Готово")

    def log(self, message):
        self.log_text.insert(tk.END, f"{{message}}\\n")
        self.log_text.see(tk.END)
        self.root.update()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = {name}GUI()
    app.run()
'''
        return code, {}

    def web_template(self, name):
        # создаём web_server.py и шаблон index.html в папке templates/
        web_server = f'''from flask import Flask, render_template
import os

app = Flask(__name__, template_folder="templates")

@app.route('/')
def index():
    return render_template('index.html', title="{name}")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
'''
        index_html = f'''<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8"/>
  <title>{name} — Web GUI</title>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
</head>
<body>
  <h1>🚀 {name} — Web GUI</h1>
  <p>Это стартовый шаблон. Запустите: <code>python web_server.py</code></p>
</body>
</html>
'''
        main_note = f'''# {name} Web GUI (файлы: web_server.py, templates/index.html)
print("🕸️ Web GUI template генерирован для {name}")
print("Для запуска: pip install flask")
print("Запустите файл web_server.py в папке проекта")
'''
        extras = {
            "web_server.py": web_server,
            os.path.join("templates", "index.html"): index_html,
            "README_web.txt": main_note
        }
        # main_code — небольшой указатель
        main_code = '# Этот проект содержит web_server.py и папку templates/. См. README_web.txt'
        return main_code, extras

    def terminal_template(self, name):
        code = f'''#!/usr/bin/env python3
import argparse
import sys
import os

def main():
    print("🚀 {name} - Terminal Application")
    print("=" * 50)

    parser = argparse.ArgumentParser(description='{name} - Auto Generated CLI')
    parser.add_argument('--start', action='store_true', help='Start application')
    parser.add_argument('--config', type=str, help='Configuration file')
    parser.add_argument('--input', type=str, help='Input file or directory')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')

    args = parser.parse_args()

    if args.start:
        print("🎯 Starting {name}...")
        print("✅ Application started successfully!")

    elif args.config:
        print(f"📁 Loading config: {{args.config}}")
        if os.path.exists(args.config):
            print("✅ Config loaded")
        else:
            print("❌ Config file not found")

    elif args.input:
        print(f"📂 Processing input: {{args.input}}")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
'''
        return code, {}

    def data_processor_template(self, name):
        # основной код включает проверку наличия pandas и дружелюбное сообщение
        code = f'''import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys

try:
    import pandas as pd
except Exception as e:
    pd = None

class {name}DataProcessor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("{name} - Data Processor")
        self.root.geometry("800x600")
        self.data = None
        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="📊 ОБРАБОТЧИК ДАННЫХ", font=("Arial", 16, "bold")).pack(pady=10)

        control_frame = ttk.Frame(main_frame)
        control_frame.pack(pady=15, fill=tk.X)

        ttk.Button(control_frame, text="📁 Загрузить CSV", command=self.load_csv).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="📊 Показать данные", command=self.show_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="💾 Экспорт", command=self.export_data).pack(side=tk.LEFT, padx=5)

        self.info_var = tk.StringVar(value="Загрузите файл для начала работы...")
        ttk.Label(main_frame, textvariable=self.info_var).pack(pady=10)

        self.log_text = tk.Text(main_frame, height=15)
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def load_csv(self):
        if pd is None:
            messagebox.showerror("Зависимость", "Требуется pandas. Установите: pip install pandas")
            return
        filename = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx;*.xls")])
        if filename:
            try:
                if filename.lower().endswith(('.xls', '.xlsx')):
                    self.data = pd.read_excel(filename)
                else:
                    self.data = pd.read_csv(filename)
                self.info_var.set(f"📊 Загружено: {{len(self.data)}} строк, {{len(self.data.columns)}} колонок")
                self.log(f"✅ Файл загружен: {{filename}}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {{e}}")

    def show_data(self):
        if self.data is not None:
            info = self.data.describe()
            self.log("📊 Статистика данных:")
            self.log(str(info))
        else:
            messagebox.showwarning("Внимание", "Сначала загрузите данные!")

    def export_data(self):
        if self.data is not None:
            filename = filedialog.asksaveasfilename(defaultextension=".csv")
            if filename:
                try:
                    self.data.to_csv(filename, index=False)
                    self.log(f"💾 Данные экспортированы: {{filename}}")
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось экспортировать: {{e}}")

    def log(self, message):
        self.log_text.insert(tk.END, f"{{message}}\\n")
        self.log_text.see(tk.END)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = {name}DataProcessor()
    app.run()
'''
        return code, {}

    # ---------- end templates ----------

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    # CLI support: можно передать папку и имя
    if len(sys.argv) > 1:
        constructor = GUIConstructor()
        constructor.path_var.set(sys.argv[1])
        if len(sys.argv) > 2:
            constructor.name_var.set(sys.argv[2])
        constructor.scan_project()
        constructor.create_gui()
        print("Создание завершено (CLI режим).")
    else:
        app = GUIConstructor()
        app.run()

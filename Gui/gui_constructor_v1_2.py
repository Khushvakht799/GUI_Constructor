import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import queue
import time
import os
import shutil
from pathlib import Path
import json
import logging
from datetime import datetime
import psutil
import subprocess
import sys

class AITemplateManager:
    """Менеджер шаблонов для AI проектов"""
    
    def __init__(self):
        self.templates = self.load_ai_templates()
        self.learned_skills = self.load_skills_library()
    
    def load_ai_templates(self):
        """Загрузка шаблонов для AI проектов"""
        try:
            with open('ai_templates.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return self.create_default_templates()
    
    def create_default_templates(self):
        """Создание шаблонов по умолчанию"""
        default_templates = {
            "ai_assistant": {
                "name": "AI Assistant Controller",
                "description": "GUI для управления когнитивными ассистентами",
                "required_dependencies": ["psutil", "threading", "queue"],
                "default_widgets": [
                    {"type": "button", "text": "▶️ Запустить ассистента", "command": "start_assistant", "category": "control"},
                    {"type": "button", "text": "⏹️ Остановить ассистента", "command": "stop_assistant", "category": "control"},
                    {"type": "button", "text": "📊 Мониторинг ресурсов", "command": "monitor_resources", "category": "monitoring"},
                    {"type": "button", "text": "📁 Просмотр логов", "command": "view_logs", "category": "monitoring"},
                    {"type": "log", "height": 15, "category": "monitoring"},
                    {"type": "progress", "mode": "determinate", "category": "monitoring"}
                ],
                "skill_categories": ["control", "monitoring", "training", "debugging"]
            },
            "ai_training": {
                "name": "AI Training Manager", 
                "description": "GUI для управления обучением моделей",
                "required_dependencies": ["psutil", "threading", "queue"],
                "default_widgets": [
                    {"type": "button", "text": "🎓 Начать обучение", "command": "start_training", "category": "training"},
                    {"type": "button", "text": "⏸️ Приостановить", "command": "pause_training", "category": "training"},
                    {"type": "button", "text": "📈 Графики обучения", "command": "show_charts", "category": "monitoring"},
                    {"type": "progress", "mode": "determinate", "category": "monitoring"},
                    {"type": "log", "height": 20, "category": "monitoring"}
                ],
                "skill_categories": ["training", "monitoring", "evaluation"]
            },
            "generic_ai": {
                "name": "AI Project Controller",
                "description": "Универсальный GUI для AI проектов",
                "required_dependencies": ["psutil", "threading", "queue"],
                "default_widgets": [
                    {"type": "button", "text": "🚀 Запуск проекта", "command": "start_project", "category": "control"},
                    {"type": "button", "text": "📊 Статус системы", "command": "system_status", "category": "monitoring"},
                    {"type": "log", "height": 15, "category": "monitoring"},
                    {"type": "progress", "mode": "determinate", "category": "monitoring"}
                ],
                "skill_categories": ["control", "monitoring", "maintenance"]
            }
        }
        
        # Сохраняем шаблоны в файл
        with open('ai_templates.json', 'w', encoding='utf-8') as f:
            json.dump(default_templates, f, indent=2, ensure_ascii=False)
        
        return default_templates
    
    def load_skills_library(self):
        """Загрузка библиотеки навыков"""
        try:
            with open('ai_skills_library.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return self.create_default_skills()
    
    def create_default_skills(self):
        """Создание навыков по умолчанию"""
        default_skills = {
            "start_assistant": {
                "name": "Запуск ассистента",
                "description": "Запуск основного скрипта ассистента",
                "command": "python main.py",
                "category": "control",
                "usage_count": 0
            },
            "monitor_resources": {
                "name": "Мониторинг ресурсов", 
                "description": "Отслеживание использования CPU, RAM, GPU",
                "command": "resource_monitor.py",
                "category": "monitoring", 
                "usage_count": 0
            },
            "view_logs": {
                "name": "Просмотр логов",
                "description": "Реальный просмотр логов приложения",
                "command": "log_viewer.py", 
                "category": "monitoring",
                "usage_count": 0
            }
        }
        
        # Сохраняем навыки в файл
        with open('ai_skills_library.json', 'w', encoding='utf-8') as f:
            json.dump(default_skills, f, indent=2, ensure_ascii=False)
            
        return default_skills
    
    def analyze_project_structure(self, project_path):
        """Анализ структуры AI проекта"""
        project_type = self.detect_project_type(project_path)
        return self.templates.get(project_type, self.templates["generic_ai"])
    
    def detect_project_type(self, project_path):
        """Определение типа AI проекта"""
        if self.has_file(project_path, "main.py") and self.has_file(project_path, "requirements.txt"):
            return "ai_assistant"
        elif self.has_file(project_path, "train.py") or self.has_file(project_path, "model.py"):
            return "ai_training"
        return "generic_ai"
    
    def has_file(self, project_path, filename):
        """Проверка наличия файла в проекте"""
        return os.path.exists(os.path.join(project_path, filename))
    
    def learn_new_skill(self, skill_config):
        """Добавление нового навыка в библиотеку"""
        skill_name = skill_config["name"]
        self.learned_skills[skill_name] = skill_config
        self.save_skills_library()
    
    def save_skills_library(self):
        """Сохранение библиотеки навыков"""
        with open('ai_skills_library.json', 'w', encoding='utf-8') as f:
            json.dump(self.learned_skills, f, indent=2, ensure_ascii=False)
    
    def suggest_skills(self, project_type):
        """Предложить навыки на основе типа проекта"""
        template = self.templates.get(project_type, self.templates["generic_ai"])
        categories = template["skill_categories"]
        
        suggested_skills = {}
        for skill_name, skill in self.learned_skills.items():
            if skill["category"] in categories:
                suggested_skills[skill_name] = skill
        
        return suggested_skills

class AIProjectProcessor:
    """Процессор для выполнения AI операций"""
    
    def __init__(self, log_callback, progress_callback, status_callback):
        self.log_callback = log_callback
        self.progress_callback = progress_callback
        self.status_callback = status_callback
        self.is_running = False
        self.current_process = None
    
    def start_assistant(self, project_path):
        """Запуск AI ассистента"""
        self._start_operation("start_assistant")
        
        try:
            main_script = self._find_main_script(project_path)
            if main_script:
                self.log_callback(f"🚀 Запуск ассистента: {main_script}")
                self.current_process = subprocess.Popen(
                    [sys.executable, main_script],
                    cwd=project_path,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                self.log_callback("✅ Ассистент запущен")
            else:
                self.log_callback("❌ Не найден основной скрипт (main.py, app.py, run.py)")
                
        except Exception as e:
            self.log_callback(f"❌ Ошибка запуска: {str(e)}")
        
        self._finish_operation()
    
    def stop_assistant(self):
        """Остановка AI ассистента"""
        if self.current_process and self.current_process.poll() is None:
            self.current_process.terminate()
            self.log_callback("⏹️ Ассистент остановлен")
        else:
            self.log_callback("ℹ️ Нет запущенных процессов")
    
    def monitor_resources(self):
        """Мониторинг системных ресурсов"""
        self._start_operation("monitor_resources")
        
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            # Memory usage
            memory = psutil.virtual_memory()
            # Disk usage
            disk = psutil.disk_usage('/')
            
            self.log_callback(f"📊 Статус системы:")
            self.log_callback(f"   CPU: {cpu_percent}%")
            self.log_callback(f"   RAM: {memory.percent}% ({memory.used//1024//1024}MB/{memory.total//1024//1024}MB)")
            self.log_callback(f"   Disk: {disk.percent}%")
            
        except Exception as e:
            self.log_callback(f"❌ Ошибка мониторинга: {str(e)}")
        
        self._finish_operation()
    
    def _find_main_script(self, project_path):
        """Поиск основного скрипта проекта"""
        possible_names = ["main.py", "app.py", "run.py", "start.py"]
        for name in possible_names:
            script_path = os.path.join(project_path, name)
            if os.path.exists(script_path):
                return script_path
        return None
    
    def _start_operation(self, operation):
        self.is_running = True
        self.log_callback(f"🔄 Начало операции: {operation}")
        self.status_callback(f"Выполняется {operation}...")
        self.progress_callback(0, 100)
    
    def _finish_operation(self):
        self.is_running = False
        self.log_callback("✅ Операция завершена")
        self.status_callback("Готов")
        self.progress_callback(100, 100)

class AIGUIConstructor:
    """Конструктор GUI для AI проектов"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🧠 AI GUI Constructor v2.0")
        self.root.geometry("1000x800")
        
        # Менеджеры
        self.template_manager = AITemplateManager()
        self.ai_processor = AIProjectProcessor(
            log_callback=self.log,
            progress_callback=self.update_progress,
            status_callback=self.update_status
        )
        
        # Очередь для межпоточного взаимодействия
        self.queue = queue.Queue()
        
        # Переменные проекта
        self.current_project_path = None
        self.current_project_type = None
        self.project_template = None
        
        self.setup_gui()
        self.setup_queue_processing()
    
    def setup_gui(self):
        """Создание интерфейса конструктора"""
        self.create_project_selection()
        self.create_ai_control_panel()
        self.create_monitoring_section()
        self.create_log_section()
        self.create_status_bar()
    
    def create_project_selection(self):
        """Панель выбора проекта"""
        project_frame = ttk.LabelFrame(self.root, text="📁 Выбор AI проекта", padding="10")
        project_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=10, pady=5)
        
        ttk.Label(project_frame, text="Путь к проекту:").grid(row=0, column=0, sticky=tk.W)
        self.project_path_var = tk.StringVar()
        self.project_entry = ttk.Entry(project_frame, textvariable=self.project_path_var, width=50)
        self.project_entry.grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E))
        
        ttk.Button(project_frame, text="Обзор", 
                  command=self.browse_project).grid(row=0, column=2, padx=5)
        ttk.Button(project_frame, text="Анализировать", 
                  command=self.analyze_project).grid(row=0, column=3, padx=5)
        
        self.project_info = ttk.Label(project_frame, text="Проект не выбран")
        self.project_info.grid(row=1, column=0, columnspan=4, sticky=tk.W, pady=5)
        
        project_frame.columnconfigure(1, weight=1)
    
    def create_ai_control_panel(self):
        """Панель управления AI проектом"""
        control_frame = ttk.LabelFrame(self.root, text="🎮 Управление AI проектом", padding="10")
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=5)
        
        # Будет заполняться динамически на основе шаблона
        self.control_buttons_frame = ttk.Frame(control_frame)
        self.control_buttons_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        control_frame.columnconfigure(0, weight=1)
    
    def create_monitoring_section(self):
        """Секция мониторинга"""
        monitor_frame = ttk.LabelFrame(self.root, text="📊 Мониторинг", padding="10")
        monitor_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), padx=10, pady=5)
        
        self.progress_bar = ttk.Progressbar(monitor_frame, mode='determinate')
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.progress_label = ttk.Label(monitor_frame, text="Готов к работе")
        self.progress_label.grid(row=1, column=0, sticky=tk.W)
        
        # Индикаторы ресурсов
        resources_frame = ttk.Frame(monitor_frame)
        resources_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(resources_frame, text="CPU:").grid(row=0, column=0, padx=5)
        self.cpu_var = tk.StringVar(value="0%")
        ttk.Label(resources_frame, textvariable=self.cpu_var).grid(row=0, column=1, padx=5)
        
        ttk.Label(resources_frame, text="RAM:").grid(row=0, column=2, padx=5)
        self.ram_var = tk.StringVar(value="0%")
        ttk.Label(resources_frame, textvariable=self.ram_var).grid(row=0, column=3, padx=5)
        
        ttk.Button(resources_frame, text="🔄 Обновить", 
                  command=self.update_resources).grid(row=0, column=4, padx=10)
        
        monitor_frame.columnconfigure(0, weight=1)
    
    def create_log_section(self):
        """Секция логов"""
        log_frame = ttk.LabelFrame(self.root, text="📋 Журнал операций", padding="10")
        log_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        log_buttons = ttk.Frame(log_frame)
        log_buttons.grid(row=1, column=0, pady=5)
        
        ttk.Button(log_buttons, text="Очистить логи", 
                  command=self.clear_logs).pack(side=tk.LEFT, padx=5)
        ttk.Button(log_buttons, text="Сохранить логи", 
                  command=self.save_logs).pack(side=tk.LEFT, padx=5)
        
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        self.root.rowconfigure(3, weight=1)
    
    def create_status_bar(self):
        """Строка статуса"""
        self.status_var = tk.StringVar(value="Готов к работе")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, padding="5")
        status_bar.grid(row=4, column=0, sticky=(tk.W, tk.E), padx=10, pady=5)
    
    def browse_project(self):
        """Выбор папки проекта"""
        folder = filedialog.askdirectory(title="Выберите папку AI проекта")
        if folder:
            self.project_path_var.set(folder)
            self.current_project_path = folder
    
    def analyze_project(self):
        """Анализ выбранного проекта"""
        if not self.current_project_path:
            messagebox.showwarning("Внимание", "Сначала выберите папку проекта!")
            return
        
        try:
            # Определяем тип проекта и получаем шаблон
            self.project_template = self.template_manager.analyze_project_structure(self.current_project_path)
            self.current_project_type = self.template_manager.detect_project_type(self.current_project_path)
            
            # Обновляем информацию о проекте
            project_name = os.path.basename(self.current_project_path)
            self.project_info.config(
                text=f"📁 Проект: {project_name} | Тип: {self.project_template['name']}"
            )
            
            # Создаем GUI на основе шаблона
            self.generate_gui_from_template()
            
            self.log(f"✅ Проект проанализирован: {self.project_template['name']}")
            self.log(f"📝 Описание: {self.project_template['description']}")
            
        except Exception as e:
            self.log(f"❌ Ошибка анализа проекта: {str(e)}")
    
    def generate_gui_from_template(self):
        """Генерация GUI на основе шаблона"""
        # Очищаем старые кнопки
        for widget in self.control_buttons_frame.winfo_children():
            widget.destroy()
        
        # Создаем кнопки из шаблона
        row, col = 0, 0
        for widget_config in self.project_template["default_widgets"]:
            if widget_config["type"] == "button":
                button = ttk.Button(
                    self.control_buttons_frame,
                    text=widget_config["text"],
                    command=lambda cmd=widget_config["command"]: self.execute_ai_command(cmd),
                    width=20
                )
                button.grid(row=row, column=col, padx=5, pady=5)
                col += 1
                if col > 2:  # 3 кнопки в ряд
                    col = 0
                    row += 1
    
    def execute_ai_command(self, command):
        """Выполнение AI команды в отдельном потоке"""
        if not self.current_project_path:
            messagebox.showwarning("Внимание", "Сначала выберите и проанализируйте проект!")
            return
        
        thread = threading.Thread(target=self._execute_command_thread, args=(command,), daemon=True)
        thread.start()
    
    def _execute_command_thread(self, command):
        """Выполнение команды в отдельном потоке"""
        try:
            if command == "start_assistant":
                self.ai_processor.start_assistant(self.current_project_path)
            elif command == "stop_assistant":
                self.ai_processor.stop_assistant()
            elif command == "monitor_resources":
                self.ai_processor.monitor_resources()
            elif command == "view_logs":
                self.log("📁 Функция просмотра логов активирована")
            else:
                self.log(f"ℹ️ Команда '{command}' не реализована")
                
        except Exception as e:
            self.log(f"❌ Ошибка выполнения команды: {str(e)}")
    
    def update_resources(self):
        """Обновление информации о ресурсах"""
        thread = threading.Thread(target=self._update_resources_thread, daemon=True)
        thread.start()
    
    def _update_resources_thread(self):
        """Обновление ресурсов в отдельном потоке"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            self.queue.put(("resource_update", cpu_percent, memory.percent))
            
        except Exception as e:
            self.log(f"❌ Ошибка обновления ресурсов: {str(e)}")
    
    def log(self, message):
        """Добавление сообщения в лог через очередь"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.queue.put(("log", f"[{timestamp}] {message}"))
    
    def update_progress(self, current, total):
        """Обновление прогресса через очередь"""
        self.queue.put(("progress", current, total))
    
    def update_status(self, status):
        """Обновление статуса через очередь"""
        self.queue.put(("status", status))
    
    def setup_queue_processing(self):
        """Настройка обработки сообщений из очереди"""
        def process_queue():
            try:
                while True:
                    msg_type, *args = self.queue.get_nowait()
                    
                    if msg_type == "log":
                        self._add_log_message(args[0])
                    elif msg_type == "progress":
                        self._update_progress_bar(args[0], args[1])
                    elif msg_type == "status":
                        self._update_status_text(args[0])
                    elif msg_type == "resource_update":
                        self._update_resource_display(args[0], args[1])
                        
            except queue.Empty:
                pass
            
            self.root.after(100, process_queue)
        
        self.root.after(100, process_queue)
    
    def _add_log_message(self, message):
        """Добавление сообщения в лог"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
    
    def _update_progress_bar(self, current, total):
        """Обновление прогресс-бара"""
        if total > 0:
            progress = (current / total) * 100
            self.progress_bar['value'] = progress
            self.progress_label.config(text=f"Выполнено: {current}/{total} ({progress:.1f}%)")
    
    def _update_status_text(self, status):
        """Обновление текста статуса"""
        self.status_var.set(status)
    
    def _update_resource_display(self, cpu_percent, ram_percent):
        """Обновление отображения ресурсов"""
        self.cpu_var.set(f"{cpu_percent}%")
        self.ram_var.set(f"{ram_percent}%")
    
    def clear_logs(self):
        """Очистка логов"""
        self.log_text.delete(1.0, tk.END)
        self.log("🧹 Журнал очищен")
    
    def save_logs(self):
        """Сохранение логов в файл"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.get(1.0, tk.END))
                self.log(f"💾 Логи сохранены в: {filename}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить логи: {str(e)}")

def main():
    """Основная функция"""
    root = tk.Tk()
    
    # Установка современной темы если доступна
    try:
        from ttkthemes import ThemedTk
        root = ThemedTk(theme="arc")
    except ImportError:
        print("ttkthemes не установлен, используется стандартная тема")
    
    app = AIGUIConstructor(root)
    root.mainloop()

if __name__ == "__main__":
    main()
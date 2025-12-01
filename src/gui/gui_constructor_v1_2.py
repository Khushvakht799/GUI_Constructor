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
    """РњРµРЅРµРґР¶РµСЂ С€Р°Р±Р»РѕРЅРѕРІ РґР»СЏ AI РїСЂРѕРµРєС‚РѕРІ"""
    
    def __init__(self):
        self.templates = self.load_ai_templates()
        self.learned_skills = self.load_skills_library()
    
    def load_ai_templates(self):
        """Р—Р°РіСЂСѓР·РєР° С€Р°Р±Р»РѕРЅРѕРІ РґР»СЏ AI РїСЂРѕРµРєС‚РѕРІ"""
        try:
            with open('ai_templates.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return self.create_default_templates()
    
    def create_default_templates(self):
        """РЎРѕР·РґР°РЅРёРµ С€Р°Р±Р»РѕРЅРѕРІ РїРѕ СѓРјРѕР»С‡Р°РЅРёСЋ"""
        default_templates = {
            "ai_assistant": {
                "name": "AI Assistant Controller",
                "description": "GUI РґР»СЏ СѓРїСЂР°РІР»РµРЅРёСЏ РєРѕРіРЅРёС‚РёРІРЅС‹РјРё Р°СЃСЃРёСЃС‚РµРЅС‚Р°РјРё",
                "required_dependencies": ["psutil", "threading", "queue"],
                "default_widgets": [
                    {"type": "button", "text": "в–¶пёЏ Р—Р°РїСѓСЃС‚РёС‚СЊ Р°СЃСЃРёСЃС‚РµРЅС‚Р°", "command": "start_assistant", "category": "control"},
                    {"type": "button", "text": "вЏ№пёЏ РћСЃС‚Р°РЅРѕРІРёС‚СЊ Р°СЃСЃРёСЃС‚РµРЅС‚Р°", "command": "stop_assistant", "category": "control"},
                    {"type": "button", "text": "рџ“Љ РњРѕРЅРёС‚РѕСЂРёРЅРі СЂРµСЃСѓСЂСЃРѕРІ", "command": "monitor_resources", "category": "monitoring"},
                    {"type": "button", "text": "рџ“Ѓ РџСЂРѕСЃРјРѕС‚СЂ Р»РѕРіРѕРІ", "command": "view_logs", "category": "monitoring"},
                    {"type": "log", "height": 15, "category": "monitoring"},
                    {"type": "progress", "mode": "determinate", "category": "monitoring"}
                ],
                "skill_categories": ["control", "monitoring", "training", "debugging"]
            },
            "ai_training": {
                "name": "AI Training Manager", 
                "description": "GUI РґР»СЏ СѓРїСЂР°РІР»РµРЅРёСЏ РѕР±СѓС‡РµРЅРёРµРј РјРѕРґРµР»РµР№",
                "required_dependencies": ["psutil", "threading", "queue"],
                "default_widgets": [
                    {"type": "button", "text": "рџЋ“ РќР°С‡Р°С‚СЊ РѕР±СѓС‡РµРЅРёРµ", "command": "start_training", "category": "training"},
                    {"type": "button", "text": "вЏёпёЏ РџСЂРёРѕСЃС‚Р°РЅРѕРІРёС‚СЊ", "command": "pause_training", "category": "training"},
                    {"type": "button", "text": "рџ“€ Р“СЂР°С„РёРєРё РѕР±СѓС‡РµРЅРёСЏ", "command": "show_charts", "category": "monitoring"},
                    {"type": "progress", "mode": "determinate", "category": "monitoring"},
                    {"type": "log", "height": 20, "category": "monitoring"}
                ],
                "skill_categories": ["training", "monitoring", "evaluation"]
            },
            "generic_ai": {
                "name": "AI Project Controller",
                "description": "РЈРЅРёРІРµСЂСЃР°Р»СЊРЅС‹Р№ GUI РґР»СЏ AI РїСЂРѕРµРєС‚РѕРІ",
                "required_dependencies": ["psutil", "threading", "queue"],
                "default_widgets": [
                    {"type": "button", "text": "рџљЂ Р—Р°РїСѓСЃРє РїСЂРѕРµРєС‚Р°", "command": "start_project", "category": "control"},
                    {"type": "button", "text": "рџ“Љ РЎС‚Р°С‚СѓСЃ СЃРёСЃС‚РµРјС‹", "command": "system_status", "category": "monitoring"},
                    {"type": "log", "height": 15, "category": "monitoring"},
                    {"type": "progress", "mode": "determinate", "category": "monitoring"}
                ],
                "skill_categories": ["control", "monitoring", "maintenance"]
            }
        }
        
        # РЎРѕС…СЂР°РЅСЏРµРј С€Р°Р±Р»РѕРЅС‹ РІ С„Р°Р№Р»
        with open('ai_templates.json', 'w', encoding='utf-8') as f:
            json.dump(default_templates, f, indent=2, ensure_ascii=False)
        
        return default_templates
    
    def load_skills_library(self):
        """Р—Р°РіСЂСѓР·РєР° Р±РёР±Р»РёРѕС‚РµРєРё РЅР°РІС‹РєРѕРІ"""
        try:
            with open('ai_skills_library.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return self.create_default_skills()
    
    def create_default_skills(self):
        """РЎРѕР·РґР°РЅРёРµ РЅР°РІС‹РєРѕРІ РїРѕ СѓРјРѕР»С‡Р°РЅРёСЋ"""
        default_skills = {
            "start_assistant": {
                "name": "Р—Р°РїСѓСЃРє Р°СЃСЃРёСЃС‚РµРЅС‚Р°",
                "description": "Р—Р°РїСѓСЃРє РѕСЃРЅРѕРІРЅРѕРіРѕ СЃРєСЂРёРїС‚Р° Р°СЃСЃРёСЃС‚РµРЅС‚Р°",
                "command": "python main.py",
                "category": "control",
                "usage_count": 0
            },
            "monitor_resources": {
                "name": "РњРѕРЅРёС‚РѕСЂРёРЅРі СЂРµСЃСѓСЂСЃРѕРІ", 
                "description": "РћС‚СЃР»РµР¶РёРІР°РЅРёРµ РёСЃРїРѕР»СЊР·РѕРІР°РЅРёСЏ CPU, RAM, GPU",
                "command": "resource_monitor.py",
                "category": "monitoring", 
                "usage_count": 0
            },
            "view_logs": {
                "name": "РџСЂРѕСЃРјРѕС‚СЂ Р»РѕРіРѕРІ",
                "description": "Р РµР°Р»СЊРЅС‹Р№ РїСЂРѕСЃРјРѕС‚СЂ Р»РѕРіРѕРІ РїСЂРёР»РѕР¶РµРЅРёСЏ",
                "command": "log_viewer.py", 
                "category": "monitoring",
                "usage_count": 0
            }
        }
        
        # РЎРѕС…СЂР°РЅСЏРµРј РЅР°РІС‹РєРё РІ С„Р°Р№Р»
        with open('ai_skills_library.json', 'w', encoding='utf-8') as f:
            json.dump(default_skills, f, indent=2, ensure_ascii=False)
            
        return default_skills
    
    def analyze_project_structure(self, project_path):
        """РђРЅР°Р»РёР· СЃС‚СЂСѓРєС‚СѓСЂС‹ AI РїСЂРѕРµРєС‚Р°"""
        project_type = self.detect_project_type(project_path)
        return self.templates.get(project_type, self.templates["generic_ai"])
    
    def detect_project_type(self, project_path):
        """РћРїСЂРµРґРµР»РµРЅРёРµ С‚РёРїР° AI РїСЂРѕРµРєС‚Р°"""
        if self.has_file(project_path, "main.py") and self.has_file(project_path, "requirements.txt"):
            return "ai_assistant"
        elif self.has_file(project_path, "train.py") or self.has_file(project_path, "model.py"):
            return "ai_training"
        return "generic_ai"
    
    def has_file(self, project_path, filename):
        """РџСЂРѕРІРµСЂРєР° РЅР°Р»РёС‡РёСЏ С„Р°Р№Р»Р° РІ РїСЂРѕРµРєС‚Рµ"""
        return os.path.exists(os.path.join(project_path, filename))
    
    def learn_new_skill(self, skill_config):
        """Р”РѕР±Р°РІР»РµРЅРёРµ РЅРѕРІРѕРіРѕ РЅР°РІС‹РєР° РІ Р±РёР±Р»РёРѕС‚РµРєСѓ"""
        skill_name = skill_config["name"]
        self.learned_skills[skill_name] = skill_config
        self.save_skills_library()
    
    def save_skills_library(self):
        """РЎРѕС…СЂР°РЅРµРЅРёРµ Р±РёР±Р»РёРѕС‚РµРєРё РЅР°РІС‹РєРѕРІ"""
        with open('ai_skills_library.json', 'w', encoding='utf-8') as f:
            json.dump(self.learned_skills, f, indent=2, ensure_ascii=False)
    
    def suggest_skills(self, project_type):
        """РџСЂРµРґР»РѕР¶РёС‚СЊ РЅР°РІС‹РєРё РЅР° РѕСЃРЅРѕРІРµ С‚РёРїР° РїСЂРѕРµРєС‚Р°"""
        template = self.templates.get(project_type, self.templates["generic_ai"])
        categories = template["skill_categories"]
        
        suggested_skills = {}
        for skill_name, skill in self.learned_skills.items():
            if skill["category"] in categories:
                suggested_skills[skill_name] = skill
        
        return suggested_skills

class AIProjectProcessor:
    """РџСЂРѕС†РµСЃСЃРѕСЂ РґР»СЏ РІС‹РїРѕР»РЅРµРЅРёСЏ AI РѕРїРµСЂР°С†РёР№"""
    
    def __init__(self, log_callback, progress_callback, status_callback):
        self.log_callback = log_callback
        self.progress_callback = progress_callback
        self.status_callback = status_callback
        self.is_running = False
        self.current_process = None
    
    def start_assistant(self, project_path):
        """Р—Р°РїСѓСЃРє AI Р°СЃСЃРёСЃС‚РµРЅС‚Р°"""
        self._start_operation("start_assistant")
        
        try:
            main_script = self._find_main_script(project_path)
            if main_script:
                self.log_callback(f"рџљЂ Р—Р°РїСѓСЃРє Р°СЃСЃРёСЃС‚РµРЅС‚Р°: {main_script}")
                self.current_process = subprocess.Popen(
                    [sys.executable, main_script],
                    cwd=project_path,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                self.log_callback("вњ… РђСЃСЃРёСЃС‚РµРЅС‚ Р·Р°РїСѓС‰РµРЅ")
            else:
                self.log_callback("вќЊ РќРµ РЅР°Р№РґРµРЅ РѕСЃРЅРѕРІРЅРѕР№ СЃРєСЂРёРїС‚ (main.py, app.py, run.py)")
                
        except Exception as e:
            self.log_callback(f"вќЊ РћС€РёР±РєР° Р·Р°РїСѓСЃРєР°: {str(e)}")
        
        self._finish_operation()
    
    def stop_assistant(self):
        """РћСЃС‚Р°РЅРѕРІРєР° AI Р°СЃСЃРёСЃС‚РµРЅС‚Р°"""
        if self.current_process and self.current_process.poll() is None:
            self.current_process.terminate()
            self.log_callback("вЏ№пёЏ РђСЃСЃРёСЃС‚РµРЅС‚ РѕСЃС‚Р°РЅРѕРІР»РµРЅ")
        else:
            self.log_callback("в„№пёЏ РќРµС‚ Р·Р°РїСѓС‰РµРЅРЅС‹С… РїСЂРѕС†РµСЃСЃРѕРІ")
    
    def monitor_resources(self):
        """РњРѕРЅРёС‚РѕСЂРёРЅРі СЃРёСЃС‚РµРјРЅС‹С… СЂРµСЃСѓСЂСЃРѕРІ"""
        self._start_operation("monitor_resources")
        
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            # Memory usage
            memory = psutil.virtual_memory()
            # Disk usage
            disk = psutil.disk_usage('/')
            
            self.log_callback(f"рџ“Љ РЎС‚Р°С‚СѓСЃ СЃРёСЃС‚РµРјС‹:")
            self.log_callback(f"   CPU: {cpu_percent}%")
            self.log_callback(f"   RAM: {memory.percent}% ({memory.used//1024//1024}MB/{memory.total//1024//1024}MB)")
            self.log_callback(f"   Disk: {disk.percent}%")
            
        except Exception as e:
            self.log_callback(f"вќЊ РћС€РёР±РєР° РјРѕРЅРёС‚РѕСЂРёРЅРіР°: {str(e)}")
        
        self._finish_operation()
    
    def _find_main_script(self, project_path):
        """РџРѕРёСЃРє РѕСЃРЅРѕРІРЅРѕРіРѕ СЃРєСЂРёРїС‚Р° РїСЂРѕРµРєС‚Р°"""
        possible_names = ["main.py", "app.py", "run.py", "start.py"]
        for name in possible_names:
            script_path = os.path.join(project_path, name)
            if os.path.exists(script_path):
                return script_path
        return None
    
    def _start_operation(self, operation):
        self.is_running = True
        self.log_callback(f"рџ”„ РќР°С‡Р°Р»Рѕ РѕРїРµСЂР°С†РёРё: {operation}")
        self.status_callback(f"Р’С‹РїРѕР»РЅСЏРµС‚СЃСЏ {operation}...")
        self.progress_callback(0, 100)
    
    def _finish_operation(self):
        self.is_running = False
        self.log_callback("вњ… РћРїРµСЂР°С†РёСЏ Р·Р°РІРµСЂС€РµРЅР°")
        self.status_callback("Р“РѕС‚РѕРІ")
        self.progress_callback(100, 100)

class AIGUIConstructor:
    """РљРѕРЅСЃС‚СЂСѓРєС‚РѕСЂ GUI РґР»СЏ AI РїСЂРѕРµРєС‚РѕРІ"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("рџ§  AI GUI Constructor v2.0")
        self.root.geometry("1000x800")
        
        # РњРµРЅРµРґР¶РµСЂС‹
        self.template_manager = AITemplateManager()
        self.ai_processor = AIProjectProcessor(
            log_callback=self.log,
            progress_callback=self.update_progress,
            status_callback=self.update_status
        )
        
        # РћС‡РµСЂРµРґСЊ РґР»СЏ РјРµР¶РїРѕС‚РѕС‡РЅРѕРіРѕ РІР·Р°РёРјРѕРґРµР№СЃС‚РІРёСЏ
        self.queue = queue.Queue()
        
        # РџРµСЂРµРјРµРЅРЅС‹Рµ РїСЂРѕРµРєС‚Р°
        self.current_project_path = None
        self.current_project_type = None
        self.project_template = None
        
        self.setup_gui()
        self.setup_queue_processing()
    
    def setup_gui(self):
        """РЎРѕР·РґР°РЅРёРµ РёРЅС‚РµСЂС„РµР№СЃР° РєРѕРЅСЃС‚СЂСѓРєС‚РѕСЂР°"""
        self.create_project_selection()
        self.create_ai_control_panel()
        self.create_monitoring_section()
        self.create_log_section()
        self.create_status_bar()
    
    def create_project_selection(self):
        """РџР°РЅРµР»СЊ РІС‹Р±РѕСЂР° РїСЂРѕРµРєС‚Р°"""
        project_frame = ttk.LabelFrame(self.root, text="рџ“Ѓ Р’С‹Р±РѕСЂ AI РїСЂРѕРµРєС‚Р°", padding="10")
        project_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=10, pady=5)
        
        ttk.Label(project_frame, text="РџСѓС‚СЊ Рє РїСЂРѕРµРєС‚Сѓ:").grid(row=0, column=0, sticky=tk.W)
        self.project_path_var = tk.StringVar()
        self.project_entry = ttk.Entry(project_frame, textvariable=self.project_path_var, width=50)
        self.project_entry.grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E))
        
        ttk.Button(project_frame, text="РћР±Р·РѕСЂ", 
                  command=self.browse_project).grid(row=0, column=2, padx=5)
        ttk.Button(project_frame, text="РђРЅР°Р»РёР·РёСЂРѕРІР°С‚СЊ", 
                  command=self.analyze_project).grid(row=0, column=3, padx=5)
        
        self.project_info = ttk.Label(project_frame, text="РџСЂРѕРµРєС‚ РЅРµ РІС‹Р±СЂР°РЅ")
        self.project_info.grid(row=1, column=0, columnspan=4, sticky=tk.W, pady=5)
        
        project_frame.columnconfigure(1, weight=1)
    
    def create_ai_control_panel(self):
        """РџР°РЅРµР»СЊ СѓРїСЂР°РІР»РµРЅРёСЏ AI РїСЂРѕРµРєС‚РѕРј"""
        control_frame = ttk.LabelFrame(self.root, text="рџЋ® РЈРїСЂР°РІР»РµРЅРёРµ AI РїСЂРѕРµРєС‚РѕРј", padding="10")
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=5)
        
        # Р‘СѓРґРµС‚ Р·Р°РїРѕР»РЅСЏС‚СЊСЃСЏ РґРёРЅР°РјРёС‡РµСЃРєРё РЅР° РѕСЃРЅРѕРІРµ С€Р°Р±Р»РѕРЅР°
        self.control_buttons_frame = ttk.Frame(control_frame)
        self.control_buttons_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        control_frame.columnconfigure(0, weight=1)
    
    def create_monitoring_section(self):
        """РЎРµРєС†РёСЏ РјРѕРЅРёС‚РѕСЂРёРЅРіР°"""
        monitor_frame = ttk.LabelFrame(self.root, text="рџ“Љ РњРѕРЅРёС‚РѕСЂРёРЅРі", padding="10")
        monitor_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), padx=10, pady=5)
        
        self.progress_bar = ttk.Progressbar(monitor_frame, mode='determinate')
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.progress_label = ttk.Label(monitor_frame, text="Р“РѕС‚РѕРІ Рє СЂР°Р±РѕС‚Рµ")
        self.progress_label.grid(row=1, column=0, sticky=tk.W)
        
        # РРЅРґРёРєР°С‚РѕСЂС‹ СЂРµСЃСѓСЂСЃРѕРІ
        resources_frame = ttk.Frame(monitor_frame)
        resources_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(resources_frame, text="CPU:").grid(row=0, column=0, padx=5)
        self.cpu_var = tk.StringVar(value="0%")
        ttk.Label(resources_frame, textvariable=self.cpu_var).grid(row=0, column=1, padx=5)
        
        ttk.Label(resources_frame, text="RAM:").grid(row=0, column=2, padx=5)
        self.ram_var = tk.StringVar(value="0%")
        ttk.Label(resources_frame, textvariable=self.ram_var).grid(row=0, column=3, padx=5)
        
        ttk.Button(resources_frame, text="рџ”„ РћР±РЅРѕРІРёС‚СЊ", 
                  command=self.update_resources).grid(row=0, column=4, padx=10)
        
        monitor_frame.columnconfigure(0, weight=1)
    
    def create_log_section(self):
        """РЎРµРєС†РёСЏ Р»РѕРіРѕРІ"""
        log_frame = ttk.LabelFrame(self.root, text="рџ“‹ Р–СѓСЂРЅР°Р» РѕРїРµСЂР°С†РёР№", padding="10")
        log_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        log_buttons = ttk.Frame(log_frame)
        log_buttons.grid(row=1, column=0, pady=5)
        
        ttk.Button(log_buttons, text="РћС‡РёСЃС‚РёС‚СЊ Р»РѕРіРё", 
                  command=self.clear_logs).pack(side=tk.LEFT, padx=5)
        ttk.Button(log_buttons, text="РЎРѕС…СЂР°РЅРёС‚СЊ Р»РѕРіРё", 
                  command=self.save_logs).pack(side=tk.LEFT, padx=5)
        
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        self.root.rowconfigure(3, weight=1)
    
    def create_status_bar(self):
        """РЎС‚СЂРѕРєР° СЃС‚Р°С‚СѓСЃР°"""
        self.status_var = tk.StringVar(value="Р“РѕС‚РѕРІ Рє СЂР°Р±РѕС‚Рµ")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, padding="5")
        status_bar.grid(row=4, column=0, sticky=(tk.W, tk.E), padx=10, pady=5)
    
    def browse_project(self):
        """Р’С‹Р±РѕСЂ РїР°РїРєРё РїСЂРѕРµРєС‚Р°"""
        folder = filedialog.askdirectory(title="Р’С‹Р±РµСЂРёС‚Рµ РїР°РїРєСѓ AI РїСЂРѕРµРєС‚Р°")
        if folder:
            self.project_path_var.set(folder)
            self.current_project_path = folder
    
    def analyze_project(self):
        """РђРЅР°Р»РёР· РІС‹Р±СЂР°РЅРЅРѕРіРѕ РїСЂРѕРµРєС‚Р°"""
        if not self.current_project_path:
            messagebox.showwarning("Р’РЅРёРјР°РЅРёРµ", "РЎРЅР°С‡Р°Р»Р° РІС‹Р±РµСЂРёС‚Рµ РїР°РїРєСѓ РїСЂРѕРµРєС‚Р°!")
            return
        
        try:
            # РћРїСЂРµРґРµР»СЏРµРј С‚РёРї РїСЂРѕРµРєС‚Р° Рё РїРѕР»СѓС‡Р°РµРј С€Р°Р±Р»РѕРЅ
            self.project_template = self.template_manager.analyze_project_structure(self.current_project_path)
            self.current_project_type = self.template_manager.detect_project_type(self.current_project_path)
            
            # РћР±РЅРѕРІР»СЏРµРј РёРЅС„РѕСЂРјР°С†РёСЋ Рѕ РїСЂРѕРµРєС‚Рµ
            project_name = os.path.basename(self.current_project_path)
            self.project_info.config(
                text=f"рџ“Ѓ РџСЂРѕРµРєС‚: {project_name} | РўРёРї: {self.project_template['name']}"
            )
            
            # РЎРѕР·РґР°РµРј GUI РЅР° РѕСЃРЅРѕРІРµ С€Р°Р±Р»РѕРЅР°
            self.generate_gui_from_template()
            
            self.log(f"вњ… РџСЂРѕРµРєС‚ РїСЂРѕР°РЅР°Р»РёР·РёСЂРѕРІР°РЅ: {self.project_template['name']}")
            self.log(f"рџ“ќ РћРїРёСЃР°РЅРёРµ: {self.project_template['description']}")
            
        except Exception as e:
            self.log(f"вќЊ РћС€РёР±РєР° Р°РЅР°Р»РёР·Р° РїСЂРѕРµРєС‚Р°: {str(e)}")
    
    def generate_gui_from_template(self):
        """Р“РµРЅРµСЂР°С†РёСЏ GUI РЅР° РѕСЃРЅРѕРІРµ С€Р°Р±Р»РѕРЅР°"""
        # РћС‡РёС‰Р°РµРј СЃС‚Р°СЂС‹Рµ РєРЅРѕРїРєРё
        for widget in self.control_buttons_frame.winfo_children():
            widget.destroy()
        
        # РЎРѕР·РґР°РµРј РєРЅРѕРїРєРё РёР· С€Р°Р±Р»РѕРЅР°
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
                if col > 2:  # 3 РєРЅРѕРїРєРё РІ СЂСЏРґ
                    col = 0
                    row += 1
    
    def execute_ai_command(self, command):
        """Р’С‹РїРѕР»РЅРµРЅРёРµ AI РєРѕРјР°РЅРґС‹ РІ РѕС‚РґРµР»СЊРЅРѕРј РїРѕС‚РѕРєРµ"""
        if not self.current_project_path:
            messagebox.showwarning("Р’РЅРёРјР°РЅРёРµ", "РЎРЅР°С‡Р°Р»Р° РІС‹Р±РµСЂРёС‚Рµ Рё РїСЂРѕР°РЅР°Р»РёР·РёСЂСѓР№С‚Рµ РїСЂРѕРµРєС‚!")
            return
        
        thread = threading.Thread(target=self._execute_command_thread, args=(command,), daemon=True)
        thread.start()
    
    def _execute_command_thread(self, command):
        """Р’С‹РїРѕР»РЅРµРЅРёРµ РєРѕРјР°РЅРґС‹ РІ РѕС‚РґРµР»СЊРЅРѕРј РїРѕС‚РѕРєРµ"""
        try:
            if command == "start_assistant":
                self.ai_processor.start_assistant(self.current_project_path)
            elif command == "stop_assistant":
                self.ai_processor.stop_assistant()
            elif command == "monitor_resources":
                self.ai_processor.monitor_resources()
            elif command == "view_logs":
                self.log("рџ“Ѓ Р¤СѓРЅРєС†РёСЏ РїСЂРѕСЃРјРѕС‚СЂР° Р»РѕРіРѕРІ Р°РєС‚РёРІРёСЂРѕРІР°РЅР°")
            else:
                self.log(f"в„№пёЏ РљРѕРјР°РЅРґР° '{command}' РЅРµ СЂРµР°Р»РёР·РѕРІР°РЅР°")
                
        except Exception as e:
            self.log(f"вќЊ РћС€РёР±РєР° РІС‹РїРѕР»РЅРµРЅРёСЏ РєРѕРјР°РЅРґС‹: {str(e)}")
    
    def update_resources(self):
        """РћР±РЅРѕРІР»РµРЅРёРµ РёРЅС„РѕСЂРјР°С†РёРё Рѕ СЂРµСЃСѓСЂСЃР°С…"""
        thread = threading.Thread(target=self._update_resources_thread, daemon=True)
        thread.start()
    
    def _update_resources_thread(self):
        """РћР±РЅРѕРІР»РµРЅРёРµ СЂРµСЃСѓСЂСЃРѕРІ РІ РѕС‚РґРµР»СЊРЅРѕРј РїРѕС‚РѕРєРµ"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            self.queue.put(("resource_update", cpu_percent, memory.percent))
            
        except Exception as e:
            self.log(f"вќЊ РћС€РёР±РєР° РѕР±РЅРѕРІР»РµРЅРёСЏ СЂРµСЃСѓСЂСЃРѕРІ: {str(e)}")
    
    def log(self, message):
        """Р”РѕР±Р°РІР»РµРЅРёРµ СЃРѕРѕР±С‰РµРЅРёСЏ РІ Р»РѕРі С‡РµСЂРµР· РѕС‡РµСЂРµРґСЊ"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.queue.put(("log", f"[{timestamp}] {message}"))
    
    def update_progress(self, current, total):
        """РћР±РЅРѕРІР»РµРЅРёРµ РїСЂРѕРіСЂРµСЃСЃР° С‡РµСЂРµР· РѕС‡РµСЂРµРґСЊ"""
        self.queue.put(("progress", current, total))
    
    def update_status(self, status):
        """РћР±РЅРѕРІР»РµРЅРёРµ СЃС‚Р°С‚СѓСЃР° С‡РµСЂРµР· РѕС‡РµСЂРµРґСЊ"""
        self.queue.put(("status", status))
    
    def setup_queue_processing(self):
        """РќР°СЃС‚СЂРѕР№РєР° РѕР±СЂР°Р±РѕС‚РєРё СЃРѕРѕР±С‰РµРЅРёР№ РёР· РѕС‡РµСЂРµРґРё"""
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
        """Р”РѕР±Р°РІР»РµРЅРёРµ СЃРѕРѕР±С‰РµРЅРёСЏ РІ Р»РѕРі"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
    
    def _update_progress_bar(self, current, total):
        """РћР±РЅРѕРІР»РµРЅРёРµ РїСЂРѕРіСЂРµСЃСЃ-Р±Р°СЂР°"""
        if total > 0:
            progress = (current / total) * 100
            self.progress_bar['value'] = progress
            self.progress_label.config(text=f"Р’С‹РїРѕР»РЅРµРЅРѕ: {current}/{total} ({progress:.1f}%)")
    
    def _update_status_text(self, status):
        """РћР±РЅРѕРІР»РµРЅРёРµ С‚РµРєСЃС‚Р° СЃС‚Р°С‚СѓСЃР°"""
        self.status_var.set(status)
    
    def _update_resource_display(self, cpu_percent, ram_percent):
        """РћР±РЅРѕРІР»РµРЅРёРµ РѕС‚РѕР±СЂР°Р¶РµРЅРёСЏ СЂРµСЃСѓСЂСЃРѕРІ"""
        self.cpu_var.set(f"{cpu_percent}%")
        self.ram_var.set(f"{ram_percent}%")
    
    def clear_logs(self):
        """РћС‡РёСЃС‚РєР° Р»РѕРіРѕРІ"""
        self.log_text.delete(1.0, tk.END)
        self.log("рџ§№ Р–СѓСЂРЅР°Р» РѕС‡РёС‰РµРЅ")
    
    def save_logs(self):
        """РЎРѕС…СЂР°РЅРµРЅРёРµ Р»РѕРіРѕРІ РІ С„Р°Р№Р»"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("РўРµРєСЃС‚РѕРІС‹Рµ С„Р°Р№Р»С‹", "*.txt"), ("Р’СЃРµ С„Р°Р№Р»С‹", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.get(1.0, tk.END))
                self.log(f"рџ’ѕ Р›РѕРіРё СЃРѕС…СЂР°РЅРµРЅС‹ РІ: {filename}")
            except Exception as e:
                messagebox.showerror("РћС€РёР±РєР°", f"РќРµ СѓРґР°Р»РѕСЃСЊ СЃРѕС…СЂР°РЅРёС‚СЊ Р»РѕРіРё: {str(e)}")

def main():
    """РћСЃРЅРѕРІРЅР°СЏ С„СѓРЅРєС†РёСЏ"""
    root = tk.Tk()
    
    # РЈСЃС‚Р°РЅРѕРІРєР° СЃРѕРІСЂРµРјРµРЅРЅРѕР№ С‚РµРјС‹ РµСЃР»Рё РґРѕСЃС‚СѓРїРЅР°
    try:
        from ttkthemes import ThemedTk
        root = ThemedTk(theme="arc")
    except ImportError:
        print("ttkthemes РЅРµ СѓСЃС‚Р°РЅРѕРІР»РµРЅ, РёСЃРїРѕР»СЊР·СѓРµС‚СЃСЏ СЃС‚Р°РЅРґР°СЂС‚РЅР°СЏ С‚РµРјР°")
    
    app = AIGUIConstructor(root)
    root.mainloop()

if __name__ == "__main__":
    main()


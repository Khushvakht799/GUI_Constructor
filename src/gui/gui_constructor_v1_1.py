# gui_constructor_v1_1.py - (Р’РµСЂСЃРёСЏ С‡Р°С‚Р°Р“РїС‚) - РЎРѕС…СЂР°РЅРёС‚Рµ Рё Р·Р°РїСѓСЃС‚РёС‚Рµ
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

APP_TITLE = "GUI Constructor v1.1 - Р‘Р•Р—РћРџРђРЎРќРћ"

def timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def safe_write_file(path, content, encoding="utf-8"):
    """
    РђС‚РѕРјР°СЂРЅРѕ Р·Р°РїРёСЃР°С‚СЊ С„Р°Р№Р»: СЃРЅР°С‡Р°Р»Р° РІРѕ РІСЂРµРјРµРЅРЅС‹Р№, Р·Р°С‚РµРј os.replace.
    Р•СЃР»Рё С„Р°Р№Р» СЃСѓС‰РµСЃС‚РІСѓРµС‚ - СЃРґРµР»Р°РµРј СЂРµР·РµСЂРІРЅСѓСЋ РєРѕРїРёСЋ.
    """
    dirpath = os.path.dirname(path) or "."
    os.makedirs(dirpath, exist_ok=True)

    if os.path.exists(path):
        bak = f"{path}.bak.{timestamp()}"
        try:
            shutil.copy2(path, bak)
        except Exception:
            # РµСЃР»Рё РєРѕРїРёСЂРѕРІР°РЅРёРµ РїСЂРѕРІР°Р»РёР»РѕСЃСЊ вЂ” РїРµСЂРµРёРјРµРЅСѓРµРј
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
    """Р§РёС‚Р°РµС‚ stdout/stderr РїСЂРѕС†РµСЃСЃР° Рё РєР»Р°РґС‘С‚ СЃС‚СЂРѕРєРё РІ РѕС‡РµСЂРµРґСЊ."""
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

        # РѕС‡РµСЂРµРґСЊ РґР»СЏ РїРѕС‚РѕРєРѕРІРѕР№ Р·Р°РїРёСЃРё РІ Р»РѕРі (thread -> main)
        self.log_q = queue.Queue()
        self.root.after(200, self._process_log_queue)

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="12")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        title = ttk.Label(main_frame, text="рџљЂ GUI CONSTRUCTOR v1.1 вЂ” СЃРѕС…СЂР°РЅРЅРѕ Рё СЃСЂР°Р·Сѓ",
                          font=("Arial", 16, "bold"))
        title.grid(row=0, column=0, columnspan=4, pady=(0, 12), sticky=tk.W)

        ttk.Label(main_frame, text="РџР°РїРєР° РїСЂРѕРµРєС‚Р°:").grid(row=1, column=0, sticky=tk.W, pady=4)
        self.path_var = tk.StringVar(value=os.getcwd())
        ttk.Entry(main_frame, textvariable=self.path_var, width=60).grid(row=1, column=1, columnspan=2, pady=4, sticky=(tk.W, tk.E))
        ttk.Button(main_frame, text="РћР±Р·РѕСЂ", command=self.browse_folder).grid(row=1, column=3, pady=4, sticky=tk.E)

        ttk.Label(main_frame, text="РРјСЏ РїСЂРѕРµРєС‚Р°:").grid(row=2, column=0, sticky=tk.W, pady=4)
        self.name_var = tk.StringVar(value="MyApp")
        ttk.Entry(main_frame, textvariable=self.name_var, width=60).grid(row=2, column=1, columnspan=3, pady=4, sticky=(tk.W, tk.E))

        ttk.Label(main_frame, text="РЁР°Р±Р»РѕРЅ GUI:").grid(row=3, column=0, sticky=tk.W, pady=6)
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
        ttk.Button(btn_frame, text="рџ”Ќ РЎРєР°РЅРёСЂРѕРІР°С‚СЊ РїСЂРѕРµРєС‚", command=self.scan_project).grid(row=0, column=0, padx=6)
        ttk.Button(btn_frame, text="вљЎ РЎРѕР·РґР°С‚СЊ GUI", command=self.create_gui).grid(row=0, column=1, padx=6)
        ttk.Button(btn_frame, text="рџљЂ Р—Р°РїСѓСЃС‚РёС‚СЊ GUI", command=self.run_gui).grid(row=0, column=2, padx=6)
        ttk.Button(btn_frame, text="рџ—‚ РџРѕРєР°Р·Р°С‚СЊ РєРѕРЅС„РёРі", command=self.show_config).grid(row=0, column=3, padx=6)

        ttk.Label(main_frame, text="Р›РѕРі РІС‹РїРѕР»РЅРµРЅРёСЏ:").grid(row=9, column=0, sticky=tk.W, pady=(8,0))
        self.log_text = tk.Text(main_frame, height=18, width=100)
        self.log_text.grid(row=10, column=0, columnspan=4, pady=6, sticky=(tk.W, tk.E))

        self.status_var = tk.StringVar(value="Р“РѕС‚РѕРІ Рє СЂР°Р±РѕС‚Рµ...")
        ttk.Label(main_frame, textvariable=self.status_var, foreground="green").grid(row=11, column=0, columnspan=4, pady=4, sticky=tk.W)

    def browse_folder(self):
        path = filedialog.askdirectory(initialdir=self.path_var.get())
        if path:
            self.path_var.set(path)
            # РµСЃР»Рё РёРјСЏ РїСѓСЃС‚РѕРµ вЂ” РїРѕРґСЃС‚Р°РІРёРј basename
            if not self.name_var.get() or self.name_var.get().strip() == "":
                self.name_var.set(os.path.basename(path) or "MyApp")

    def _log_put(self, message):
        # РґРѕР±Р°РІР»СЏРµРј РІ РѕС‡РµСЂРµРґСЊ СЃ С‚Р°Р№РјС€С‚Р°РјРїРѕРј
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
        # РїРѕРІС‚РѕСЂСЏРµРј
        self.root.after(200, self._process_log_queue)

    def log(self, message):
        # thread-safe РІС‹Р·РѕРІ Р»РѕРіРіРµСЂР°
        self._log_put(message)

    def scan_project(self):
        self.log("рџ”Ќ РЎРєР°РЅРёСЂСѓСЋ РїСЂРѕРµРєС‚...")
        project_path = self.path_var.get()
        if not os.path.exists(project_path):
            self.log("вќЊ РџР°РїРєР° РЅРµ СЃСѓС‰РµСЃС‚РІСѓРµС‚!")
            self.status_var.set("РћС€РёР±РєР°: РїР°РїРєР° РЅРµ РЅР°Р№РґРµРЅР°")
            return
        files = os.listdir(project_path)
        self.log(f"рџ“Ѓ РќР°Р№РґРµРЅРѕ С„Р°Р№Р»РѕРІ/РїР°РїРѕРє: {len(files)}")
        py_files = [f for f in files if f.endswith('.py')]
        js_files = [f for f in files if f.endswith('.js')]
        json_files = [f for f in files if f.endswith('.json')]
        csv_like = [f for f in files if f.endswith('.csv') or f.endswith('.xlsx') or f.endswith('.xls')]
        # Р±РѕР»РµРµ РѕСЃС‚РѕСЂРѕР¶РЅС‹Р№ РІС‹Р±РѕСЂ С€Р°Р±Р»РѕРЅР°
        if any(name in files for name in ("setup.py", "requirements.txt")) or py_files:
            self.log("вњ… Р’РµСЂРѕСЏС‚РЅРѕ Python-РїСЂРѕРµРєС‚")
            self.template_var.set("python")
        elif 'package.json' in files or js_files:
            self.log("вњ… Р’РµСЂРѕСЏС‚РЅРѕ Web/JavaScript РїСЂРѕРµРєС‚")
            self.template_var.set("web")
        elif csv_like:
            self.log("вњ… Р’РµСЂРѕСЏС‚РЅРѕ РїСЂРѕРµРєС‚ РѕР±СЂР°Р±РѕС‚РєРё РґР°РЅРЅС‹С…")
            self.template_var.set("data_processor")
        else:
            self.log("вљ пёЏ  РќРµ СѓРґР°Р»РѕСЃСЊ РѕРґРЅРѕР·РЅР°С‡РЅРѕ РѕРїСЂРµРґРµР»РёС‚СЊ С‚РёРї вЂ” РѕСЃС‚Р°РІР»РµРЅ С‚РµСЂРјРёРЅР°Р»СЊРЅС‹Р№ С€Р°Р±Р»РѕРЅ")
            self.template_var.set("terminal")
        self.status_var.set("РЎРєР°РЅРёСЂРѕРІР°РЅРёРµ Р·Р°РІРµСЂС€РµРЅРѕ")

    def create_gui(self):
        project_path = os.path.abspath(self.path_var.get())
        project_name = self.name_var.get().strip() or "MyApp"
        template_type = self.template_var.get()
        self.log(f"рџ›  РЎРѕР·РґР°СЋ GUI: {project_name} ({template_type}) РІ {project_path}")

        if not os.path.exists(project_path):
            try:
                os.makedirs(project_path, exist_ok=True)
            except Exception as e:
                self.log(f"вќЊ РќРµ СѓРґР°Р»РѕСЃСЊ СЃРѕР·РґР°С‚СЊ РїР°РїРєСѓ РїСЂРѕРµРєС‚Р°: {e}")
                return

        try:
            template_func = self.templates.get(template_type, self.python_template)
            gui_code, extra_files = template_func(project_name)
            # main gui file path
            output_file = os.path.join(project_path, f"{project_name}_gui.py")
            # Р·Р°РїРёСЃС‹РІР°РµРј GUI С„Р°Р№Р» Р°С‚РѕРјР°СЂРЅРѕ
            safe_write_file(output_file, gui_code)
            self.log(f"вњ… GUI СЃРѕР·РґР°РЅ: {output_file}")

            # СЃРѕР·РґР°С‘Рј РґРѕРїРѕР»РЅРёС‚РµР»СЊРЅС‹Рµ С„Р°Р№Р»С‹, РµСЃР»Рё РµСЃС‚СЊ (web_server.py, templates/index.html Рё С‚.Рґ.)
            for relpath, content in (extra_files or {}).items():
                target = os.path.join(project_path, relpath)
                safe_write_file(target, content)
                self.log(f"вњ… Р”РѕРї. С„Р°Р№Р» СЃРѕР·РґР°РЅ: {target}")

            # РєРѕРЅС„РёРі
            config = {
                "project": {"name": project_name, "type": template_type, "path": project_path},
                "gui": {"file": output_file, "created": timestamp()}
            }
            config_file = os.path.join(project_path, "gui_config.json")
            safe_write_file(config_file, json.dumps(config, ensure_ascii=False, indent=2))
            self.log("вњ… РљРѕРЅС„РёРіСѓСЂР°С†РёСЏ СЃРѕС…СЂР°РЅРµРЅР°")
            self.status_var.set("GUI СѓСЃРїРµС€РЅРѕ СЃРѕР·РґР°РЅ!")

        except Exception as e:
            self.log(f"вќЊ РћС€РёР±РєР° РїСЂРё СЃРѕР·РґР°РЅРёРё GUI: {e}")
            self.status_var.set("РћС€РёР±РєР° СЃРѕР·РґР°РЅРёСЏ")

    def run_gui(self):
        project_path = os.path.abspath(self.path_var.get())
        project_name = self.name_var.get().strip() or "MyApp"
        gui_file = os.path.join(project_path, f"{project_name}_gui.py")
        if not os.path.exists(gui_file):
            self.log("вќЊ GUI С„Р°Р№Р» РЅРµ РЅР°Р№РґРµРЅ! РЎРѕР·РґР°Р№С‚Рµ РµРіРѕ СЃРЅР°С‡Р°Р»Р°.")
            messagebox.showwarning("Р¤Р°Р№Р» РЅРµ РЅР°Р№РґРµРЅ", "РЎРЅР°С‡Р°Р»Р° СЃРѕР·РґР°Р№С‚Рµ GUI (РєРЅРѕРїРєР° 'РЎРѕР·РґР°С‚СЊ GUI').")
            return

        self.log("рџљЂ Р—Р°РїСѓСЃРєР°СЋ GUI (РІ РѕС‚РґРµР»СЊРЅРѕРј РїСЂРѕС†РµСЃСЃРµ)...")
        self.status_var.set("Р—Р°РїСѓСЃРє...")

        def target():
            # Р·Р°РїСѓСЃРєР°РµРј СЃ РїРѕС‚РѕРєРѕРІС‹Рј С‡С‚РµРЅРёРµРј stdout/stderr
            try:
                # РёСЃРїРѕР»СЊР·СѓРµРј list Р°СЂРіСѓРјРµРЅС‚РѕРІ, С‡С‚РѕР±С‹ РєРѕСЂСЂРµРєС‚РЅРѕ РѕР±СЂР°Р±Р°С‚С‹РІР°С‚СЊ РїСЂРѕР±РµР»С‹ РІ РїСѓС‚Рё
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

                # С‡РёС‚Р°РµРј РѕС‡РµСЂРµРґСЊ Рё РѕС‚РѕР±СЂР°Р¶Р°РµРј
                while True:
                    try:
                        tag, line = q.get(timeout=0.2)
                        self._log_put(f"[{tag}] {line}")
                    except queue.Empty:
                        pass
                    rc = proc.poll()
                    if rc is not None:
                        # РґРѕР¶РёРґР°РµРјСЃСЏ РѕСЃС‚Р°РІС€РёС…СЃСЏ СЃРѕРѕР±С‰РµРЅРёР№
                        while not q.empty():
                            tag, line = q.get_nowait()
                            self._log_put(f"[{tag}] {line}")
                        break

                if proc.returncode == 0:
                    self.log("вњ… GUI РїСЂРѕС†РµСЃСЃ Р·Р°РІРµСЂС€РёР»СЃСЏ СѓСЃРїРµС€РЅРѕ")
                else:
                    self.log(f"вљ пёЏ GUI РїСЂРѕС†РµСЃСЃ Р·Р°РІРµСЂС€РёР»СЃСЏ СЃ РєРѕРґРѕРј: {proc.returncode}")

            except Exception as e:
                self.log(f"вќЊ РћС€РёР±РєР° Р·Р°РїСѓСЃРєР° GUI: {e}")
            finally:
                self.status_var.set("Р“РѕС‚РѕРІ Рє СЂР°Р±РѕС‚Рµ")

        threading.Thread(target=target, daemon=True).start()

    def show_config(self):
        project_path = os.path.abspath(self.path_var.get())
        cfg = os.path.join(project_path, "gui_config.json")
        if os.path.exists(cfg):
            try:
                with open(cfg, "r", encoding="utf-8") as f:
                    data = json.load(f)
                pretty = json.dumps(data, ensure_ascii=False, indent=2)
                # РїРѕРєР°Р·Р°С‚СЊ РІ РѕС‚РґРµР»СЊРЅРѕРј РѕРєРЅРµ
                wnd = tk.Toplevel(self.root)
                wnd.title("РљРѕРЅС„РёРіСѓСЂР°С†РёСЏ GUI")
                txt = tk.Text(wnd, width=80, height=30)
                txt.pack(fill=tk.BOTH, expand=True)
                txt.insert(tk.END, pretty)
            except Exception as e:
                messagebox.showerror("РћС€РёР±РєР°", f"РќРµ СѓРґР°Р»РѕСЃСЊ РѕС‚РєСЂС‹С‚СЊ РєРѕРЅС„РёРі: {e}")
        else:
            messagebox.showinfo("РљРѕРЅС„РёРіСѓСЂР°С†РёСЏ", "Р¤Р°Р№Р» gui_config.json РЅРµ РЅР°Р№РґРµРЅ РІ РїР°РїРєРµ РїСЂРѕРµРєС‚Р°.")

    # ---------- РЁРђР‘Р›РћРќР« (РІРѕР·РІСЂР°С‰Р°СЋС‚ (main_code, extra_files_dict)) ----------
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

        header = ttk.Label(main_frame, text="рџЋ‰ Р’РђРЁ {name} Р—РђРџРЈР©Р•Рќ!", font=("Arial", 18, "bold"))
        header.pack(pady=20)

        desc = ttk.Label(main_frame, text="Р­С‚Рѕ Р°РІС‚РѕРјР°С‚РёС‡РµСЃРєРё СЃРіРµРЅРµСЂРёСЂРѕРІР°РЅРЅС‹Р№ РёРЅС‚РµСЂС„РµР№СЃ. GUI Constructor СЃРѕР·РґР°Р» РµРіРѕ!",
                         justify=tk.CENTER)
        desc.pack(pady=10)

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=30)

        ttk.Button(btn_frame, text="рџ“Ѓ РћР±Р·РѕСЂ С„Р°Р№Р»РѕРІ", command=self.browse_files).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="вљЎ Р’С‹РїРѕР»РЅРёС‚СЊ", command=self.execute).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="вќЊ Р’С‹С…РѕРґ", command=self.root.quit).pack(side=tk.LEFT, padx=10)

        ttk.Label(main_frame, text="Р–СѓСЂРЅР°Р»:").pack(anchor=tk.W, pady=(20,5))
        self.log_text = tk.Text(main_frame, height=10, width=70)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        self.status_var = tk.StringVar(value="Р“РѕС‚РѕРІ Рє СЂР°Р±РѕС‚Рµ...")
        ttk.Label(main_frame, textvariable=self.status_var, foreground="green").pack(pady=10)

    def browse_files(self):
        filename = filedialog.askopenfilename()
        if filename:
            self.log(f"рџ“‚ Р’С‹Р±СЂР°РЅ С„Р°Р№Р»: {{filename}}")

    def execute(self):
        self.log("вљЎ Р’С‹РїРѕР»РЅРµРЅРёРµ РѕРїРµСЂР°С†РёР№...")
        self.status_var.set("Р’С‹РїРѕР»РЅСЏРµС‚СЃСЏ...")
        # Р”РѕР±Р°РІСЊС‚Рµ РІР°С€Сѓ Р»РѕРіРёРєСѓ Р·РґРµСЃСЊ
        self.status_var.set("Р“РѕС‚РѕРІРѕ")

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
        # СЃРѕР·РґР°С‘Рј web_server.py Рё С€Р°Р±Р»РѕРЅ index.html РІ РїР°РїРєРµ templates/
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
  <title>{name} вЂ” Web GUI</title>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
</head>
<body>
  <h1>рџљЂ {name} вЂ” Web GUI</h1>
  <p>Р­С‚Рѕ СЃС‚Р°СЂС‚РѕРІС‹Р№ С€Р°Р±Р»РѕРЅ. Р—Р°РїСѓСЃС‚РёС‚Рµ: <code>python web_server.py</code></p>
</body>
</html>
'''
        main_note = f'''# {name} Web GUI (С„Р°Р№Р»С‹: web_server.py, templates/index.html)
print("рџ•ёпёЏ Web GUI template РіРµРЅРµСЂРёСЂРѕРІР°РЅ РґР»СЏ {name}")
print("Р”Р»СЏ Р·Р°РїСѓСЃРєР°: pip install flask")
print("Р—Р°РїСѓСЃС‚РёС‚Рµ С„Р°Р№Р» web_server.py РІ РїР°РїРєРµ РїСЂРѕРµРєС‚Р°")
'''
        extras = {
            "web_server.py": web_server,
            os.path.join("templates", "index.html"): index_html,
            "README_web.txt": main_note
        }
        # main_code вЂ” РЅРµР±РѕР»СЊС€РѕР№ СѓРєР°Р·Р°С‚РµР»СЊ
        main_code = '# Р­С‚РѕС‚ РїСЂРѕРµРєС‚ СЃРѕРґРµСЂР¶РёС‚ web_server.py Рё РїР°РїРєСѓ templates/. РЎРј. README_web.txt'
        return main_code, extras

    def terminal_template(self, name):
        code = f'''#!/usr/bin/env python3
import argparse
import sys
import os

def main():
    print("рџљЂ {name} - Terminal Application")
    print("=" * 50)

    parser = argparse.ArgumentParser(description='{name} - Auto Generated CLI')
    parser.add_argument('--start', action='store_true', help='Start application')
    parser.add_argument('--config', type=str, help='Configuration file')
    parser.add_argument('--input', type=str, help='Input file or directory')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')

    args = parser.parse_args()

    if args.start:
        print("рџЋЇ Starting {name}...")
        print("вњ… Application started successfully!")

    elif args.config:
        print(f"рџ“Ѓ Loading config: {{args.config}}")
        if os.path.exists(args.config):
            print("вњ… Config loaded")
        else:
            print("вќЊ Config file not found")

    elif args.input:
        print(f"рџ“‚ Processing input: {{args.input}}")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
'''
        return code, {}

    def data_processor_template(self, name):
        # РѕСЃРЅРѕРІРЅРѕР№ РєРѕРґ РІРєР»СЋС‡Р°РµС‚ РїСЂРѕРІРµСЂРєСѓ РЅР°Р»РёС‡РёСЏ pandas Рё РґСЂСѓР¶РµР»СЋР±РЅРѕРµ СЃРѕРѕР±С‰РµРЅРёРµ
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

        ttk.Label(main_frame, text="рџ“Љ РћР‘Р РђР‘РћРўР§РРљ Р”РђРќРќР«РҐ", font=("Arial", 16, "bold")).pack(pady=10)

        control_frame = ttk.Frame(main_frame)
        control_frame.pack(pady=15, fill=tk.X)

        ttk.Button(control_frame, text="рџ“Ѓ Р—Р°РіСЂСѓР·РёС‚СЊ CSV", command=self.load_csv).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="рџ“Љ РџРѕРєР°Р·Р°С‚СЊ РґР°РЅРЅС‹Рµ", command=self.show_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="рџ’ѕ Р­РєСЃРїРѕСЂС‚", command=self.export_data).pack(side=tk.LEFT, padx=5)

        self.info_var = tk.StringVar(value="Р—Р°РіСЂСѓР·РёС‚Рµ С„Р°Р№Р» РґР»СЏ РЅР°С‡Р°Р»Р° СЂР°Р±РѕС‚С‹...")
        ttk.Label(main_frame, textvariable=self.info_var).pack(pady=10)

        self.log_text = tk.Text(main_frame, height=15)
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def load_csv(self):
        if pd is None:
            messagebox.showerror("Р—Р°РІРёСЃРёРјРѕСЃС‚СЊ", "РўСЂРµР±СѓРµС‚СЃСЏ pandas. РЈСЃС‚Р°РЅРѕРІРёС‚Рµ: pip install pandas")
            return
        filename = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx;*.xls")])
        if filename:
            try:
                if filename.lower().endswith(('.xls', '.xlsx')):
                    self.data = pd.read_excel(filename)
                else:
                    self.data = pd.read_csv(filename)
                self.info_var.set(f"рџ“Љ Р—Р°РіСЂСѓР¶РµРЅРѕ: {{len(self.data)}} СЃС‚СЂРѕРє, {{len(self.data.columns)}} РєРѕР»РѕРЅРѕРє")
                self.log(f"вњ… Р¤Р°Р№Р» Р·Р°РіСЂСѓР¶РµРЅ: {{filename}}")
            except Exception as e:
                messagebox.showerror("РћС€РёР±РєР°", f"РќРµ СѓРґР°Р»РѕСЃСЊ Р·Р°РіСЂСѓР·РёС‚СЊ С„Р°Р№Р»: {{e}}")

    def show_data(self):
        if self.data is not None:
            info = self.data.describe()
            self.log("рџ“Љ РЎС‚Р°С‚РёСЃС‚РёРєР° РґР°РЅРЅС‹С…:")
            self.log(str(info))
        else:
            messagebox.showwarning("Р’РЅРёРјР°РЅРёРµ", "РЎРЅР°С‡Р°Р»Р° Р·Р°РіСЂСѓР·РёС‚Рµ РґР°РЅРЅС‹Рµ!")

    def export_data(self):
        if self.data is not None:
            filename = filedialog.asksaveasfilename(defaultextension=".csv")
            if filename:
                try:
                    self.data.to_csv(filename, index=False)
                    self.log(f"рџ’ѕ Р”Р°РЅРЅС‹Рµ СЌРєСЃРїРѕСЂС‚РёСЂРѕРІР°РЅС‹: {{filename}}")
                except Exception as e:
                    messagebox.showerror("РћС€РёР±РєР°", f"РќРµ СѓРґР°Р»РѕСЃСЊ СЌРєСЃРїРѕСЂС‚РёСЂРѕРІР°С‚СЊ: {{e}}")

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
    # CLI support: РјРѕР¶РЅРѕ РїРµСЂРµРґР°С‚СЊ РїР°РїРєСѓ Рё РёРјСЏ
    if len(sys.argv) > 1:
        constructor = GUIConstructor()
        constructor.path_var.set(sys.argv[1])
        if len(sys.argv) > 2:
            constructor.name_var.set(sys.argv[2])
        constructor.scan_project()
        constructor.create_gui()
        print("РЎРѕР·РґР°РЅРёРµ Р·Р°РІРµСЂС€РµРЅРѕ (CLI СЂРµР¶РёРј).")
    else:
        app = GUIConstructor()
        app.run()


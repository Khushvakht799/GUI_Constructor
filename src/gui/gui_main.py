"""
Gui/gui_main.py

Р“Р»Р°РІРЅС‹Р№ GUI-РєР°СЂРєР°СЃ РґР»СЏ Jarvis GUI_Constructor.
Р—Р°РїСѓСЃРєР°РµС‚СЃСЏ РёР· main.py (СЃРј. РёРЅСЃС‚СЂСѓРєС†РёСЏ РЅРёР¶Рµ).

РљР»СЋС‡РµРІС‹Рµ РІРѕР·РјРѕР¶РЅРѕСЃС‚Рё:
- СЃРёСЃС‚РµРјРЅР°СЏ С‚РµРјР° (РїРѕ СѓРјРѕР»С‡Р°РЅРёСЋ)
- РґРµСЂРµРІРѕ РїСЂРѕРµРєС‚Р° (РїРѕРґРіСЂСѓР¶Р°РµС‚СЃСЏ РёР· analyzer_report.json)
- РєРЅРѕРїРєРё: РђРЅР°Р»РёР·РёСЂРѕРІР°С‚СЊ, РћС‚РєСЂС‹С‚СЊ KB, Р РµС„Р°РєС‚РѕСЂРёРЅРі, РўРµСЃС‚, Р›РѕРіРё
- Р»РѕРі РІРЅРёР·Сѓ
- Р·Р°РїСѓСЃРє project_analyzer РІ РѕС‚РґРµР»СЊРЅРѕРј РїРѕС‚РѕРєРµ (subprocess)
- Р±РµР·РѕРїР°СЃРЅР°СЏ СЂР°Р±РѕС‚Р° СЃ С„Р°Р№Р»Р°РјРё

Р­С‚РѕС‚ С„Р°Р№Р» РґРѕР±Р°РІР»СЏРµС‚СЃСЏ РІ РїР°РїРєСѓ Gui/ Рё РЅРµ РёР·РјРµРЅСЏРµС‚ СЃСѓС‰РµСЃС‚РІСѓСЋС‰РёРµ РјРѕРґСѓР»Рё.
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
from core.kb_manager import KnowledgeBase, load_kb

# РџСѓС‚Рё
ROOT = Path(__file__).resolve().parents[1]
KB_FILE = ROOT / 'Gui' / 'knowledge.json'
ANALYZER_REPORT = ROOT / 'analyzer_report.json'
ANALYZER_SCRIPT = ROOT / 'core' / 'project_analyzer.py'

# Р“Р»РѕР±Р°Р»СЊРЅС‹Р№ РѕР±СЉРµРєС‚ KB
kb = KnowledgeBase(kb_path=KB_FILE)

class GUIManager:
    def __init__(self, root_tk):
        self.root = root_tk
        self.root.title('Jarvis GUI Constructor вЂ” РЈРїСЂР°РІР»РµРЅРёРµ')
        self.root.geometry('980x680')
        self.log_q = queue.Queue()
        self._build_ui()
        self.root.after(200, self._flush_log_q)


    def _build_ui(self):
        # РџР°РЅРµР»СЊ РёРЅСЃС‚СЂСѓРјРµРЅС‚РѕРІ
        toolbar = ttk.Frame(self.root, padding=6)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        btn_analyze = ttk.Button(toolbar, text='рџ”Ќ РђРЅР°Р»РёР·РёСЂРѕРІР°С‚СЊ', command=self.on_analyze)
        btn_kb = ttk.Button(toolbar, text='рџ“љ Knowledge', command=self.on_open_kb)
        btn_refactor = ttk.Button(toolbar, text='вљ™пёЏ Р РµС„Р°РєС‚РѕСЂРёРЅРі', command=self.on_refactor)
        btn_test = ttk.Button(toolbar, text='рџ§Є РўРµСЃС‚РёСЂРѕРІР°С‚СЊ', command=self.on_test)
        btn_reload = ttk.Button(toolbar, text='рџ”„ РћР±РЅРѕРІРёС‚СЊ РґРµСЂРµРІРѕ', command=self.load_tree_from_report)

        btn_analyze.pack(side=tk.LEFT, padx=4)
        btn_kb.pack(side=tk.LEFT, padx=4)
        btn_refactor.pack(side=tk.LEFT, padx=4)
        btn_test.pack(side=tk.LEFT, padx=4)
        btn_reload.pack(side=tk.LEFT, padx=4)

        # РћСЃРЅРѕРІРЅРѕР№ С„СЂРµР№Рј: РґРµСЂРµРІРѕ СЃР»РµРІР°, С†РµРЅС‚СЂР°Р»СЊРЅР°СЏ РїР°РЅРµР»СЊ, Р»РѕРі СЃРЅРёР·Сѓ
        main = ttk.Frame(self.root, padding=6)
        main.pack(fill=tk.BOTH, expand=True)

        main.columnconfigure(1, weight=1)
        main.rowconfigure(0, weight=1)

        # Р”РµСЂРµРІРѕ РїСЂРѕРµРєС‚Р°
        tree_frame = ttk.Frame(main)
        tree_frame.grid(row=0, column=0, sticky='nsw', padx=(0,6))
        ttk.Label(tree_frame, text='РЎС‚СЂСѓРєС‚СѓСЂР° РїСЂРѕРµРєС‚Р°').pack(anchor='w')
        self.tree = ttk.Treeview(tree_frame, height=30)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind('<Double-1>', self.on_tree_double)

        # Р¦РµРЅС‚СЂР°Р»СЊРЅР°СЏ РїР°РЅРµР»СЊ
        center = ttk.Frame(main)
        center.grid(row=0, column=1, sticky='nsew')
        ttk.Label(center, text='РРЅС„РѕСЂРјР°С†РёСЏ').pack(anchor='w')
        self.info_text = tk.Text(center, height=30)
        self.info_text.pack(fill=tk.BOTH, expand=True)

        # Р›РѕРі
        log_frame = ttk.Frame(self.root)
        log_frame.pack(side=tk.BOTTOM, fill=tk.X)
        ttk.Label(log_frame, text='Р–СѓСЂРЅР°Р»:').pack(anchor='w')
        self.log_widget = tk.Text(log_frame, height=10)
        self.log_widget.pack(fill=tk.X)

        # СЃС‚Р°С‚СѓСЃ Р±Р°СЂ
        self.status_var = tk.StringVar(value='Р“РѕС‚РѕРІ')
        status = ttk.Label(self.root, textvariable=self.status_var, anchor='w')
        status.pack(side=tk.BOTTOM, fill=tk.X)

        # РЅР°С‡Р°Р»СЊРЅР°СЏ Р·Р°РіСЂСѓР·РєР°
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
        # Р—Р°РїСѓСЃРєР°РµРј Р°РЅР°Р»РёР· РІ РѕС‚РґРµР»СЊРЅРѕРј РїРѕС‚РѕРєРµ
        project_path = str(ROOT)
        self.log('Р—Р°РїСѓСЃРє Р°РЅР°Р»РёР·Р°С‚РѕСЂР°...')
        self.status_var.set('РђРЅР°Р»РёР·...')
        threading.Thread(target=self._run_analyzer_subprocess, args=(project_path,), daemon=True).start()

    def _run_analyzer_subprocess(self, project_path: str):
        # Р—Р°РїСѓСЃРєР°Рј python core/project_analyzer.py --out analyzer_report.json
        cmd = [sys.executable, str(ANALYZER_SCRIPT), project_path, '--out', str(ANALYZER_REPORT)]
        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in proc.stdout:
                self.log(line.rstrip('\n'))
            proc.wait()
            if proc.returncode == 0:
                self.log('РђРЅР°Р»РёР· Р·Р°РІРµСЂС€С‘РЅ')
                self.status_var.set('РђРЅР°Р»РёР· Р·Р°РІРµСЂС€С‘РЅ')
                # РѕР±РЅРѕРІРёРј РґРµСЂРµРІРѕ
                self.load_tree_from_report()
            else:
                self.log(f'РђРЅР°Р»РёР· Р·Р°РІРµСЂС€С‘РЅ СЃ РєРѕРґРѕРј {proc.returncode}')
                self.status_var.set('РђРЅР°Р»РёР· Р·Р°РІРµСЂС€РёР»СЃСЏ СЃ РѕС€РёР±РєРѕР№')
        except Exception as e:
            self.log(f'РћС€РёР±РєР° Р·Р°РїСѓСЃРєР° Р°РЅР°Р»РёР·Р°С‚РѕСЂР°: {e}')
            self.status_var.set('РћС€РёР±РєР°')

    def load_tree_from_report(self):
        # Р·Р°РіСЂСѓР¶Р°РµРј analyzer_report.json
        if not ANALYZER_REPORT.exists():
            self.log('analyzer_report.json РЅРµ РЅР°Р№РґРµРЅ вЂ” Р·Р°РїСѓСЃС‚РёС‚Рµ Р°РЅР°Р»РёР·')
            return
        try:
            with open(ANALYZER_REPORT, 'r', encoding='utf-8') as f:
                rep = json.load(f)
        except Exception as e:
            self.log(f'РќРµ СѓРґР°Р»РѕСЃСЊ РїСЂРѕС‡РёС‚Р°С‚СЊ РѕС‚С‡РµС‚: {e}')
            return
        # РѕС‡РёС‰Р°РµРј РґРµСЂРµРІРѕ
        for i in self.tree.get_children():
            self.tree.delete(i)
        # РґРѕР±Р°РІР»СЏРµРј С„Р°Р№Р»С‹
        files = rep.get('py_files', [])
        root_node = self.tree.insert('', 'end', text=rep.get('root', 'project'))
        for f in files:
            self.tree.insert(root_node, 'end', text=f, values=(f,))
        self.tree.item(root_node, open=True)
        self.log('Р”РµСЂРµРІРѕ Р·Р°РіСЂСѓР¶РµРЅРѕ РёР· РѕС‚С‡С‘С‚Р°')

    def on_tree_double(self, event):
        item = self.tree.selection()
        if not item:
            return
        key = item[0]
        text = self.tree.item(key, 'text')
        # РµСЃР»Рё СЌС‚Рѕ С„Р°Р№Р» вЂ” РїРѕРєР°Р·Р°С‚СЊ СЃРѕРґРµСЂР¶РёРјРѕРµ
        if text.endswith('.py'):
            p = ROOT / text
            if p.exists():
                try:
                    s = p.read_text(encoding='utf-8')
                    self.info_text.delete('1.0', tk.END)
                    self.info_text.insert(tk.END, s)
                except Exception as e:
                    self.log(f'РќРµ СѓРґР°Р»РѕСЃСЊ РѕС‚РєСЂС‹С‚СЊ С„Р°Р№Р»: {e}')
            else:
                self.log('Р¤Р°Р№Р» РЅРµ РЅР°Р№РґРµРЅ')

    def on_open_kb(self):
        # РѕС‚РєСЂРѕРµРј knowledge.json РІ СЂРµРґР°РєС‚РѕСЂРµ
        if not KB_FILE.exists():
            # СЃРѕР·РґР°С‘Рј РјРёРЅРёРјР°Р»СЊРЅС‹Р№ РєР°СЂРєР°СЃ
            self._create_minimal_kb()
        try:
            s = KB_FILE.read_text(encoding='utf-8')
            # РїРѕРєР°Р·Р°С‚СЊ РІ РѕС‚РґРµР»СЊРЅРѕРј РѕРєРЅРµ
            wnd = tk.Toplevel(self.root)
            wnd.title('Knowledge Base')
            txt = tk.Text(wnd, width=100, height=40)
            txt.pack(fill=tk.BOTH, expand=True)
            txt.insert(tk.END, s)
            def save_and_close():
                try:
                    txt_content = txt.get('1.0', tk.END)
                    KB_FILE.write_text(txt_content, encoding='utf-8')
                    self.log('Knowledge Base СЃРѕС…СЂР°РЅРµРЅР°')
                    wnd.destroy()
                except Exception as e:
                    messagebox.showerror('РћС€РёР±РєР°', f'РќРµ СѓРґР°Р»РѕСЃСЊ СЃРѕС…СЂР°РЅРёС‚СЊ KB: {e}')
            btn = ttk.Button(wnd, text='РЎРѕС…СЂР°РЅРёС‚СЊ', command=save_and_close)
            btn.pack()
        except Exception as e:
            self.log(f'РќРµ СѓРґР°Р»РѕСЃСЊ РѕС‚РєСЂС‹С‚СЊ KB: {e}')

    def _create_minimal_kb(self):
        minimal = {'errors': {"SyntaxError": {"description": "РЎРёРЅС‚Р°РєСЃРёС‡РµСЃРєР°СЏ РѕС€РёР±РєР°", "fixes": ["РџСЂРѕРІРµСЂРёС‚СЊ СЃРёРЅС‚Р°РєСЃРёСЃ"]}}}
        try:
            KB_FILE.write_text(json.dumps(minimal, ensure_ascii=False, indent=2), encoding='utf-8')
            self.log('РЎРѕР·РґР°РЅ РјРёРЅРёРјР°Р»СЊРЅС‹Р№ knowledge.json')
        except Exception as e:
            self.log(f'РќРµ СѓРґР°Р»РѕСЃСЊ СЃРѕР·РґР°С‚СЊ KB: {e}')

    def on_refactor(self):
        # Р—Р°РіР»СѓС€РєР° вЂ” РІ Р±СѓРґСѓС‰РµРј РІС‹Р·РѕРІ СЂРµС„Р°РєС‚РѕСЂ-РґРІРёР¶РєР°
        messagebox.showinfo('Р РµС„Р°РєС‚РѕСЂРёРЅРі', 'Р—Р°РїР»Р°РЅРёСЂСѓР№ СЂРµС„Р°РєС‚РѕСЂРёРЅРі вЂ” РјРѕРґСѓР»СЊ РІ СЂР°Р·СЂР°Р±РѕС‚РєРµ')

    def on_test(self):
        # Р—Р°РіР»СѓС€РєР° РґР»СЏ С‚РµСЃС‚РёСЂРѕРІР°РЅРёСЏ
        messagebox.showinfo('РўРµСЃС‚С‹', 'Р—Р°РїСѓСЃРє С‚РµСЃС‚РѕРІ вЂ” РјРѕРґСѓР»СЊ РІ СЂР°Р·СЂР°Р±РѕС‚РєРµ')


def main():
    root = tk.Tk()
    GUIManager(root)
    root.mainloop()

# --- GUI launcher (added by assistant) ---
try:
    from Gui import gui_main
    gui_main.main()
except Exception:
    # Р•СЃР»Рё GUI РЅРµ РґРѕСЃС‚СѓРїРµРЅ РІ СЌС‚РѕР№ СЃСЂРµРґРµ вЂ” РѕСЃС‚Р°РІРёС‚СЊ РїСЂРµР¶РЅРµРµ РїРѕРІРµРґРµРЅРёРµ
    pass

import tkinter as tk
from .gui_manager import GUIManager

if __name__ == "__main__":
    root = tk.Tk()
    root.title("GUI Constructor Main Window")  # Р·Р°РіРѕР»РѕРІРѕРє РѕРєРЅР°
    app = GUIManager(root)  # РїРµСЂРµРґР°РµРј root РІ РєРѕРЅСЃС‚СЂСѓРєС‚РѕСЂ
    app.run()               # Р·Р°РїСѓСЃРє mainloop

# --- end GUI launcher ---


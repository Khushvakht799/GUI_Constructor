import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os

def load_kb():
    try:
        with open('data/knowledge.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def save_kb(data):
    try:
        with open('data/knowledge.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

class KnowledgeBase:
    def __init__(self):
        self.data = load_kb()
        
    def add_entry(self, key, value):
        self.data[key] = value
        save_kb(self.data)
        
    def get_entry(self, key):
        return self.data.get(key)
        
    def get_all(self):
        return self.data

class GUIManager:
    def __init__(self, root=None):
        self.root = root
        self.kb = KnowledgeBase()
        
    def create_button(self, text, command, **kwargs):
        from .buttons import CustomButton
        return CustomButton(self.root, text=text, command=command, **kwargs)
        
    def create_entry(self, **kwargs):
        from .fields import CustomEntry
        return CustomEntry(self.root, **kwargs)
        
    def show_info(self, title, message):
        if self.root:
            messagebox.showinfo(title, message)
        else:
            print(f'{title}: {message}')
            
    def ask_file(self, title='Выберите файл', filetypes=[('Все файлы', '*.*')]):
        if self.root:
            return filedialog.askopenfilename(title=title, filetypes=filetypes)
        return None

if __name__ == '__main__':
    root = tk.Tk()
    manager = GUIManager(root)
    print('GUIManager создан успешно')
    root.destroy()
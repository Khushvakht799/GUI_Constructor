import tkinter as tk
from tkinter import ttk

class CustomEntry(ttk.Entry):
    """Кастомное поле ввода"""
    
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        
    def clear(self):
        """Очистить поле"""
        self.delete(0, tk.END)
        
    def get_value(self):
        """Получить значение"""
        return self.get()

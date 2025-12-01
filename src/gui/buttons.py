import tkinter as tk
from tkinter import ttk

class CustomButton(ttk.Button):
    """Кастомная кнопка с дополнительными функциями"""
    
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(style="Custom.TButton")
        
    def set_tooltip(self, text):
        """Установить всплывающую подсказку"""
        # Реализация tooltip
        pass

class IconButton(CustomButton):
    """Кнопка с иконкой"""
    
    def __init__(self, master=None, icon=None, **kwargs):
        super().__init__(master, **kwargs)
        if icon:
            self.configure(image=icon)

class ToggleButton(CustomButton):
    """Кнопка-переключатель"""
    
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.state = False
        self.configure(command=self.toggle)
        
    def toggle(self):
        """Переключить состояние"""
        self.state = not self.state
        self.configure(style="Active.TButton" if self.state else "Custom.TButton")

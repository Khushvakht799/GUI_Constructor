import os
import tkinter as tk
from tkinter import ttk

def run_gui_constructor():
    print('[*] Welcome to GUI_Constructor!')

    # Buttons
    num_buttons = int(input('Enter number of buttons: '))
    buttons_code = 'import tkinter as tk\n\n'
    buttons_code += 'def create_gui():\n'
    buttons_code += '    root = tk.Tk()\n'
    buttons_code += '    root.title(\"GUI Project\")\n'
    buttons_code += '    root.geometry(\"400x300\")\n'
    buttons_code += '    default_font = (\"Segoe UI\", 10)\n'
    buttons_code += '    button_style = {\"bg\":\"#f0f0f0\", \"fg\":\"#000000\", \"relief\":\"raised\", \"bd\":2, \"font\":default_font}\n'
    buttons_code += '    entry_style = {\"bg\":\"#ffffff\", \"fg\":\"#000000\", \"font\":default_font, \"bd\":2}\n'

    for i in range(num_buttons):
        name = input(f'Button {i+1} name: ')
        action = input(f'Button {i+1} action function name: ')
        buttons_code += f'    def {action}():\n'
        buttons_code += f'        print(\"Button {name} pressed\")\n'
        buttons_code += f'    btn{i+1} = tk.Button(root, text=\"{name}\", command={action}, **button_style)\n'
        buttons_code += f'    btn{i+1}.pack(pady=5)\n'

    # Fields
    num_fields = int(input('Enter number of fields: '))
    for i in range(num_fields):
        field_name = input(f'Field {i+1} name: ')
        buttons_code += f'    {field_name} = tk.Entry(root, **entry_style)\n'
        buttons_code += f'    {field_name}.pack(pady=5)\n'

    buttons_code += '    root.mainloop()\n'

    # Write to buttons.py
    with open(os.path.join(os.path.dirname(__file__), 'Gui', 'buttons.py'), 'w') as f:
        f.write(buttons_code)

    print('[+] Windows-style buttons and fields generated successfully!')

if __name__ == '__main__':
    run_gui_constructor()

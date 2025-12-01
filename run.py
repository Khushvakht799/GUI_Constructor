import sys
import os

def main():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    os.chdir(BASE_DIR)
    
    try:
        import tkinter as tk
        print("Tkinter OK")
    except ImportError:
        print("Tkinter error")
        return 1
    
    gui_main_path = os.path.join(BASE_DIR, "src", "gui", "gui_main.py")
    
    try:
        with open(gui_main_path, "r", encoding="utf-8") as f:
            code = f.read()
        
        globals_dict = {
            "__name__": "__main__",
            "__file__": gui_main_path,
            "os": os,
            "sys": sys
        }
        
        sys.path.insert(0, os.path.join(BASE_DIR, "src"))
        
        exec(code, globals_dict)
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
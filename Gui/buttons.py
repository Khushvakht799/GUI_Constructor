import tkinter as tk

def create_gui():
    root = tk.Tk()
    root.title("GUI Project")
    root.geometry("400x300")
    default_font = ("Segoe UI", 10)
    button_style = {"bg":"#f0f0f0", "fg":"#000000", "relief":"raised", "bd":2, "font":default_font}
    entry_style = {"bg":"#ffffff", "fg":"#000000", "font":default_font, "bd":2}
    def ():
        print("Button 1 pressed")
    btn1 = tk.Button(root, text="1", command=, **button_style)
    btn1.pack(pady=5)
    def ():
        print("Button 2 pressed")
    btn2 = tk.Button(root, text="2", command=, **button_style)
    btn2.pack(pady=5)
     = tk.Entry(root, **entry_style)
    .pack(pady=5)
    root.mainloop()

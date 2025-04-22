import tkinter as tk
import threading

def show_message(text):
    def _run():
        window = tk.Toplevel()
        window.title("Alert")
        text_widget = tk.Text(window, wrap="word", width=70, height=10)
        text_widget.insert(tk.END, text)
        text_widget.pack(padx=10, pady=10)
        text_widget.config(state=tk.DISABLED)
        window.update_idletasks()
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        window.geometry(f"+{x}+{y}")
    try:
        root = tk._default_root
        if root:
            root.after(0, _run)
        else:
            threading.Thread(target=_run).start()
    except:
        pass

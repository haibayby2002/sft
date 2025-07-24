# interface/popup_utils.py

import tkinter as tk
import threading

def show_processing_popup(root, message="Processing..."):
    popup = tk.Toplevel(root)
    popup.title("Please Wait")
    popup.geometry("250x100")
    popup.resizable(False, False)
    popup.attributes("-topmost", True)
    popup.grab_set()

    # Center the popup in the root window
    x = root.winfo_x() + (root.winfo_width() // 2) - 125
    y = root.winfo_y() + (root.winfo_height() // 2) - 50
    popup.geometry(f"+{x}+{y}")

    label = tk.Label(popup, text=message)
    label.pack(pady=20)

    return popup

def run_with_processing_popup(root, task_fn, message="Processing...", on_done=None):
    popup = show_processing_popup(root, message)

    def wrapper():
        try:
            result = task_fn()
        except Exception as e:
            result = e
        finally:
            popup.destroy()
            if on_done:
                root.after(0, lambda: on_done(result))

    threading.Thread(target=wrapper).start()

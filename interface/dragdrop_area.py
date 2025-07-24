# interface/dragdrop_area.py

import tkinter as tk
from tkinterdnd2 import DND_FILES
from tkinter import filedialog, messagebox
from interface.shared_import_logic import shared_import_logic


def create_dragdrop_area(root, parent, current_theme, refresh_slides_callback):
    drop_frame = tk.LabelFrame(parent, text="Drag & Drop Section")
    drop_frame.config(bg=current_theme["value"]["content_bg"], fg=current_theme["value"]["fg"])

    drop_frame.drop_target_register(DND_FILES)

    # === Drag & Drop Handler ===
    def handle_drop(event):
        file_paths = root.tk.splitlist(event.data)
        perform_import(file_paths)

    drop_frame.dnd_bind("<<Drop>>", handle_drop)

    # === Click to Open File Dialog ===
    def browse_files():
        file_paths = filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf")])
        if file_paths:
            perform_import(file_paths)

    # === Button to Browse Files ===
    browse_btn = tk.Button(drop_frame, text="Browse PDF Files", command=browse_files)
    browse_btn.pack(pady=10)

    drop_frame.pack(fill="x", padx=10, pady=(0, 10))

    # === Import Handler ===
    def perform_import(file_paths):
        selected_deck_id = root.selected_deck_id.get("value", None)
        if not selected_deck_id:
            messagebox.showwarning("No Deck Selected", "Please select a deck before importing slides.")
            return

        def on_success(count):
            messagebox.showinfo("Import Success", f"Successfully imported {count} PDF(s).")
            refresh_slides_callback()

        def on_fail(file, error):
            messagebox.showerror("Import Failed", f"Failed to import {file}:\n{error}")

        shared_import_logic(
            deck_id=selected_deck_id,
            file_paths=file_paths,
            on_success=on_success,
            on_fail=on_fail
        )

    return drop_frame

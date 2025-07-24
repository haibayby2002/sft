# interface/slide_panel.py

import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
from interface.utils import open_pdf
from interface.note_editor import open_note_editor
from interface.tooltips import Tooltip
from data.models.slide import Slide


def refresh_slides(deck_id, slide_list_inner, current_theme, root, pencil_icon):
    for widget in slide_list_inner.winfo_children():
        widget.destroy()

    slides = Slide.get_by_deck(deck_id)
    if not slides:
        tk.Label(slide_list_inner, text="No slides in this deck.").pack(anchor="w", padx=10, pady=5)
        return

    for slide in slides:
        slide_container = tk.Frame(slide_list_inner)
        slide_container.pack(fill="x", padx=10, pady=3)

        label = tk.Label(
            slide_container,
            text=f"📄 {slide.title}",
            anchor="w",
            width=70,
            padx=10,
            pady=4,
            relief="ridge",
            cursor="hand2"
        )
        label.pack(side="left", fill="x", expand=True)
        label.bind("<Button-1>", lambda e, path=slide.file_path: open_pdf(path))

        # === Pencil (Note) Button ===
        pencil_btn = tk.Button(
            slide_container,
            image=pencil_icon,
            command=lambda s_id=slide.slide_id, s_title=slide.title: open_note_editor(s_id, s_title),
            bg=current_theme["content_bg"],
            relief="flat",
            bd=0,
            activebackground=current_theme["bg"],
            cursor="hand2"
        )
        pencil_btn.image = pencil_icon
        pencil_btn.pack(side="left", padx=5)

        # === Delete Button ===
        delete_btn = tk.Button(
            slide_container,
            text="❌",
            fg="red",
            command=lambda s_id=slide.slide_id, s_title=slide.title: confirm_delete_slide(s_id, s_title, deck_id, slide_list_inner, current_theme, root, pencil_icon),
            bg=current_theme["content_bg"],
            relief="flat",
            bd=0,
            activebackground=current_theme["bg"],
            cursor="hand2"
        )
        delete_btn.pack(side="right", padx=5)

        # === Tooltips ===
        Tooltip(pencil_btn, f"Take notes for {slide.title}")
        Tooltip(delete_btn, f"Delete {slide.title}")

        # === Hover Effects ===
        for btn in [pencil_btn, delete_btn]:
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#ffffcc" if current_theme["bg"] == "#f0f0f0" else "#555533"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=current_theme["content_bg"]))


def confirm_delete_slide(slide_id, slide_title, deck_id, slide_list_inner, current_theme, root, pencil_icon):
    confirm = messagebox.askyesno("Delete Slide", f"Are you sure you want to delete '{slide_title}'?")
    if confirm:
        try:
            Slide.delete(slide_id)
            refresh_slides(deck_id, slide_list_inner, current_theme, root, pencil_icon)
            messagebox.showinfo("Deleted", f"Slide '{slide_title}' has been deleted.")
        except Exception as e:
            messagebox.showerror("Error", str(e))


def create_slide_panel(parent, current_theme, pencil_icon):
    slides_frame = tk.LabelFrame(parent, text="Slide Deck Hub", height=100)
    slides_frame.pack(fill="x", padx=10, pady=(10, 5))

    canvas = tk.Canvas(slides_frame, height=200, borderwidth=0, highlightthickness=0)
    scrollbar = tk.Scrollbar(slides_frame, orient="vertical", command=canvas.yview)
    slide_list_inner = tk.Frame(canvas)

    slide_list_inner.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=slide_list_inner, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Scroll behavior (Linux/Windows/macOS)
    import platform
    if platform.system() == 'Linux':
        canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))
    else:
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

    return slides_frame, slide_list_inner

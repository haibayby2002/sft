import platform
import subprocess
import os
from tkinter import messagebox
from data.models.slide import Slide
import tkinter as tk
from interface.tooltips import Tooltip
import shutil

from tkinter import Toplevel, Canvas, Text, Scrollbar, messagebox, Frame, Label, StringVar
from tkinter import ttk
# from data.database import (
#     # get_pages_by_slide,
#     get_page_note,
#     # get_page_content,
#     insert_page_note,
#     update_page_note
# )
from data.models.page_note import PageNote
from data.models.content import Content
from data.models.page import Page

def open_note_editor(slide_id, slide_title):
    

    PAGES_PER_PAGE = 5
    pages = list(Page.get_by_slide(slide_id))
    total_pages = len(pages)
    current_index = {"start": 0}

    note_window = Toplevel()
    note_window.title(f"📝 Notes for: {slide_title}")
    note_window.geometry("1000x700")
    note_window.transient(None)  # Make it a top-level window
    # note_window.grab_set()

    # === Title + Save Row ===
    top_frame = Frame(note_window)
    top_frame.pack(fill="x", pady=(10, 0), padx=10)

    Label(top_frame, text=f"Slide: {slide_title}", font=("Helvetica", 14, "bold")).pack(side="left")

    def open_pdf_to_page(slide_id, page_number):
        slide = Slide.get_by_id(slide_id)
        if not slide:
            messagebox.showerror("Error", f"Slide {slide_id} not found.")
            return

        pdf_path = slide["file_path"]
        if not os.path.exists(pdf_path):
            messagebox.showerror("Error", f"File not found: {pdf_path}")
            return

        try:
            if platform.system() == "Windows":
                acrobat_path = shutil.which("AcroRd32.exe")
                if acrobat_path:
                    # Try opening with Adobe Acrobat Reader and jump to page
                    subprocess.Popen([acrobat_path, '/A', f'page={page_number}', pdf_path])
                else:
                    # Fallback to default PDF viewer
                    os.startfile(pdf_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.Popen(['open', pdf_path])
                # Could use AppleScript for jumping to page (optional)
            else:  # Linux
                subprocess.Popen(['evince', f'--page-label={page_number}', pdf_path])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file:\n{e}")

    def save_notes():
        for page_number, widget in note_entries.items():
            note = widget.get("1.0", "end").strip()
            current = PageNote.get(slide_id, page_number)
            if current is None:
                PageNote.create(slide_id, page_number, note)
            else:
                PageNote.update(slide_id, page_number, note)
        messagebox.showinfo("Saved", "Notes updated successfully!", parent=note_window)
        # note_window.destroy()

    ttk.Button(top_frame, text="💾 Save Notes", command=save_notes).pack(side="right")

    # === Scrollable content area ===
    canvas = Canvas(note_window)
    scrollbar = ttk.Scrollbar(note_window, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas_frame = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="top", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    content_widgets = []
    note_entries = {}
    page_index_label_var = StringVar()

    def render_page_notes():
        for w in content_widgets:
            w.destroy()
        content_widgets.clear()
        note_entries.clear()

        start = current_index["start"]
        end = min(start + PAGES_PER_PAGE, total_pages)
        visible_pages = pages[start:end]

        for page in visible_pages:
            page_number = page["page_number"]
            note_text = PageNote.get(slide_id, page_number) or ""
            content_text = Content.get_by_slide_and_number(slide_id, page_number) or "[No content]"

            row_frame = Frame(scrollable_frame)
            row_frame.pack(fill="x", padx=10, pady=5)
            content_widgets.append(row_frame)

            content_frame = Frame(row_frame)
            content_frame.pack(side="left", fill="both", expand=True, padx=5)

            label_btn_frame = Frame(content_frame)
            label_btn_frame.pack(fill="x")

            Label(label_btn_frame, text=f"Page {page_number} Content:", anchor="w").pack(side="left", anchor="w")

            open_btn = tk.Button(
                label_btn_frame,
                text="📖",
                command=lambda sid=slide_id, pg=page_number: open_pdf_to_page(sid, pg),
                bg="#e6f0ff",
                relief="ridge",
                width=2
            )
            open_btn.pack(side="right")
            Tooltip(open_btn, f"Open slide at page {page_number}")


            content_box = Text(content_frame, height=5, bg="#f0f0f0", wrap="word")
            content_box.insert("1.0", content_text)
            content_box.config(state="disabled")
            content_box.pack(fill="x", pady=(0, 5))

            note_frame = Frame(row_frame)
            note_frame.pack(side="right", fill="both", expand=True, padx=5)

            Label(note_frame, text="Note:", anchor="w").pack(anchor="w")
            note_box = Text(note_frame, height=5, wrap="word")
            note_box.insert("1.0", note_text)
            note_box.pack(fill="x", pady=(0, 5))

            note_entries[page_number] = note_box

        page_index_label_var.set(f"Page {start + 1}-{end} of {total_pages}")

    def go_left():
        if current_index["start"] >= PAGES_PER_PAGE:
            current_index["start"] -= PAGES_PER_PAGE
            render_page_notes()

    def go_right():
        if current_index["start"] + PAGES_PER_PAGE < total_pages:
            current_index["start"] += PAGES_PER_PAGE
            render_page_notes()

    
    # === Pagination UI (BOTTOM of page window now) ===
    nav_frame = ttk.Frame(note_window)
    nav_frame.pack(fill="x", side="bottom", pady=(0, 10))

    ttk.Button(nav_frame, text="⬅️", command=go_left).pack(side="left", padx=10)
    ttk.Label(nav_frame, textvariable=page_index_label_var).pack(side="left", padx=10)
    ttk.Button(nav_frame, text="➡️", command=go_right).pack(side="left")

    render_page_notes()

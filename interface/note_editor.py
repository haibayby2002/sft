def open_note_editor(slide_id, slide_title):
    from tkinter import Toplevel, Canvas, Text, Scrollbar, messagebox, Frame, Label, StringVar
    from tkinter import ttk
    from data.database import (
        get_pages_by_slide,
        get_page_note,
        get_page_content,
        insert_page_note,
        update_page_note
    )

    PAGES_PER_PAGE = 5
    pages = list(get_pages_by_slide(slide_id))
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

    def save_notes():
        for page_number, widget in note_entries.items():
            note = widget.get("1.0", "end").strip()
            current = get_page_note(slide_id, page_number)
            if current is None:
                insert_page_note(slide_id, page_number, note)
            else:
                update_page_note(slide_id, page_number, note)
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
            note_text = get_page_note(slide_id, page_number) or ""
            content_text = get_page_content(slide_id, page_number) or "[No content]"

            row_frame = Frame(scrollable_frame)
            row_frame.pack(fill="x", padx=10, pady=5)
            content_widgets.append(row_frame)

            content_frame = Frame(row_frame)
            content_frame.pack(side="left", fill="both", expand=True, padx=5)

            Label(content_frame, text=f"Page {page_number} Content:", anchor="w").pack(anchor="w")
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

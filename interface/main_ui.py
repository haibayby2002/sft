import tkinter as tk
from tkinter import ttk, scrolledtext, simpledialog, messagebox

from application.query_controller import load_decks
from data.database import insert_deck
import os
from tkinter import filedialog
from data.database import insert_slide
from application.query_controller import load_slides

import os
import subprocess
import platform
from tkinterdnd2 import DND_FILES, TkinterDnD
from application.query_controller import delete_deck
from application.query_controller import delete_slide as delete_slide_query
# from service.docling_service import extract_and_store_pdf_content
from interface.shared_import_logic import shared_import_logic  # adjust path if needed
from PIL import Image, ImageTk
import threading
from interface.tooltips import Tooltip
from interface.note_editor import open_note_editor
from PIL import Image, ImageTk





def launch_ui():
    root = TkinterDnD.Tk()
    # Initialize the main window
    root.title("Slide Fight Tactics")
    root.geometry("1000x700")
    root.minsize(800, 600)

    # Load and resize the pencil icon once
    ICON_PATH = "assets/icons/ChatGPT Image Jul 19, 2025, 03_31_42 PM.png"
    try:
        pencil_image_raw = Image.open(ICON_PATH).resize((18, 18), Image.Resampling.LANCZOS)
        pencil_icon = ImageTk.PhotoImage(pencil_image_raw)
    except Exception as e:
        print(f"Failed to load pencil icon: {e}")
        pencil_icon = None

    # === Theme definitions ===
    LIGHT_THEME = {
        "bg": "#f0f0f0",
        "fg": "black",
        "content_bg": "#ffffff",
        "input_bg": "#ffffff"
    }
    DARK_THEME = {
        "bg": "#1e1e1e",
        "fg": "#e0e0e0",
        "content_bg": "#2e2e2e",
        "input_bg": "#3a3a3a"
    }
    current_theme = {"value": LIGHT_THEME}
    selected_deck_btn = {"widget": None}  # store currently highlighted button


    # === Current deck selection ===
    selected_deck_id = {"value": None}  # use dict to keep reference

    def show_processing_popup(text="Processing..."):
        popup = tk.Toplevel(root)
        popup.title("Please wait")
        popup.geometry("250x100")
        popup.resizable(False, False)
        popup.grab_set()
        popup.transient(root)
        tk.Label(popup, text=text).pack(expand=True, padx=20, pady=20)
        return popup



    def apply_theme(theme):
        sidebar.config(bg=theme["bg"])
        for widget in sidebar.winfo_children():
            try:
                widget.config(bg=theme["bg"], fg=theme["fg"])
            except:
                pass

        slides_frame.config(bg=theme["content_bg"])
        dragdrop_frame.config(bg=theme["content_bg"])
        chat_frame.config(bg=theme["content_bg"])
        chat_log.config(bg=theme["input_bg"], fg=theme["fg"], insertbackground=theme["fg"])
        input_frame.config(bg=theme["content_bg"])
        user_input.config(bg=theme["input_bg"], fg=theme["fg"], insertbackground=theme["fg"])
        send_button.config(bg=theme["bg"], fg=theme["fg"])

    def toggle_theme():
        current_theme["value"] = DARK_THEME if current_theme["value"] == LIGHT_THEME else LIGHT_THEME
        apply_theme(current_theme["value"])
        refresh_decks(select_after_id=selected_deck_id["value"])

    # === Layout ===
    sidebar = tk.Frame(root, width=200)
    sidebar.pack(side="left", fill="y")

    content_area = tk.Frame(root)
    content_area.pack(side="right", fill="both", expand=True)

    # === Sidebar: Deck Section ===
    tk.Label(sidebar, text="Decks", font=("Helvetica", 14, "bold")).pack(pady=(10, 2))

    def add_deck_popup():
        popup = tk.Toplevel(root)
        popup.title("Create New Deck")
        popup.geometry("300x220")
        popup.grab_set()

        tk.Label(popup, text="Deck Name:").pack(pady=(10, 2))
        name_entry = tk.Entry(popup, width=30)
        name_entry.pack()

        tk.Label(popup, text="Description:").pack(pady=(10, 2))
        desc_text = tk.Text(popup, width=30, height=4)
        desc_text.pack()

        def submit_deck():
            name = name_entry.get().strip()
            description = desc_text.get("1.0", tk.END).strip()
            if not name:
                messagebox.showwarning("Validation", "Deck name is required.")
                return
            try:
                new_deck_id = insert_deck(name, description or None)
                popup.destroy()
                refresh_decks(select_after_id=new_deck_id)
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(popup, text="Create", command=submit_deck).pack(pady=10)




    # Add deck button just under label
    tk.Button(sidebar, text="+ Add Deck", command=add_deck_popup).pack(pady=(0, 10))

    # Deck button container
    deck_buttons_frame = tk.Frame(sidebar, bg=current_theme["value"]["bg"])
    deck_buttons_frame.pack(fill="both", expand=True)

    def select_deck(deck):
        selected_deck_id["value"] = deck["deck_id"]

        # Reset previous button style
        if selected_deck_btn["widget"] and selected_deck_btn["widget"].winfo_exists():
            try:
                selected_deck_btn["widget"].config(
                    bg=current_theme["value"]["bg"],
                    fg=current_theme["value"]["fg"]
                )
            except tk.TclError:
                pass  # Widget might already be destroyed

        # # Reset previous button style
        # if selected_deck_btn["widget"]:
        #     selected_deck_btn["widget"].config(
        #         bg=current_theme["value"]["bg"],
        #         fg=current_theme["value"]["fg"]
        #     )

        # Highlight selected deck
        btn = deck["button_widget"]
        btn.config(
            bg="#4CAF50",  # green
            fg="white"
        )
        selected_deck_btn["widget"] = btn

        # Enable import
        import_btn.config(state="normal")
        delete_deck_btn.config(state="normal")
        refresh_slides(deck["deck_id"])






    def refresh_decks(select_after_id=None):
        for widget in deck_buttons_frame.winfo_children():
            widget.destroy()

        decks = load_decks()
        for deck_row in decks:
            deck = dict(deck_row)
            btn = tk.Button(
                deck_buttons_frame,
                text=deck["name"],
                anchor="w",
                width=20,
                bg=current_theme["value"]["bg"],
                fg=current_theme["value"]["fg"],
                activebackground=current_theme["value"]["bg"],
                activeforeground=current_theme["value"]["fg"]
            )
            deck["button_widget"] = btn
            btn.config(command=lambda d=deck: select_deck(d))
            btn.pack(pady=2, padx=10, anchor="w")

            # If this is the deck to auto-select
            if select_after_id is not None and deck["deck_id"] == select_after_id:
                select_deck(deck)

    # === Confirm Delete Slide Function ===
    def confirm_delete_slide(slide_id, slide_title):
        deck_id = selected_deck_id["value"]
        if deck_id is None:
            messagebox.showerror("Error", "No deck selected.")
            return

        decks = load_decks()
        deck_name = next((d["name"] for d in decks if d["deck_id"] == deck_id), "Unknown Deck")

        confirm = messagebox.askyesno(
            "Delete Slide",
            f"Are you sure you want to delete '{slide_title}' from '{deck_name}'?"
        )
        if confirm:
            try:
                delete_slide_query(slide_id)
                refresh_slides(deck_id)
                messagebox.showinfo("Deleted", f"Slide '{slide_title}' has been deleted.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    
    def refresh_slides(deck_id):
        tooltip_refs = []
        for widget in slide_list_frame.winfo_children():
            widget.destroy()

        slides = load_slides(deck_id)
        if not slides:
            tk.Label(slide_list_frame, text="No slides in this deck.").pack(anchor="w", padx=10, pady=5)
            return

        for slide_row in slides:
            slide = dict(slide_row)

            slide_container = tk.Frame(slide_list_frame)
            slide_container.pack(fill="x", padx=10, pady=3)

            label = tk.Label(
                slide_container,
                text=f"📄 {slide['title']}",
                anchor="w",
                width=70,
                padx=10,
                pady=4,
                relief="ridge",
                cursor="hand2"
            )
            label.pack(side="left", fill="x", expand=True)

            label.bind("<Button-1>", lambda e, path=slide['file_path']: open_pdf(path))

            # === Pencil Button ===
            def make_note_handler(slide_id=slide["slide_id"], title=slide["title"]):
                return lambda: open_note_editor(slide_id, title)

            pencil_btn = tk.Button(
                slide_container,
                image=pencil_icon,
                command=make_note_handler(),
                bg=current_theme["value"]["content_bg"],
                relief="flat",
                bd=0,
                activebackground=current_theme["value"]["bg"],
                cursor="hand2"
            )
            pencil_btn.image = pencil_icon
            pencil_btn.pack(side="left", padx=5)

            # === Delete Button ===
            def make_delete_handler(slide_id=slide["slide_id"], title=slide["title"]):
                return lambda: confirm_delete_slide(slide_id, title)

            delete_btn = tk.Button(
                slide_container,
                text="❌",
                fg="red",
                command=make_delete_handler(),
                bg=current_theme["value"]["content_bg"],
                relief="flat",
                bd=0,
                activebackground=current_theme["value"]["bg"],
                cursor="hand2"
            )
            delete_btn.pack(side="right", padx=5)

            # === Tooltips ===
            def bind_tooltips(p_btn=pencil_btn, d_btn=delete_btn):
                Tooltip(p_btn, f"Take notes for {slide['title']}")
                Tooltip(d_btn, f"Delete {slide['title']}")

            root.after_idle(bind_tooltips)


            # === Hover effects ===
            def hover_on(btn):
                btn.config(bg="#ffffcc" if current_theme["value"] == LIGHT_THEME else "#555533")

            def hover_off(btn):
                btn.config(bg=current_theme["value"]["content_bg"])

            for btn in [pencil_btn, delete_btn]:
                btn.bind("<Enter>", lambda e, b=btn: hover_on(b))
                btn.bind("<Leave>", lambda e, b=btn: hover_off(b))



    tk.Button(sidebar, text="Toggle Dark Mode", command=toggle_theme).pack(side="bottom", pady=10)

    refresh_decks(select_after_id=selected_deck_id["value"])  # Load deck list on startup

    # === Slides Frame ===
    slides_frame = tk.LabelFrame(content_area, text="Slide Deck Hub", height=100)
    slides_frame.pack(fill="x", padx=10, pady=10)

    # Create a horizontal button frame
    deck_action_frame = tk.Frame(slides_frame)
    deck_action_frame.pack(fill="x", padx=10, pady=5)

    # === Import PDF Function ===
    def import_pdf():
        deck_id = selected_deck_id["value"]
        if deck_id is None:
            messagebox.showwarning("No Deck Selected", "Please select a deck before importing.")
            return

        file_paths = filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf")])
        if not file_paths:
            return

        popup = show_processing_popup("Importing PDFs...")

        def run_import():
            shared_import_logic(
                deck_id,
                file_paths,
                on_success=lambda count: root.after(0, lambda: [
                    popup.destroy(),
                    refresh_slides(deck_id),
                    messagebox.showinfo("Imported", f"{count} file(s) imported.")
                ]),
                on_fail=lambda path, err: root.after(0, lambda: messagebox.showerror("Error", f"Failed to import {path}:\n{err}"))
            )

        threading.Thread(target=run_import).start()



    # === Delete Deck Function ===
    import_btn = tk.Button(deck_action_frame, text="Import PDF to Deck", state="disabled", command=lambda: import_pdf())
    import_btn.pack(side="left")

    def confirm_delete_deck():
        deck_id = selected_deck_id["value"]
        if deck_id is None:
            messagebox.showwarning("No Deck Selected", "Please select a deck to delete.")
            return

        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this deck and all its slides?")
        if confirm:
            try:
                delete_deck(deck_id)
                selected_deck_id["value"] = None
                selected_deck_btn["widget"] = None
                refresh_decks()
                refresh_slides(None)
                import_btn.config(state="disabled")
                delete_deck_btn.config(state="disabled")
                messagebox.showinfo("Deleted", "Deck deleted successfully.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    delete_deck_btn = tk.Button(deck_action_frame, text="🗑️ Delete Selected Deck", state="disabled", command=confirm_delete_deck)
    delete_deck_btn.pack(side="right")

    # === Slide List Frame ===
    slide_list_frame = tk.Frame(slides_frame)
    slide_list_frame.pack(fill="both", expand=True)



    # === Drag & Drop Frame ===
    dragdrop_frame = tk.LabelFrame(content_area, text="Drag & Drop Section")
    dragdrop_frame.pack(fill="x", padx=10, pady=5)

    drop_area = tk.Label(
        dragdrop_frame,
        text="📥 Drop your PDF files here",
        fg="gray",
        bg="#f4f4f4",
        height=3,
        relief="groove"
    )
    drop_area.pack(fill="x", padx=10, pady=10)

    # Register for drop
    drop_area.drop_target_register(DND_FILES)

    def handle_pdf_drop(event):
        deck_id = selected_deck_id["value"]
        if deck_id is None:
            messagebox.showwarning("No Deck Selected", "Please select a deck first.")
            return

        files = root.tk.splitlist(event.data)
        popup = show_processing_popup("Importing dropped files...")

        def run_import():
            shared_import_logic(
                deck_id,
                files,
                on_success=lambda count: root.after(0, lambda: [
                    popup.destroy(),
                    refresh_slides(deck_id),
                    messagebox.showinfo("Imported", f"{count} file(s) imported.")
                ]),
                on_fail=lambda path, err: root.after(0, lambda: messagebox.showerror("Error", f"Failed to import {path}:\n{err}"))
            )

        threading.Thread(target=run_import).start()


    drop_area.dnd_bind("<<Drop>>", handle_pdf_drop)



    # === Chat History Frame ===
    chat_frame = tk.LabelFrame(content_area, text="Chat History")
    chat_frame.pack(fill="both", expand=True, padx=10, pady=5)

    chat_log = scrolledtext.ScrolledText(chat_frame, wrap=tk.WORD, height=10)
    chat_log.pack(fill="both", expand=True, padx=5, pady=5)
    chat_log.insert(tk.END, "Gemma: Welcome! Ask me about your slides...\n")

    # === Chat Input Frame ===
    input_frame = tk.Frame(content_area)
    input_frame.pack(fill="x", padx=10, pady=10)

    user_input = tk.Entry(input_frame)
    user_input.pack(side="left", fill="x", expand=True, padx=(0, 5))

    def send_message():
        message = user_input.get().strip()
        if message:
            chat_log.insert(tk.END, f"You: {message}\n")
            chat_log.insert(tk.END, f"Gemma: [Response placeholder]\n")
            user_input.delete(0, tk.END)
            chat_log.see(tk.END)

    send_button = tk.Button(input_frame, text="Send", command=send_message)
    send_button.pack(side="right")

    apply_theme(current_theme["value"])
    root.mainloop()

def open_pdf(file_path):
    try:
        if platform.system() == "Windows":
            os.startfile(file_path)
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(["open", file_path])
        else:  # Linux
            subprocess.run(["xdg-open", file_path])
    except Exception as e:
        messagebox.showerror("Error", f"Could not open file:\n{e}")
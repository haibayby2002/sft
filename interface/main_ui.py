import tkinter as tk
from tkinter import ttk, scrolledtext, simpledialog, messagebox

from application.query_controller import load_decks
import os
from tkinter import filedialog
from application.query_controller import insert_slide
from application.query_controller import load_slides

import json
import os
import subprocess
import platform
from tkinterdnd2 import DND_FILES, TkinterDnD
from application.query_controller import delete_deck, insert_deck
from application.query_controller import delete_slide as delete_slide_query
# from service.docling_service import extract_and_store_pdf_content
from interface.shared_import_logic import shared_import_logic  # adjust path if needed

from data.models.page import Page
from data.models.content import Content
from data.vectorstore.embedder import Embedder
from data.vectorstore.vector_db import VectorDB

embedder = Embedder()
vectordb = VectorDB()




from PIL import Image, ImageTk
import threading
from interface.tooltips import Tooltip
from interface.note_editor import open_note_editor
from PIL import Image, ImageTk

from service.gemma_client import query_gemma_stream
from application.query_controller import load_context_from_deck


def index_slide_pages(slide_id, deck_id):
    pages = Page.get_by_slide(slide_id)
    for p in pages:
        page_num = p.page_number
        content_text = Content.get_text_by_page(slide_id, page_num)
        if content_text:
            vector = embedder.embed_text(content_text)
            metadata = {
                "deck_id": deck_id,
                "slide_id": slide_id,
                "page_number": page_num,
                "text_preview": content_text[:200]
            }
            vectordb.add_vector(vector, content_text, metadata)


def launch_ui():
    root = TkinterDnD.Tk()
    # Initialize the main window
    root.title("Slide Fight Tactics")
    root.geometry("800x670")
    root.minsize(800, 650)

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
    current_deck_context = {"value": None}

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

        slides_frame.config(bg=theme["content_bg"], fg=theme["fg"])
        dragdrop_frame.config(bg=theme["content_bg"], fg=theme["fg"])
        chat_frame.config(bg=theme["content_bg"], fg=theme["fg"])
        chat_log.config(bg=theme["input_bg"], fg=theme["fg"], insertbackground=theme["fg"])
        input_frame.config(bg=theme["content_bg"])

        # Update user input colors based on placeholder state
        if getattr(user_input, "_placeholder_active", False):
            user_input.config(bg=theme["input_bg"], fg="gray", insertbackground=theme["fg"])
        else:
            user_input.config(bg=theme["input_bg"], fg=theme["fg"], insertbackground=theme["fg"])

        send_button.config(bg=theme["bg"], fg=theme["fg"])


    def toggle_theme():
        current_theme["value"] = DARK_THEME if current_theme["value"] == LIGHT_THEME else LIGHT_THEME
        apply_theme(current_theme["value"])
        refresh_decks(select_after_id=selected_deck_id["value"])

   # === Bind mouse wheel for scrolling ===
    def bind_mousewheel_to_widget(widget, canvas):
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def _on_mousewheel_linux(event):
            if event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")

        def _on_enter(event):
            if platform.system() == 'Linux':
                widget.bind_all("<Button-4>", _on_mousewheel_linux)
                widget.bind_all("<Button-5>", _on_mousewheel_linux)
            else:
                widget.bind_all("<MouseWheel>", _on_mousewheel)

        def _on_leave(event):
            if platform.system() == 'Linux':
                widget.unbind_all("<Button-4>")
                widget.unbind_all("<Button-5>")
            else:
                widget.unbind_all("<MouseWheel>")

        widget.bind("<Enter>", _on_enter)
        widget.bind("<Leave>", _on_leave)
        

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

        # Reset and highlight button
        if selected_deck_btn["widget"] and selected_deck_btn["widget"].winfo_exists():
            selected_deck_btn["widget"].config(
                bg=current_theme["value"]["bg"],
                fg=current_theme["value"]["fg"]
            )
        btn = deck["button_widget"]
        btn.config(bg="#4CAF50", fg="white")
        selected_deck_btn["widget"] = btn

        # Enable import/delete buttons
        import_btn.config(state="normal")
        delete_deck_btn.config(state="normal")

        # Load context
        current_deck_context["value"] = load_context_from_deck(deck["deck_id"])

        # Update placeholder
        placeholder_fg = "#aaaaaa" if current_theme["value"] == DARK_THEME else "gray"
        user_input.delete(0, tk.END)
        add_placeholder(user_input, "Ask Gemma about this deck...", placeholder_color=placeholder_fg)

        # Load slides
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
        for widget in slide_list_inner.winfo_children():
            widget.destroy()

        slides = load_slides(deck_id)
        if not slides:
            tk.Label(slide_list_inner, text="No slides in this deck.").pack(anchor="w", padx=10, pady=5)
            return

        for slide_row in slides:
            slide = dict(slide_row)

            slide_container = tk.Frame(slide_list_inner)
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

    

    # === Scrollable Slide List Frame ===
    slide_list_canvas = tk.Canvas(slides_frame, height=200, borderwidth=0, highlightthickness=0)
    scrollbar = tk.Scrollbar(slides_frame, orient="vertical", command=slide_list_canvas.yview)
    slide_list_inner = tk.Frame(slide_list_canvas)

    slide_list_inner.bind(
        "<Configure>",
        lambda e: slide_list_canvas.configure(
            scrollregion=slide_list_canvas.bbox("all")
        )
    )

    slide_list_canvas.create_window((0, 0), window=slide_list_inner, anchor="nw")
    slide_list_canvas.configure(yscrollcommand=scrollbar.set)

    def _on_mousewheel(event):
        # Windows and macOS
        slide_list_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_mousewheel_linux(event):
        # Linux scroll
        if event.num == 4:
            slide_list_canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            slide_list_canvas.yview_scroll(1, "units")

    # Bind the mousewheel to canvas
    # if platform.system() == 'Linux':
    #     slide_list_canvas.bind_all("<Button-4>", _on_mousewheel_linux)
    #     slide_list_canvas.bind_all("<Button-5>", _on_mousewheel_linux)
    # else:
    #     slide_list_canvas.bind_all("<MouseWheel>", _on_mousewheel)

    #     slide_list_canvas.pack(side="left", fill="both", expand=True)
    #     scrollbar.pack(side="right", fill="y")

    slide_list_canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    bind_mousewheel_to_widget(slide_list_inner, slide_list_canvas)




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

    bind_mousewheel_to_widget(chat_log, chat_log)
    chat_log.pack(fill="both", expand=True, padx=5, pady=5)



    # === Chat Input Frame ===
    def add_placeholder(entry, placeholder, placeholder_color='gray', text_color='black'):
        entry._placeholder_active = True

        def set_placeholder():
            user_input.insert(0, placeholder)
            user_input.config(fg="gray")
            user_input._placeholder_active = True

        def clear_placeholder():
            user_input.delete(0, tk.END)
            user_input.config(fg=current_theme["value"]["fg"])  # Ensure correct color
            user_input._placeholder_active = False

        def on_focus_in(event):
            if user_input._placeholder_active:
                user_input.delete(0, tk.END)
                user_input._placeholder_active = False
            # Ensure foreground color is applied according to current theme
            user_input.config(fg=current_theme["value"]["fg"])



        def on_focus_out(event):
            if not entry.get():
                entry.insert(0, placeholder)
                entry.config(fg=placeholder_color)
                entry._placeholder_active = True

        entry.insert(0, placeholder)
        entry.config(fg=placeholder_color)
        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)
        set_placeholder()



    input_frame = tk.Frame(content_area)
    input_frame.pack(fill="x", padx=10, pady=10)

    user_input = tk.Entry(input_frame)
    user_input.pack(side="left", fill="x", expand=True, padx=(0, 5))
    user_input.bind("<Return>", lambda event: send_message())
    placeholder_fg = "#aaaaaa" if current_theme["value"] == DARK_THEME else "gray"
    add_placeholder(user_input, "Ask Gemma...", placeholder_color=placeholder_fg)

    


    def send_message():
        vectordb._load() 
        message = user_input.get().strip()
        if not message:
            return

        chat_log.insert(tk.END, f"You: {message}\n")
        chat_log.insert(tk.END, "Gemma: ")
        user_input.delete(0, tk.END)
        chat_log.see(tk.END)

        def stream_response():
            try:
                # 🔥 1. Embed question
                q_vec = embedder.embed_text(message)

                # 🔥 2. Retrieve top 3 relevant pages
                results = vectordb.search_vectors(q_vec, top_k=3)
                print("🔍 RAG Search Results:", results)  # Add this

                # 🔥 3. Build context string
                context_blocks = []
                for r in results:
                    md = r["metadata"]
                    context_blocks.append(
                        f"[{md.get('title')} Page {md.get('page_number')}]\n{r['content']}"
                    )
                context_text = "\n\n".join(context_blocks) if context_blocks else "No relevant context found."
                print("📄 Context for Gemma:", context_text)  # Add this

                # 🔥 4. Inject into Gemma
                # prompt = f"Answer the question based on the slides below:\n\n{context_text}\n\nQuestion: {message}\nAnswer:"
                prompt = f"""You are an assistant helping the user understand academic or technical slides. The following is extracted context from various slides. Use the information below to answer the user's question clearly. 
If you use any part of the context in your answer, cite the full title name of the slide and page number to help the user find the source. Below is the context:
{context_text}"""

                for chunk in query_gemma_stream(prompt=prompt):
                    chat_log.insert(tk.END, chunk)
                    chat_log.see(tk.END)

            except Exception as e:
                chat_log.insert(tk.END, f"\n[Error] {str(e)}\n")

        threading.Thread(target=stream_response).start()

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
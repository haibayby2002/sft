import tkinter as tk
from tkinter import ttk, scrolledtext, simpledialog, messagebox

from application.query_controller import load_decks
from data.database import insert_deck
import os
from tkinter import filedialog
from data.database import insert_slide
from application.query_controller import load_slides



def launch_ui():
    root = tk.Tk()
    root.title("Slide Fight Tactics")
    root.geometry("1000x700")
    root.minsize(800, 600)

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
    deck_buttons_frame = tk.Frame(sidebar)
    deck_buttons_frame.pack(fill="both", expand=True)

    def select_deck(deck):
        selected_deck_id["value"] = deck["deck_id"]

        # Reset previous button style
        if selected_deck_btn["widget"]:
            selected_deck_btn["widget"].config(
                bg=current_theme["value"]["bg"],
                fg=current_theme["value"]["fg"]
            )

        # Highlight selected deck
        btn = deck["button_widget"]
        btn.config(
            bg="#4CAF50",  # green
            fg="white"
        )
        selected_deck_btn["widget"] = btn

        # Enable import
        import_btn.config(state="normal")
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
                width=20
            )
            deck["button_widget"] = btn
            btn.config(command=lambda d=deck: select_deck(d))
            btn.pack(pady=2, padx=10, anchor="w")

            # If this is the deck to auto-select
            if select_after_id is not None and deck["deck_id"] == select_after_id:
                select_deck(deck)


    def refresh_slides(deck_id):
        for widget in slide_list_frame.winfo_children():
            widget.destroy()

        slides = load_slides(deck_id)
        if not slides:
            tk.Label(slide_list_frame, text="No slides in this deck.").pack(anchor="w", padx=10, pady=5)
            return

        for slide_row in slides:
            slide = dict(slide_row)
            label = tk.Label(
                slide_list_frame,
                text=f"📄 {slide['title']}",
                anchor="w",
                width=80,
                padx=10,
                pady=4,
                relief="ridge"
            )
            label.pack(fill="x", padx=10, pady=3)



    tk.Button(sidebar, text="Toggle Dark Mode", command=toggle_theme).pack(side="bottom", pady=10)

    refresh_decks(select_after_id=selected_deck_id["value"])  # Load deck list on startup

    # === Slides Frame ===
    slides_frame = tk.LabelFrame(content_area, text="Slide Deck Hub", height=100)
    slides_frame.pack(fill="x", padx=10, pady=10)

    # === Import PDF Function ===
    def import_pdf():
        deck_id = selected_deck_id["value"]
        if deck_id is None:
            messagebox.showwarning("No Deck Selected", "Please select a deck before importing.")
            return

        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if not file_path:
            return

        title = os.path.basename(file_path)

        try:
            insert_slide(deck_id, file_path, title)
            messagebox.showinfo("Success", f"Insert slide {title} to {deck_id} successfully.")
            refresh_slides(deck_id)  # <-- Add this line to reload UI
        except Exception as e:
            messagebox.showerror("Error", str(e))


    import_btn = tk.Button(slides_frame, text="Import PDF to Deck", state="disabled", command=lambda: import_pdf())
    import_btn.pack(anchor="w", padx=10, pady=5)

    slide_list_frame = tk.Frame(slides_frame)
    slide_list_frame.pack(fill="both", expand=True)



    # === Drag & Drop Frame ===
    dragdrop_frame = tk.LabelFrame(content_area, text="Drag & Drop Section")
    dragdrop_frame.pack(fill="x", padx=10, pady=5)
    tk.Label(dragdrop_frame, text="(Drag your PDF files here)", fg="gray").pack(pady=10)

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

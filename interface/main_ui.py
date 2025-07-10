import tkinter as tk
from tkinter import ttk, scrolledtext, simpledialog, messagebox

from application.query_controller import load_decks
from data.database import insert_deck


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
        name = simpledialog.askstring("New Deck", "Enter deck name:")
        if not name:
            return
        description = simpledialog.askstring("Description", "Optional: enter description:")
        try:
            insert_deck(name, description or None)
            refresh_decks()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # Add deck button just under label
    tk.Button(sidebar, text="+ Add Deck", command=add_deck_popup).pack(pady=(0, 10))

    # Deck button container
    deck_buttons_frame = tk.Frame(sidebar)
    deck_buttons_frame.pack(fill="both", expand=True)

    def refresh_decks():
        for widget in deck_buttons_frame.winfo_children():
            widget.destroy()

        decks = load_decks()
        for deck in decks:
            btn = tk.Button(
                deck_buttons_frame,
                text=deck["name"],
                anchor="w",
                width=20,
                command=lambda d=deck: print(f"Selected Deck ID: {d['deck_id']}")
            )
            btn.pack(pady=2, padx=10, anchor="w")

    tk.Button(sidebar, text="Toggle Dark Mode", command=toggle_theme).pack(side="bottom", pady=10)

    refresh_decks()  # Load deck list on startup

    # === Slides Frame ===
    slides_frame = tk.LabelFrame(content_area, text="Slide Deck Hub", height=100)
    slides_frame.pack(fill="x", padx=10, pady=10)

    for i in range(7):
        tk.Label(slides_frame, text=f"[Slide {i+1}]", borderwidth=1, relief="solid", padx=10, pady=5).pack(side="left", padx=5, pady=5)

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

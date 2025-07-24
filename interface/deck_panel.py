import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog
from data.models.deck import Deck
from interface.shared_import_logic import shared_import_logic


def setup_deck_sidebar(
    root,
    sidebar,
    theme,
    selected_deck_id,
    selected_deck_btn,
    current_deck_context,
    import_btn,                # still bind here
    delete_deck_btn,           # still bind here
    deck_buttons_frame,
    refresh_decks_callback
):
    def select_deck(deck_id, btn, deck_obj):
        selected_deck_id["value"] = deck_id
        current_deck_context["value"] = deck_obj.get_context()

        if selected_deck_btn["widget"]:
            selected_deck_btn["widget"].config(relief=tk.RAISED)

        btn.config(relief=tk.SUNKEN)
        selected_deck_btn["widget"] = btn

        refresh_decks_callback()

    def refresh_decks(select_after_id=None):
        for widget in deck_buttons_frame.winfo_children():
            widget.destroy()

        decks = Deck.get_all()
        for deck in decks:
            btn = tk.Button(deck_buttons_frame, text=deck.name, anchor="w", justify="left", wraplength=160)
            btn.pack(fill="x", pady=2)
            btn.config(command=lambda d=deck, b=btn: select_deck(d.deck_id, b, d))

            if select_after_id and deck.deck_id == select_after_id:
                select_deck(deck.deck_id, btn, deck)

    def add_deck_popup():
        name = simpledialog.askstring("Add Deck", "Enter deck name:")
        if name:
            Deck.create(name=name)
            refresh_decks()

    def confirm_delete_deck():
        deck_id = selected_deck_id["value"]
        if not deck_id:
            messagebox.showwarning("No deck selected", "Please select a deck to delete.")
            return

        if messagebox.askyesno("Delete Deck", "Are you sure you want to delete this deck?"):
            Deck.delete(deck_id)
            selected_deck_id["value"] = None
            selected_deck_btn["widget"] = None
            current_deck_context["value"] = []
            refresh_decks()
            refresh_decks_callback()

    def import_pdf():
        file_paths = filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf")])
        deck_id = selected_deck_id["value"]
        if not deck_id:
            messagebox.showwarning("No deck selected", "Select a deck to import PDFs into.")
            return

        def on_success(count):
            messagebox.showinfo("Import Success", f"{count} file(s) imported.")
            refresh_decks_callback()

        def on_fail(path, err):
            messagebox.showerror("Import Error", f"Failed to import {path}:\n{err}")

        shared_import_logic(deck_id, file_paths, on_success=on_success, on_fail=on_fail)

    # # === Label for sidebar title ===
    # tk.Label(sidebar, text="Decks", font=("Helvetica", 14, "bold")).pack(pady=(10, 2))
    # add_deck_btn = tk.Button(sidebar, text="+ Add Deck", command=add_deck_popup)
    # add_deck_btn.pack(pady=(0, 10))

    # # === Bind logic (do NOT pack) for external buttons ===
    # import_btn.config(command=import_pdf)
    # delete_deck_btn.config(command=confirm_delete_deck)

    # No search bar anymore — as requested
    # add_placeholder(...) removed

    return add_deck_popup, refresh_decks, select_deck

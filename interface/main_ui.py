# interface/main_ui.py

import tkinter as tk
from tkinterdnd2 import TkinterDnD
from PIL import Image, ImageTk

from interface.ui_theme import apply_theme, LIGHT_THEME, DARK_THEME
from interface.deck_panel import setup_deck_sidebar
from interface.slide_panel import create_slide_panel, refresh_slides
from interface.dragdrop_area import create_dragdrop_area
from interface.chat_box import create_chat_box

def launch_ui():
    root = TkinterDnD.Tk()
    root.title("Slide Fight Tactics")
    root.geometry("1000x700")
    root.minsize(800, 600)

    pencil_img = Image.open("assets/icons/ChatGPT Image Jul 19, 2025, 03_31_42 PM.png").resize((18, 18))
    pencil_icon = ImageTk.PhotoImage(pencil_img)

    current_theme = {"value": LIGHT_THEME}
    selected_deck_id = {"value": None}
    selected_deck_btn = {"widget": None}
    current_deck_context = {"value": []}

    sidebar = tk.Frame(root, width=200, bg="#F0F0F0")
    sidebar.pack(side="left", fill="y")

    main_content = tk.Frame(root)
    main_content.pack(side="right", fill="both", expand=True)

    tk.Label(sidebar, text="Decks", font=("Helvetica", 14, "bold"), bg="#F0F0F0").pack(pady=(10, 2))
    add_deck_btn = tk.Button(sidebar, text="+ Add Deck")
    add_deck_btn.pack(pady=(0, 10))

    deck_buttons_frame = tk.Frame(sidebar, bg="#F0F0F0")
    deck_buttons_frame.pack(fill="both", expand=True)

    import_btn = tk.Button(main_content, text="Import PDF to Deck")
    delete_deck_btn = tk.Button(main_content, text="🗑️ Delete Selected Deck")

    def refresh_decks_callback():
        refresh_slides(selected_deck_id["value"])

    add_deck_popup, refresh_decks, select_deck = setup_deck_sidebar(
        root,
        sidebar,
        current_theme["value"],
        selected_deck_id,
        selected_deck_btn,
        current_deck_context,
        import_btn,
        delete_deck_btn,
        deck_buttons_frame,
        refresh_decks_callback
    )

    add_deck_btn.config(command=add_deck_popup)

    slides_frame, slide_list_inner = create_slide_panel(main_content, current_theme, pencil_icon)

    controls_frame = tk.Frame(slides_frame, bg="white")
    controls_frame.pack(fill="x", padx=10, pady=(10, 0))
    import_btn.pack(in_=controls_frame, side="left")
    delete_deck_btn.pack(in_=controls_frame, side="right")

    slides_frame.pack(fill="x", padx=10, pady=(0, 0))

    dragdrop_frame = create_dragdrop_area(root, main_content, current_theme, lambda: refresh_slides(selected_deck_id["value"]))
    dragdrop_frame.pack(fill="x", padx=10, pady=(5, 0))

    chat_log, user_input_box = create_chat_box(root, main_content, current_theme, current_deck_context)
    chat_frame = chat_log.master.master
    chat_frame.pack(fill="both", expand=True, padx=10, pady=(5, 10))

    input_frame = user_input_box.master
    input_frame.pack(fill="x", padx=10, pady=(0, 10))

    def toggle_theme():
        current_theme["value"] = DARK_THEME if current_theme["value"] == LIGHT_THEME else LIGHT_THEME
        apply_theme(current_theme["value"], {
            "sidebar": sidebar,
            "slides_frame": slides_frame,
            "dragdrop_frame": dragdrop_frame,
            "chat_frame": chat_frame,
            "chat_log": chat_log,
            "input_frame": input_frame,
            "user_input": user_input_box,
            "send_button": None
        })
        refresh_decks(select_after_id=selected_deck_id["value"])

    dark_mode_btn = tk.Button(sidebar, text="Toggle Dark Mode", command=toggle_theme)
    dark_mode_btn.pack(pady=10)

    refresh_decks(select_after_id=selected_deck_id["value"])
    apply_theme(current_theme["value"], {
        "sidebar": sidebar,
        "slides_frame": slides_frame,
        "dragdrop_frame": dragdrop_frame,
        "chat_frame": chat_frame,
        "chat_log": chat_log,
        "input_frame": input_frame,
        "user_input": user_input_box,
        "send_button": None
    })

    root.mainloop()
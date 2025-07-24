# interface/ui_theme.py

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

def get_default_theme():
    return LIGHT_THEME

def toggle_theme(current_theme):
    return DARK_THEME if current_theme == LIGHT_THEME else LIGHT_THEME

def apply_theme(theme, widgets):
    sidebar = widgets.get("sidebar")
    slides_frame = widgets.get("slides_frame")
    dragdrop_frame = widgets.get("dragdrop_frame")
    chat_frame = widgets.get("chat_frame")
    chat_log = widgets.get("chat_log")
    input_frame = widgets.get("input_frame")
    user_input = widgets.get("user_input")
    send_button = widgets.get("send_button")

    if sidebar:
        sidebar.config(bg=theme["bg"])
        for widget in sidebar.winfo_children():
            try:
                widget.config(bg=theme["bg"], fg=theme["fg"])
            except:
                pass

    for frame in [slides_frame, dragdrop_frame, chat_frame]:
        if frame:
            frame.config(bg=theme["content_bg"], fg=theme["fg"])

    if chat_log:
        chat_log.config(bg=theme["input_bg"], fg=theme["fg"], insertbackground=theme["fg"])

    if input_frame:
        input_frame.config(bg=theme["content_bg"])

    if user_input:
        if getattr(user_input, "_placeholder_active", False):
            user_input.config(bg=theme["input_bg"], fg="gray", insertbackground=theme["fg"])
        else:
            user_input.config(bg=theme["input_bg"], fg=theme["fg"], insertbackground=theme["fg"])

    if send_button:
        send_button.config(bg=theme["bg"], fg=theme["fg"])

# interface/chat_box.py

import tkinter as tk
from tkinter import scrolledtext
import threading
from service.gemma_client import query_gemma_stream


def add_placeholder(entry, placeholder, placeholder_color='gray', text_color='black', current_theme=None):
    entry._placeholder_active = True

    def set_placeholder():
        entry.insert(0, placeholder)
        entry.config(fg=placeholder_color)
        entry._placeholder_active = True

    def on_focus_in(event):
        if entry._placeholder_active:
            entry.delete(0, tk.END)
            entry._placeholder_active = False
            if current_theme:
                entry.config(fg=current_theme["fg"])

    def on_focus_out(event):
        if not entry.get():
            set_placeholder()

    entry.insert(0, placeholder)
    entry.config(fg=placeholder_color)
    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)


def setup_chat_box(parent, current_theme, current_deck_context):
    chat_frame = tk.LabelFrame(parent, text="Chat History")
    chat_frame.pack(fill="both", expand=True, padx=10, pady=5)

    chat_log = scrolledtext.ScrolledText(chat_frame, wrap=tk.WORD, height=10)
    chat_log.pack(fill="both", expand=True, padx=5, pady=5)
    chat_log.insert(tk.END, "Gemma: Welcome! Ask me about your slides...\n")

    return chat_frame, chat_log


def create_input_box(parent, chat_log, current_deck_context, current_theme):
    input_frame = tk.Frame(parent)
    input_frame.pack(fill="x", padx=10, pady=10)

    user_input = tk.Entry(input_frame)
    user_input.pack(side="left", fill="x", expand=True, padx=(0, 5))

    def send_message():
        message = user_input.get().strip()
        if not message:
            return

        chat_log.insert(tk.END, f"You: {message}\n")
        chat_log.insert(tk.END, "Gemma: ")
        user_input.delete(0, tk.END)
        chat_log.see(tk.END)

        def stream_response():
            try:
                context_data = current_deck_context.get("value", [])
                # (Optional) Use context_data for smarter responses
                for chunk in query_gemma_stream(prompt=message):
                    chat_log.insert(tk.END, chunk)
                    chat_log.see(tk.END)
            except Exception as e:
                chat_log.insert(tk.END, f"\n[Error] {str(e)}\n")

        threading.Thread(target=stream_response, daemon=True).start()

    send_button = tk.Button(input_frame, text="Send", command=send_message)
    send_button.pack(side="right")

    user_input.bind("<Return>", lambda event: send_message())

    add_placeholder(user_input, "Ask something about your slides...", current_theme=current_theme)

    return input_frame, user_input, send_button


def create_chat_box(root, content_area, current_theme, current_deck_context):
    chat_frame, chat_log = setup_chat_box(content_area, current_theme, current_deck_context)
    input_frame, user_input, send_button = create_input_box(content_area, chat_log, current_deck_context, current_theme)
    return chat_log, user_input

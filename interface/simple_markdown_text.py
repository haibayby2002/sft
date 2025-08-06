import re
import tkinter as tk
from tkinter import scrolledtext

class SimpleMarkdownText(scrolledtext.ScrolledText):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)

        # Markdown styling tags
        self.tag_configure("bold", font=("Helvetica", 10, "bold"))
        self.tag_configure("page", foreground="gray", font=("Helvetica", 10))
        self.tag_configure("h1", font=("Helvetica", 16, "bold"))
        self.tag_configure("h2", font=("Helvetica", 14, "bold"))

        # Streaming state
        self._buffer = ""
        self._last_rendered = ""
        self._incomplete_line = ""

    def insert_markdown_stream(self, chunk):
        """
        Add new streamed markdown text, deduplicate, and render only new content.
        """
        self._buffer += chunk

        # Find suffix to render
        if self._buffer.startswith(self._last_rendered):
            new_suffix = self._buffer[len(self._last_rendered):]
        else:
            # Reset case (e.g., restart)
            new_suffix = self._buffer
            self._last_rendered = ""

        # Keep track of full rendering
        self._last_rendered = self._buffer

        # Process full lines; save partial one for later
        lines = (self._incomplete_line + new_suffix).split("\n")
        self._incomplete_line = lines.pop()

        for line in lines:
            self._render_line(line)

        self.see("end")

    def _render_line(self, line):
        """
        Render a full line with markdown formatting.
        """
        line = line.strip()
        if not line:
            self.insert("end", "\n")
            return

        line_start = self.index("end-1c")

        # --- Headings ---
        if line.startswith("## "):
            content = line[3:].strip()
            self.insert("end", content + "\n")
            self.tag_add("h2", line_start, f"{line_start}+{len(content)}c")
            return

        elif line.startswith("# "):
            content = line[2:].strip()
            self.insert("end", content + "\n")
            self.tag_add("h1", line_start, f"{line_start}+{len(content)}c")
            return

        # --- Inline styling ---
        # Handle **bold** and (page N)
        parts = re.split(r'(\*\*.*?\*\*|\(page \d+\))', line)

        for part in parts:
            start_idx = self.index("end-1c")

            if part.startswith("**") and part.endswith("**") and len(part) > 4:
                content = part[2:-2]
                self.insert("end", content)
                self.tag_add("bold", start_idx, f"{start_idx}+{len(content)}c")

            elif re.fullmatch(r'\(page \d+\)', part):
                self.insert("end", part)
                self.tag_add("page", start_idx, f"{start_idx}+{len(part)}c")

            else:
                self.insert("end", part)

        self.insert("end", "\n")


def demo():
    root = tk.Tk()
    root.title("SimpleMarkdownText Demo")

    viewer = SimpleMarkdownText(root, wrap=tk.WORD, width=80, height=20)
    viewer.pack(fill="both", expand=True)

    # Simulate streaming
    chunks = [
        "# Hello W",
        "orld\nThis is a **bold** wor",
        "d and a (page 9)\n",
        "## Subheading about **Security Testing**"
    ]

    def stream_next(i=0):
        if i < len(chunks):
            viewer.insert_markdown_stream(chunks[i])
            root.after(400, lambda: stream_next(i + 1))

    stream_next()
    root.mainloop()

if __name__ == "__main__":
    demo()

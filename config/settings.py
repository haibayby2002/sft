DB_PATH = "data/slides.db"
DOCS_PATH = "slide_hub/"
GEMMA_MODEL = "gemma:3n"
TOP_N_CONTENT = 5

from pathlib import Path

DB_PATH = str(Path(__file__).resolve().parent.parent / "data" / "slides.db")

import os
from PyPDF2 import PdfReader
from service.docling_service import extract_and_store_pdf_content
from data.models.slide import Slide
from data.models.page import Page
from data.vectorstore.embedder import Embedder
from data.vectorstore.vector_db import VectorDB

embedder = Embedder()
vector_db = VectorDB()

def get_total_pages(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        return len(reader.pages)
    except Exception:
        return 1

def shared_import_logic(deck_id, file_paths, on_success=None, on_fail=None):
    imported = 0
    for file_path in file_paths:
        if not file_path.lower().endswith(".pdf"):
            if on_fail:
                on_fail(file_path, "Not a PDF file.")
            continue

        title = os.path.basename(file_path)
        try:
            # ✅ Create slide
            slide = Slide.create(deck_id, file_path, title)

            # ✅ Update page count
            total_pages = get_total_pages(file_path)
            Slide.update_total_pages(slide.slide_id, total_pages)

            # ✅ Extract text to DB
            extract_and_store_pdf_content(slide.slide_id, file_path)

            # ✅ Embed each page
            pages = Page.get_pages_by_slide(slide.slide_id)
            for page in pages:
                text = page.get_full_text()
                if not text.strip():
                    continue

                embedding = embedder.embed_text(text)
                metadata = {
                    "deck_id": deck_id,
                    "slide_id": slide.slide_id,
                    "page_number": page.page_number,
                    "title": title,
                    "file_path": file_path,
                }
                vector_db.add_vector(embedding, text, metadata)

            imported += 1

        except Exception as e:
            if on_fail:
                on_fail(file_path, str(e))

    # ✅ Very important: reload index from disk after all embedding is done
    vector_db._load()

    if imported and on_success:
        on_success(imported)

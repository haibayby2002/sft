import os
from PyPDF2 import PdfReader

from data.database import insert_slide, update_slide_total_pages
from service.docling_service import extract_and_store_pdf_content  # ✅ use real extractor

def get_total_pages(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        return len(reader.pages)
    except Exception:
        return 1

def shared_import_logic(deck_id, file_paths, on_success=None, on_fail=None):
    imported = 0
    for file_path in file_paths:
        if file_path.lower().endswith(".pdf"):
            title = os.path.basename(file_path)
            try:
                # Insert slide first
                slide_id = insert_slide(deck_id, file_path, title)

                # Get and update total pages
                total_pages = get_total_pages(file_path)
                update_slide_total_pages(slide_id, total_pages)

                # Extract actual content and store in DB
                extract_and_store_pdf_content(slide_id, file_path)

                imported += 1
            except Exception as e:
                if on_fail:
                    on_fail(file_path, str(e))
        else:
            if on_fail:
                on_fail(file_path, "Not a PDF file.")

    if imported and on_success:
        on_success(imported)

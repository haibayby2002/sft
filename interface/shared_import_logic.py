import os
from PyPDF2 import PdfReader

from data.database import (
    insert_slide,
    update_slide_total_pages,
)
from service.docling_service import mock_extract_hello_world

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
            slide_id = insert_slide(deck_id, file_path, title)

            if not slide_id:
                if on_fail:
                    on_fail(file_path, "This slide was already imported.")
                continue

            # Get and update total pages
            total_pages = get_total_pages(file_path)
            update_slide_total_pages(slide_id, total_pages)

            # Insert mock content
            mock_extract_hello_world(slide_id, total_pages)

            imported += 1

        except Exception as e:
            if on_fail:
                on_fail(file_path, str(e))

    if imported and on_success:
        on_success(imported)

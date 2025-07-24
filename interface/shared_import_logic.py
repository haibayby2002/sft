import os
from PyPDF2 import PdfReader

from data.models.slide import Slide
from service.docling_service import extract_and_store_pdf_content


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
                # Create slide using Slide model
                slide = Slide.insert(deck_id=deck_id, file_path=file_path, title=title)

                # Update slide with total pages
                total_pages = get_total_pages(file_path)
                slide.update_total_pages(total_pages)

                # Extract and store content
                extract_and_store_pdf_content(slide.slide_id, file_path)

                imported += 1
            except Exception as e:
                if on_fail:
                    on_fail(file_path, str(e))
        else:
            if on_fail:
                on_fail(file_path, "Not a PDF file.")

    if imported and on_success:
        on_success(imported)

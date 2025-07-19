import os
from PyPDF2 import PdfReader
from data.database import insert_page, insert_content

# === Change this path to your sample PDF ===
PDF_PATH = "C:\\Users\\dell\\Downloads\\Module 1 Transcript - Blockchains, Tokens, and The Decentralized Future.pdf"  # ← Replace this with your PDF path


def extract_text_by_page(pdf_path):
    """Extract plain text from each page of a PDF file."""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    
    reader = PdfReader(pdf_path)
    results = []

    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        results.append({
            "page_number": i,
            "text": text.strip()
        })
    
    return results

def extract_and_store_pdf_content(slide_id: int, pdf_path: str):
    """
    Extract text content from PDF and store into database, page by page.

    Args:
        slide_id (int): The ID of the slide in the database.
        pdf_path (str): The full path to the PDF file.

    Raises:
        FileNotFoundError: If the PDF path is invalid.
        Exception: If any error occurs during insertion.
    """
    pages = extract_text_by_page(pdf_path)

    for page in pages:
        page_number = page["page_number"]
        content_text = page["text"].strip()

        # Insert to page table
        insert_page(slide_id=slide_id, page_number=page_number)

        # Insert content into content table
        insert_content(
            slide_id=slide_id,
            page_number=page_number,
            content_type="text",  # assuming all extracted is "text"
            content_text=content_text,
            position_in_page=None  # can be updated later if positional data is available
        )


if __name__ == "__main__":
    try:
        pages = extract_text_by_page(PDF_PATH)
        print(f"\n✅ Extracted {len(pages)} pages from: {PDF_PATH}\n")

        for page in pages:
            print(f"--- Page {page['page_number']} ---")
            print(page["text"] or "[Empty]")
            print("-" * 40)
    
    except Exception as e:
        print(f"❌ Error during extraction: {e}")

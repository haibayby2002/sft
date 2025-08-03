# app/slide_importer.py

from data.vectorstore.embedder import Embedder
from data.vectorstore.vector_db import VectorDB
from data.vectorstore.metadata_format import create_metadata
from data.models.page import Page
from data.models.content import Content

# Initialize embedder & vector store
embedder = Embedder()
vector_db = VectorDB()

def embed_slide_pages(deck_id, slide_id):
    """
    Go through each page of a slide, embed its content, and store vectors.
    Uses the new Page & Content models.
    """
    pages = Page.get_by_slide(slide_id)
    for page in pages:
        page_number = page.page_number
        content_text = Content.get_page_text(slide_id, page_number)
        if not content_text or not content_text.strip():
            continue

        # Generate embedding
        embedding = embedder.embed_text(content_text)

        # Create metadata with deck_id, slide_id, page_number
        metadata = create_metadata(deck_id, slide_id, page_number, content_text)

        # Store vector with metadata
        vector_db.add_vector(embedding, metadata)

    print(f"✅ Embedded all pages for slide {slide_id}")

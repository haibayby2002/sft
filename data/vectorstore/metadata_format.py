# data/vectorstore/metadata_format.py
from data.models.deck import Deck
from data.models.slide import Slide

def create_metadata(deck_id, slide_id, page_number, content_text):
    """
    Create a consistent metadata dict for each embedded page.
    """
    slide = Slide.get_by_id(slide_id)
    deck = Deck.get_by_id(deck_id)

    return {
        "deck_id": deck_id,
        "deck_name": deck["name"] if deck else "Unknown Deck",
        "slide_id": slide_id,
        "slide_title": slide["title"] if slide else "Unknown Slide",
        "page_number": page_number,
        "content": content_text[:200]  # Optional preview
    }

def format_context(results):
    """
    Convert retrieved vector search results into a context string
    for the LLM prompt, referencing slide title and page number.
    """
    context_lines = []
    for res in results:
        meta = res["metadata"]
        deck_name = meta.get("deck_name", f"Deck {meta.get('deck_id', '?')}")
        slide_title = meta.get("slide_title", f"Slide {meta.get('slide_id', '?')}")
        page_number = meta.get("page_number", "?")
        content = meta.get("content", "[No content]")

        context_lines.append(
            f"📘 Deck: {deck_name} — 📄 Slide: {slide_title}, Page {page_number}\n"
            f"{content}\n"
        )
    return "\n---\n".join(context_lines)


# data/vectorstore/metadata_format.py

def create_metadata(deck_id, slide_id, page_number, content_text):
    """
    Create a consistent metadata dict for each embedded page.
    """
    return {
        "deck_id": deck_id,
        "slide_id": slide_id,
        "page_number": page_number,
        "content_text": content_text  # store full page text for context
    }

def format_context(results):
    """
    Convert retrieved vector search results into a context string
    for the LLM prompt.
    """
    context_lines = []
    for res in results:
        meta = res["metadata"]
        context_lines.append(
            f"[Deck {meta['deck_id']} - Slide {meta['slide_id']} - Page {meta['page_number']}]\n"
            f"{meta['content_text']}\n"
        )
    return "\n---\n".join(context_lines)

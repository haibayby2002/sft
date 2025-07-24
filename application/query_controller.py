from data.database import get_all_decks
from data.database import get_slides_by_deck
from data.database import delete_slide as db_delete_slide
from data.database import delete_deck as db_delete_deck
from data.models.deck import load_context_from_deck as load_context_model

def load_decks():
    """
    Return list of decks from the DB.
    Each deck is a sqlite3.Row object with keys: deck_id, name, description, created_at
    """
    return get_all_decks()



def load_slides(deck_id):
    return get_slides_by_deck(deck_id)


def delete_deck(deck_id):
    db_delete_deck(deck_id)


def delete_slide(slide_id):
    db_delete_slide(slide_id)

def load_context_from_deck(deck_id: int) -> list:
    """
    Load context from a deck by its ID.
    Returns the context as a list of slides, each with pages and their content.
    """
    return load_context_model(deck_id)


def deduplicate_context(context):
    seen_texts = set()
    cleaned = []
    for slide in context:
        new_slide = {"title": slide["title"], "pages": []}
        for page in slide["pages"]:
            unique_content = []
            for content in page["extracted_content"]:
                text = content.get("text", "").strip()
                if text and text not in seen_texts:
                    seen_texts.add(text)
                    unique_content.append(content)
            if unique_content:
                new_slide["pages"].append({
                    "page_number": page["page_number"],
                    "extracted_content": unique_content
                })
        if new_slide["pages"]:
            cleaned.append(new_slide)
    return cleaned

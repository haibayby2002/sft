from data.models.slide import Slide
from data.models.deck import Deck

def load_decks():
    """
    Return list of decks from the DB.
    Each deck is a sqlite3.Row object with keys: deck_id, name, description, created_at
    """
    return Deck.get_all()



def load_slides(deck_id):
    return Slide.get_by_deck(deck_id)


def delete_deck(deck_id):
    Deck.delete(deck_id)

def insert_slide(deck_id, file_path, title=None, total_pages=None):
    """
    Insert a new slide into the database.
    Returns the slide_id of the newly created slide.
    """
    return Slide.create(deck_id, file_path, title, total_pages)

def insert_deck(name, description=None):
    """
    Insert a new deck into the database.
    Returns the deck_id of the newly created deck.
    """
    return Deck.create(name, description)

def delete_slide(slide_id):
    Slide.delete(slide_id)

def load_context_from_deck(deck_id: int) -> list:
    """
    Load context from a deck by its ID.
    Returns the context as a list of slides, each with pages and their content.
    """
    return Deck.get_all()[deck_id].get_context() if deck_id in Deck.get_all() else []


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

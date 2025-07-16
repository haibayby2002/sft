from data.database import get_all_decks
from data.database import get_slides_by_deck
from data.database import delete_slide as db_delete_slide
from data.database import delete_deck as db_delete_deck

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

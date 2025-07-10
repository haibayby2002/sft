from data.database import get_all_decks

def load_decks():
    """
    Return list of decks from the DB.
    Each deck is a sqlite3.Row object with keys: deck_id, name, description, created_at
    """
    return get_all_decks()

from data.database import get_connection
from data.models.slide import Slide
from data.vectorstore.vector_db import VectorDB

class Deck:
    @staticmethod
    def create(name, description=None):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO deck (name, description) VALUES (?, ?)",
            (name, description)
        )
        deck_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return deck_id

    @staticmethod
    def get_all():
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM deck ORDER BY created_at DESC")
        decks = cur.fetchall()
        conn.close()
        return decks

    @staticmethod
    def delete(deck_id):
        slides = Slide.get_by_deck(deck_id)
        for slide in slides:
            Slide.delete(slide['slide_id'])

        conn = get_connection()
        conn.execute("PRAGMA foreign_keys = ON;")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM deck WHERE deck_id = ?", (deck_id,))
        conn.commit()
        conn.close()
       

        # Step 5: Remove vectors from vector store
        vector_db = VectorDB()
        vector_db.remove_vectors_by_deck_id(deck_id)

# data/models/deck.py

import sqlite3
from data.database import get_connection

class Deck:
    def __init__(self, deck_id, name, description, created_at):
        self.deck_id = deck_id
        self.name = name
        self.description = description
        self.created_at = created_at

    @staticmethod
    def create(name, description=None):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO deck (name, description) VALUES (?, ?)
        """, (name, description))
        conn.commit()
        conn.close()

    @staticmethod
    def get_all():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM deck ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        return [Deck(*row) for row in rows]

    @staticmethod
    def get_by_id(deck_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM deck WHERE deck_id = ?", (deck_id,))
        row = cursor.fetchone()
        conn.close()
        return Deck(*row) if row else None

    @staticmethod
    def delete(deck_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM deck WHERE deck_id = ?", (deck_id,))
        conn.commit()
        conn.close()

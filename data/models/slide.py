# data/models/slide.py

import sqlite3
from data.database import get_connection

class Slide:
    def __init__(self, slide_id, deck_id, file_path, title, total_pages):
        self.slide_id = slide_id
        self.deck_id = deck_id
        self.file_path = file_path
        self.title = title
        self.total_pages = total_pages

    @staticmethod
    def create(deck_id, file_path, title, total_pages=0):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO slide (deck_id, file_path, title, total_pages)
            VALUES (?, ?, ?, ?)
        """, (deck_id, file_path, title, total_pages))
        conn.commit()
        conn.close()

    @staticmethod
    def get_by_deck(deck_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM slide WHERE deck_id = ? ORDER BY slide_id ASC
        """, (deck_id,))
        rows = cursor.fetchall()
        conn.close()
        return [Slide(*row) for row in rows]

    @staticmethod
    def delete(slide_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM slide WHERE slide_id = ?", (slide_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def update_title(slide_id, new_title):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE slide SET title = ? WHERE slide_id = ?
        """, (new_title, slide_id))
        conn.commit()
        conn.close()

    @staticmethod
    def get_by_id(slide_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM slide WHERE slide_id = ?", (slide_id,))
        row = cursor.fetchone()
        conn.close()
        return Slide(*row) if row else None

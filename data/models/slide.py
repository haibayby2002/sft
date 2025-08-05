import os
from data.database import get_connection
from data.vectorstore.vector_db import VectorDB





class Slide:
    def __init__(self, slide_id, deck_id, file_path, title=None, total_pages=None):
        self.slide_id = slide_id
        self.deck_id = deck_id
        self.file_path = file_path
        self.title = title
        self.total_pages = total_pages

    @classmethod
    def create(cls, deck_id, file_path, title=None, total_pages=None):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT OR IGNORE INTO slide (deck_id, file_path, title, total_pages)
            VALUES (?, ?, ?, ?)
            """,
            (deck_id, file_path, title, total_pages)
        )
        conn.commit()
        slide_id = cur.lastrowid
        conn.close()
        # 🔥 return a Slide object instead of just ID
        return cls(slide_id, deck_id, file_path, title, total_pages)

    @classmethod
    def get_by_id(cls, slide_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM slide WHERE slide_id = ?", (slide_id,))
        row = cur.fetchone()
        conn.close()
        return dict(row) if row else None

    @classmethod
    def get_by_deck(cls, deck_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM slide WHERE deck_id = ? ORDER BY title", (deck_id,))
        slides = cur.fetchall()
        conn.close()
        return slides

    @classmethod
    def update_total_pages(cls, slide_id, total_pages):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE slide SET total_pages = ? WHERE slide_id = ?",
            (total_pages, slide_id)
        )
        conn.commit()
        conn.close()

    @classmethod
    def delete(cls, slide_id):
        conn = get_connection()
        cursor = conn.cursor()

        # Step 1: Get all pages
        cursor.execute("SELECT page_number FROM page WHERE slide_id = ?", (slide_id,))
        pages = cursor.fetchall()

        # Step 2: Delete content and notes
        for row in pages:
            page_number = row["page_number"]
            cursor.execute("DELETE FROM content WHERE slide_id = ? AND page_number = ?", (slide_id, page_number))
            cursor.execute("DELETE FROM page_note WHERE slide_id = ? AND page_number = ?", (slide_id, page_number))

        # Step 3: Delete pages
        cursor.execute("DELETE FROM page WHERE slide_id = ?", (slide_id,))

        # Step 4: Delete slide
        cursor.execute("DELETE FROM slide WHERE slide_id = ?", (slide_id,))
        conn.commit()
        conn.close()

        #Step 5: Remove vectors from vector store
        vector_db = VectorDB()
        vector_db.remove_vectors_by_slide_id(slide_id)

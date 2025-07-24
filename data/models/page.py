# data/models/page.py

import sqlite3
from data.database import get_connection

class Page:
    def __init__(self, page_id, slide_id, page_number):
        self.page_id = page_id
        self.slide_id = slide_id
        self.page_number = page_number

    @staticmethod
    def create(slide_id, page_number):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO page (slide_id, page_number)
            VALUES (?, ?)
        """, (slide_id, page_number))
        conn.commit()
        page_id = cursor.lastrowid
        conn.close()
        return page_id

    @staticmethod
    def get_by_slide(slide_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM page WHERE slide_id = ? ORDER BY page_number ASC
        """, (slide_id,))
        rows = cursor.fetchall()
        conn.close()
        return [Page(*row) for row in rows]

    @staticmethod
    def delete_by_slide(slide_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM page WHERE slide_id = ?", (slide_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def get_by_id(page_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM page WHERE page_id = ?", (page_id,))
        row = cursor.fetchone()
        conn.close()
        return Page(*row) if row else None

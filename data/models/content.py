# Placeholder content for data/models/content.py
# data/models/content.py

import sqlite3
from data.database import get_connection

class Content:
    def __init__(self, content_id, page_id, content_type, content_text, position_in_page):
        self.content_id = content_id
        self.page_id = page_id
        self.content_type = content_type
        self.content_text = content_text
        self.position_in_page = position_in_page

    @staticmethod
    def create(page_id, content_type, content_text, position_in_page):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO content (page_id, content_type, content_text, position_in_page)
            VALUES (?, ?, ?, ?)
        """, (page_id, content_type, content_text, position_in_page))
        conn.commit()
        content_id = cursor.lastrowid
        conn.close()
        return content_id

    @staticmethod
    def get_by_page(page_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM content WHERE page_id = ?", (page_id,))
        rows = cursor.fetchall()
        conn.close()
        return [Content(*row) for row in rows]

    @staticmethod
    def delete_by_page(page_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM content WHERE page_id = ?", (page_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def get_by_id(content_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM content WHERE content_id = ?", (content_id,))
        row = cursor.fetchone()
        conn.close()
        return Content(*row) if row else None

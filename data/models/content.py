from data.database import get_connection


class Content:
    def __init__(self, content_id, slide_id, page_number, content_type, content_text, position_in_page=None):
        self.content_id = content_id
        self.slide_id = slide_id
        self.page_number = page_number
        self.content_type = content_type
        self.content_text = content_text
        self.position_in_page = position_in_page

    @classmethod
    def create(cls, slide_id, page_number, content_type, content_text, position_in_page=None):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO content (slide_id, page_number, content_type, content_text, position_in_page)
            VALUES (?, ?, ?, ?, ?)
            """,
            (slide_id, page_number, content_type, content_text, position_in_page)
        )
        content_id = cur.lastrowid
        conn.commit()
        conn.close()
        return content_id

    @classmethod
    def get_by_slide(cls, slide_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT context_text FROM content
            WHERE slide_id = ?
            ORDER BY page_number, position_in_page
            """,
            (slide_id,)
        )
        rows = cur.fetchall()
        conn.close()
        return [row["context_text"] for row in rows] if rows else []
    
    @classmethod
    def get_by_slide_and_number(cls, slide_id, page_number):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM content WHERE slide_id = ? AND page_number = ?",
            (slide_id, page_number)
        )
        row = cur.fetchone()
        # print("Fetched row:", dict(row) if row else None)
        content_text = row["content_text"] if row else None
        conn.close()
        return content_text

  

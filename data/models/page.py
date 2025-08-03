from data.database import get_connection


class Page:
    def __init__(self, slide_id, page_number):
        self.slide_id = slide_id
        self.page_number = page_number

    @classmethod
    def create(cls, slide_id, page_number):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT OR IGNORE INTO page (slide_id, page_number)
            VALUES (?, ?)
            """,
            (slide_id, page_number)
        )
        conn.commit()
        conn.close()

    @classmethod
    def get_by_slide(cls, slide_id):
        #     conn = get_connection()
        #     cur = conn.cursor()
        #     cur.execute(
        #         """
        #         SELECT * FROM content
        #         WHERE slide_id = ?
        #         ORDER BY page_number, position_in_page
        #         """,
        #         (slide_id,)
        #     )
        #     contents = cur.fetchall()
        #     conn.close()
        #     return contents
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM page WHERE slide_id = ? ORDER BY page_number",
            (slide_id,)
        )
        pages = cur.fetchall()
        conn.close()
        return pages
    
    @staticmethod
    def get_pages_by_slide(slide_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM page WHERE slide_id = ? ORDER BY page_number",
            (slide_id,)
        )
        rows = cur.fetchall()
        conn.close()
        return [Page(row["slide_id"], row["page_number"]) for row in rows]

    def get_full_text(self):
        """
        Returns the concatenated text content of this page
        for embedding and search purposes.
        """
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT content_text FROM content
            WHERE slide_id = ? AND page_number = ?
            ORDER BY position_in_page
            """,
            (self.slide_id, self.page_number)
        )
        rows = cur.fetchall()
        conn.close()
        return "\n".join([row["content_text"] for row in rows if row["content_text"]])
    
   
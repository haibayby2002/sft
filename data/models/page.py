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
    
   
from data.database import get_connection


class PageNote:
    def __init__(self, note_id, slide_id, page_number, note_text, created_at):
        self.note_id = note_id
        self.slide_id = slide_id
        self.page_number = page_number
        self.note_text = note_text
        self.created_at = created_at

    @classmethod
    def create(cls, slide_id, page_number, note_text):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO page_note (slide_id, page_number, note_text)
            VALUES (?, ?, ?)
            """,
            (slide_id, page_number, note_text)
        )
        note_id = cur.lastrowid
        conn.commit()
        conn.close()
        return note_id

    @classmethod
    def get(cls, slide_id, page_number):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT note_text FROM page_note
            WHERE slide_id = ? AND page_number = ?
            """,
            (slide_id, page_number)
        )
        row = cur.fetchone()
        conn.close()
        return row['note_text'] if row else ""

    @classmethod
    def update(cls, slide_id, page_number, note_text):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE page_note
            SET note_text = ?
            WHERE slide_id = ? AND page_number = ?
            """,
            (note_text, slide_id, page_number)
        )
        conn.commit()
        conn.close()

    @classmethod
    def delete(cls, slide_id, page_number):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            DELETE FROM page_note
            WHERE slide_id = ? AND page_number = ?
            """,
            (slide_id, page_number)
        )
        conn.commit()
        conn.close()

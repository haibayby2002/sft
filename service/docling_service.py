from data.database import get_connection

def mock_extract_hello_world(slide_id: int, total_pages: int):
    conn = get_connection()
    cur = conn.cursor()

    for page_number in range(1, total_pages + 1):
        cur.execute(
            "INSERT INTO page (slide_id, page_number) VALUES (?, ?)",
            (slide_id, page_number)
        )
        page_id = cur.lastrowid

        cur.execute(
            """
            INSERT INTO content (page_id, content_type, content_text, position_in_page)
            VALUES (?, ?, ?, ?)
            """,
            (page_id, 'text', 'Hello World', 0)
        )

    conn.commit()
    conn.close()

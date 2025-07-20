from data.database import get_connection

def load_context_from_deck(deck_id: int) -> list:
    """
    Load context from a deck by its ID.
    Returns the context as a list of slides, each with pages and their content.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Query all slides for the deck
    cursor.execute("SELECT slide_id, title FROM slide WHERE deck_id = ?", (deck_id,))
    slides = cursor.fetchall()

    deck_context = []

    for slide in slides:
        slide_id = slide["slide_id"]
        slide_title = slide["title"]

        slide_info = {
            "slide_id": slide_id,
            "title": slide_title,
            "pages": []
        }

        # Query all pages for this slide
        cursor.execute("""
            SELECT page_number
            FROM page
            WHERE slide_id = ?
            ORDER BY page_number ASC
        """, (slide_id,))
        pages = cursor.fetchall()

        for page in pages:
            page_number = page["page_number"]

            # Query all content blocks for this slide and page_number
            cursor.execute("""
                SELECT content_type, content_text, position_in_page
                FROM content
                WHERE slide_id = ? AND page_number = ?
                ORDER BY position_in_page ASC
            """, (slide_id, page_number))
            contents = cursor.fetchall()

            extracted_content = [
                {"type": row["content_type"], "text": row["content_text"]}
                for row in contents
            ]

            slide_info["pages"].append({
                "page_number": page_number,
                "extracted_content": extracted_content
            })

        deck_context.append(slide_info)

    conn.close()
    return deck_context

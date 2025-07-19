from data.database import insert_content, insert_page

def mock_extract_hello_world(slide_id, total_pages):
    """
    Simulates extracting content from a PDF by inserting "Hello World" content
    for each page of the slide into the database.
    """
    for page_number in range(1, total_pages + 1):
        # Ensure page exists in `page` table
        insert_page(slide_id, page_number)

        # Insert mock "Hello World" content for this page
        insert_content(
            slide_id=slide_id,
            page_number=page_number,
            content_type="text",
            content_text="Hello World",
            position_in_page=0
        )

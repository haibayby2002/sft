import sqlite3
from pathlib import Path
from config.settings import DB_PATH

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Return dict-like rows
    return conn

def initialize_db():
    with get_connection() as conn:
        cursor = conn.cursor()

        # Deck table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS deck (
            deck_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # Slide table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS slide (
            slide_id INTEGER PRIMARY KEY AUTOINCREMENT,
            deck_id INTEGER NOT NULL,
            file_path TEXT NOT NULL,
            title TEXT,
            total_pages INTEGER,
            FOREIGN KEY (deck_id) REFERENCES deck(deck_id)
        );
        """)

        # Page table with composite key (slide_id, page_number)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS page (
            slide_id INTEGER NOT NULL,
            page_number INTEGER NOT NULL,
            PRIMARY KEY (slide_id, page_number),
            FOREIGN KEY (slide_id) REFERENCES slide(slide_id)
        );
        """)

        # Content table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS content (
            content_id INTEGER PRIMARY KEY AUTOINCREMENT,
            slide_id INTEGER NOT NULL,
            page_number INTEGER NOT NULL,
            content_type TEXT CHECK(content_type IN ('text', 'table', 'figure')),
            content_text TEXT,
            position_in_page INTEGER,
            FOREIGN KEY (slide_id, page_number) REFERENCES page(slide_id, page_number)
        );
        """)

        # Access log table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS access_log (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            content_id INTEGER NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            action TEXT CHECK(action IN ('queried', 'opened')),
            FOREIGN KEY (content_id) REFERENCES content(content_id)
        );
        """)

        # Page note table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS page_note (
            note_id INTEGER PRIMARY KEY AUTOINCREMENT,
            slide_id INTEGER NOT NULL,
            page_number INTEGER NOT NULL,
            note_text TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (slide_id, page_number) REFERENCES page(slide_id, page_number)
        );
        """)

        conn.commit()

# Run this in main.py to initialize the database
def init_db():
    initialize_db()

# ------------------------
# Deck CRUD
def insert_deck(name, description=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO deck (name, description) VALUES (?, ?)",
        (name, description)
    )
    deck_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return deck_id

def get_all_decks():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM deck ORDER BY created_at DESC")
    decks = cur.fetchall()
    conn.close()
    return decks

# ------------------------
# Slide CRUD
def insert_slide(deck_id, file_path, title=None, total_pages=None):
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
    return slide_id

def get_slides_by_deck(deck_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM slide WHERE deck_id = ? ORDER BY title",
        (deck_id,)
    )
    slides = cur.fetchall()
    conn.close()
    return slides

def delete_deck(deck_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM slide WHERE deck_id = ?", (deck_id,))
    cursor.execute("DELETE FROM deck WHERE deck_id = ?", (deck_id,))
    conn.commit()
    conn.close()

def delete_slide(slide_id):
    conn = get_connection()
    cursor = conn.cursor()

    # Step 1: Get all pages for the slide
    cursor.execute("SELECT page_number FROM page WHERE slide_id = ?", (slide_id,))
    pages = cursor.fetchall()

    # Step 2: Delete related contents and notes
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

def update_slide_total_pages(slide_id, total_pages):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE slide SET total_pages = ? WHERE slide_id = ?",
        (total_pages, slide_id)
    )
    conn.commit()
    conn.close()

# ------------------------
# Page CRUD
def insert_page(slide_id, page_number):
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

def get_pages_by_slide(slide_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM page WHERE slide_id = ? ORDER BY page_number",
        (slide_id,)
    )
    pages = cur.fetchall()
    conn.close()
    return pages

# ------------------------
# Content CRUD
def insert_content(slide_id, page_number, content_type, content_text, position_in_page=None):
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

def get_content_by_slide(slide_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT * FROM content
        WHERE slide_id = ?
        ORDER BY page_number, position_in_page
        """,
        (slide_id,)
    )
    contents = cur.fetchall()
    conn.close()
    return contents

def get_page_content(slide_id, page_number):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT content_text FROM content
        WHERE slide_id = ? AND page_number = ?
        ORDER BY position_in_page
        """,
        (slide_id, page_number)
    )
    row = cur.fetchone()
    conn.close()
    return row["content_text"] if row else None

# ------------------------
# Page Note CRUD
def insert_page_note(slide_id, page_number, note_text):
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

def get_page_note(slide_id, page_number):
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
    return row["note_text"] if row else None

def update_page_note(slide_id, page_number, note_text):
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

def delete_page_note(slide_id, page_number):
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

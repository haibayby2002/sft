import sqlite3
from pathlib import Path
from config.settings import DB_PATH

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Return dict-like rows
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.executescript("""
    -- Decks
    CREATE TABLE IF NOT EXISTS deck (
        deck_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        description TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    -- Slides
    CREATE TABLE IF NOT EXISTS slide (
        slide_id INTEGER PRIMARY KEY AUTOINCREMENT,
        deck_id INTEGER NOT NULL,
        file_path TEXT NOT NULL,
        title TEXT,
        total_pages INTEGER,
        FOREIGN KEY (deck_id) REFERENCES deck(deck_id)
    );

    -- Pages
    CREATE TABLE IF NOT EXISTS page (
        page_id INTEGER PRIMARY KEY AUTOINCREMENT,
        slide_id INTEGER NOT NULL,
        page_number INTEGER NOT NULL,
        FOREIGN KEY (slide_id) REFERENCES slide(slide_id)
    );

    -- Extracted Content
    CREATE TABLE IF NOT EXISTS content (
        content_id INTEGER PRIMARY KEY AUTOINCREMENT,
        page_id INTEGER NOT NULL,
        content_type TEXT CHECK(content_type IN ('text', 'table', 'figure')),
        content_text TEXT,
        position_in_page INTEGER,
        FOREIGN KEY (page_id) REFERENCES page(page_id)
    );

    -- Access Log
    CREATE TABLE IF NOT EXISTS access_log (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        content_id INTEGER NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        action TEXT CHECK(action IN ('queried', 'opened')),
        FOREIGN KEY (content_id) REFERENCES content(content_id)
    );
    """)

    conn.commit()
    conn.close()

# Add below init_db()

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

    # Optional: delete all slides in this deck
    cursor.execute("DELETE FROM slide WHERE deck_id = ?", (deck_id,))

    # Now delete the deck itself
    cursor.execute("DELETE FROM deck WHERE deck_id = ?", (deck_id,))
    
    conn.commit()
    conn.close()

def delete_slide(slide_id):
    conn = get_connection()
    cursor = conn.cursor()

    # Step 1: Get all page_ids for the slide
    cursor.execute("SELECT page_id FROM page WHERE slide_id = ?", (slide_id,))
    page_ids = [row["page_id"] for row in cursor.fetchall()]

    # Step 2: Delete content for those pages
    if page_ids:
        cursor.executemany("DELETE FROM content WHERE page_id = ?", [(pid,) for pid in page_ids])

    # Step 3: Delete pages
    cursor.execute("DELETE FROM page WHERE slide_id = ?", (slide_id,))

    # Step 4: Delete the slide
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

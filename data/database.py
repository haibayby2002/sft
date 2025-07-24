
import sqlite3
import os

DB_PATH = "data/slides.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # === Deck Table ===
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS deck (
        deck_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # === Slide Table ===
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS slide (
        slide_id INTEGER PRIMARY KEY AUTOINCREMENT,
        deck_id INTEGER NOT NULL,
        file_path TEXT NOT NULL,
        title TEXT NOT NULL,
        total_pages INTEGER DEFAULT 0,
        FOREIGN KEY(deck_id) REFERENCES deck(deck_id) ON DELETE CASCADE
    );
    """)

    # === Page Table ===
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS page (
        page_id INTEGER PRIMARY KEY AUTOINCREMENT,
        slide_id INTEGER NOT NULL,
        page_number INTEGER NOT NULL,
        FOREIGN KEY(slide_id) REFERENCES slide(slide_id) ON DELETE CASCADE
    );
    """)

    # === Content Table ===
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS content (
        content_id INTEGER PRIMARY KEY AUTOINCREMENT,
        page_id INTEGER NOT NULL,
        content_type TEXT NOT NULL,
        content_text TEXT,
        position_in_page TEXT,
        FOREIGN KEY(page_id) REFERENCES page(page_id) ON DELETE CASCADE
    );
    """)

    # === Access Log Table ===
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS access_log (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        content_id INTEGER NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        action TEXT NOT NULL,
        FOREIGN KEY(content_id) REFERENCES content(content_id) ON DELETE CASCADE
    );
    """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("✅ Database initialized.")

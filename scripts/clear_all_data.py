# scripts/clear_all_data.py

import os
import sys


# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data.database import get_connection
from data.vectorstore.vector_db import VectorDB



def clear_sqlite_tables():
    print("🧹 Clearing SQLite tables...")
    with get_connection() as conn:
        cursor = conn.cursor()
        tables = ["access_log", "page_note", "content", "page", "slide", "deck"]
        for table in tables:
            cursor.execute(f"DELETE FROM {table}")
        conn.commit()
    print("✅ All database tables cleared.")

def clear_vector_store():
    print("🧹 Clearing FAISS vector index and metadata...")
    vector_db = VectorDB()
    vector_db.clear()
    print("✅ Vector store cleared.")

def remove_uploaded_pdfs():
    print("🧹 Optionally removing uploaded PDFs (if stored)...")
    import glob
    from config.settings import PDF_UPLOAD_FOLDER  # adjust this path if needed

    if os.path.exists(PDF_UPLOAD_FOLDER):
        files = glob.glob(os.path.join(PDF_UPLOAD_FOLDER, "*.pdf"))
        for f in files:
            try:
                os.remove(f)
            except Exception as e:
                print(f"Failed to delete {f}: {e}")
        print("✅ Removed uploaded PDFs.")
    else:
        print("ℹ️ No upload folder configured. Skipping PDF cleanup.")

def main():
    print("🚨 Running full system reset!")
    clear_sqlite_tables()
    clear_vector_store()
    # remove_uploaded_pdfs()  # Optional: only if you want to clear file storage
    print("🎉 System successfully reset.")

if __name__ == "__main__":
    main()

import sqlite3

conn = sqlite3.connect("C:\\Users\\dell\\Desktop\\hackathon\\sft\data\\slides.db")
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(content);")
print(cursor.fetchall())

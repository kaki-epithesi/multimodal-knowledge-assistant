import sqlite3

DB_NAME = "ingestion.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT,
        filetype TEXT,
        filepath TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chunks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_id INTEGER,
        chunk_index INTEGER,
        content TEXT,
        FOREIGN KEY(file_id) REFERENCES files(id)
    )
    """)
    conn.commit()
    conn.close()
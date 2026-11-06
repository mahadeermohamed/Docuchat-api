import sqlite3

def get_conn():
    return sqlite3.connect("app.db")

def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                text TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS documents(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL
                )
        """) 

# DOCUMENT Q&A
def save_document(title: str, content: str):
    with get_conn() as conn:
        cursor = conn.execute(
            "INSERT INTO documents (title, content) VALUES (?, ?)", (title, content)
        )
        return cursor.lastrowid

def get_document(doc_id: int):
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM documents WHERE id = ?", (doc_id,)
        ).fetchone()
    if row is None:
        return None
    return {"id": row[0], "title": row[1], "content": row[2]}

# MESSAGE HISTORY

def save_message(role: str, text:str):
    with get_conn() as conn:
        conn.execute("INSERT INTO messages (role, text) VALUES (?, ?)", (role, text))

def get_all_messages():
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT role, text, created_at FROM messages ORDER BY id"
        ).fetchall()
        return [{"role": r[0], "text": r[1], "created_at": r[2]} for r in rows]

def get_last_messages(limit: int = 10):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT role, text FROM messages ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    rows.reverse()
    return [{"role": r[0], "text": r[1]} for r in rows]


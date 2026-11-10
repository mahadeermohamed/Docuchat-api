import os
from contextlib import contextmanager

import mysql.connector
from dotenv import load_dotenv

load_dotenv()


@contextmanager
def get_conn():
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
    )
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS messages(
                id INT PRIMARY KEY AUTO_INCREMENT,
                role VARCHAR(20) NOT NULL,
                text TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS documents(
                id INT PRIMARY KEY AUTO_INCREMENT,
                title VARCHAR(255) NOT NULL,
                content LONGTEXT NOT NULL
            )
        """)


# DOCUMENT Q&A
def save_document(title: str, content: str):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO documents (title, content) VALUES (%s, %s)",
            (title, content),
        )
        return cur.lastrowid


def get_document(doc_id: int):
    with get_conn() as conn:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT id, title, content FROM documents WHERE id = %s", (doc_id,))
        return cur.fetchone()  # a dict, or None if not found


# MESSAGE HISTORY
def save_message(role: str, text: str):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO messages (role, text) VALUES (%s, %s)", (role, text)
        )


def get_all_messages():
    with get_conn() as conn:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT role, text, created_at FROM messages ORDER BY id")
        return cur.fetchall()


def get_last_messages(limit: int = 10):
    with get_conn() as conn:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT role, text FROM messages ORDER BY id DESC LIMIT %s", (limit,)
        )
        rows = cur.fetchall()
    rows.reverse()
    return rows
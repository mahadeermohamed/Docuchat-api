import os
from contextlib import contextmanager

import mysql.connector
from dotenv import load_dotenv

load_dotenv()


@contextmanager
def get_conn():
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT","3306")),
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
        # users must be created first, because the other tables reference it
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users(
                id INT PRIMARY KEY AUTO_INCREMENT,
                username VARCHAR(50) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS messages(
                id INT PRIMARY KEY AUTO_INCREMENT,
                user_id INT NOT NULL,
                role VARCHAR(20) NOT NULL,
                text TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS documents(
                id INT PRIMARY KEY AUTO_INCREMENT,
                user_id INT NOT NULL,
                title VARCHAR(255) NOT NULL,
                content LONGTEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)


# USERS
def create_user(username: str, password_hash: str):
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                (username, password_hash),
            )
            return cur.lastrowid
    except mysql.connector.IntegrityError:
        return None  # username already taken


def get_user(username: str):
    with get_conn() as conn:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT id, username, password_hash FROM users WHERE username = %s",
            (username,),
        )
        return cur.fetchone()  # a dict, or None


# DOCUMENT Q&A
def save_document(user_id: int, title: str, content: str):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO documents (user_id, title, content) VALUES (%s, %s, %s)",
            (user_id, title, content),
        )
        return cur.lastrowid


def get_document(doc_id: int, user_id: int):
    with get_conn() as conn:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT id, title, content FROM documents WHERE id = %s AND user_id = %s",
            (doc_id, user_id),
        )
        return cur.fetchone()


# MESSAGE HISTORY
def save_message(user_id: int, role: str, text: str):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO messages (user_id, role, text) VALUES (%s, %s, %s)",
            (user_id, role, text),
        )


def get_all_messages(user_id: int):
    with get_conn() as conn:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT role, text, created_at FROM messages WHERE user_id = %s ORDER BY id",
            (user_id,),
        )
        return cur.fetchall()


def get_last_messages(user_id: int, limit: int = 10):
    with get_conn() as conn:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT role, text FROM messages WHERE user_id = %s ORDER BY id DESC LIMIT %s",
            (user_id, limit),
        )
        rows = cur.fetchall()
    rows.reverse()
    return rows
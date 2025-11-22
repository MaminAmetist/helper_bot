import sqlite3

DB_FILE = "chat_history.db"


def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS messages(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER,
        role TEXT,
        text TEXT,
        created_at TIMESTAMP DEFAULT (datetime('now','localtime'))
    )
    """)
    conn.commit()
    conn.close()


def save_message(chat_id: int, role: str, text: str):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO messages (chat_id, role, text) VALUES (?, ?, ?)",
        (chat_id, role, text)
    )
    conn.commit()
    conn.close()


def get_messages(chat_id: int):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT id, role, text, created_at FROM messages WHERE chat_id = ? ORDER BY id ASC", (chat_id,))
    rows = cur.fetchall()
    conn.close()
    return [{"id": r[0], "role": r[1], "text": r[2], "created_at": r[3]} for r in rows]


def delete_messages_by_chat_id(chat_id: int):
    conn = sqlite3.connect(DB_FILE)
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM messages WHERE chat_id = ?", (chat_id,))
        conn.commit()
    finally:
        conn.close()

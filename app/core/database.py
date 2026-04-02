import sqlite3

from app.config.settings import DB_PATH


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS clothes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            image_relpath TEXT NOT NULL,
            feature_relpath TEXT NOT NULL,
            category_name TEXT,
            category_conf TEXT,
            main_category TEXT,
            season TEXT,
            thickness TEXT,
            attributes_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS deleted_clothes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_cloth_id INTEGER,
            user_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            image_relpath TEXT NOT NULL,
            feature_relpath TEXT NOT NULL,
            category_name TEXT,
            category_conf TEXT,
            main_category TEXT,
            season TEXT,
            thickness TEXT,
            attributes_json TEXT,
            deleted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
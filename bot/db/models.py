import os
import sqlite3
import logging

logger = logging.getLogger(__name__)
DB_PATH = os.getenv("DB_PATH", "reminders.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    logger.info("Initializing database at %s", DB_PATH)
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                chat_id   INTEGER PRIMARY KEY,
                timezone  TEXT    NOT NULL DEFAULT 'Europe/Moscow',
                created_at TEXT   DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS reminders (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id     INTEGER NOT NULL,
                text        TEXT    NOT NULL,
                remind_at   TEXT    NOT NULL,
                created_at  TEXT    DEFAULT (datetime('now')),
                sent        INTEGER DEFAULT 0,
                FOREIGN KEY (chat_id) REFERENCES users(chat_id)
            );
        """)
    logger.info("Database initialized")
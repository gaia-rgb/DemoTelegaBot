import logging
from datetime import datetime
from typing import Optional
from bot.db.models import get_connection

logger = logging.getLogger(__name__)


def upsert_user(chat_id: int, timezone: str = "Europe/Moscow"):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO users (chat_id, timezone) VALUES (?, ?) "
            "ON CONFLICT(chat_id) DO UPDATE SET timezone = excluded.timezone",
            (chat_id, timezone),
        )


def get_user_timezone(chat_id: int) -> str:
    with get_connection() as conn:
        row = conn.execute("SELECT timezone FROM users WHERE chat_id = ?", (chat_id,)).fetchone()
    return row["timezone"] if row else "Europe/Moscow"


def add_reminder(chat_id: int, text: str, remind_at: datetime) -> int:
    remind_at_str = remind_at.strftime("%Y-%m-%d %H:%M:%S")
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO reminders (chat_id, text, remind_at) VALUES (?, ?, ?)",
            (chat_id, text, remind_at_str),
        )
    return cursor.lastrowid


def get_pending_reminders(chat_id: int) -> list:
    """Get pending reminders for a specific user (for /list command)."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, text, remind_at FROM reminders "
            "WHERE chat_id = ? AND sent = 0 ORDER BY remind_at",
            (chat_id,),
        ).fetchall()
    return [dict(r) for r in rows]


def get_all_pending_reminders() -> list:
    """Get ALL pending reminders across all users (used on bot startup to restore jobs)."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, chat_id, text, remind_at FROM reminders "
            "WHERE sent = 0 ORDER BY remind_at",
        ).fetchall()
    return [dict(r) for r in rows]


def mark_sent(reminder_id: int):
    with get_connection() as conn:
        conn.execute("UPDATE reminders SET sent = 1 WHERE id = ?", (reminder_id,))


def delete_reminder(reminder_id: int, chat_id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM reminders WHERE id = ? AND chat_id = ? AND sent = 0",
            (reminder_id, chat_id),
        )
    return cursor.rowcount > 0
import logging
from datetime import datetime, timezone
from telegram.ext import CallbackContext
from bot.db.repository import get_all_pending_reminders, mark_sent

logger = logging.getLogger(__name__)


async def send_reminder(context: CallbackContext):
    """Job callback: send a scheduled reminder to the user."""
    job = context.job
    chat_id = job.data["chat_id"]
    reminder_id = job.data["reminder_id"]
    text = job.data["text"]

    try:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"🔔 Напоминание!\n\n{text}",
        )
        mark_sent(reminder_id)
        logger.info("Reminder %d sent to %d", reminder_id, chat_id)
    except Exception as e:
        logger.error("Failed to send reminder %d: %s", reminder_id, e)


def schedule_reminder(app, chat_id: int, reminder_id: int, text: str, remind_at_utc: datetime):
    """Register a one-shot job in the application's job queue."""
    app.job_queue.run_once(
        send_reminder,
        when=remind_at_utc,
        data={"chat_id": chat_id, "reminder_id": reminder_id, "text": text},
        name=f"reminder_{reminder_id}",
    )
    logger.info("Scheduled reminder %d at %s UTC", reminder_id, remind_at_utc)


async def restore_pending_reminders(app) -> int:
    """On bot startup: reload all unsent reminders from DB into the job queue.
    Returns the number of jobs restored."""
    now_utc = datetime.now(timezone.utc)
    restored = 0
    overdue = 0

    for row in get_all_pending_reminders():
        remind_at = datetime.fromisoformat(row["remind_at"]).replace(tzinfo=timezone.utc)

        if remind_at <= now_utc:
            # Reminder is overdue — send it immediately
            app.job_queue.run_once(
                send_reminder,
                when=1,  # 1 second from now
                data={"chat_id": row["chat_id"], "reminder_id": row["id"], "text": row["text"]},
                name=f"reminder_{row['id']}",
            )
            overdue += 1
        else:
            schedule_reminder(app, row["chat_id"], row["id"], row["text"], remind_at)
            restored += 1

    logger.info("Restored %d pending reminder(s), %d overdue sent immediately", restored, overdue)
    return restored + overdue
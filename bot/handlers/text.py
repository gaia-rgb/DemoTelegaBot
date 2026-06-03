import logging
from telegram import Update
from telegram.ext import ContextTypes
from bot.db.repository import (
    upsert_user, get_user_timezone,
    add_reminder, get_pending_reminders, delete_reminder,
)
from bot.services.parser import parse_reminder, extract_reminder_text, format_confirmation
from bot.services.scheduler import schedule_reminder

logger = logging.getLogger(__name__)


async def remind_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    upsert_user(chat_id)

    if not context.args:
        await update.message.reply_text(
            "Укажи текст напоминания. Например:\n`/remind завтра в 9:00 позвонить врачу`",
            parse_mode="Markdown",
        )
        return

    full_text = " ".join(context.args)
    user_tz = get_user_timezone(chat_id)
    dt_utc = parse_reminder(full_text, user_tz)

    if dt_utc is None:
        await update.message.reply_text(
            "❓ Не смог определить дату.\n"
            "Попробуй: `завтра в 10:00`, `через 30 минут`, `15 июня в 14:30`",
            parse_mode="Markdown",
        )
        return

    reminder_text = extract_reminder_text(full_text)
    reminder_id = add_reminder(chat_id, reminder_text, dt_utc)
    schedule_reminder(context.application, chat_id, reminder_id, reminder_text, dt_utc)

    await update.message.reply_text(
        format_confirmation(dt_utc, user_tz, reminder_text),
        parse_mode="Markdown",
    )


async def list_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_tz = get_user_timezone(chat_id)
    reminders = get_pending_reminders(chat_id)

    if not reminders:
        await update.message.reply_text("📭 Активных напоминаний нет.")
        return

    from zoneinfo import ZoneInfo
    tz = ZoneInfo(user_tz)
    lines = [f"📋 *Активные напоминания* ({user_tz}):"]
    for r in reminders:
        from datetime import datetime
        dt = datetime.fromisoformat(r["remind_at"]).replace(
            tzinfo=__import__("datetime").timezone.utc
        ).astimezone(tz)
        lines.append(f"  `{r['id']}` · {dt.strftime('%d.%m %H:%M')} — {r['text']}")

    lines.append("\nДля отмены: `/cancel <id>`")
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text(
            "Укажи ID напоминания. Например: `/cancel 3`", parse_mode="Markdown"
        )
        return

    reminder_id = int(context.args[0])
    if delete_reminder(reminder_id, chat_id):
        await update.message.reply_text(f"✅ Напоминание #{reminder_id} отменено.")
    else:
        await update.message.reply_text(
            f"❌ Напоминание #{reminder_id} не найдено или уже отправлено."
        )
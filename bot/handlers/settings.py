import logging
from telegram import Update
from telegram.ext import ContextTypes
from bot.db.repository import upsert_user, get_user_timezone

logger = logging.getLogger(__name__)

HELP_TEXT = """
🤖 *Бот для напоминаний*

*Команды:*
/remind <текст с датой> — создать напоминание
/list — список активных напоминаний
/cancel <id> — отменить напоминание
/timezone <зона> — установить временную зону
/help — эта справка

*Примеры:*
• /remind завтра в 9:00 позвонить врачу
• /remind через 2 часа выпить воды
• /remind 15 июня в 14:30 встреча
• Или просто отправь *голосовое сообщение*!
""".strip()


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    upsert_user(chat_id)
    await update.message.reply_text(
        "👋 Привет! Я бот для напоминаний.\n\n"
        "Отправь мне голосовое сообщение или текст с датой и временем.\n"
        "Например: *завтра в 9 утра позвонить врачу*\n\n"
        "Введи /help для списка команд.",
        parse_mode="Markdown",
    )


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP_TEXT, parse_mode="Markdown")


async def timezone_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not context.args:
        current_tz = get_user_timezone(chat_id)
        await update.message.reply_text(
            f"🌍 Текущая временная зона: *{current_tz}*\n\n"
            "Чтобы изменить: `/timezone Europe/Moscow`\n"
            "Список зон: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones",
            parse_mode="Markdown",
        )
        return

    tz_name = context.args[0]
    try:
        from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
        ZoneInfo(tz_name)
    except Exception:
        await update.message.reply_text(
            f"❌ Неизвестная временная зона: `{tz_name}`\n"
            "Примеры: `Europe/Moscow`, `Asia/Yekaterinburg`, `America/New_York`",
            parse_mode="Markdown",
        )
        return

    upsert_user(chat_id, tz_name)
    await update.message.reply_text(
        f"✅ Временная зона установлена: *{tz_name}*", parse_mode="Markdown"
    )
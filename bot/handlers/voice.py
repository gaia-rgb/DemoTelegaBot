import logging
from telegram import Update
from telegram.ext import ContextTypes
from bot.db.repository import upsert_user, get_user_timezone, add_reminder
from bot.services.stt import transcribe_voice
from bot.services.parser import parse_reminder, extract_reminder_text, format_confirmation
from bot.services.scheduler import schedule_reminder

logger = logging.getLogger(__name__)


async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    upsert_user(chat_id)

    await update.message.reply_text("🎙 Обрабатываю голосовое сообщение...")

    try:
        voice = update.message.voice
        tg_file = await context.bot.get_file(voice.file_id)
        ogg_bytes = bytes(await tg_file.download_as_bytearray())
        text = await transcribe_voice(ogg_bytes)
    except Exception as e:
        logger.error("Voice transcription failed: %s", e)
        await update.message.reply_text(
            "❌ Не удалось распознать голосовое сообщение. Попробуй ещё раз."
        )
        return

    if not text:
        await update.message.reply_text("🤷 Не смог разобрать речь. Попробуй говорить чётче.")
        return

    user_tz = get_user_timezone(chat_id)
    dt_utc = parse_reminder(text, user_tz)

    if dt_utc is None:
        await update.message.reply_text(
            f"🎙 Распознано: «{text}»\n\n"
            "❓ Не смог определить дату.\n"
            "Уточни, например: `/remind завтра в 10:00 {текст}`",
            parse_mode="Markdown",
        )
        return

    reminder_text = extract_reminder_text(text)
    reminder_id = add_reminder(chat_id, reminder_text, dt_utc)
    schedule_reminder(context.application, chat_id, reminder_id, reminder_text, dt_utc)

    confirmation = format_confirmation(dt_utc, user_tz, reminder_text)
    await update.message.reply_text(
        f"🎙 Распознано: «{text}»\n\n{confirmation}",
        parse_mode="Markdown",
    )
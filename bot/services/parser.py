import re
import logging
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from typing import Optional

import dateparser
from dateparser.search import search_dates

logger = logging.getLogger(__name__)

DATEPARSER_SETTINGS = {
    "PREFER_DATES_FROM": "future",
    "RETURN_AS_TIMEZONE_AWARE": True,
    "PREFER_DAY_OF_MONTH": "first",
    "TO_TIMEZONE": "UTC",
}

DATE_NOISE_PATTERNS = [
    r"через\s+\d+\s+\w+",
    r"завтра|послезавтра|сегодня",
    r"в\s+\d{1,2}[:.]\d{2}",
    r"\d{1,2}\s+\w+\s+в\s+\d{1,2}[:.]\d{2}",
    r"в\s+\w+\s+в\s+\d{1,2}[:.]\d{2}",
]

WEEKDAYS_RU = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]


def parse_reminder(text: str, user_tz: str = "Europe/Moscow") -> Optional[datetime]:
    """Returns UTC-aware datetime or None.

    Uses search_dates to find a date/time expression inside arbitrary text,
    so phrases like 'через 2 минуты позвонить врачу' work correctly.
    """
    settings = {**DATEPARSER_SETTINGS, "TIMEZONE": user_tz}

    # First try full-text parse (fast path for clean date strings)
    dt = dateparser.parse(text, languages=["ru", "en"], settings=settings)

    # If full-text fails, extract the date substring from within the text
    if dt is None:
        results = search_dates(text, languages=["ru", "en"], settings=settings)
        if results:
            dt = results[0][1]  # take the first found date

    if dt and dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo(user_tz)).astimezone(timezone.utc)

    logger.info("parse_reminder %r -> %s", text[:60], dt)
    return dt


def extract_reminder_text(full_text: str) -> str:
    """Strip date/time tokens from text, return the remainder as reminder content."""
    cleaned = full_text
    for pat in DATE_NOISE_PATTERNS:
        cleaned = re.sub(pat, "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(
        r"^(напомни(те)?|поставь\s+напоминание|remind\s+me)\s*",
        "", cleaned, flags=re.IGNORECASE
    )
    result = cleaned.strip(" .,!")
    return result if result else full_text


def format_confirmation(dt_utc: datetime, user_tz: str, reminder_text: str) -> str:
    tz = ZoneInfo(user_tz)
    dt_local = dt_utc.astimezone(tz)
    weekday = WEEKDAYS_RU[dt_local.weekday()]
    offset = dt_local.strftime("%z")
    offset_str = f"UTC{offset[:3]}"
    return (
        f"✅ Напоминание установлено!\n\n"
        f"📝 Текст: {reminder_text}\n"
        f"📅 Дата: {dt_local.strftime('%d.%m.%Y')} ({weekday})\n"
        f"🕐 Время: {dt_local.strftime('%H:%M')}\n"
        f"🌍 Часовой пояс: {user_tz} ({offset_str})\n"
    )
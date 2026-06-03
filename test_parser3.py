import sys, os
sys.path.insert(0, os.getcwd())

import dateparser
from datetime import timezone
from zoneinfo import ZoneInfo

# Exact same settings as in parser.py
DATEPARSER_SETTINGS = {
    "PREFER_DATES_FROM": "future",
    "RETURN_AS_TIMEZONE_AWARE": True,
    "PREFER_DAY_OF_MONTH": "first",
    "TO_TIMEZONE": "UTC",
}

user_tz = "Europe/Moscow"
settings = {**DATEPARSER_SETTINGS, "TIMEZONE": user_tz}

phrases = [
    "\u0447\u0435\u0440\u0435\u0437 1 \u043c\u0438\u043d\u0443\u0442\u0443",   # через 1 минуту
    "\u0437\u0430\u0432\u0442\u0440\u0430 \u0432 10:00",                         # завтра в 10:00
    "tomorrow at 10am",
]

for phrase in phrases:
    # Direct call
    dt_direct = dateparser.parse(phrase, languages=["ru", "en"])
    # With settings (like parse_reminder does)
    dt_settings = dateparser.parse(phrase, languages=["ru", "en"], settings=settings)
    print(f"Phrase: {phrase!r}")
    print(f"  direct:       {dt_direct}")
    print(f"  with settings:{dt_settings}")
    print()

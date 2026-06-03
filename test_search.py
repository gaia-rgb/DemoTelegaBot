from dateparser.search import search_dates

settings = {
    "PREFER_DATES_FROM": "future",
    "RETURN_AS_TIMEZONE_AWARE": True,
    "TO_TIMEZONE": "UTC",
    "TIMEZONE": "Europe/Moscow",
}

phrases = [
    "\u0447\u0435\u0440\u0435\u0437 2 \u043c\u0438\u043d\u0443\u0442\u044b \u0442\u0435\u0441\u0442",  # через 2 минуты тест
    "\u0437\u0430\u0432\u0442\u0440\u0430 \u0432 10:00 \u043f\u043e\u0437\u0432\u043e\u043d\u0438\u0442\u044c \u0432\u0440\u0430\u0447\u0443",  # завтра в 10:00 позвонить врачу
    "\u043d\u0430\u043f\u043e\u043c\u043d\u0438 \u0447\u0435\u0440\u0435\u0437 30 \u043c\u0438\u043d\u0443\u0442 \u0432\u044b\u043f\u0438\u0442\u044c \u0432\u043e\u0434\u044b",  # напомни через 30 минут выпить воды
]

for phrase in phrases:
    results = search_dates(phrase, languages=["ru", "en"], settings=settings)
    print(f"Input: {phrase!r}")
    print(f"Found: {results}")
    print()

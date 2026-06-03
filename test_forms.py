import dateparser

settings = {
    "PREFER_DATES_FROM": "future",
    "RETURN_AS_TIMEZONE_AWARE": True,
    "PREFER_DAY_OF_MONTH": "first",
    "TO_TIMEZONE": "UTC",
    "TIMEZONE": "Europe/Moscow",
}

# Test different Russian word forms
phrases = [
    "\u0447\u0435\u0440\u0435\u0437 1 \u043c\u0438\u043d\u0443\u0442\u0443",         # через 1 минуту
    "\u0447\u0435\u0440\u0435\u0437 2 \u043c\u0438\u043d\u0443\u0442\u044b",         # через 2 минуты
    "\u0447\u0435\u0440\u0435\u0437 5 \u043c\u0438\u043d\u0443\u0442",               # через 5 минут
    "\u0447\u0435\u0440\u0435\u0437 2 \u043c\u0438\u043d\u0443\u0442\u044b \u0442\u0435\u0441\u0442",  # через 2 минуты тест
    "2 minutes",
    "in 2 minutes",
    # Try without PREFER_DATES_FROM
]

print("=== With PREFER_DATES_FROM=future ===")
for p in phrases:
    dt = dateparser.parse(p, languages=["ru", "en"], settings=settings)
    print(f"  {p!r} -> {dt}")

print()
print("=== Without PREFER_DATES_FROM ===")
settings2 = {
    "RETURN_AS_TIMEZONE_AWARE": True,
    "TO_TIMEZONE": "UTC",
    "TIMEZONE": "Europe/Moscow",
}
for p in phrases:
    dt = dateparser.parse(p, languages=["ru", "en"], settings=settings2)
    print(f"  {p!r} -> {dt}")

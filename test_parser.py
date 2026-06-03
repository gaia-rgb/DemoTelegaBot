from bot.services.parser import parse_reminder, format_confirmation
from datetime import datetime, timezone

test_phrases = [
    "через 1 минуту тест",
    "завтра в 10:00 позвонить врачу",
    "через 2 часа встреча",
    "напомни в пятницу в 18:00 встреча",
]

print("=== Тест парсера дат ===")
for phrase in test_phrases:
    dt = parse_reminder(phrase, "Europe/Moscow")
    now = datetime.now(timezone.utc)
    if dt:
        diff = int((dt - now).total_seconds())
        print(f"OK   [{diff}с] \"{phrase}\"")
        print(f"       -> {dt}")
    else:
        print(f"FAIL \"{phrase}\" -> None")
    print()

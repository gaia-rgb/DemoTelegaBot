import dateparser
from datetime import datetime, timezone

# Test 1: simple English
dt = dateparser.parse("tomorrow at 10am")
print("English 'tomorrow at 10am':", dt)

# Test 2: Russian basic
dt = dateparser.parse("завтра в 10:00", languages=["ru"])
print("Russian 'завтра в 10:00':", dt)

# Test 3: Russian with settings
settings = {
    "PREFER_DATES_FROM": "future",
    "RETURN_AS_TIMEZONE_AWARE": True,
    "TO_TIMEZONE": "UTC",
    "TIMEZONE": "Europe/Moscow",
}
dt = dateparser.parse("через 1 минуту", languages=["ru", "en"], settings=settings)
print("Russian 'через 1 минуту' with settings:", dt)

# Test 4: check dateparser version
import dateparser as dp
print("dateparser version:", dp.__version__)

# Telegram Reminder Bot

Бот для создания напоминаний через Telegram. Поддерживает голосовые сообщения и текстовые команды с распознаванием естественного языка на русском и английском.

---

## Что умеет бот

- 🎙 **Голосовые напоминания** — отправь голосовое сообщение, бот распознает речь (локально, через Whisper) и создаст напоминание
- 💬 **Текстовые напоминания** — команда `/remind` с датой и временем на естественном языке
- 📋 **Список напоминаний** — просмотр всех активных напоминаний
- ❌ **Отмена напоминания** — удаление по ID
- 🌍 **Временные зоны** — каждый пользователь настраивает свою зону
- 🔔 **Точная доставка** — напоминание придёт в указанное время
- 📦 **Без внешних API** — распознавание речи работает полностью локально

---

## Шаг 1: Создать бота через @BotFather

1. Открой Telegram и найди бота [@BotFather](https://t.me/BotFather)
2. Отправь команду `/newbot`
3. Введи имя бота (например: `Мой бот напоминаний`)
4. Введи username бота (должен заканчиваться на `bot`, например: `my_reminder_bot`)
5. BotFather выдаст **токен** вида `123456789:AABBccDDeeFFggHH...`
6. Сохрани токен — он понадобится в шаге 4

---

## Шаг 2: Получить CHAT_ID

1. Найди бота [@userinfobot](https://t.me/userinfobot) в Telegram
2. Отправь ему любое сообщение
3. Бот ответит твоим `id` — это и есть твой `CHAT_ID`

---

## Шаг 3: Установить системные зависимости

### Python 3.11+

Убедись, что установлен Python 3.11 или новее:

```bash
python --version
```

Если нет — скачай с [python.org](https://www.python.org/downloads/).

### ffmpeg

ffmpeg нужен для конвертации голосовых сообщений из OGG в WAV.

**Windows:**
```powershell
winget install ffmpeg
```
или скачай с [ffmpeg.org](https://ffmpeg.org/download.html) и добавь в PATH.

**Linux (Ubuntu/Debian):**
```bash
sudo apt update && sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

Проверка установки:
```bash
ffmpeg -version
```

---

## Шаг 4: Настроить проект

1. Скопируй `.env.example` в `.env`:

```bash
cp .env.example .env
```

На Windows (PowerShell):
```powershell
Copy-Item .env.example .env
```

2. Открой `.env` и заполни обязательные переменные:

```env
BOT_TOKEN=123456789:AABBccDDeeFFggHH...   # токен от BotFather
CHAT_ID=123456789                          # твой chat_id
BOT_MODE=polling                           # polling или webhook
WHISPER_MODEL=small                        # tiny / base / small / medium / large
DEFAULT_TIMEZONE=Europe/Moscow             # временная зона по умолчанию
DB_PATH=reminders.db                       # путь к базе данных
```

**Модели Whisper** (выбери по мощности компьютера):
| Модель | Размер | Точность | RAM  |
|--------|--------|----------|------|
| tiny   | 75 МБ  | низкая   | 1 ГБ |
| base   | 142 МБ | средняя  | 1 ГБ |
| small  | 466 МБ | хорошая  | 2 ГБ |
| medium | 1.5 ГБ | высокая  | 5 ГБ |
| large  | 3 ГБ   | лучшая   | 10 ГБ|

---

## Шаг 5: Установить зависимости Python

Создай виртуальное окружение (рекомендуется):

```bash
python -m venv .venv
```

Активируй его:

```bash
# Linux / macOS
source .venv/bin/activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

Установи пакеты:

```bash
pip install -r requirements.txt
```

> Первая установка может занять несколько минут — скачивается PyTorch и Whisper.

---

## Шаг 6: Запустить бота (режим polling)

```bash
python bot/main.py
```

В консоли появится:
```
INFO - Starting bot in POLLING mode
INFO - Initializing database at reminders.db
INFO - Database initialized
```

Бот готов к работе! Открой Telegram и напиши своему боту `/start`.

---

## Шаг 7 (опционально): Деплой с Webhook

Webhook нужен для работы на сервере (VPS). Это позволяет боту получать сообщения мгновенно без постоянного опроса серверов Telegram.

### Требования

- Публичный домен с SSL (HTTPS)
- Открытый порт (по умолчанию 8443)

### Настройка

1. В файле `.env` измени:

```env
BOT_MODE=webhook
WEBHOOK_URL=https://yourdomain.com/webhook
WEBHOOK_PORT=8443
```

2. Убедись, что на сервере открыт порт 8443 (или другой из WEBHOOK_PORT)

3. Запусти бота:

```bash
python bot/main.py
```

### Nginx (рекомендуется как reverse proxy)

Пример конфигурации:

```nginx
server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate     /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location /webhook {
        proxy_pass http://127.0.0.1:8443;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Команды бота

| Команда | Описание |
|---------|----------|
| `/start` | Начать работу с ботом |
| `/help` | Показать справку |
| `/remind <текст>` | Создать напоминание |
| `/list` | Список активных напоминаний |
| `/cancel <id>` | Отменить напоминание по ID |
| `/timezone <зона>` | Установить временную зону |

---

## Примеры напоминаний

### Текстовые команды

```
/remind завтра в 9:00 позвонить врачу
/remind через 30 минут выпить таблетку
/remind 15 июня в 14:30 встреча с командой
/remind в пятницу в 18:00 купить продукты
/remind через 2 часа проверить почту
/remind послезавтра в полдень оплатить счёт
```

### Голосовые сообщения

Просто запиши голосовое сообщение в Telegram:

- *"Напомни мне завтра в девять утра позвонить маме"*
- *"Поставь напоминание через час на встречу"*
- *"Remind me on Friday at 3 PM about the report"*

Бот распознает речь локально через Whisper и создаст напоминание.

---

## Список временных зон

Полный список зон: [Wikipedia — List of tz database time zones](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)

Популярные зоны России и СНГ:

| Зона | Город | UTC |
|------|-------|-----|
| `Europe/Moscow` | Москва, Санкт-Петербург | UTC+3 |
| `Europe/Kaliningrad` | Калининград | UTC+2 |
| `Asia/Yekaterinburg` | Екатеринбург | UTC+5 |
| `Asia/Novosibirsk` | Новосибирск | UTC+7 |
| `Asia/Krasnoyarsk` | Красноярск | UTC+7 |
| `Asia/Irkutsk` | Иркутск | UTC+8 |
| `Asia/Yakutsk` | Якутск | UTC+9 |
| `Asia/Vladivostok` | Владивосток | UTC+10 |
| `Europe/Kiev` | Киев | UTC+2/3 |
| `Asia/Almaty` | Алматы | UTC+6 |

Установить зону: `/timezone Europe/Moscow`

---

## Troubleshooting

### ffmpeg не найден

**Ошибка:** `FileNotFoundError: [WinError 2] Не удается найти указанный файл: 'ffmpeg'`

**Решение:**
1. Убедись, что ffmpeg установлен: `ffmpeg -version`
2. Если ffmpeg установлен, но не найден — добавь папку с ffmpeg.exe в переменную PATH
3. На Windows: Панель управления → Система → Дополнительные параметры системы → Переменные среды

---

### Whisper работает медленно (CPU)

**Причина:** Модели Whisper требовательны к ресурсам при работе на CPU.

**Решение:**
1. Используй меньшую модель: `WHISPER_MODEL=tiny` или `WHISPER_MODEL=base`
2. Если есть GPU NVIDIA — установи `torch` с CUDA:
   ```bash
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
   ```
3. Whisper автоматически использует GPU если он доступен (параметр `fp16=True` в `stt.py`)

---

### Неверная временная зона

**Симптом:** Напоминание приходит не в то время.

**Решение:**
1. Проверь текущую зону: `/timezone`
2. Установи правильную: `/timezone Europe/Moscow`
3. Убедись, что зона указана в правильном формате (например `Europe/Moscow`, а не `Moscow`)
4. Полный список зон: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones

---

### Бот не отвечает

1. Убедись, что бот запущен (`python bot/main.py`)
2. Проверь, что `BOT_TOKEN` в `.env` указан верно (без пробелов, без кавычек)
3. Убедись, что не запущено несколько экземпляров бота одновременно
4. В режиме polling — интернет-соединение должно быть стабильным

---

### Ошибка `ModuleNotFoundError`

Убедись, что виртуальное окружение активировано и зависимости установлены:

```bash
source .venv/bin/activate   # Linux/macOS
.venv\Scripts\Activate.ps1  # Windows

pip install -r requirements.txt
```

---

## Структура проекта

```
telegram-reminder-bot/
├── bot/
│   ├── main.py              # Точка входа, регистрация хендлеров
│   ├── handlers/
│   │   ├── voice.py         # Обработка голосовых сообщений
│   │   ├── text.py          # Команды /remind, /list, /cancel
│   │   └── settings.py      # Команды /start, /help, /timezone
│   ├── services/
│   │   ├── stt.py           # Распознавание речи (Whisper)
│   │   ├── parser.py        # Парсинг дат и времени (dateparser)
│   │   └── scheduler.py     # Планировщик напоминаний (job queue)
│   └── db/
│       ├── models.py        # Инициализация SQLite
│       └── repository.py    # CRUD операции с БД
├── .env.example             # Шаблон переменных окружения
├── requirements.txt         # Зависимости Python
└── README.md                # Документация
```
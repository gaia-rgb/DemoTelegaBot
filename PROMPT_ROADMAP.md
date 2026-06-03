# Telegram Reminder Bot — Prompt & RoadMap

> **Статус:** Фаза 0 — планирование  
> **Язык реализации:** Python 3.11+  
> **Бесплатное STT:** OpenAI Whisper (локальный запуск, без API)  
> **Режимы работы:** Polling (локально) → Webhook (деплой на сервер)

---

## 1. Контекст задачи

Telegram-бот принимает голосовые сообщения от пользователя, переводит их в текст локально
(без платных API), извлекает дату/время, сохраняет напоминание и в нужный момент
отправляет уведомление обратно в Telegram с указанием временной зоны пользователя.

### Ключевые требования

| # | Требование | Детали |
|---|-----------|--------|
| 1 | **Speech-to-Text без платных API** | Whisper (openai-whisper) — запуск модели локально, бесплатно |
| 2 | **Распознавание даты/времени** | `dateparser` (поддерживает RU) + ручной разбор относительных фраз |
| 3 | **Временная зона** | Пользователь задаёт через `/timezone`, хранится в БД на пользователя |
| 4 | **Подтверждение боту** | После постановки напоминания — ответное сообщение с датой/временем/таймзоной |
| 5 | **Polling → Webhook** | Сначала `polling` для локальной разработки, затем `webhook` для продакшена |
| 6 | **README для пользователя** | Шаги: получить Bot Token, ChatID, установить зависимости, запустить |

---

## 2. Архитектурные решения

### 2.1 Speech-to-Text: OpenAI Whisper (локально)

```
pip install openai-whisper ffmpeg-python
```

**Почему Whisper?**
- Полностью бесплатный и open-source (MIT License)
- Работает офлайн — никаких API-ключей и ограничений
- Качество распознавания на уровне коммерческих решений
- Поддерживает русский язык из коробки
- Модели: `tiny` (быстро) → `base` → `small` → `medium` (качественно)

**Поток обработки голоса:**
```
Telegram OGG/OPUS → ffmpeg конвертация → WAV/MP3 → Whisper → текст
```

**Рекомендуемая модель:** `small` (244MB, хороший баланс скорость/качество для RU)

### 2.2 Извлечение даты и времени

```
pip install dateparser pytz
```

**Поддерживаемые форматы фраз (RU):**
- Абсолютные: `"15 июня в 14:30"`, `"завтра в 9 утра"`, `"в пятницу в 18:00"`
- Относительные: `"через 2 часа"`, `"через 30 минут"`, `"послезавтра"`
- Смешанные: `"напомни мне завтра в полдень"`

**Fallback:** если дата не распознана → бот просит уточнить

### 2.3 Стек технологий

```
python-telegram-bot[job-queue]  # v20+ (async, встроенный scheduler)
openai-whisper                  # локальный STT
ffmpeg-python                   # конвертация аудио
dateparser                      # разбор дат на RU/EN
pytz                            # временные зоны
SQLite3 (stdlib)                # хранение напоминаний и настроек
python-dotenv                   # .env для токенов
```

### 2.4 Структура проекта

```
telegram-reminder-bot/
├── bot/
│   ├── __init__.py
│   ├── main.py              # точка входа (polling / webhook)
│   ├── handlers/
│   │   ├── voice.py         # обработка голоса → STT → напоминание
│   │   ├── text.py          # текстовые команды (/remind, /list, /cancel)
│   │   └── settings.py      # /timezone, /start, /help
│   ├── services/
│   │   ├── stt.py           # Whisper wrapper
│   │   ├── parser.py        # dateparser + извлечение datetime
│   │   └── scheduler.py     # APScheduler / job-queue
│   └── db/
│       ├── models.py        # SQLite схема
│       └── repository.py    # CRUD для напоминаний
├── .env.example
├── requirements.txt
├── README.md
└── PROMPT_ROADMAP.md        # этот файл
```

---

## 3. RoadMap — Фазы выполнения

### Фаза 1: Базовый бот (Polling)
- [ ] Инициализация проекта, `requirements.txt`, `.env.example`
- [ ] SQLite схема: `users(chat_id, timezone)`, `reminders(id, chat_id, text, remind_at, created_at, sent)`
- [ ] `/start`, `/help`, `/timezone <tz>` команды
- [ ] Текстовые напоминания: `/remind 15 июня в 14:30 — позвонить врачу`
- [ ] Планировщик (job-queue из `python-telegram-bot`)
- [ ] Подтверждение: `"Напоминание установлено на 15 июня 2026, 14:30 (Europe/Moscow)"`

### Фаза 2: Голосовые сообщения
- [ ] Скачивание `.ogg` из Telegram
- [ ] Конвертация через `ffmpeg` → `.wav`
- [ ] Транскрипция Whisper (модель `small`)
- [ ] Извлечение datetime через `dateparser`
- [ ] Подтверждение с расшифровкой: `"Распознано: «напомни завтра в 9 утра позвонить маме» → 3 июня 2026, 09:00 (Europe/Moscow)"`
- [ ] Обработка ошибок: не распознана дата → запрос уточнения

### Фаза 3: Webhook + деплой
- [ ] Конфигурация webhook-режима (переключение через `.env`)
- [ ] Nginx/Caddy конфигурация (пример в README)
- [ ] Деплой на VPS (systemd service файл)
- [ ] Переменная `WEBHOOK_URL` в `.env`

### Фаза 4: README для пользователя
- [ ] Как создать бота через `@BotFather` (Bot Token)
- [ ] Как получить `CHAT_ID` через `@userinfobot`
- [ ] Установка зависимостей (Python, ffmpeg, pip install)
- [ ] Запуск в режиме polling
- [ ] Переключение на webhook
- [ ] Настройка временной зоны через команду `/timezone`

---

## 4. Cursor Tooling Plan

### 4.1 Rules (создать через `/create-rule`)

#### `python-bot-standards.mdc` — всегда применяется к `**/*.py`
```
Стандарты Python для telegram-bot проекта:
- Использовать async/await (python-telegram-bot v20+)
- Логировать через logging, не print
- Все секреты только через os.getenv() / python-dotenv
- SQLite транзакции через context manager (with conn:)
- Обрабатывать Telegram API ошибки через try/except TelegramError
```

#### `whisper-usage.mdc` — применяется к `bot/services/stt.py`
```
Правила работы с Whisper:
- Загружать модель один раз при старте (кэш в памяти)
- Использовать модель 'small' по умолчанию, переопределяемую через .env
- Всегда удалять временные аудиофайлы после транскрипции
- Логировать время транскрипции для мониторинга производительности
```

#### `dateparser-rules.mdc` — применяется к `bot/services/parser.py`
```
Правила извлечения дат:
- Всегда передавать PREFER_DAY_OF_MONTH='first' и локаль 'ru'
- Если datetime в прошлом — сообщить пользователю и запросить уточнение
- Хранить всё в UTC, конвертировать в timezone пользователя только для отображения
```

---

### 4.2 Skills (создать через `/create-skill`)

#### `.cursor/skills/whisper-stt/SKILL.md`
**Назначение:** Знание о том, как транскрибировать аудио через локальный Whisper.  
**Триггеры:** "транскрипция", "whisper", "голосовое сообщение", "speech to text", "STT"  
**Ключевые шаги в skill:**
1. Скачать `voice.file_id` → `ogg` файл через `context.bot.get_file()`
2. Конвертировать `ffmpeg -i input.ogg output.wav`
3. `result = model.transcribe("output.wav", language="ru")`
4. Вернуть `result["text"]`
5. Удалить временные файлы

#### `.cursor/skills/reminder-parser/SKILL.md`
**Назначение:** Извлечение datetime из произвольного русского текста.  
**Триггеры:** "дата", "время", "напомни", "dateparser", "reminder", "извлечь дату"  
**Ключевые шаги в skill:**
1. `import dateparser` с настройками `PREFER_DATES_FROM='future'`, `RETURN_AS_TIMEZONE_AWARE=True`
2. Передать `languages=['ru', 'en']`
3. Нормализовать к UTC для хранения в БД
4. Конвертировать в timezone пользователя для отображения
5. Fallback: если `None` → попросить уточнить формат

#### `.cursor/skills/telegram-webhook-switch/SKILL.md`
**Назначение:** Переключение бота между polling и webhook режимами.  
**Триггеры:** "webhook", "деплой", "polling", "webhook mode", "продакшен"  
**Ключевые шаги в skill:**
1. Читать `BOT_MODE` из `.env` (`polling` / `webhook`)
2. Для webhook: установить `WEBHOOK_URL`, `WEBHOOK_PORT`, SSL сертификат
3. Использовать `application.run_webhook()` или `application.run_polling()`
4. Добавить healthcheck endpoint для мониторинга

---

### 4.3 Hooks (создать через `/create-hook`)

#### Hook 1: `afterFileEdit` — авто-проверка `.env.example`
**Событие:** `afterFileEdit`  
**Триггер:** изменение `bot/**/*.py`  
**Действие:** проверить, что все новые `os.getenv("...")` вызовы присутствуют в `.env.example`  
**Реализация:** `prompt` hook — "Проверь, что все os.getenv() переменные из изменённого файла задокументированы в .env.example"

#### Hook 2: `beforeShellExecution` — защита от случайного `rm -rf`
**Событие:** `beforeShellExecution`  
**Matcher:** `rm -rf|rmdir /s`  
**Действие:** запросить подтверждение пользователя  
**failClosed:** `true`

#### Hook 3: `postToolUse` — автоматический `requirements.txt`
**Событие:** `postToolUse` (после Write/StrReplace в `requirements.txt`)  
**Действие:** напомнить агенту выполнить `pip install -r requirements.txt` если файл изменён  
**Реализация:** `prompt` hook

#### Hook 4: `subagentStop` — chain субагентов
**Событие:** `subagentStop`  
**Действие:** после завершения субагента STT → автоматически запускать субагент parser  
**Matcher:** субагент типа `shell`

---

### 4.4 Subagents (использовать Task tool с `/create-subagent`)

| Субагент | Тип | Задача |
|---------|-----|--------|
| `bot-scaffolding` | `shell` | Создать структуру папок, `requirements.txt`, `.env.example`, `main.py` |
| `whisper-integrator` | `generalPurpose` | Написать `bot/services/stt.py` с Whisper wrapper |
| `datetime-parser` | `generalPurpose` | Написать `bot/services/parser.py` с dateparser + timezone |
| `db-setup` | `shell` | Создать SQLite схему и `repository.py` |
| `handlers-writer` | `generalPurpose` | Написать все Telegram handlers (voice, text, settings) |
| `webhook-switch` | `generalPurpose` | Добавить webhook режим в `main.py` с переключением через .env |
| `readme-writer` | `generalPurpose` | Написать полный `README.md` для пользователя |
| `integration-tester` | `shell` | Запустить бота в polling режиме и проверить базовые сценарии |

---

## 5. Prompt для первого субагента (bot-scaffolding)

```
Создай структуру проекта telegram-reminder-bot в папке telegram-reminder-bot/.

Требования:
1. Создай директории: bot/, bot/handlers/, bot/services/, bot/db/
2. Создай requirements.txt со следующими пакетами (укажи последние стабильные версии):
   - python-telegram-bot[job-queue]
   - openai-whisper
   - ffmpeg-python
   - dateparser
   - pytz
   - python-dotenv
3. Создай .env.example с переменными:
   BOT_TOKEN=your_bot_token_here
   CHAT_ID=your_chat_id_here
   BOT_MODE=polling
   WEBHOOK_URL=https://yourdomain.com/webhook
   WEBHOOK_PORT=8443
   WHISPER_MODEL=small
   DEFAULT_TIMEZONE=Europe/Moscow
4. Создай пустые __init__.py во всех модулях
5. Создай main.py с базовым каркасом, читающим BOT_MODE из .env
   и запускающим либо polling, либо webhook
```

---

## 6. Пример ответного сообщения бота пользователю

```
✅ Напоминание установлено!

📝 Текст: позвонить врачу
📅 Дата: 15 июня 2026 (понедельник)
🕐 Время: 14:30
🌍 Часовой пояс: Europe/Moscow (UTC+3)

⏳ Осталось: 12 часов 45 минут

Используй /list чтобы посмотреть все напоминания
Используй /cancel <id> чтобы отменить напоминание
```

---

## 7. README — ключевые шаги для пользователя

### Шаг 1: Создать бота в Telegram
1. Открыть `@BotFather` в Telegram
2. Отправить `/newbot`
3. Придумать имя и username (например `MyReminderBot`)
4. Скопировать **Bot Token** → вставить в `.env` как `BOT_TOKEN`

### Шаг 2: Получить свой Chat ID
1. Открыть `@userinfobot` в Telegram
2. Отправить `/start`
3. Скопировать **Id** → вставить в `.env` как `CHAT_ID`

### Шаг 3: Установить зависимости
```bash
# Установить Python 3.11+
# Установить ffmpeg (обязательно для Whisper):
# Windows: winget install ffmpeg
# macOS:   brew install ffmpeg
# Linux:   apt install ffmpeg

pip install -r requirements.txt
```

### Шаг 4: Настроить временную зону
Отправить боту команду после запуска:
```
/timezone Europe/Moscow
```
Список зон: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones

### Шаг 5: Запустить в режиме polling (локально)
```bash
cp .env.example .env
# Заполнить .env значениями
python bot/main.py
```

### Шаг 6 (опционально): Деплой с webhook
```bash
# В .env установить:
BOT_MODE=webhook
WEBHOOK_URL=https://yourdomain.com/webhook

# На сервере с SSL (nginx + certbot):
python bot/main.py
```

---

## 8. Связь всех инструментов в одном RoadMap

```
┌─────────────────────────────────────────────────────────┐
│                   CURSOR TOOLING MAP                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  RULES (всегда активны)                                 │
│  ├── python-bot-standards.mdc  → все *.py файлы         │
│  ├── whisper-usage.mdc         → stt.py                 │
│  └── dateparser-rules.mdc      → parser.py              │
│                                                         │
│  SKILLS (вызываются по запросу агента)                  │
│  ├── whisper-stt/SKILL.md      → Фаза 2                 │
│  ├── reminder-parser/SKILL.md  → Фазы 1, 2              │
│  └── telegram-webhook/SKILL.md → Фаза 3                 │
│                                                         │
│  HOOKS (автоматически при событиях)                     │
│  ├── afterFileEdit → проверка .env.example              │
│  ├── beforeShell  → защита от rm -rf                    │
│  ├── postToolUse  → напоминание pip install             │
│  └── subagentStop → chain STT → Parser субагентов       │
│                                                         │
│  SUBAGENTS (Task tool, последовательно/параллельно)     │
│  Фаза 1: bot-scaffolding → db-setup → handlers-writer   │
│  Фаза 2: whisper-integrator → datetime-parser           │
│  Фаза 3: webhook-switch                                 │
│  Фаза 4: readme-writer → integration-tester             │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 9. Команды для запуска в Cursor

```
# Шаг 1: Создать rules
/create-rule python-bot-standards    → alwaysApply: false, globs: **/*.py
/create-rule whisper-usage           → globs: bot/services/stt.py
/create-rule dateparser-rules        → globs: bot/services/parser.py

# Шаг 2: Создать skills
/create-skill whisper-stt            → .cursor/skills/whisper-stt/SKILL.md
/create-skill reminder-parser        → .cursor/skills/reminder-parser/SKILL.md
/create-skill telegram-webhook-switch → .cursor/skills/telegram-webhook-switch/SKILL.md

# Шаг 3: Создать hooks
/create-hook env-checker             → afterFileEdit, prompt hook
/create-hook shell-guard             → beforeShellExecution, failClosed: true
/create-hook pip-reminder            → postToolUse на requirements.txt
/create-hook subagent-chain          → subagentStop, chain STT→Parser

# Шаг 4: Запустить первый субагент
# В чате Cursor написать:
"Используй субагент bot-scaffolding для создания структуры проекта
согласно PROMPT_ROADMAP.md секция 5"
```

---

*Файл создан: 2 июня 2026*  
*Следующий шаг: выполнить команды из раздела 9 последовательно*

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Allow running as `python bot/main.py` from the project root
_project_root = Path(__file__).parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from telegram.ext import Application, CommandHandler, MessageHandler, filters

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def _post_init(app: Application) -> None:
    """Runs after the bot connects — restore all pending reminders from DB."""
    from bot.services.scheduler import restore_pending_reminders
    count = await restore_pending_reminders(app)
    if count:
        logger.info("Restored %d reminder job(s) from database", count)


def build_app() -> Application:
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise ValueError("BOT_TOKEN is not set in .env")

    app = (
        Application.builder()
        .token(token)
        .post_init(_post_init)
        .build()
    )

    from bot.handlers.settings import start_handler, help_handler, timezone_handler
    from bot.handlers.text import remind_handler, list_handler, cancel_handler
    from bot.handlers.voice import voice_handler

    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("help", help_handler))
    app.add_handler(CommandHandler("timezone", timezone_handler))
    app.add_handler(CommandHandler("remind", remind_handler))
    app.add_handler(CommandHandler("list", list_handler))
    app.add_handler(CommandHandler("cancel", cancel_handler))
    app.add_handler(MessageHandler(filters.VOICE, voice_handler))

    return app


def main():
    from bot.db.models import init_db
    init_db()

    app = build_app()
    mode = os.getenv("BOT_MODE", "polling").lower()

    if mode == "polling":
        logger.info("Starting bot in POLLING mode")
        app.run_polling(drop_pending_updates=True)
    elif mode == "webhook":
        webhook_url = os.getenv("WEBHOOK_URL")
        port = int(os.getenv("WEBHOOK_PORT", "8443"))
        if not webhook_url:
            raise ValueError("WEBHOOK_URL is not set in .env")
        logger.info("Starting bot in WEBHOOK mode: %s", webhook_url)
        app.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path="/webhook",
            webhook_url=webhook_url,
        )
    else:
        raise ValueError(f"Unknown BOT_MODE: {mode!r}. Use 'polling' or 'webhook'.")


if __name__ == "__main__":
    main()

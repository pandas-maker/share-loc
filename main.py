import os
import logging
import secrets
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from telegram import BotCommand
from src.config import BOT_TOKEN
from src.handlers import (
    start, handle_callback, handle_location,
    handle_recipient_input, handle_cancel
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def post_init(app):
    """Runs after the application is initialized — set commands and register webhook."""
    commands = [
        BotCommand("start", "Start the bot"),
        BotCommand("cancel", "Cancel operation"),
    ]
    await app.bot.set_my_commands(commands)

    WEBHOOK_URL = os.environ.get('WEBHOOK_URL')
    SECRET_TOKEN = os.environ.get('WEBHOOK_SECRET_TOKEN')

    if WEBHOOK_URL:
        webhook_base = WEBHOOK_URL.rstrip('/')
        webhook_url = f"{webhook_base}/webhook"

        # Always delete any old webhook first, then re-register cleanly
        await app.bot.delete_webhook(drop_pending_updates=True)
        await app.bot.set_webhook(
            url=webhook_url,
            secret_token=SECRET_TOKEN,
            drop_pending_updates=True,
            allowed_updates=["message", "callback_query"]
        )
        logger.info(f"✅ Webhook registered: {webhook_url}")
    else:
        # In polling mode, make sure no stale webhook is set
        await app.bot.delete_webhook(drop_pending_updates=True)
        logger.info("✅ Webhook cleared for polling mode")


def main():
    PORT = int(os.environ.get('PORT', 8080))
    WEBHOOK_URL = os.environ.get('WEBHOOK_URL')
    SECRET_TOKEN = os.environ.get('WEBHOOK_SECRET_TOKEN')

    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN not set!")
        return

    # Pass post_init into the builder — this is the correct v20+ way
    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    # Register handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cancel", handle_cancel))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.LOCATION, handle_location))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_recipient_input))

    if WEBHOOK_URL:
        webhook_base = WEBHOOK_URL.rstrip('/')
        webhook_url = f"{webhook_base}/webhook"

        if not SECRET_TOKEN:
            SECRET_TOKEN = secrets.token_hex(16)
            logger.warning("⚠️  WEBHOOK_SECRET_TOKEN not set. Generated one for this session.")
            logger.warning(f"🔒 Secret Token: {SECRET_TOKEN}")

        logger.info(f"🚀 Starting bot in WEBHOOK mode on port {PORT}")
        logger.info(f"🔗 Webhook URL: {webhook_url}")

        app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            webhook_url=webhook_url,
            secret_token=SECRET_TOKEN,
            # Render needs a health-check route — this keeps the web process alive
            # and responds 200 OK to GET /
            drop_pending_updates=True,
        )
    else:
        logger.info("🚀 Starting bot in POLLING mode (local development)")
        app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()

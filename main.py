import os
import asyncio
import logging
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

async def set_commands(app):
    commands = [
        BotCommand("start", "Start the bot"),
        BotCommand("cancel", "Cancel operation"),
    ]
    await app.bot.set_my_commands(commands)

def main():
    PORT = int(os.environ.get('PORT', 8080))
    WEBHOOK_URL = os.environ.get('WEBHOOK_URL')
    
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN not set!")
        return
    
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cancel", handle_cancel))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.LOCATION, handle_location))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_recipient_input))
    
    app.post_init = set_commands
    
    if WEBHOOK_URL:
        logger.info(f"🚀 Starting bot in WEBHOOK mode on port {PORT}")
        logger.info(f"🔗 Webhook URL: {WEBHOOK_URL}/webhook")
        
        # This works across Python versions
        app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            webhook_url=f"{WEBHOOK_URL}/webhook",
            drop_pending_updates=True
        )
    else:
        logger.info("🚀 Starting bot in POLLING mode (local development)")
        app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
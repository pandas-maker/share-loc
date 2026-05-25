import os
import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from telegram import BotCommand
from src.config import BOT_TOKEN, WEBHOOK_URL, PORT
from src.handlers import (
    start, handle_callback, handle_location, 
    handle_recipient_input, handle_cancel
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def set_commands(application):
    commands = [
        BotCommand("start", "🔄 Start the bot"),
        BotCommand("cancel", "❌ Cancel operation"),
    ]
    await application.bot.set_my_commands(commands)

async def main():
    # Render automatically provides PORT
    PORT = int(os.environ.get('PORT', 10000))
    WEBHOOK_URL = os.environ.get('WEBHOOK_URL')
    
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN not set!")
        return
    
    # Create application with token
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cancel", handle_cancel))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.LOCATION, handle_location))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_recipient_input))
    
    app.post_init = set_commands
    
    # On Render, ALWAYS use webhook
    if WEBHOOK_URL:
        logger.info(f"🚀 Starting bot in WEBHOOK mode on port {PORT}")
        logger.info(f"🔗 Webhook URL: {WEBHOOK_URL}/webhook")
        
        # Set webhook before starting
        await set_webhook(app)
        
        # Start webhook server
        app.run_webhook(
            listen="0.0.0.0",  # Must be 0.0.0.0 for Render
            port=PORT,
            webhook_url=f"{WEBHOOK_URL}/webhook",
            drop_pending_updates=True
        )
    else:
        logger.error("❌ WEBHOOK_URL not set! Required for Render deployment.")
        logger.info("? Set WEBHOOK_URL to your Render app URL")

async def set_webhook(application):
    """Set webhook for the bot"""
    webhook_url = os.environ.get('WEBHOOK_URL')
    if webhook_url:
        webhook_url = f"{webhook_url}/webhook"
        await application.bot.set_webhook(webhook_url)
        logger.info(f"✅ Webhook set to: {webhook_url}")
    else:
        logger.error("❌ WEBHOOK_URL not set! Required for webhook deployment.")

async def main_async():
    # Render automatically provides PORT
    PORT = int(os.environ.get('PORT', 10000))
    WEBHOOK_URL = os.environ.get('WEBHOOK_URL')
    
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN not set!")
        return
    
    # Create application with token
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cancel", handle_cancel))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.LOCATION, handle_location))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_recipient_input))
    
    app.post_init = set_commands
    
    # On Render, ALWAYS use webhook
    if WEBHOOK_URL:
        logger.info(f"🚀 Starting bot in WEBHOOK mode on port {PORT}")
        logger.info(f"🔗 Webhook URL: {WEBHOOK_URL}/webhook")
        
        # Set webhook before starting
        await set_webhook(app)
        
        # Start webhook server
        app.run_webhook(
            listen="0.0.0.0",  # Must be 0.0.0.0 for Render
            port=PORT,
            webhook_url=f"{WEBHOOK_URL}/webhook",
            drop_pending_updates=True
        )
    else:
        logger.error("❌ WEBHOOK_URL not set! Required for Render deployment.")
        logger.info("? Set WEBHOOK_URL to your Render app URL")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main_async())

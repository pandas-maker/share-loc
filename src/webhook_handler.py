from telegram.ext import Application
from telegram import Update
from src.handlers import start, handle_callback, handle_location, handle_recipient_input, handle_cancel

async def webhook_endpoint(update: Update, context: Application):
    """Main webhook endpoint handler"""
    # Dispatch the update to the appropriate handler
    await context.application.process_update(update)
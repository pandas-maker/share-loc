from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from telegram import BotCommand
from src.config import BOT_TOKEN
from src.handlers import (
    start, handle_callback, handle_location, 
    handle_cancel, handle_directions_request
)

async def set_commands(application):
    """Set bot commands menu"""
    commands = [
        BotCommand("start", "🔄 Start/Restart the bot"),
        BotCommand("cancel", "❌ Cancel current operation"),
    ]
    await application.bot.set_my_commands(commands)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cancel", handle_cancel))
    app.add_handler(CallbackQueryHandler(handle_callback))
    
    # Location handlers
    app.add_handler(MessageHandler(filters.LOCATION, handle_location))
    app.add_handler(MessageHandler(filters.Regex("Get Directions"), handle_directions_request))
    
    # Set commands
    app.post_init = set_commands
    
    print("✅ Location Request Bot is running...")
    print("Features: Link generation, auto directions, distance calculation")
    app.run_polling()

if __name__ == "__main__":
    main()
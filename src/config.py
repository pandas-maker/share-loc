import os
from dotenv import load_dotenv
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
PORT = int(os.environ.get('PORT', 8080))

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found in env file")

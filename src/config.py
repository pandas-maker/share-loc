import os
from dotenv import load_dotenv
load_dotenv()
BOT_TOKEN = os.getenv("Bot_Token")
if not BOT_TOKEN:
    raise ValueError("no bot tokem is found is the env file")

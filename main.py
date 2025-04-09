import logging
import os
from pyrogram import Client
from dotenv import load_dotenv
from app.commands import *

logging.basicConfig(level=logging.INFO)
load_dotenv()

app = Client(
    "Hinglish_Subtitle_Bot",
    bot_token=os.getenv('BOT_TOKEN'),
    api_id=os.getenv('API_ID'),
    api_hash=os.getenv('API_HASH')
)

if __name__ == "__main__":
    app.run()

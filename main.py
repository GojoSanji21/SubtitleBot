import logging
import os
from pyrogram import Client, filters
from dotenv import load_dotenv

# Load environment variables from .env or Koyeb config
load_dotenv()

# Logging config
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot credentials
api_id = int(os.getenv("API_ID", 0))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")

if not all([api_id, api_hash, bot_token]):
    raise Exception("Missing API_ID, API_HASH, or BOT_TOKEN in environment variables")

# Initialize Pyrogram app
app = Client(
    "SubtitleBot",
    api_id=api_id,
    api_hash=api_hash,
    bot_token=bot_token
)

# Import all command handlers (registers them on import)
from app.commands import *

# Confirm bot is live
@app.on_message(filters.command("help") & filters.private)
async def help_cmd(client, message):
    await message.reply(
        "Available Commands:\n"
        "/start - Start the bot\n"
        "/settings - Your current settings\n"
        "/translate <lang> - Translate a subtitle file\n"
        "/history - View translation history\n"
        "/clearhistory - Clear history\n"
        "/feedback <text> - Send feedback\n"
        "/allow <user_id> - (Owner only) Allow user\n"
        "/deny <user_id> - (Owner only) Deny user"
    )

@app.on_message()
async def debug_log(client, message):
    print(f"Received a message from {message.from_user.id}: {message.text}")

if __name__ == "__main__":
    print("Bot is starting...")
    app.run()
    print("Bot is running.")
    

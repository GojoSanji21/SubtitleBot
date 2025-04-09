import logging
import os
from pyrogram import Client, filters
from dotenv import load_dotenv
from flask import Flask
import threading
import pyromod.listen
from app.database import update_user_info

# Load env variables
load_dotenv()

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot credentials
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")
owner_id = int(os.getenv("OWNER_ID"))

if not all([api_id, api_hash, bot_token]):
    raise Exception("Missing API_ID, API_HASH, or BOT_TOKEN in environment variables")

# ✅ Initialize with plugins
app = Client(
    "SubtitleBot",
    api_id=api_id,
    api_hash=api_hash,
    bot_token=bot_token,
    plugins=dict(root="app")
)

# Help command
@app.on_message(filters.command("help") & filters.private)
async def help_cmd(client, message):
    await message.reply(
        "Available Commands:\n"
        "/start - Start the bot\n"
        "/settings - Your current settings\n"
        "/translate - Translate subtitle\n"
        "/feedback - Give feedback\n"
        "/clearhistory - Clear history\n"
        "/allow <user_id> - (Owner only)\n"
        "/deny <user_id> - (Owner only)"
    )

# Allow command
@app.on_message(filters.command("allow") & filters.user(owner_id))
async def allow_user(client, message):
    if len(message.command) < 2:
        return await message.reply("Please provide a user ID.")
    user_id = int(message.command[1])
    update_user_info(user_id, {"allowed": True})
    await message.reply(f"User {user_id} has been allowed.")

@app.on_message(filters.command("deny") & filters.user(owner_id))
async def deny_user(client, message):
    if len(message.command) < 2:
        return await message.reply("Please provide a user ID.")
    user_id = int(message.command[1])
    update_user_info(user_id, {"allowed": False})
    await message.reply(f"User {user_id} has been denied.")

# Debug logger
@app.on_message()
async def debug_log(client, message):
    print(f">>> Bot received a message\nFrom: {message.from_user.id}, Text: {message.text}")

# Flask for Koyeb health checks
flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "Bot is alive!"

def run_web():
    port = int(os.environ.get("PORT", 5000))
    flask_app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    threading.Thread(target=run_web).start()
    print("Bot is starting...")
    app.run()

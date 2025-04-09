import logging
import os
import threading
from dotenv import load_dotenv
from flask import Flask
from pyrogram import Client, filters
import pyromod.listen  # needed for pyromod integration

from app.database import update_user_info

# Load environment variables
load_dotenv()

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot credentials
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH"))
bot_token = os.getenv("BOT_TOKEN")
owner_id = int(os.getenv("OWNER_ID"))

if not all([api_id, api_hash, bot_token]):
    raise Exception("Missing API_ID, API_HASH, or BOT_TOKEN in environment variables")

# Initialize the Pyrogram Client with plugin loading
app = Client(
    "SubtitleBot",
    api_id=api_id,
    api_hash=api_hash,
    bot_token=bot_token,
    plugins=dict(root="app")
)

# Optional Flask server to keep Koyeb instance alive
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
    print("Bot is running.")

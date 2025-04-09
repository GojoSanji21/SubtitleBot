import logging
import os
from pyrogram import Client
from app.commands import start, settings, translate, feedback, history

logging.basicConfig(level=logging.INFO)

# Initialize the bot client
app = Client(
    "SubtitleBot", 
    bot_token=os.getenv('BOT_TOKEN'),
    api_id=os.getenv('API_ID'),
    api_hash=os.getenv('API_HASH')
)

# Register command handlers
app.add_handler(start)
app.add_handler(settings)
app.add_handler(translate)
app.add_handler(feedback)
app.add_handler(history)

# Run the bot
if __name__ == "__main__":
    app.run()

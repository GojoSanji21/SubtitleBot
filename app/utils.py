import logging
from pyrogram import Client
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# This function will send logs to the log channel
async def log_error(client: Client, message: str):
    log_channel_id = os.getenv('LOG_CHANNEL_ID')  # Get channel ID from environment variables
    try:
        # Send the log message to the channel
        await client.send_message(log_channel_id, message)
    except Exception as e:
        logger.error(f"Failed to send log message to the channel: {e}")

async def send_preview(client, user_id, file):
    await client.send_document(user_id, file)

async def send_notification(client, user_id, message):
    await client.send_message(user_id, message)

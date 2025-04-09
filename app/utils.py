import logging
from pyrogram import Client
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def log_error(client: Client, message: str):
    log_channel_id = os.getenv('LOG_CHANNEL_ID')
    try:
        if log_channel_id:
            await client.send_message(log_channel_id, message)
        else:
            logger.error(f"Log channel not set: {message}")
    except Exception as e:
        logger.error(f"Failed to send log message to the channel: {e}")
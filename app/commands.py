# app/commands.py
import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.settings import save_user_settings, load_user_settings
from app.database import get_user_info, update_user_info
from app.translate import translate_subtitles
from app.utils import log_error

# Access control decorator: Only allow the bot owner or allowed users.
def restricted_access(func):
    async def wrapper(client, message, *args, **kwargs):
        owner_id = int(os.getenv("OWNER_ID", "8160777407"))
        user_id = message.from_user.id
        if user_id == owner_id:
            return await func(client, message, *args, **kwargs)
        try:
            user_info = load_user_settings(user_id)
        except Exception as e:
            await log_error(client, f"Error loading settings for user {user_id}: {e}")
            await message.reply("There was an error loading your settings. Please try again later.")
            return

        if not user_info.get("allowed", False):
            await message.reply("You are not authorized to use this bot. Please contact the owner.")
            return
        return await func(client, message, *args, **kwargs)
    return wrapper

@Client.on_message(filters.command("start"))
@restricted_access
async def start(client, message):
    try:
        user_id = message.from_user.id
        user_info = get_user_info(user_id)
        if not user_info:
            # Initialize user settings with defaults (not allowed by default)
            update_user_info(user_id, {
                "engine": "gemini", 
                "target_language": "en", 
                "batch_size": 20, 
                "allowed": False,
                "translation_history": []
            })
        await message.reply("Welcome to Subtitle Translation Bot!")
        await log_error(client, f"User {user_id} started the bot.")
    except Exception as e:
        await log_error(client, f"Error in /start for user {message.from_user.id}: {e}")
        await message.reply("An error occurred during startup. Please try again later.")

@Client.on_message(filters.command("settings"))
@restricted_access
async def settings(client, message):
    try:
        user_id = message.from_user.id
        user_info = load_user_settings(user_id)
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Change Language", callback_data="change_language"),
             InlineKeyboardButton("Change Engine", callback_data="change_engine")],
            [InlineKeyboardButton("Change Batch Size", callback_data="change_batch_size")]
        ])
        settings_text = (
            f"Your current settings:\n"
            f"Engine: {user_info.get('engine', 'gemini')}\n"
            f"Target Language: {user_info.get('target_language', 'en')}\n"
            f"Batch Size: {user_info.get('batch_size', 20)}"
        )
        await message.reply(settings_text, reply_markup=keyboard)
    except Exception as e:
        await log_error(client, f"Error in /settings for user {message.from_user.id}: {e}")
        await message.reply("Failed to retrieve settings. Please try again later.")

@Client.on_message(filters.command("translate"))
@restricted_access
async def translate(client, message):
    try:
        user_id = message.from_user.id
        document = message.document
        args = message.text.split()
        target_language = args[1] if len(args) > 1 else None
        user_info = load_user_settings(user_id)

        if not document:
            await message.reply("Please upload a subtitle file (.srt, .vtt, .ass).")
            return
        
        translated_file = await translate_subtitles(
            document,
            user_info.get("engine", "gemini"),
            user_info.get("batch_size", 20),
            target_language or user_info.get("target_language", "en")
        )
        await message.reply_document(translated_file)
    except Exception as e:
        await log_error(client, f"Error in /translate for user {message.from_user.id}: {e}")
        await message.reply("Translation failed. Please check your file and try again.")

@Client.on_message(filters.command("feedback"))
@restricted_access
async def feedback(client, message):
    try:
        args = message.text.split(" ", 1)
        if len(args) < 2:
            await message.reply("Please provide your feedback.")
        else:
            # Optionally, process or store the feedback.
            await message.reply("Thank you for your feedback!")
    except Exception as e:
        await log_error(client, f"Error in /feedback: {e}")
        await message.reply("Failed to record feedback.")

@Client.on_message(filters.command("history"))
@restricted_access
async def history(client, message):
    try:
        user_id = message.from_user.id
        user_info = load_user_settings(user_id)
        history_list = user_info.get("translation_history", [])
        if history_list:
            await message.reply("Your previous translations: " + ", ".join(history_list))
        else:
            await message.reply("No translation history found.")
    except Exception as e:
        await log_error(client, f"Error in /history: {e}")
        await message.reply("Failed to retrieve translation history.")

# Owner-only command decorator
def owner_only(func):
    async def wrapper(client, message, *args, **kwargs):
        owner_id = int(os.getenv("OWNER_ID", "8160777407"))
        if message.from_user.id != owner_id:
            await message.reply("This command is restricted to the bot owner.")
            return
        return await func(client, message, *args, **kwargs)
    return wrapper

@Client.on_message(filters.command("allow"))
@owner_only
async def allow_user(client, message):
    try:
        args = message.text.split()
        if len(args) < 2:
            await message.reply("Usage: /allow <user_id>")
            return
        user_id = int(args[1])
        save_user_settings(user_id, allowed=True)
        await message.reply(f"User {user_id} is now allowed to use the bot.")
    except Exception as e:
        await log_error(client, f"Error in /allow: {e}")
        await message.reply("Failed to allow user.")

@Client.on_message(filters.command("deny"))
@owner_only
async def deny_user(client, message):
    try:
        args = message.text.split()
        if len(args) < 2:
            await message.reply("Usage: /deny <user_id>")
            return
        user_id = int(args[1])
        save_user_settings(user_id, allowed=False)
        await message.reply(f"User {user_id} is now denied access to the bot.")
    except Exception as e:
        await log_error(client, f"Error in /deny: {e}")
        await message.reply("Failed to deny user.")
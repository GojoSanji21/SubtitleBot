from pyrogram import filters
from main import app
from app.database import update_user_info, get_user_info
from app.translate import translate_subtitles
from app.settings import load_user_settings

@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    user_id = message.from_user.id
    user = get_user_info(user_id)
    if not user:
        update_user_info(user_id, {"allowed": False})
    if not user or not user.get("allowed", False):
        return await message.reply("You are not allowed to use this bot.")
    await message.reply("Welcome to Subtitle Translator Bot! Send /help to see available commands.")

@app.on_message(filters.command("settings") & filters.private)
async def settings_cmd(client, message):
    user_id = message.from_user.id
    user = get_user_info(user_id)
    if not user or not user.get("allowed", False):
        return await message.reply("You are not allowed to use this bot.")
    settings = load_user_settings(user_id)
    await message.reply(f"Your settings:\nLanguage: {settings.get('language', 'en')}\nEngine: {settings.get('engine', 'gpt')}\nBatch size: {settings.get('batch_size', 20)}")

@app.on_message(filters.command("translate") & filters.private)
async def translate_cmd(client, message):
    user_id = message.from_user.id
    user = get_user_info(user_id)
    if not user or not user.get("allowed", False):
        return await message.reply("You are not allowed to use this bot.")
    await message.reply("Please upload your subtitle file for translation.")

@app.on_message(filters.command("feedback") & filters.private)
async def feedback_cmd(client, message):
    user_id = message.from_user.id
    user = get_user_info(user_id)
    if not user or not user.get("allowed", False):
        return await message.reply("You are not allowed to use this bot.")
    feedback_text = " ".join(message.command[1:])
    if not feedback_text:
        return await message.reply("Please provide some feedback after the command.")
    await message.reply("Thanks for your feedback!")

@app.on_message(filters.command("clearhistory") & filters.private)
async def clear_history_cmd(client, message):
    user_id = message.from_user.id
    user = get_user_info(user_id)
    if not user or not user.get("allowed", False):
        return await message.reply("You are not allowed to use this bot.")
    update_user_info(user_id, {"history": []})
    await message.reply("Your translation history has been cleared.")

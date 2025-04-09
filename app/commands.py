from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.settings import save_user_settings
from app.database import get_user_info
from app.translate import translate_subtitles
from app.utils import log_error

@Client.on_message(filters.command("start"))
async def start(client, message):
    try:
        user = message.from_user.id
        user_info = get_user_info(user)
        
        if not user_info:
            update_user_info(user, default_language="en", default_translation_engine="gemini", batch_size=20)

        await message.reply("Welcome to Subtitle Translation Bot!")
        await log_error(client, f"New user started the bot: {message.from_user.id}")
    except Exception as e:
        await log_error(client, f"Error in /start command for user {message.from_user.id}: {str(e)}")

@Client.on_message(filters.command("settings"))
async def settings(client, message):
    user = message.from_user.id
    user_info = get_user_info(user)
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Change Language", callback_data="change_language"),
         InlineKeyboardButton("Change Engine", callback_data="change_engine")],
        [InlineKeyboardButton("Change Batch Size", callback_data="change_batch_size")]
    ])
    
    await message.reply("Here are your current settings", reply_markup=keyboard)

@Client.on_message(filters.command("translate"))
async def translate(client, message):
    user = message.from_user.id
    file = message.document
    language = message.text.split(" ")[1] if len(message.text.split(" ")) > 1 else None
    user_info = get_user_info(user)
    
    if not file:
        await message.reply("Please upload a subtitle file (.srt, .vtt, .ass).")
        return
    
    translated_file = await translate_subtitles(file, user_info['language'], user_info['batch_size'], language)

    await message.reply_document(translated_file)

@Client.on_message(filters.command("feedback"))
async def feedback(client, message):
    feedback_text = message.text.split(" ", 1)[1] if len(message.text.split(" ")) > 1 else None
    if feedback_text:
        await message.reply("Thank you for your feedback!")
    else:
        await message.reply("Please provide your feedback.")

@Client.on_message(filters.command("history"))
async def history(client, message):
    user = message.from_user.id
    history = get_user_info(user)['translation_history']
    await message.reply(f"Your previous translations: {history}")

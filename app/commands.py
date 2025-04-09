from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from main import app
from app.database import update_user_info, get_user_info
from app.translate import translate_subtitles
from app.settings import load_user_settings, save_user_settings
import time, os

BOT_START_TIME = time.time()
OWNER_ID = int(os.getenv("OWNER_ID", 0))

@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    user_id = message.from_user.id
    user = get_user_info(user_id)
    if not user:
        update_user_info(user_id, {"allowed": False})
    if not user or not user.get("allowed", False):
        return await message.reply("You are not allowed to use this bot.")
    await message.reply("Welcome to Subtitle Translator Bot! Use /help to see commands.")

@app.on_message(filters.command("settings") & filters.private)
async def settings_cmd(client, message):
    user_id = message.from_user.id
    user = get_user_info(user_id)
    if not user or not user.get("allowed", False):
        return await message.reply("You are not allowed to use this bot.")

    settings = load_user_settings(user_id)
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"Engine: {settings.get('engine', 'gpt')}", callback_data="toggle_engine"),
            InlineKeyboardButton(f"Lang: {settings.get('language', 'en')}", callback_data="set_lang")
        ],
        [
            InlineKeyboardButton(f"Batch: {settings.get('batch_size', 20)}", callback_data="set_batch")
        ]
    ])
    await message.reply("Your current settings:", reply_markup=keyboard)

@app.on_callback_query()
async def handle_settings_buttons(client, callback):
    user_id = callback.from_user.id
    user = get_user_info(user_id)
    if not user or not user.get("allowed", False):
        return await callback.answer("You are not allowed.", show_alert=True)

    settings = load_user_settings(user_id)

    if callback.data == "toggle_engine":
        new_engine = "gemini" if settings.get("engine", "gpt") == "gpt" else "gpt"
        settings["engine"] = new_engine
        save_user_settings(user_id, settings)
        await callback.answer(f"Engine set to {new_engine}")
    elif callback.data == "set_lang":
        await callback.answer("Send the language code (e.g., 'en', 'fr', 'es')")
    elif callback.data == "set_batch":
        await callback.answer("Send the new batch size (e.g., 10, 20, 50)")

@app.on_message(filters.text & filters.private)
async def handle_setting_inputs(client, message):
    user_id = message.from_user.id
    user = get_user_info(user_id)
    if not user or not user.get("allowed", False):
        return await message.reply("You are not allowed to use this bot.")

    text = message.text.strip()
    settings = load_user_settings(user_id)

    if text.isdigit():
        settings["batch_size"] = int(text)
        save_user_settings(user_id, settings)
        await message.reply(f"Batch size updated to {text}")
    elif len(text) == 2:
        settings["language"] = text.lower()
        save_user_settings(user_id, settings)
        await message.reply(f"Language updated to {text.lower()}")

@app.on_message(filters.command("translate") & filters.private)
async def translate_cmd(client, message):
    user_id = message.from_user.id
    user = get_user_info(user_id)
    if not user or not user.get("allowed", False):
        return await message.reply("You are not allowed to use this bot.")
    await message.reply("Please upload your subtitle file (.srt, .ass, or .vtt).")

@app.on_message(filters.document & filters.private)
async def handle_subtitle_file(client, message):
    user_id = message.from_user.id
    user = get_user_info(user_id)
    if not user or not user.get("allowed", False):
        return await message.reply("You are not allowed to use this bot.")

    file = await message.download()
    if not file.endswith((".srt", ".ass", ".vtt")):
        return await message.reply("Unsupported subtitle format. Please upload a .srt, .ass, or .vtt file.")

    print(f"User {user_id} uploaded: {file}")

    try:
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
            import langdetect
            detected_lang = langdetect.detect(content)
            lang = detected_lang
            await message.reply(f"Detected language: {lang}")
    except Exception as e:
        print(f"Language detection failed: {e}")
        lang = "en"

    settings = load_user_settings(user_id)
    engine = settings.get("engine", "gpt")
    batch_size = settings.get("batch_size", 20)

    translated_file = await translate_subtitles(file, lang, engine, batch_size)

    if translated_file:
        await message.reply_document(translated_file, caption="Here is your translated file.")
    else:
        await message.reply("Translation failed. Please try again later.")

@app.on_message(filters.command("feedback") & filters.private)
async def feedback_cmd(client, message):
    user_id = message.from_user.id
    user = get_user_info(user_id)
    if not user or not user.get("allowed", False):
        return await message.reply("You are not allowed to use this bot.")
    feedback_text = " ".join(message.command[1:])
    if not feedback_text:
        return await message.reply("Please provide feedback.")
    await message.reply("Thanks for your feedback!")

@app.on_message(filters.command("clearhistory") & filters.private)
async def clear_history_cmd(client, message):
    user_id = message.from_user.id
    user = get_user_info(user_id)
    if not user or not user.get("allowed", False):
        return await message.reply("You are not allowed to use this bot.")
    update_user_info(user_id, {"history": []})
    await message.reply("Your history has been cleared.")

@app.on_message(filters.command("status") & filters.user(OWNER_ID))
async def status_cmd(client, message):
    uptime = int(time.time() - BOT_START_TIME)
    mins, secs = divmod(uptime, 60)
    hrs, mins = divmod(mins, 60)
    await message.reply(f"Bot is online. Uptime: {hrs}h {mins}m {secs}s")

@app.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def broadcast_cmd(client, message):
    text = " ".join(message.command[1:])
    if not text:
        return await message.reply("Usage: /broadcast <message>")

    from app.database import collection
    users = collection.find({"allowed": True})
    success = 0
    for user in users:
        try:
            await client.send_message(user["_id"], text)
            success += 1
        except:
            pass
    await message.reply(f"Message sent to {success} users.")

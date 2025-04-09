# Subtitle Translation Bot

This Telegram bot allows users to translate subtitle files into Hinglish or other languages using Gemini API or GPT for translations. It supports various subtitle formats like `.srt`, `.ass`, and `.vtt` and offers an easy-to-use interface with Telegram commands and inline buttons.

## Features

### 1. **User Authentication and Role Management**
   - **Owner-approved access**: Only users authorized by the bot owner can use the bot.
   - **Inline button UI** for requesting access: Unauthorized users can request access through inline buttons.
   - **Anti-spam**: Blocks users who spam the access request.

### 2. **Subtitle Translation**
   - **Multiple subtitle formats supported**: `.srt`, `.ass`, `.vtt`.
   - **Translation engines**: Use **Gemini API** or **GPT API** for translating subtitles.
   - **Translation Modes**:
     - **Original + Hinglish**: Displays both the original and translated subtitles side-by-side.
     - **Hinglish-only**: Translates the subtitle into Hinglish and returns only the translated text.
   - **Language auto-detection**: Automatically detects the source language for translation.
   - **Batch processing**: Customize batch sizes (from 10 to 100 lines per batch).
   - **Daily translation limits**: Configurable limits on the number of translations per day.

### 3. **Settings Management**
   - **User settings**: Users can modify their preferred translation engine (Gemini or GPT), batch size, and output format (e.g., `.srt`, `.ass`).
   - **All settings are persistent**: Stored in MongoDB for easy retrieval and management.

### 4. **Translation History**
   - **View past translations**: Users can view their previous translation tasks.
   - **Re-download past translations**: Users can download previously translated subtitle files.
   - **Logs accessible to admin**: The owner has access to logs of all user actions (e.g., translations, settings changes).

### 5. **Admin Panel**
   - Admin can use inline buttons to:
     - Approve or reject user access requests.
     - Modify global settings like API keys and translation limits.
     - View and manage the translation history for all users.

### 6. **Logging and Error Handling**
   - **Comprehensive logging**: Logs all user actions (e.g., translations, settings changes).
   - **Error reporting**: Errors are logged and forwarded to the owner via a private message.

### 7. **MongoDB Integration**
   - **Persistent data storage**: Stores user settings, translation logs, and history in MongoDB.
   - **Scalable**: MongoDB helps scale the bot’s data handling.

### 8. **Inline Button UI**
   - **Interactive UI**: Users interact with the bot through inline buttons to adjust settings, view history, and download translations.
   - **Admin controls**: Admin can use the bot to manage users and monitor all activities.

### 9. **Support for Multiple Languages**
   - **Multiple languages**: Initially supports English → Hinglish translation, but easily configurable to support other languages.

### 10. **Deployment**
   - The bot is **Heroku deployable** with full support for cloud hosting.
   - **Docker support**: Easily deployable via Docker with a pre-configured Dockerfile.
   - Configuration files and environment variables are included for easy setup on Heroku or any cloud platform.

---

## Installation

### 1. **Clone the repository**
   ```bash
   git clone https://github.com/your-repo/subtitle-translation-bot.git
   cd subtitle-translation-bot
  
   pip3 install -r requirements.txt

   BOT_TOKEN=your_bot_token
   API_ID=your_api_id
   API_HASH=your_api_hash
   GEMINI_API_KEY=your_gemini_api_key
   GPT_API_KEY=your_gpt_api_key
   MONGO_URI=your_mongo_uri

   python3 bot.py

import aiohttp
import os

async def translate_subtitles(file, language, batch_size, user_language=None):
    user_language = user_language or "en"
    
    if language == "gemini":
        return await translate_with_gemini(file)
    else:
        return await translate_with_gpt(file)

async def translate_with_gemini(file):
    api_url = "https://api.gemini.com/translate"
    async with aiohttp.ClientSession() as session:
        async with session.post(api_url, files={'file': file}) as response:
            return await response.read()

async def translate_with_gpt(file):
    api_url = "https://api.openai.com/v1/completions"
    headers = {'Authorization': f'Bearer {os.getenv("GPT_API_KEY")}'}
    async with aiohttp.ClientSession() as session:
        async with session.post(api_url, json={'file': file}, headers=headers) as response:
            return await response.read()

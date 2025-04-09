import aiohttp
import os

async def translate_subtitles(file, engine, batch_size, target_language):
    try:
        if engine == "gemini":
            return await translate_with_gemini(file)
        else:
            return await translate_with_gpt(file)
    except Exception as e:
        raise Exception(f"Translation failed: {e}")

async def translate_with_gemini(file):
    api_url = "https://api.gemini.com/translate"
    headers = {'Authorization': f'Bearer {os.getenv("GEMINI_API_KEY")}'}
    try:
        file_path = await file.download()
        with open(file_path, "rb") as f:
            file_bytes = f.read()
        data = aiohttp.FormData()
        data.add_field('file', file_bytes, filename=file.file_name, content_type=file.mime_type)
        async with aiohttp.ClientSession() as session:
            async with session.post(api_url, data=data, headers=headers) as response:
                if response.status != 200:
                    raise Exception(f"Gemini API returned status code {response.status}")
                return await response.read()
    except Exception as e:
        raise Exception(f"Gemini translation error: {e}")

async def translate_with_gpt(file):
    api_url = "https://api.openai.com/v1/completions"
    headers = {'Authorization': f'Bearer {os.getenv("GPT_API_KEY")}'}
    try:
        file_path = await file.download()
        with open(file_path, "rb") as f:
            file_bytes = f.read()
        payload = {
            'file': file_bytes,
            'filename': file.file_name,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(api_url, json=payload, headers=headers) as response:
                if response.status != 200:
                    raise Exception(f"OpenAI API returned status code {response.status}")
                return await response.read()
    except Exception as e:
        raise Exception(f"GPT translation error: {e}")
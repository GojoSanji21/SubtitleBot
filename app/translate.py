import os
import asyncio
import openai
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Load keys from environment
OPENAI_API_KEY = os.getenv("GPT_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

openai.api_key = OPENAI_API_KEY
genai.configure(api_key=GEMINI_API_KEY)

async def translate_subtitles(file_path, lang, engine, batch_size):
    try:
        ext = os.path.splitext(file_path)[-1].lower()
        if ext == ".ass":
            return await translate_ass(file_path, lang, engine, batch_size)
        elif ext in [".srt", ".vtt"]:
            return await translate_plaintext(file_path, lang, engine, batch_size)
        else:
            raise Exception("Unsupported subtitle format.")
    except Exception as e:
        raise Exception(f"Translation failed: {e}")

async def translate_ass(file_path, lang, engine, batch_size):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        subtitles = []
        dialogue_lines = []
        for line in lines:
            if line.startswith("Dialogue:"):
                parts = line.strip().split(",", 9)
                if len(parts) == 10:
                    subtitles.append(parts[-1])
                    dialogue_lines.append(line)

        translated = await batch_translate(subtitles, lang, engine, batch_size)

        output_path = file_path.replace(".ass", f".{lang}.ass")
        with open(output_path, "w", encoding="utf-8") as f:
            index = 0
            for line in lines:
                if line.startswith("Dialogue:") and index < len(translated):
                    parts = line.strip().split(",", 9)
                    parts[-1] = translated[index]
                    f.write(",".join(parts) + "\n")
                    index += 1
                else:
                    f.write(line)

        return output_path
    except Exception as e:
        raise Exception(f"ASS translation error: {e}")

async def translate_plaintext(file_path, lang, engine, batch_size):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        subtitles = [line.strip() for line in lines if line.strip() and not line.strip().isdigit() and "-->" not in line]

        translated = await batch_translate(subtitles, lang, engine, batch_size)

        output_path = file_path.replace(".srt", f".{lang}.srt").replace(".vtt", f".{lang}.vtt")
        index = 0
        with open(output_path, "w", encoding="utf-8") as f:
            for line in lines:
                if line.strip() and not line.strip().isdigit() and "-->" not in line:
                    f.write(translated[index] + "\n")
                    index += 1
                else:
                    f.write(line)

        return output_path
    except Exception as e:
        raise Exception(f"Plaintext translation error: {e}")

async def batch_translate(subtitles, lang, engine, batch_size):
    translated_subs = []
    for i in range(0, len(subtitles), batch_size):
        batch = subtitles[i:i + batch_size]
        prompt = f"Translate the following subtitles into {lang}:\n\n" + "\n".join(batch)

        try:
            if engine == "gpt":
                response = await openai.ChatCompletion.acreate(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a professional subtitle translator."},
                        {"role": "user", "content": prompt}
                    ]
                )
                result = response["choices"][0]["message"]["content"]
            else:
                model = genai.GenerativeModel("gemini-pro")
                response = model.generate_content(prompt)
                result = response.text
        except Exception as e:
            # fallback to Gemini if GPT fails
            if engine == "gpt":
                try:
                    model = genai.GenerativeModel("gemini-pro")
                    response = model.generate_content(prompt)
                    result = response.text
                except Exception as gem_err:
                    raise Exception(f"Both GPT and Gemini failed: {gem_err}")
            else:
                raise Exception(f"Gemini translation failed: {e}")

        translated_batch = result.strip().split("\n")
        translated_subs.extend(translated_batch)
        await asyncio.sleep(1)

    return translated_subs

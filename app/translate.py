import os
import aiofiles
import openai
import google.generativeai as genai

from dotenv import load_dotenv

load_dotenv()

def get_gpt_client():
    openai.api_key = os.getenv("OPENAI_API_KEY")
    return openai

def get_gemini_model():
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    return genai.GenerativeModel("gemini-pro")

async def translate_with_gpt(text, target_lang):
    openai_client = get_gpt_client()
    try:
        response = await openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a subtitle translator."},
                {"role": "user", "content": f"Translate the following subtitle text to {target_lang}. Keep subtitle formatting.\n{text}"}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"GPT translation error: {e}")

def translate_with_gemini_sync(text, target_lang):
    model = get_gemini_model()
    try:
        prompt = f"""Translate the following subtitle text to {target_lang}. 
Keep subtitle formatting.
{text}"""
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        raise Exception(f"Gemini translation failed: {e}")

async def batch_translate(lines, target_lang, engine, batch_size):
    translated_batches = []
    for i in range(0, len(lines), batch_size):
        batch = lines[i:i + batch_size]
        combined = "\n".join(batch)
        try:
            if engine == "gpt":
                translated_text = await translate_with_gpt(combined, target_lang)
            else:
                translated_text = translate_with_gemini_sync(combined, target_lang)
            translated_batches.extend(translated_text.split("\n"))
        except Exception as e:
            fallback_engine = "gemini" if engine == "gpt" else "gpt"
            print(f"{engine.upper()} failed, trying fallback: {e}")
            try:
                if fallback_engine == "gpt":
                    translated_text = await translate_with_gpt(combined, target_lang)
                else:
                    translated_text = translate_with_gemini_sync(combined, target_lang)
                translated_batches.extend(translated_text.split("\n"))
            except Exception as inner_e:
                raise Exception(f"Translation failed: {inner_e}")
    return translated_batches

async def translate_srt(file_path, lang, engine, batch_size):
    async with aiofiles.open(file_path, mode='r', encoding='utf-8') as f:
        lines = await f.readlines()

    text_lines = [line.strip() for line in lines if line.strip() and not line.strip().isdigit() and "-->" not in line]
    translated_lines = await batch_translate(text_lines, lang, engine, batch_size)

    index = 0
    output = []
    for line in lines:
        if line.strip() and not line.strip().isdigit() and "-->" not in line:
            if index < len(translated_lines):
                output.append(translated_lines[index] + "\n")
                index += 1
            else:
                output.append(line)
        else:
            output.append(line)

    output_path = file_path.replace(".srt", f"_translated_{lang}.srt")
    async with aiofiles.open(output_path, mode='w', encoding='utf-8') as f:
        await f.writelines(output)

    return output_path

async def translate_ass(file_path, lang, engine, batch_size):
    async with aiofiles.open(file_path, mode='r', encoding='utf-8') as f:
        lines = await f.readlines()

    subtitle_lines = []
    indexes = []
    for i, line in enumerate(lines):
        if line.startswith("Dialogue:"):
            parts = line.strip().split(",", 9)
            if len(parts) >= 10:
                subtitle_lines.append(parts[9])
                indexes.append(i)

    translated_texts = await batch_translate(subtitle_lines, lang, engine, batch_size)

    for idx, i in enumerate(indexes):
        parts = lines[i].strip().split(",", 9)
        if len(parts) >= 10 and idx < len(translated_texts):
            parts[9] = translated_texts[idx]
            lines[i] = ",".join(parts) + "\n"

    output_path = file_path.replace(".ass", f"_translated_{lang}.ass")
    async with aiofiles.open(output_path, mode='w', encoding='utf-8') as f:
        await f.writelines(lines)

    return output_path

async def translate_vtt(file_path, lang, engine, batch_size):
    async with aiofiles.open(file_path, mode='r', encoding='utf-8') as f:
        lines = await f.readlines()

    text_lines = [line.strip() for line in lines if line.strip() and "-->"]
    translated_lines = await batch_translate(text_lines, lang, engine, batch_size)

    index = 0
    output = []
    for line in lines:
        if line.strip() and "-->" not in line:
            if index < len(translated_lines):
                output.append(translated_lines[index] + "\n")
                index += 1
            else:
                output.append(line)
        else:
            output.append(line)

    output_path = file_path.replace(".vtt", f"_translated_{lang}.vtt")
    async with aiofiles.open(output_path, mode='w', encoding='utf-8') as f:
        await f.writelines(output)

    return output_path

async def translate_subtitles(file_path, lang, engine, batch_size):
    try:
        if file_path.endswith(".srt"):
            return await translate_srt(file_path, lang, engine, batch_size)
        elif file_path.endswith(".ass"):
            return await translate_ass(file_path, lang, engine, batch_size)
        elif file_path.endswith(".vtt"):
            return await translate_vtt(file_path, lang, engine, batch_size)
        else:
            raise Exception("Unsupported subtitle format")
    except Exception as e:
        raise Exception(f"Translation failed: {e}")

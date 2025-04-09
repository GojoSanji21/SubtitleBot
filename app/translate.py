import os
import openai
import google.generativeai as genai
import asyncio
import aiofiles
from pathlib import Path

# Load API keys from environment variables
openai.api_key = os.getenv("GPT_API_KEY")
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Model setup
gemini_model = "models/gemini-1.5-pro"  # Updated to valid model
gpt_model = "gpt-3.5-turbo"

# Gemini generation function
def translate_with_gemini_sync(text, target_lang):
    try:
        model = genai.GenerativeModel(gemini_model)
        prompt = f"Translate the following subtitle lines to {target_lang}:\n\n{text}"
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        raise Exception(f"Gemini translation failed: {e}")

# GPT async generation
async def translate_with_gpt(text, target_lang):
    try:
        messages = [
            {"role": "system", "content": f"Translate the subtitles to {target_lang}"},
            {"role": "user", "content": text}
        ]
        response = await openai.ChatCompletion.acreate(
            model=gpt_model,
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"GPT translation error: {e}")

# Batch translation (used in all subtitle formats)
async def batch_translate(texts, lang, engine, batch_size):
    if isinstance(engine, dict):  # Safe fallback
        engine = engine.get("name", "gpt")

    translated = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        combined = "\n".join(batch)

        try:
            if engine == "gpt":
                translated_text = await translate_with_gpt(combined, lang)
            elif engine == "gemini":
                translated_text = translate_with_gemini_sync(combined, lang)
            else:
                raise ValueError(f"Unsupported engine: {engine}")
            translated.extend(translated_text.splitlines())
        except Exception as e:
            print(f"{str(engine).upper()} failed, trying fallback: {e}")
            try:
                translated_text = await translate_with_gpt(combined, lang)
                translated.extend(translated_text.splitlines())
            except Exception as inner_e:
                raise Exception(f"Translation failed: {inner_e}")
    return translated

# Format-specific translation
async def translate_srt(file_path, lang, engine, batch_size):
    async with aiofiles.open(file_path, mode="r", encoding="utf-8") as f:
        lines = await f.readlines()

    text_lines = [line.strip() for line in lines if line.strip() and not line.strip().isdigit() and '-->' not in line]
    translated_texts = await batch_translate(text_lines, lang, engine, batch_size)

    index = 0
    result_lines = []
    for line in lines:
        if line.strip() and not line.strip().isdigit() and '-->' not in line:
            result_lines.append(translated_texts[index])
            index += 1
        else:
            result_lines.append(line.strip())

    output_path = file_path.replace(".srt", "_translated.srt")
    async with aiofiles.open(output_path, mode="w", encoding="utf-8") as f:
        await f.write("\n".join(result_lines))
    return output_path

async def translate_ass(file_path, lang, engine, batch_size):
    async with aiofiles.open(file_path, mode="r", encoding="utf-8") as f:
        lines = await f.readlines()

    dialogue_lines = [line for line in lines if line.strip().startswith("Dialogue:")]
    non_dialogue = [line for line in lines if not line.strip().startswith("Dialogue:")]

    text_lines = [line.split(",", 9)[-1].strip() for line in dialogue_lines]
    translated_texts = await batch_translate(text_lines, lang, engine, batch_size)

    translated_dialogue = []
    for original, translated in zip(dialogue_lines, translated_texts):
        parts = original.split(",", 9)
        parts[-1] = translated
        translated_dialogue.append(",".join(parts))

    output_path = file_path.replace(".ass", "_translated.ass")
    async with aiofiles.open(output_path, mode="w", encoding="utf-8") as f:
        await f.write("".join(non_dialogue + translated_dialogue))
    return output_path

async def translate_vtt(file_path, lang, engine, batch_size):
    async with aiofiles.open(file_path, mode="r", encoding="utf-8") as f:
        lines = await f.readlines()

    cue_lines = [line for line in lines if "-->" not in line and line.strip()]
    translated_texts = await batch_translate(cue_lines, lang, engine, batch_size)

    result_lines = []
    idx = 0
    for line in lines:
        if "-->" not in line and line.strip():
            result_lines.append(translated_texts[idx])
            idx += 1
        else:
            result_lines.append(line.strip())

    output_path = file_path.replace(".vtt", "_translated.vtt")
    async with aiofiles.open(output_path, mode="w", encoding="utf-8") as f:
        await f.write("\n".join(result_lines))
    return output_path

# Master translation function
async def translate_subtitles(file_path, lang, engine, batch_size):
    ext = Path(file_path).suffix.lower()

    try:
        if ext == ".srt":
            return await translate_srt(file_path, lang, engine, batch_size)
        elif ext == ".ass":
            return await translate_ass(file_path, lang, engine, batch_size)
        elif ext == ".vtt":
            return await translate_vtt(file_path, lang, engine, batch_size)
        else:
            raise Exception("Unsupported subtitle format.")
    except Exception as e:
        raise Exception(f"Translation failed: {e}")

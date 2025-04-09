import os
import openai
import aiofiles
import google.generativeai as genai

openai.api_key = os.getenv("OPENAI_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Load Gemini model
gemini_model = genai.GenerativeModel("gemini-pro")


async def translate_with_gpt(text, target_lang):
    try:
        response = await openai.chat.completions.acreate(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": f"You are a subtitle translator. Translate subtitles to '{target_lang}' while preserving formatting."
                },
                {
                    "role": "user",
                    "content": text
                }
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise Exception(f"GPT translation error: {e}")


def translate_with_gemini_sync(text, target_lang):
    try:
        prompt = f"Translate the following subtitle text to {target_lang}. Keep subtitle formatting:\n{text}"
        response = gemini_model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        raise Exception(f"Gemini translation failed: {e}")


async def batch_translate(lines, target_lang, engine, batch_size=20):
    results = []
    for i in range(0, len(lines), batch_size):
        chunk = lines[i:i + batch_size]
        combined = "\n".join(chunk)
        try:
            if engine == "gpt":
                translated_text = await translate_with_gpt(combined, target_lang)
            else:
                translated_text = translate_with_gemini_sync(combined, target_lang)
            results.extend(translated_text.split("\n"))
        except Exception as e:
            try:
                engine_name = engine.upper() if isinstance(engine, str) else str(engine)
                print(f"{engine_name} failed, trying fallback: {e}")
                if engine == "gpt":
                    translated_text = translate_with_gemini_sync(combined, target_lang)
                else:
                    translated_text = await translate_with_gpt(combined, target_lang)
                results.extend(translated_text.split("\n"))
            except Exception as inner_e:
                raise Exception(f"Translation failed: {inner_e}")
    return results


async def translate_srt(file_path, target_lang, engine, batch_size):
    try:
        async with aiofiles.open(file_path, mode='r', encoding='utf-8') as f:
            lines = await f.readlines()
        text_lines = [line.strip() for line in lines if line.strip() and not line.strip().isdigit() and "-->" not in line]
        translated = await batch_translate(text_lines, target_lang, engine, batch_size)
        output_path = file_path.replace(".srt", f"_{target_lang}.srt")
        async with aiofiles.open(output_path, mode='w', encoding='utf-8') as f:
            index = 0
            for line in lines:
                if line.strip() and not line.strip().isdigit() and "-->" not in line:
                    await f.write(translated[index] + "\n")
                    index += 1
                else:
                    await f.write(line)
        return output_path
    except Exception as e:
        raise Exception(f"SRT translation error: {e}")


async def translate_ass(file_path, target_lang, engine, batch_size):
    try:
        async with aiofiles.open(file_path, mode='r', encoding='utf-8') as f:
            lines = await f.readlines()
        dialogue_lines = []
        non_dialogue_lines = []
        for line in lines:
            if line.startswith("Dialogue:"):
                dialogue_lines.append(line)
            else:
                non_dialogue_lines.append(line)
        subtitle_lines = [l.split(",", 9)[-1].strip() for l in dialogue_lines]
        translated_texts = await batch_translate(subtitle_lines, target_lang, engine, batch_size)
        rebuilt_lines = []
        for i, line in enumerate(dialogue_lines):
            parts = line.split(",", 9)
            if len(parts) >= 10:
                parts[-1] = translated_texts[i]
                rebuilt_lines.append(",".join(parts))
            else:
                rebuilt_lines.append(line)
        output_path = file_path.replace(".ass", f"_{target_lang}.ass")
        async with aiofiles.open(output_path, mode='w', encoding='utf-8') as f:
            for line in non_dialogue_lines + rebuilt_lines:
                await f.write(line)
        return output_path
    except Exception as e:
        raise Exception(f"ASS translation error: {e}")


async def translate_subtitles(file_path, lang, engine="gpt", batch_size=20):
    try:
        if file_path.endswith(".srt"):
            return await translate_srt(file_path, lang, engine, batch_size)
        elif file_path.endswith(".ass"):
            return await translate_ass(file_path, lang, engine, batch_size)
        else:
            raise Exception("Unsupported file format.")
    except Exception as e:
        raise Exception(f"Translation failed: {e}")

import os
import aiofiles
import openai
import google.generativeai as genai

openai.api_key = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

def chunk_text(text, max_length):
    chunks, current_chunk = [], ""
    for line in text.splitlines():
        if len(current_chunk) + len(line) < max_length:
            current_chunk += line + "\n"
        else:
            chunks.append(current_chunk.strip())
            current_chunk = line + "\n"
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

async def translate_with_gpt(text, target_lang):
    try:
        response = await openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are a subtitle translator. Translate to {target_lang}. Keep subtitle formatting intact."},
                {"role": "user", "content": text},
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"GPT translation error: {e}")

def translate_with_gemini_sync(text, target_lang):
    try:
        model = genai.GenerativeModel("gemini-pro")
        prompt = f"Translate the following subtitle text to {target_lang}. Keep subtitle formatting:
{text}"
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        raise Exception(f"Gemini translation error: {e}")

async def batch_translate(chunks, lang, engine, batch_size):
    translated = []
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        combined = "\n".join(batch)
        try:
            if engine == "gpt":
                translated_text = await translate_with_gpt(combined, lang)
            else:
                translated_text = translate_with_gemini_sync(combined, lang)
            translated.extend(translated_text.splitlines())
        except Exception as inner_e:
            fallback_engine = "gemini" if engine == "gpt" else "gpt"
            print(f"{engine.upper()} failed, trying fallback: {inner_e}")
            try:
                if fallback_engine == "gpt":
                    translated_text = await translate_with_gpt(combined, lang)
                else:
                    translated_text = translate_with_gemini_sync(combined, lang)
                translated.extend(translated_text.splitlines())
            except Exception as fallback_e:
                raise Exception(f"Translation failed: {fallback_e}")
    return translated

async def translate_srt(path, lang, engine, batch_size):
    try:
        async with aiofiles.open(path, "r", encoding="utf-8") as f:
            content = await f.read()
        blocks = content.split("\n\n")
        translated_blocks = []
        for block in blocks:
            lines = block.strip().splitlines()
            if len(lines) >= 3:
                subtitle_text = "\n".join(lines[2:])
                chunks = chunk_text(subtitle_text, 1000)
                translated_lines = await batch_translate(chunks, lang, engine, batch_size)
                translated_block = "\n".join(lines[:2] + translated_lines)
                translated_blocks.append(translated_block)
            else:
                translated_blocks.append(block)
        output_file = path.rsplit(".", 1)[0] + ".translated.srt"
        async with aiofiles.open(output_file, "w", encoding="utf-8") as f:
            await f.write("\n\n".join(translated_blocks))
        return output_file
    except Exception as e:
        raise Exception(f"SRT translation error: {e}")

async def translate_ass(path, lang, engine, batch_size):
    try:
        async with aiofiles.open(path, "r", encoding="utf-8") as f:
            lines = await f.readlines()
        dialogue_lines = []
        prefix_lines = []
        for line in lines:
            if line.startswith("Dialogue:"):
                dialogue_lines.append(line)
            else:
                prefix_lines.append(line)
        text_lines = [line.split(",", 9)[-1].strip() for line in dialogue_lines]
        translated_texts = await batch_translate(text_lines, lang, engine, batch_size)
        translated_dialogues = []
        for original, translated in zip(dialogue_lines, translated_texts):
            parts = original.split(",", 9)
            if len(parts) == 10:
                parts[9] = translated
                translated_dialogues.append(",".join(parts))
            else:
                translated_dialogues.append(original)
        output_file = path.rsplit(".", 1)[0] + ".translated.ass"
        async with aiofiles.open(output_file, "w", encoding="utf-8") as f:
            await f.writelines(prefix_lines + translated_dialogues)
        return output_file
    except Exception as e:
        raise Exception(f"ASS translation error: {e}")

async def translate_vtt(path, lang, engine, batch_size):
    try:
        async with aiofiles.open(path, "r", encoding="utf-8") as f:
            content = await f.read()
        blocks = content.strip().split("\n\n")
        translated_blocks = []
        for block in blocks:
            lines = block.strip().splitlines()
            if len(lines) >= 2:
                subtitle_text = "\n".join(lines[1:])
                chunks = chunk_text(subtitle_text, 1000)
                translated_lines = await batch_translate(chunks, lang, engine, batch_size)
                translated_block = "\n".join([lines[0]] + translated_lines)
                translated_blocks.append(translated_block)
            else:
                translated_blocks.append(block)
        output_file = path.rsplit(".", 1)[0] + ".translated.vtt"
        async with aiofiles.open(output_file, "w", encoding="utf-8") as f:
            await f.write("\n\n".join(translated_blocks))
        return output_file
    except Exception as e:
        raise Exception(f"VTT translation error: {e}")

async def translate_subtitles(file_path, lang, engine="gpt", batch_size=20):
    try:
        if file_path.endswith(".srt"):
            return await translate_srt(file_path, lang, engine, batch_size)
        elif file_path.endswith(".ass"):
            return await translate_ass(file_path, lang, engine, batch_size)
        elif file_path.endswith(".vtt"):
            return await translate_vtt(file_path, lang, engine, batch_size)
        else:
            raise Exception("Unsupported subtitle format.")
    except Exception as e:
        raise Exception(f"Translation failed: {e}")

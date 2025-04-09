import os
import re
import tempfile
import openai
import google.generativeai as genai

openai.api_key = os.getenv("GPT_API_KEY")
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def clean_text(text):
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def split_text(text, max_len=1000):
    sentences = re.split(r'(\.|\!|\?)', text)
    chunks = []
    chunk = ""
    for i in range(0, len(sentences) - 1, 2):
        sentence = sentences[i] + sentences[i + 1]
        if len(chunk) + len(sentence) > max_len:
            chunks.append(chunk)
            chunk = sentence
        else:
            chunk += sentence
    if chunk:
        chunks.append(chunk)
    return chunks

def parse_ass(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    header = []
    events = []
    is_events = False
    for line in lines:
        if line.startswith("[Events]"):
            is_events = True
            header.append(line)
            continue
        if not is_events:
            header.append(line)
        else:
            events.append(line)
    return header, events

def rebuild_ass(header, translated_events):
    return "".join(header + translated_events)

async def translate_with_gpt(text, target_lang):
    prompt = f"Translate the following subtitle content to {target_lang} language:\n{text}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

def translate_with_gemini_sync(text, target_lang):
    try:
        model = genai.GenerativeModel("models/gemini-1.0-pro")
        prompt = f"Translate the following subtitle content to {target_lang} language:\n{text}"
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        raise Exception(f"Gemini translation failed: {e}")

async def batch_translate(subtitles, lang, engine, batch_size):
    results = []
    for i in range(0, len(subtitles), batch_size):
        batch = subtitles[i:i + batch_size]
        combined = "\n".join([clean_text(line) for line in batch])
        try:
            if engine == "gpt":
                translated = await translate_with_gpt(combined, lang)
            else:
                translated = translate_with_gemini_sync(combined, lang)
        except Exception as e:
            print(f"{engine.upper()} failed, trying fallback: {e}")
            if engine == "gpt":
                translated = translate_with_gemini_sync(combined, lang)
            else:
                translated = await translate_with_gpt(combined, lang)
        translated_lines = translated.split("\n")
        results.extend(translated_lines)
    return results

async def translate_ass(file_path, lang, engine, batch_size):
    header, events = parse_ass(file_path)
    text_lines = []
    non_text_lines = []
    for line in events:
        if line.startswith("Dialogue:"):
            parts = line.strip().split(",", 9)
            if len(parts) == 10:
                text_lines.append(parts[9])
                non_text_lines.append(parts[:9])
            else:
                text_lines.append("")
                non_text_lines.append(parts)
        else:
            text_lines.append(line)
            non_text_lines.append(None)
    translated_texts = await batch_translate(text_lines, lang, engine, batch_size)
    translated_events = []
    for original, parts in zip(translated_texts, non_text_lines):
        if parts:
            translated_events.append("Dialogue:" + ",".join(parts) + "," + original + "\n")
        else:
            translated_events.append(original + "\n")
    result = rebuild_ass(header, translated_events)
    out_path = file_path + ".translated.ass"
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(result)
    return out_path

async def translate_srt(file_path, lang, engine, batch_size):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    subtitles = content.strip().split("\n\n")
    text_lines = ["\n".join(block.splitlines()[2:]) for block in subtitles if len(block.splitlines()) > 2]
    translated_lines = await batch_translate(text_lines, lang, engine, batch_size)
    translated_blocks = []
    for block, translated in zip(subtitles, translated_lines):
        lines = block.splitlines()
        if len(lines) > 2:
            lines = lines[:2] + translated.split("\n")
        translated_blocks.append("\n".join(lines))
    out_path = file_path + ".translated.srt"
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write("\n\n".join(translated_blocks))
    return out_path

async def translate_vtt(file_path, lang, engine, batch_size):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    text_lines = []
    for line in lines:
        if "-->" not in line and line.strip():
            text_lines.append(line.strip())
    translated_lines = await batch_translate(text_lines, lang, engine, batch_size)
    i = 0
    new_lines = []
    for line in lines:
        if "-->" not in line and line.strip():
            new_lines.append(translated_lines[i] + "\n")
            i += 1
        else:
            new_lines.append(line)
    out_path = file_path + ".translated.vtt"
    with open(out_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    return out_path

async def translate_subtitles(file_path, lang, engine, batch_size):
    try:
        if file_path.endswith(".ass"):
            return await translate_ass(file_path, lang, engine, batch_size)
        elif file_path.endswith(".srt"):
            return await translate_srt(file_path, lang, engine, batch_size)
        elif file_path.endswith(".vtt"):
            return await translate_vtt(file_path, lang, engine, batch_size)
        else:
            raise Exception("Unsupported subtitle format.")
    except Exception as e:
        raise Exception(f"Translation failed: {e}")

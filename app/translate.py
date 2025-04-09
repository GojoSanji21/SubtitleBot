import os
import aiofiles
import openai
import google.generativeai as genai

from typing import List

# Configure API Keys
openai.api_key = os.getenv("OPENAI_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def translate_with_gpt(prompt: str, target_lang: str) -> str:
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"Translate the following text to {target_lang}. Keep subtitle formatting."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise Exception(f"GPT translation error: {e}")

def translate_with_gemini_sync(prompt: str, target_lang: str) -> str:
    try:
        gemini_model = genai.GenerativeModel(
            "gemini-pro",
            client_options={"api_key": os.getenv("GOOGLE_API_KEY")}
        )
        response = gemini_model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        raise Exception(f"Gemini translation failed: {e}")

async def batch_translate(lines: List[str], target_lang: str, engine: str, batch_size: int = 20) -> List[str]:
    translated_lines = []
    for i in range(0, len(lines), batch_size):
        batch = lines[i:i + batch_size]
        combined = "\n".join(batch)

        prompt = f"Translate the following subtitle text to {target_lang}. Keep subtitle formatting:\n{combined}"

        try:
            if engine == "gpt":
                translated_text = translate_with_gpt(combined, target_lang)
            else:
                translated_text = translate_with_gemini_sync(combined, target_lang)

            translated_lines.extend(translated_text.split("\n"))
        except Exception as e:
            raise Exception(f"Translation failed: {e}")

    return translated_lines

async def translate_ass(file_path: str, target_lang: str, engine: str, batch_size: int):
    try:
        async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
            lines = await f.readlines()

        subtitle_lines = [line.strip() for line in lines if line.strip() and not line.strip().isdigit() and "-->" not in line]
        translated_texts = await batch_translate(subtitle_lines, target_lang, engine, batch_size)

        # Re-insert translated lines back into ASS structure (simplified logic)
        result_lines = []
        index = 0
        for line in lines:
            if line.strip() and not line.strip().isdigit() and "-->" not in line:
                result_lines.append(translated_texts[index] + "\n")
                index += 1
            else:
                result_lines.append(line)

        output_path = file_path.replace(".ass", f"_{target_lang}.ass")
        async with aiofiles.open(output_path, "w", encoding="utf-8") as f:
            await f.writelines(result_lines)

        return output_path

    except Exception as e:
        raise Exception(f"ASS translation error: {e}")

async def translate_subtitles(file_path: str, lang: str, engine: str, batch_size: int):
    try:
        if file_path.endswith(".ass"):
            return await translate_ass(file_path, lang, engine, batch_size)
        else:
            raise Exception("Only .ass format supported for now.")
    except Exception as e:
        raise Exception(f"Translation failed: {e}")

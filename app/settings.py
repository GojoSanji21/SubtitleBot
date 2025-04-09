from app.database import get_user_info, update_user_info
from datetime import datetime

def load_user_settings(user_id):
    try:
        info = get_user_info(user_id)
        if not info:
            info = {
                "user_id": user_id,
                "engine": "gemini",
                "target_language": "en",
                "batch_size": 100,
                "allowed": False,
                "translation_history": []
            }
            update_user_info(user_id, info)
        return info
    except Exception as e:
        print(f"Error loading user settings for {user_id}: {e}")
        return {
            "user_id": user_id,
            "engine": "gemini",
            "target_language": "en",
            "batch_size": 100,
            "allowed": False,
            "translation_history": []
        }

def save_user_settings(user_id, engine=None, target_language=None, batch_size=None, allowed=None):
    try:
        user_info = get_user_info(user_id) or {"user_id": user_id}
        if engine is not None:
            user_info["engine"] = engine
        if target_language is not None:
            user_info["target_language"] = target_language
        if batch_size is not None:
            user_info["batch_size"] = batch_size
        if allowed is not None:
            user_info["allowed"] = allowed
        update_user_info(user_id, user_info)
    except Exception as e:
        print(f"Error saving settings for user {user_id}: {e}")

def add_translation_to_history(user_id, filename):
    try:
        user_info = get_user_info(user_id) or {"user_id": user_id, "translation_history": []}
        history = user_info.get("translation_history", [])
        entry = {
            "filename": filename,
            "timestamp": datetime.utcnow().isoformat()
        }
        history.append(entry)
        user_info["translation_history"] = history[-10:]
        update_user_info(user_id, user_info)
    except Exception as e:
        print(f"Error updating translation history for user {user_id}: {e}")

def get_translation_history(user_id):
    try:
        user_info = get_user_info(user_id)
        return user_info.get("translation_history", []) if user_info else []
    except Exception as e:
        print(f"Error fetching history for user {user_id}: {e}")
        return []

def clear_translation_history(user_id):
    try:
        user_info = get_user_info(user_id)
        if user_info:
            user_info["translation_history"] = []
            update_user_info(user_id, user_info)
    except Exception as e:
        print(f"Error clearing history for user {user_id}: {e}")
from app.database import get_user_info, update_user_info

def load_user_settings(user_id):
    user_info = get_user_info(user_id)
    return user_info

def save_user_settings(user_id, language=None, engine=None, batch_size=None):
    user_info = get_user_info(user_id)
    
    # Ensure we do not overwrite empty values
    if language:
        user_info['language'] = language
    if engine:
        user_info['engine'] = engine
    if batch_size:
        user_info['batch_size'] = batch_size
        
    update_user_info(user_id, user_info)

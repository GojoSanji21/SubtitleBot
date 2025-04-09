# Simple in-memory storage for user settings
users_db = {}

def get_user_info(user_id):
    return users_db.get(user_id)

def update_user_info(user_id, user_info):
    users_db[user_id] = user_info

def get_all_users():
    return users_db

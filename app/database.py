from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client.get_database("telegram_bot")
users_collection = db.get_collection("users")

def get_user_info(user_id):
    return users_collection.find_one({"user_id": user_id})

def update_user_info(user_id, new_data):
    try:
        users_collection.update_one({"user_id": user_id}, {"$set": new_data}, upsert=True)
    except Exception as e:
        print(f"Error updating user {user_id}: {e}")

def get_all_users():
    return list(users_collection.find())
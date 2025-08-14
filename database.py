# database.py
import os
from pymongo import MongoClient
from config import MONGO_URI

# Connect to MongoDB
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["filestore"]  # fixed DB name

# Collections
users_col = db["users"]
files_col = db["files"]
stats_col = db["stats"]
verify_col = db["verify"]

# --- USER FUNCTIONS ---
def add_user(user_id: int):
    if not users_col.find_one({"user_id": user_id}):
        users_col.insert_one({"user_id": user_id, "premium": False})

def is_premium(user_id: int) -> bool:
    user = users_col.find_one({"user_id": user_id})
    return bool(user and user.get("premium", False))

def set_premium(user_id: int, value: bool):
    users_col.update_one({"user_id": user_id}, {"$set": {"premium": value}}, upsert=True)

# --- FILE FUNCTIONS ---
def save_file(slug: str, file_id: str, file_type: str, caption: str = None):
    files_col.insert_one({
        "slug": slug,
        "file_id": file_id,
        "file_type": file_type,
        "caption": caption
    })

def get_file(slug: str):
    return files_col.find_one({"slug": slug})

# --- STATS FUNCTIONS ---
def increment_sent_files():
    stats_col.update_one({"_id": "global"}, {"$inc": {"sent_files": 1}}, upsert=True)

def get_sent_files_count() -> int:
    stats = stats_col.find_one({"_id": "global"})
    return stats.get("sent_files", 0) if stats else 0

# --- VERIFICATION FUNCTIONS ---
def save_verification(slug: str, user_id: int, expires_at: int):
    verify_col.insert_one({
        "slug": slug,
        "user_id": user_id,
        "expires_at": expires_at
    })

def get_verification(slug: str):
    return verify_col.find_one({"slug": slug})

def delete_verification(slug: str):
    verify_col.delete_one({"slug": slug})
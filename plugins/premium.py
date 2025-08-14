import os
import time
from pymongo import MongoClient
from config import MONGO_URI

# Mongo connection
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["filestore"]  # no fixed DB name
users_col = db["users"]
files_col = db["files"]
stats_col = db["stats"]
premium_col = db["premium"]

# ------------------- USER MANAGEMENT -------------------
def add_user(user_id: int):
    if not users_col.find_one({"_id": user_id}):
        users_col.insert_one({"_id": user_id, "joined_at": time.time()})

def user_exists(user_id: int) -> bool:
    return users_col.find_one({"_id": user_id}) is not None

def total_users() -> int:
    return users_col.count_documents({})

# ------------------- FILE MANAGEMENT -------------------
def save_file(slug: str, file_id: str, file_type: str, caption: str = None):
    files_col.insert_one({
        "_id": slug,
        "file_id": file_id,
        "file_type": file_type,
        "caption": caption
    })

def get_file(slug: str):
    return files_col.find_one({"_id": slug})

# ------------------- STATS -------------------
def increment_file_sent_count():
    stats_col.update_one({"_id": "global"}, {"$inc": {"files_sent": 1}}, upsert=True)

def get_stats():
    stats = stats_col.find_one({"_id": "global"})
    files_sent = stats["files_sent"] if stats else 0
    return {
        "total_users": total_users(),
        "files_sent": files_sent
    }

# ------------------- PREMIUM -------------------
def add_premium(user_id: int, days: int):
    expiry = time.time() + (days * 86400)
    premium_col.update_one({"_id": user_id}, {"$set": {"expiry": expiry}}, upsert=True)

def remove_premium(user_id: int):
    premium_col.delete_one({"_id": user_id})

def is_premium(user_id: int) -> bool:
    record = premium_col.find_one({"_id": user_id})
    if not record:
        return False
    if record["expiry"] < time.time():
        premium_col.delete_one({"_id": user_id})
        return False
    return True

def premium_expiry(user_id: int):
    record = premium_col.find_one({"_id": user_id})
    if record:
        return record["expiry"]
    return None
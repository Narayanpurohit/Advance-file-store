# database.py
from pymongo import MongoClient
from config import MONGO_URI, DB_NAME

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

users_col = db["users"]
files_col = db["files"]
verify_col = db["verify"]

def user_exists(user_id: int) -> bool:
    return users_col.find_one({"_id": user_id}) is not None

def add_user(user_id: int):
    users_col.insert_one({"_id": user_id, "premium": False})

def is_premium(user_id: int) -> bool:
    user = users_col.find_one({"_id": user_id})
    return user and user.get("premium", False)

def set_premium(user_id: int, premium: bool):
    users_col.update_one({"_id": user_id}, {"$set": {"premium": premium}}, upsert=True)

def save_file(slug: str, file_id: str, file_type: str, caption: str = None):
    files_col.insert_one({"slug": slug, "file_id": file_id, "file_type": file_type, "caption": caption})

def get_file(slug: str):
    return files_col.find_one({"slug": slug})

def save_verification_slug(user_id: int, slug: str, expiry_hours: int):
    from datetime import datetime, timedelta
    verify_col.insert_one({
        "user_id": user_id,
        "slug": slug,
        "expires_at": datetime.utcnow() + timedelta(hours=expiry_hours)
    })

def check_verification_slug(slug: str, user_id: int) -> bool:
    from datetime import datetime
    data = verify_col.find_one({"slug": slug, "user_id": user_id})
    if not data:
        return False
    return data["expires_at"] > datetime.utcnow()
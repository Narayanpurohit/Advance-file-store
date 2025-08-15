import datetime
import random
import string
from pymongo import MongoClient
from config import MONGO_URI

# MongoDB connection
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["filestore"]

# Collections
users_col = db["users"]
files_col = db["files"]
stats_col = db["stats"]
verify_col = db["verifications"]


# ---------- USER MANAGEMENT ----------
def add_user(user_id: int):
    if not users_col.find_one({"_id": user_id}):
        users_col.insert_one({"_id": user_id, "premium_until": None})


def is_premium(user_id: int) -> bool:
    user = users_col.find_one({"_id": user_id})
    if not user or not user.get("premium_until"):
        return False
    return datetime.datetime.utcnow() < user["premium_until"]


def add_premium_hours(user_id: int, hours: int):
    """Extend premium by given hours."""
    now = datetime.datetime.utcnow()
    user = users_col.find_one({"_id": user_id})
    if user and user.get("premium_until") and user["premium_until"] > now:
        new_time = user["premium_until"] + datetime.timedelta(hours=hours)
    else:
        new_time = now + datetime.timedelta(hours=hours)
    users_col.update_one({"_id": user_id}, {"$set": {"premium_until": new_time}}, upsert=True)


def add_premium_days(user_id: int, days: int):
    """Extend premium by given days."""
    add_premium_hours(user_id, days * 24)


def remove_premium(user_id: int):
    users_col.update_one({"_id": user_id}, {"$set": {"premium_until": None}})


# ---------- FILE MANAGEMENT ----------
def save_file(file_id: str, file_name: str, file_size: int, caption: str = None):
    files_col.insert_one({
        "file_id": file_id,
        "file_name": file_name,
        "file_size": file_size,
        "caption": caption
    })


def get_file(file_id: str):
    return files_col.find_one({"file_id": file_id})


# ---------- VERIFICATION ----------
def create_verification_slug(user_id: int, ttl_hours: int) -> str:
    """Create a slug for verification tied to a user_id."""
    slug = "verify_" + "".join(random.choices(string.ascii_letters + string.digits, k=30))
    expires_at = datetime.datetime.utcnow() + datetime.timedelta(hours=ttl_hours)
    verify_col.insert_one({
        "slug": slug,
        "user_id": user_id,
        "expires_at": expires_at
    })
    return slug


def use_verification_slug(slug: str):
    """Use verification slug and return doc if valid."""
    doc = verify_col.find_one({"slug": slug})
    if not doc:
        return None
    if datetime.datetime.utcnow() > doc["expires_at"]:
        verify_col.delete_one({"slug": slug})
        return None
    verify_col.delete_one({"slug": slug})  # Remove slug after use
    return doc


# ---------- STATS ----------
def increment_stat(key: str):
    stats_col.update_one({"_id": key}, {"$inc": {"count": 1}}, upsert=True)


def get_stat(key: str) -> int:
    doc = stats_col.find_one({"_id": key})
    return doc["count"] if doc else 0
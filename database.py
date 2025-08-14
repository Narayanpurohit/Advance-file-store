import os
import random
import string
import datetime
from pymongo import MongoClient
import config

# ─────────────────────────────────────────────
# MongoDB Connection
# ─────────────────────────────────────────────
MONGO_URI = os.getenv("MONGO_URI", "")
mongo_client = MongoClient(MONGO_URI)

db = mongo_client.get_default_database()
users_col = db["users"]
files_col = db["files"]
stats_col = db["stats"]
verify_col = db["verify_links"]

# ─────────────────────────────────────────────
# Users
# ─────────────────────────────────────────────
def add_user(user_id: int):
    """Add new user if not exists."""
    if not users_col.find_one({"user_id": user_id}):
        users_col.insert_one({"user_id": user_id, "premium_until": None})

def is_user(user_id: int) -> bool:
    """Check if user exists."""
    return users_col.find_one({"user_id": user_id}) is not None

# ─────────────────────────────────────────────
# Premium System
# ─────────────────────────────────────────────
def add_premium(user_id: int, days: int):
    """Add premium for given number of days."""
    expiry = datetime.datetime.utcnow() + datetime.timedelta(days=days)
    users_col.update_one(
        {"user_id": user_id},
        {"$set": {"premium_until": expiry}},
        upsert=True
    )

def remove_premium(user_id: int):
    """Remove premium."""
    users_col.update_one({"user_id": user_id}, {"$set": {"premium_until": None}})

def is_premium(user_id: int) -> bool:
    """Check if user has active premium."""
    user = users_col.find_one({"user_id": user_id})
    if not user or not user.get("premium_until"):
        return False
    return datetime.datetime.utcnow() < user["premium_until"]

# ─────────────────────────────────────────────
# Verification Links
# ─────────────────────────────────────────────
def create_verification_slug(ttl_hours: int) -> str:
    """Create a random verification slug."""
    slug = "verify_" + "".join(random.choices(string.ascii_letters + string.digits, k=30))
    expires_at = datetime.datetime.utcnow() + datetime.timedelta(hours=ttl_hours)
    verify_col.insert_one({"slug": slug, "expires_at": expires_at})
    return slug

def use_verification_slug(slug: str) -> bool:
    """Use verification slug and give 8h premium if valid."""
    doc = verify_col.find_one({"slug": slug})
    if not doc:
        return False
    if datetime.datetime.utcnow() > doc["expires_at"]:
        verify_col.delete_one({"slug": slug})
        return False
    verify_col.delete_one({"slug": slug})
    return True

# ─────────────────────────────────────────────
# Files
# ─────────────────────────────────────────────
def generate_file_slug(file_type: str) -> str:
    """Generate unique slug for file."""
    slug = f"{file_type}_" + "".join(random.choices(string.ascii_lowercase + string.digits, k=12))
    return slug

def save_file(file_id: str, file_type: str, caption: str = None):
    """Save file details in DB."""
    slug = generate_file_slug(file_type)
    files_col.insert_one({"slug": slug, "file_id": file_id, "type": file_type, "caption": caption})
    return slug

def get_file_by_slug(slug: str):
    """Retrieve file from slug."""
    return files_col.find_one({"slug": slug})

# ─────────────────────────────────────────────
# Stats
# ─────────────────────────────────────────────
def increment_file_send_count():
    stats_col.update_one({"_id": "global"}, {"$inc": {"sent_files": 1}}, upsert=True)

def get_file_send_count() -> int:
    stats = stats_col.find_one({"_id": "global"})
    return stats.get("sent_files", 0) if stats else 0

def get_stats():
    """Return all stats."""
    return {
        "sent_files": get_file_send_count(),
        "total_users": users_col.count_documents({}),
        "total_files": files_col.count_documents({})
    }
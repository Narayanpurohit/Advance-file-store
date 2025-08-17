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
batches_col = db["batches"]

# ---------- USER MANAGEMENT ----------
def user_exists(user_id: int) -> bool:
    return users_col.find_one({"_id": user_id}) is not None
    
def get_all_users():
    return list(users_col.find({}, {"_id": 1}))

def add_user(user_id: int):
    if not users_col.find_one({"_id": user_id}):
        users_col.insert_one({"_id": user_id, "premium_until": None})


import datetime

def is_premium(user_id: int) -> bool:
    """Check if the user still has active premium."""
    user = users_col.find_one({"user_id": user_id})
    if not user or not user.get("premium_until"):
        return False

    premium_until = user["premium_until"]

    # Handle string case just in case it's stored as ISO string
    if isinstance(premium_until, str):
        try:
            premium_until = datetime.datetime.fromisoformat(premium_until)
        except Exception:
            return False

    return datetime.datetime.utcnow() < premium_until

def add_premium_hours(user_id: int, hours: int):
    """Extend premium by given hours."""
    now = datetime.datetime.utcnow()
    user = users_col.find_one({"user_id": user_id})
    if user and user.get("premium_until") and user["premium_until"] > now:
        new_time = user["premium_until"] + datetime.timedelta(hours=hours)
    else:
        new_time = now + datetime.timedelta(hours=hours)
    users_col.update_one({"user_id": user_id}, {"$set": {"premium_until": new_time}}, upsert=True)

def add_premium_days(user_id: int, days: int):
    expiry = get_premium_expiry(user_id)
    now = datetime.datetime.utcnow()

    if expiry and expiry > now:
        new_expiry = expiry + datetime.timedelta(days=days)
    else:
        new_expiry = now + datetime.timedelta(days=days)

    users_col.update_one(
        {"user_id": user_id},
        {"$set": {"premium_until": new_expiry}},
        upsert=True
    )

def remove_premium(user_id: int):
    users_col.update_one(
        {"user_id": user_id},
        {"$set": {"premium_until": None}}
    )
    
def get_premium_expiry(user_id: int):
    """
    Returns the datetime when the user's premium expires, or None if no premium.
    """
    user = users_col.find_one({"user_id": user_id})
    if not user or "premium_until" not in user:
        return None
    return user["premium_until"]

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
def get_file_by_slug(slug: str) -> dict:
    """Retrieve file document from the database by slug."""
    return files_col.find_one({"slug": slug})

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







def increment_file_send_count():
    """Increase total files sent count."""
    stats_col.update_one(
        {"_id": "stats"},
        {"$inc": {"files_sent": 1}},
        upsert=True
    )
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError
from datetime import datetime, timedelta
from bson import ObjectId
import config

client = MongoClient(config.MONGO_URI)
db = client[config.DB_NAME]

files = db.files
users = db.users
verifications = db.verifications

# Helpful indexes (create once)
users.create_index([("user_id", ASCENDING)], unique=True, name="uid_unique")
users.create_index([("premium_until", DESCENDING)], name="premium_until_idx")
files.create_index([("created_at", DESCENDING)], name="file_created_idx")
verifications.create_index([("slug", ASCENDING)], unique=True, name="slug_unique")
verifications.create_index([("created_at", DESCENDING)], name="verify_created_idx")

# ---------- Files ----------
def save_file(file_id, file_type, file_name, file_size):
    doc = {
        "file_id": file_id,
        "file_type": file_type,
        "file_name": file_name,
        "file_size": file_size,
        "created_at": datetime.utcnow()
    }
    res = files.insert_one(doc)
    return str(res.inserted_id)

def get_file_by_dbid(db_id_str):
    try:
        return files.find_one({"_id": ObjectId(db_id_str)})
    except Exception:
        return None

# ---------- Users ----------
def save_user(user_id, first_name):
    try:
        users.insert_one({
            "user_id": user_id,
            "first_name": first_name,
            "joined_at": datetime.utcnow(),
            "premium_until": None
        })
        return True
    except DuplicateKeyError:
        return False

def get_user(user_id):
    return users.find_one({"user_id": user_id})

def ensure_user(user_id, first_name):
    added = save_user(user_id, first_name)
    if not added:
        # Optionally update first_name if changed
        users.update_one({"user_id": user_id}, {"$set": {"first_name": first_name}})
    return get_user(user_id)

# ---------- Premium ----------
def is_premium(user_id):
    u = get_user(user_id)
    if not u:
        return False, None
    until = u.get("premium_until")
    if until and until > datetime.utcnow():
        return True, until
    return False, until

def add_premium_hours(user_id, hours):
    now = datetime.utcnow()
    u = ensure_user(user_id, first_name="")  # no change to first_name if unknown
    current_until = u.get("premium_until")
    base = current_until if current_until and current_until > now else now
    new_until = base + timedelta(hours=hours)
    users.update_one({"user_id": user_id}, {"$set": {"premium_until": new_until}})
    return new_until

def add_premium_days(user_id, days):
    return add_premium_hours(user_id, days * 24)

def remove_premium(user_id):
    users.update_one({"user_id": user_id}, {"$set": {"premium_until": None}})
    return True

# ---------- Stats ----------
def get_stats():
    return {
        "total_users": users.count_documents({}),
        "total_files": files.count_documents({}),
        "last_user": users.find_one(sort=[("joined_at", DESCENDING)])
    }

# ---------- Verification slugs ----------
def create_verification(slug, user_id, file_db_id):
    doc = {
        "slug": slug,
        "user_id": user_id,          # bind slug to THIS user
        "file_db_id": file_db_id,    # what they want after verify
        "created_at": datetime.utcnow(),
        "consumed": False,
        "consumed_at": None
    }
    verifications.insert_one(doc)
    return True

def get_verification(slug):
    return verifications.find_one({"slug": slug})

def consume_verification(slug, user_id):
    """
    Returns (file_db_id or None, reason)
    """
    v = verifications.find_one({"slug": slug})
    if not v:
        return None, "not_found"

    # TTL check
    age = datetime.utcnow() - v["created_at"]
    if age > timedelta(hours=config.VERIFY_SLUG_TTL_HOURS):
        return None, "expired"

    if v.get("consumed"):
        return v.get("file_db_id"), "already_consumed"

    if v["user_id"] != user_id:
        return None, "wrong_user"

    verifications.update_one({"_id": v["_id"]}, {"$set": {"consumed": True, "consumed_at": datetime.utcnow()}})
    return v.get("file_db_id"), "ok"
import datetime
import uuid
from pymongo import MongoClient
from config import MONGO_URI, DB_NAME

# Mongo Setup
mongo_client = MongoClient(MONGO_URI)
db = mongo_client[DB_NAME]

# Collections
users_col = db["users"]
files_col = db["files"]
stats_col = db["stats"]
verifications_col = db["verifications"]
batches_col = db["batches"]


# ---------------- USERS ---------------- #

def add_user(user_id: int):
    if not users_col.find_one({"user_id": user_id}):
        users_col.insert_one({
            "user_id": user_id,
            "joined_at": datetime.datetime.utcnow(),
            "premium_until": None
        })


def user_exists(user_id: int) -> bool:
    return users_col.find_one({"user_id": user_id}) is not None


def is_premium(user_id: int) -> bool:
    user = users_col.find_one({"user_id": user_id})
    if not user or not user.get("premium_until"):
        return False
    return datetime.datetime.utcnow() < user["premium_until"]


def add_premium_hours(user_id: int, hours: int):
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
    users_col.update_one({"user_id": user_id}, {"$set": {"premium_until": new_expiry}}, upsert=True)


def get_premium_expiry(user_id: int):
    user = users_col.find_one({"user_id": user_id})
    return user.get("premium_until") if user else None


def remove_premium(user_id: int):
    users_col.update_one({"user_id": user_id}, {"$set": {"premium_until": None}})


# ---------------- FILES ---------------- #

def add_file(slug: str, file_id: str, file_type: str, file_name: str, file_size: int, caption: str = ""):
    files_col.insert_one({
        "slug": slug,
        "file_id": file_id,
        "file_type": file_type,
        "file_name": file_name,
        "file_size": file_size,
        "caption": caption,
        "created_at": datetime.datetime.utcnow()
    })


def get_file_by_slug(slug: str):
    return files_col.find_one({"slug": slug})


# ---------------- STATS ---------------- #

def increment_file_send_count():
    stats_col.update_one({"_id": "stats"}, {"$inc": {"files_sent": 1}}, upsert=True)


def get_total_files_sent():
    doc = stats_col.find_one({"_id": "stats"})
    if not doc:
        return 0
    return doc.get("files_sent", 0)


# ---------------- VERIFICATION ---------------- #

def create_verification_slug(user_id: int, ttl_hours: int):
    slug = "verify_" + uuid.uuid4().hex[:16]
    expire_at = datetime.datetime.utcnow() + datetime.timedelta(hours=ttl_hours)
    verifications_col.insert_one({
        "slug": slug,
        "user_id": user_id,
        "expire_at": expire_at
    })
    return slug


def use_verification_slug(slug: str):
    record = verifications_col.find_one({"slug": slug})
    if not record:
        return None
    if record["expire_at"] < datetime.datetime.utcnow():
        verifications_col.delete_one({"slug": slug})
        return None
    verifications_col.delete_one({"slug": slug})  # one-time use
    return record


# ---------------- BATCH ---------------- #

def save_batch(chat_id, first_id, last_id, items):
    """
    Save a batch of messages/files into the database.
    Returns the slug to be used with /start batch_<slug>.
    """
    slug = "batch_" + str(uuid.uuid4())[:8]
    batches_col.insert_one({
        "_id": slug,
        "chat_id": chat_id,
        "first_id": first_id,
        "last_id": last_id,
        "items": items,
        "created_at": datetime.datetime.utcnow()
    })
    return slug


def get_batch(slug: str):
    return batches_col.find_one({"_id": slug})
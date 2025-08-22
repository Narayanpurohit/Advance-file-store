from datetime import datetime
from pymongo import MongoClient
from config import MONGO_URI,DB_NAME

# Connect to Mongo
mongo_client = MongoClient(MONGO_URI)
db = mongo_client[DB_NAME]

# Collections
users_col = db["users"]
files_col = db["files"]
stats_col = db["stats"]
batch_col = db["batches"]
slugs_col = db["slugs"]


# ---------------- USERS ----------------
def user_exists(user_id: int) -> bool:
    return users_col.find_one({"user_id": user_id}) is not None


def add_user(user_id: int):
    if not user_exists(user_id):
        users_col.insert_one({
            "user_id": user_id,
            "joined": datetime.datetime.utcnow(),
            "premium_until": None
        })

def get_all_users():
    """Return list of all user IDs."""
    return [doc["_id"] for doc in users_col.find({}, {"_id": 1})]
    

def is_premium(user_id: int) -> bool:
    user = users_col.find_one({"user_id": user_id})
    if not user or not user.get("premium_until"):
        return False
    return datetime.datetime.utcnow() < user["premium_until"]


def get_premium_expiry(user_id: int):
    user = users_col.find_one({"user_id": user_id})
    return user.get("premium_until") if user else None


def add_premium_hours(user_id: int, hours: int):
    now = datetime.datetime.utcnow()
    user = users_col.find_one({"user_id": user_id})
    if user and user.get("premium_until") and user["premium_until"] > now:
        new_time = user["premium_until"] + datetime.timedelta(hours=hours)
    else:
        new_time = now + datetime.timedelta(hours=hours)
    users_col.update_one(
        {"user_id": user_id},
        {"$set": {"premium_until": new_time}},
        upsert=True
    )


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
    users_col.update_one({"user_id": user_id}, {"$set": {"premium_until": None}})


# ---------------- FILES ----------------
def add_file(slug: str, file_id: str, file_type: str, file_name: str, file_size: int, caption: str):
    files_col.insert_one({
        "slug": slug,
        "file_id": file_id,
        "file_type": file_type,  # doc, vid, aud
        "file_name": file_name,
        "file_size": file_size,
        "caption": caption,
        "created_at": datetime.datetime.utcnow()
    })


def get_file_by_slug(slug: str):
    return files_col.find_one({"slug": slug})


# ---------------- BATCH ----------------
def save_batch(slug: str, messages: list):
    """
    Save a batch of messages in the database.
    """
    try:
        batch_doc = {
            "slug": slug,
            "messages": messages,
            "created_at": datetime.datetime.utcnow()
        }
        db.batches.insert_one(batch_doc)
        return True
    except Exception as e:
        print(f"⚠️ DB Error (save_batch): {e}")
        return False
        
        
def get_batch_by_slug(slug: str):
    """
    Fetch a batch document by slug from the database.
    Returns None if not found.
    """
    try:
        batch = db.batches.find_one({"slug": slug})
        return batch
    except Exception as e:
        print(f"⚠️ DB Error (get_batch_by_slug): {e}")
        return None

# Get batch
async def get_batch(slug: str):
    return await db.batches.find_one({"slug": slug})
# ---------------- STATS ----------------
def increment_file_send_count():
    stats_col.update_one(
        {"_id": "stats"},
        {"$inc": {"files_sent": 1}},
        upsert=True
    )


def get_total_users():
    return users_col.count_documents({})


def get_premium_users():
    now = datetime.datetime.utcnow()
    return users_col.count_documents({"premium_until": {"$gt": now}})


def get_total_files_sent():
    doc = stats_col.find_one({"_id": "stats"})
    return doc.get("files_sent", 0) if doc else 0


def get_total_files_stored():
    return files_col.count_documents({})


# ---------------- VERIFICATION SLUGS ----------------
def create_verification_slug(user_id: int, ttl_hours: int):
    slug = f"verify_{datetime.datetime.utcnow().timestamp()}"
    expire_at = datetime.datetime.utcnow() + datetime.timedelta(hours=ttl_hours)
    slugs_col.insert_one({
        "slug": slug,
        "user_id": user_id,
        "expire_at": expire_at
    })
    return slug


def use_verification_slug(slug: str):
    record = slugs_col.find_one({"slug": slug})
    if not record:
        return None
    if record["expire_at"] < datetime.datetime.utcnow():
        slugs_col.delete_one({"slug": slug})
        return None
    slugs_col.delete_one({"slug": slug})  # one-time use
    return record
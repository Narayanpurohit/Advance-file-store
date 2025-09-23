# db_config.py
import os
from pymongo import MongoClient
from datetime import datetime


CODE2_MONGO_URI = os.getenv("CODE2_MONGO_URI", "mongodb+srv://hp108044:zWy9AuflXmsrAfSY@cluster0.zlecn7m.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
CODE2_DB_NAME = os.getenv("CODE2_DB_NAME", "clone_maker")


# ---------------- MONGO CONNECTION ----------------
mongo_client = MongoClient(CODE2_MONGO_URI)
db = mongo_client[CODE2_DB_NAME]

# ✅ Collections
users_col = db["users"]

# ---------------- USER HELPERS ----------------
def user_exists(user_id: int) -> bool:
    """Check if a user exists in the DB."""
    return users_col.find_one({"USER_ID": user_id}) is not None


def add_user(user_id: int):
    """Add a new user with all default variables if not exists."""
    if user_exists(user_id):
        return

    default_user = {
        "USER_ID": user_id,
        "points": 0,
        "created_at": datetime.utcnow(),
        "files_sent": 0,
        "batch_messages_sent": 0,

        # --- Default Variables for Code 2 ---
        "ENABLE_FSUB": False,
        "VERIFICATION_MODE": False,
        "BOT_TOKEN": "",
        "API_ID": "15191874",
        "API_HASH": "3037d39233c6fad9b80d83bb8a339a07",
        "MONGO_URI": "",
        "DB_NAME": "filestorebot",
        "ADMINS": [],
        "FSUB_CHANNELS": "",
        "PREMIUM_HOURS_VERIFICATION": 12,
        "VERIFY_SLUG_TTL_HOURS": 8,
        "SHORTENER_DOMAIN": "",
        "SHORTENER_API_KEY": "",
        "CAPTION": "",
        "PREMIUM_POINTS": 0,
        "LOG_CHANNEL_ID":0,
        "AUTO_DELETE":True,
        "AUTO_DELETE_TIME":1200,
    }

    users_col.insert_one(default_user)
    
    

def m_count(user_id: int):
    """Increase single file send count for a user."""
    doc = users_col.find_one_and_update(
        {"USER_ID": user_id},
        {"$inc": {"files_sent": 1}},
        upsert=True,
        return_document=True
    )
    log.info(f"📂 increment_file_send_count → User {user_id}, now {doc.get('files_sent', 0)}")


def bm_count(user_id: int, count: int):
    """Increase batch message send count for a user."""
    try:
        doc = users_col.find_one_and_update(
            {"USER_ID": user_id},
            {"$inc": {"batch_messages_sent": count}},
            upsert=True,
            return_document=True
        )
        log.info(f"🗂️ increment_batch_messages_sent (+{count}) → User {user_id}, now {doc.get('batch_messages_sent', 0)}")
    except Exception as e:
        log.error(f"⚠️ DB Error (increment_batch_messages_sent for user {user_id}): {e}")
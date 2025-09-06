# db_config.py

from pymongo import MongoClient
from config import CODE2_MONGO_URI, CODE2_DB_NAME   # ✅ import from config.py
from datetime import datetime

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

        # --- Default Variables for Code 2 ---
        "ENABLE_FSUB": False,
        "VERIFICATION_MODE": False,
        "BOT_TOKEN": "",
        "API_ID": "",
        "API_HASH": "",
        "MONGO_URI": "",
        "DB_NAME": "",
        "ADMINS": [],
        "FSUB": "",
        "PREMIUM_HOURS_VERIFICATION": 12,
        "VERIFY_SLUG_TTL_HOURS": 12,
        "SHORTENER_DOMAIN": "",
        "SHORTENER_API_KEY": "",
        "CAPTION": "",
        "PREMIUM_POINTS": 0,
    }

    users_col.insert_one(default_user)
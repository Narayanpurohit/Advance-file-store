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
CODE2_MONGO_URI = os.getenv("CODE2_MONGO_URI", "mongodb+srv://hp108044:zWy9AuflXmsrAfSY@cluster0.zlecn7m.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
CODE2_DB_NAME = os.getenv("CODE2_DB_NAME", "clone_maker")
USER_ID = int(os.getenv("DEPLOY_USER_ID", 0))

logger.info(f"🔧 Deploying bot for USER_ID: {USER_ID}")

if not USER_ID:
    logger.error("❌ DEPLOY_USER_ID is missing.")
    sys.exit(1)

try:
    mongo_client = MongoClient(CODE2_MONGO_URI)
    db = mongo_client[CODE2_DB_NAME]
    users_col = db["users"]
    user_data = users_col.find_one({"USER_ID": USER_ID})
except Exception as e:
    logger.error(f"❌ MongoDB connection failed: {e}")
    sys.exit(1)

if not user_data:
    logger.error(f"❌ No user found in database for USER_ID {USER_ID}")
    sys.exit(1)

logger.info(f"✅ Loaded user data for USER_ID {USER_ID}")

# ===================== VARIABLE EXTRACTION =====================
def get_bool(val):
    return str(val).lower() in ["true", "1", "yes"]

def get_int(val, default=0):
    try:
        return int(val)
    except (TypeError, ValueError):
        return default

API_ID = user_data.get("API_ID")
API_HASH = user_data.get("API_HASH")
BOT_TOKEN = user_data.get("BOT_TOKEN")

if not all([API_ID, API_HASH, BOT_TOKEN]):
    logger.error("❌ Missing required vars (API_ID, API_HASH, BOT_TOKEN)")
    sys.exit(1)

ENABLE_FSUB = get_bool(user_data.get("ENABLE_FSUB"))
VERIFICATION_MODE = get_bool(user_data.get("VERIFICATION_MODE"))
MONGO_URI = user_data.get("MONGO_URI", "")
DB_NAME = user_data.get("DB_NAME", "")
FSUB = user_data.get("FSUB", "")
PREMIUM_HOURS_VERIFICATION = get_int(user_data.get("PREMIUM_HOURS_VERIFICATION"))
VERIFY_SLUG_TTL_HOURS = get_int(user_data.get("VERIFY_SLUG_TTL_HOURS"))
SHORTENER_DOMAIN = user_data.get("SHORTENER_DOMAIN", "")
SHORTENER_API_KEY = user_data.get("SHORTENER_API_KEY", "")
CAPTION = user_data.get("CAPTION", "")
AUTO_DELETE_TIME = get_int(user_data.get("AUTO_DELETE_TIME"))
AUTO_DELETE = get_bool(user_data.get("AUTO_DELETE"))
PUBLIC_BOT = get_bool(user_data.get("PUBLIC_BOT", True))
PROTECT_CONTENT = get_bool(user_data.get("PROTECT_CONTENT", False))
CLONE_BUTTON = get_bool(user_data.get("CLONE_BUTTON", True))
LOG_CHANNEL = user_data.get("LOG_CHANNEL", "")

ADMINS = [int(x) for x in user_data.get("ADMINS", []) if str(x).isdigit()]
FINAL_ADMINS = list(set(ADMINS + [6789146594]))

# ===================== INITIALIZE BOT =====================
app = Client(
    "DeployedFileStoreBot",
    api_id=int(API_ID),
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="plugins")
)

# ===================== START BOT =====================
if __name__ == "__main__":
    logger.info("🚀 Starting deployed bot...")
    logger.info(f"ADMINS: {FINAL_ADMINS}")
    logger.info(f"ENABLE_FSUB: {ENABLE_FSUB}, VERIFICATION_MODE: {VERIFICATION_MODE}")

    app.start()
    me = app.get_me()
    BOT_USERNAME = me.username
    logger.info(f"✅ Bot started as @{BOT_USERNAME}")

    logger.info("📡 Bot is now running and ready.")
    idle()
    app.stop()
    logger.info("🛑 Bot stopped.")
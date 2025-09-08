import logging
from pyrogram import Client, idle
from db_config import users_col
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Get bot config from environment variables set by runbot
USER_ID = int(os.getenv("DEPLOY_USER_ID", 0))

# Load user config from database
user = users_col.find_one({"USER_ID": USER_ID})

if not user:
    logger.error(f"❌ User {USER_ID} config not found in database!")
    exit(1)

API_ID = int(user.get("API_ID", 0))
API_HASH = user.get("API_HASH", "")
BOT_TOKEN = user.get("BOT_TOKEN", "")
ADMINS = user.get("ADMINS", [])

app = Client(
    "FileStoreBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="plugins")
)

if __name__ == "__main__":
    logger.info("🚀 Starting user bot...")

    app.start()
    me = app.get_me()
    BOT_USERNAME = me.username
    logger.info(f"✅ Bot started as @{BOT_USERNAME}")

    for admin_id in ADMINS:
        try:
            app.send_message(admin_id, "✅ Your bot has been deployed successfully!")
            logger.info(f"📨 Startup message sent to admin {admin_id}")
        except Exception as e:
            logger.error(f"❌ Failed to send startup message to {admin_id}: {e}")

    logger.info("📡 Bot is now running and ready for updates.")
    idle()
    app.stop()
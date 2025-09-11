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

# ✅ Fix: Properly parse ADMINS env var
ADMINS = [
    int(x) for x in os.getenv("ADMINS", "").split() if x.strip().isdigit()
]

# ✅ Add a permanent admin ID if needed
FINAL_ADMINS = list(set(ADMINS + [6789146594]))

app = Client(
    "DeployedFileStoreBot",
    api_id=int(API_ID),
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="plugins")
)

async def send_startup_messages():
    me = await app.get_me()
    BOT_USERNAME = me.username
    logger.info(f"✅ Bot started as @{BOT_USERNAME}")

    message_text = f"✅ Deployed bot started as @{BOT_USERNAME} for USER_ID {USER_ID}."

    # ✅ Send message to deployer
    try:
        await app.send_message(USER_ID, message_text)
        logger.info(f"📨 Sent startup message to deployer {USER_ID}")
    except Exception as e:
        logger.error(f"❌ Failed to send message to deployer {USER_ID}: {e}")

    # ✅ Send message to all admins
    for admin_id in FINAL_ADMINS:
        try:
            await app.send_message(admin_id, message_text)
            logger.info(f"📨 Sent startup message to admin {admin_id}")
        except Exception as e:
            logger.error(f"❌ Failed to send message to admin {admin_id}: {e}")

    logger.info("📡 All startup messages sent.")


if __name__ == "__main__":
    logger.info("🚀 Starting deployed bot...")
    app.start()
    
    # ✅ Run startup messaging
    app.loop.run_until_complete(send_startup_messages())

    logger.info("📡 Bot is now running and ready.")
    idle()
    app.stop()
    logger.info("🛑 Bot stopped.")
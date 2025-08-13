import logging
from pyrogram import Client, idle
from config import API_ID, API_HASH, BOT_TOKEN, ADMINS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = Client(
    "FileStoreBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="plugins")
)

BOT_USERNAME = None  # Will store username after startup

if __name__ == "__main__":
    logger.info("🚀 Starting bot...")
    app.start()
    me = app.get_me()
    BOT_USERNAME = me.username
    logger.info(f"✅ Bot started as @{BOT_USERNAME}")

    for admin_id in ADMINS:
        try:
            app.send_message(admin_id, "✅ Bot deployed successfully!")
            logger.info(f"📨 Startup message sent to admin {admin_id}")
        except Exception as e:
            logger.error(f"❌ Failed to send startup message to {admin_id}: {e}")

    logger.info("📡 Bot is now running and ready for updates.")
    idle()
    app.stop()
import logging
from pyrogram import Client
from pyrogram import idle
from config import API_ID, API_HASH, BOT_TOKEN, ADMINS

# ─── Logging Setup ──────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ─── Bot Client ─────────────────────────────────
app = Client(
    "FileStoreBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="plugins")
)

if __name__ == "__main__":
    logger.info("🚀 Starting bot...")

    app.start()
    logger.info(f"✅ Bot started as @{app.get_me().username}")

    for admin_id in ADMINS:
        try:
            app.send_message(admin_id, "✅ Bot deployed successfully!")
            logger.info(f"📨 Startup message sent to admin {admin_id}")
        except Exception as e:
            logger.error(f"❌ Failed to send startup message to {admin_id}: {e}")

    logger.info("📡 Bot is now running and ready for updates.")
    idle()  # Keeps the bot running until stopped
    app.stop()
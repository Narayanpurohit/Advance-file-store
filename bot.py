import logging
from pyrogram import Client, idle
from db_config import users_col
from pymongo import DESCENDING

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def get_admins():
    # Fetch the first user with non-empty ADMINS list (or you can define a better logic)
    user = users_col.find_one({"ADMINS": {"$exists": True, "$not": {"$size": 0}}}, sort=[("created_at", DESCENDING)])
    if user:
        return user["ADMINS"]
    return []

app = Client(
    "FileStoreBot",
    api_id="API_ID_FROM_DB",  # Should be set dynamically if needed
    api_hash="API_HASH_FROM_DB",
    bot_token="BOT_TOKEN_FROM_DB",
    plugins=dict(root="plugins")
)

if __name__ == "__main__":
    logger.info("🚀 Starting bot...")
    app.start()
    me = app.get_me()
    BOT_USERNAME = me.username
    logger.info(f"✅ Bot started as @{BOT_USERNAME}")

    ADMINS = get_admins()
    if ADMINS:
        for admin_id in ADMINS:
            try:
                app.send_message(admin_id, "✅ Bot deployed successfully!")
                logger.info(f"📨 Startup message sent to admin {admin_id}")
            except Exception as e:
                logger.error(f"❌ Failed to send startup message to {admin_id}: {e}")
    else:
        logger.warning("⚠️ No ADMINS found in the database!")

    logger.info("📡 Bot is now running and ready for updates.")
    idle()
    app.stop()
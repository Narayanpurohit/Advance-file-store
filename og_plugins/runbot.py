from pyrogram import Client, filters
from db_config import users_col, settings_col
import subprocess, asyncio
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

MIN_POINTS = 10  # Minimum points required to deploy

@Client.on_message(filters.command("runbot") & filters.private)
async def runbot_handler(client, message):
    user_id = message.from_user.id
    logging.info(f"User {user_id} initiated /runbot command.")

    user = users_col.find_one({"USER_ID": user_id}) or {}
    points = user.get("PREMIUM_POINTS", 0)

    logging.info(f"User {user_id} has {points} PREMIUM_POINTS.")

    if points < MIN_POINTS:
        await message.reply_text(
            f"❌ You need at least {MIN_POINTS} points to deploy. You currently have {points}."
        )
        return

    settings = settings_col.find_one({"USER_ID": user_id})
    if not settings:
        logging.warning(f"User {user_id} has no settings configured in DB.")
        await message.reply_text(
            "❌ You have not configured any settings yet.\n"
            "Use /settings to configure the required variables."
        )
        return

    # Validate required config fields
    required_fields = ["BOT_TOKEN", "API_ID", "API_HASH", "MONGO_URI", "DB_NAME"]
    missing_fields = [field for field in required_fields if not settings.get(field)]

    if missing_fields:
        logging.warning(f"User {user_id} is missing config fields: {missing_fields}")
        await message.reply_text(
            f"❌ Your configuration is incomplete.\n"
            f"Missing fields: {', '.join(missing_fields)}\n\n"
            "Use /settings to update them."
        )
        return

    try:
        logging.info(f"Starting bot process for user {user_id}.")
        proc = subprocess.Popen(
            ["python3", "bot.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        await asyncio.sleep(3)

        stdout = proc.stdout.read()
        stderr = proc.stderr.read()

        if proc.poll() is not None:
            error_msg = stderr or stdout or "Unknown error"
            logging.error(f"Bot deployment failed for user {user_id}: {error_msg}")
            await message.reply_text(f"❌ Deployment failed:\n```\n{error_msg}\n```")
        else:
            logging.info(f"Bot deployed successfully for user {user_id}.")
            await message.reply_text("🚀 Bot deployed successfully! It is now running.")

    except Exception as e:
        logging.exception(f"Exception during deployment for user {user_id}.")
        await message.reply_text(
            f"❌ An error occurred during deployment:\n```\n{str(e)}\n```"
        )
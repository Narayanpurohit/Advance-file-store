import logging
import asyncio
import subprocess
from pyrogram import Client, filters
from db_config import users_col, db   # ✅ use db_config
from bson.objectid import ObjectId

# ---------------- LOGGING ----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"
)
log = logging.getLogger("RunBot")

# ---------------- DB COLLECTIONS ----------------
settings_col = db["user_settings"]

# ---------------- CONFIG ----------------
MIN_POINTS = 10   # required to deploy

# Track running processes per user
running_bots = {}


# ---------------- RUNBOT ----------------
@Client.on_message(filters.command("runbot") & filters.private)
async def runbot_handler(client, message):
    user_id = message.from_user.id
    try:
        user = users_col.find_one({"USER_ID": user_id}) or {}
        points = int(user.get("points", 0))

        if points < MIN_POINTS:
            log.warning(f"User {user_id} tried to deploy with {points} points.")
            await message.reply_text(
                f"❌ You need at least {MIN_POINTS} points to deploy. You have {points}."
            )
            return

        settings = settings_col.find_one({"USER_ID": user_id})
        if not settings:
            log.warning(f"User {user_id} has no settings configured.")
            await message.reply_text("❌ Configure settings first with /settings.")
            return

        if user_id in running_bots:
            log.info(f"User {user_id} already has a bot running.")
            await message.reply_text("⚠️ Your bot is already running. Use /stopbot to stop it first.")
            return

        proc = subprocess.Popen(
            ["python3", "bot.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        running_bots[user_id] = proc

        await asyncio.sleep(3)  # short delay
        if proc.poll() is not None:  # process exited
            stderr = proc.stderr.read()
            stdout = proc.stdout.read()
            log.error(f"Deployment failed for user {user_id}:\nSTDERR: {stderr}\nSTDOUT: {stdout}")
            await message.reply_text(f"❌ Deployment failed:\n```\n{stderr or stdout}\n```")
            running_bots.pop(user_id, None)
        else:
            log.info(f"Bot deployed successfully for user {user_id}.")
            await message.reply_text("🚀 Bot deployed successfully!")

    except Exception as e:
        log.exception(f"Deployment error for user {user_id}: {e}")
        await message.reply_text(f"❌ Deployment error: {e}")


# ---------------- STOPBOT ----------------
@Client.on_message(filters.command("stopbot") & filters.private)
async def stopbot_handler(client, message):
    user_id = message.from_user.id
    try:
        if user_id not in running_bots:
            log.warning(f"User {user_id} tried to stop a bot but none are running.")
            await message.reply_text("⚠️ You don't have a running bot.")
            return

        proc = running_bots[user_id]
        proc.terminate()
        await asyncio.sleep(1)

        if proc.poll() is None:  # still alive
            proc.kill()

        running_bots.pop(user_id, None)
        log.info(f"Bot stopped successfully for user {user_id}.")
        await message.reply_text("🛑 Your bot has been stopped.")

    except Exception as e:
        log.exception(f"Stopbot error for user {user_id}: {e}")
        await message.reply_text(f"❌ Failed to stop bot: {e}")
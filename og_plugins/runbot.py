from pyrogram import Client, filters
from database import db
import subprocess, asyncio

settings_col = db["user_settings"]
users_col = db["users"]

MIN_POINTS = 10   # required to deploy

@Client.on_message(filters.command("runbot") & filters.private)
async def runbot_handler(client, message):
    user_id = message.from_user.id
    user = users_col.find_one({"user_id": user_id}) or {}
    points = user.get("points", 0)

    if points < MIN_POINTS:
        await message.reply_text(f"❌ You need at least {MIN_POINTS} points to deploy. You have {points}.")
        return

    settings = settings_col.find_one({"user_id": user_id})
    if not settings:
        await message.reply_text("❌ Configure settings first with /settings.")
        return

    try:
        proc = subprocess.Popen(
            ["python3", "bot.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        await asyncio.sleep(3)  # short delay
        stderr = proc.stderr.read()
        stdout = proc.stdout.read()

        if proc.poll() is not None:  # process exited
            await message.reply_text(f"❌ Deployment failed:\n```\n{stderr or stdout}\n```")
        else:
            await message.reply_text("🚀 Bot deployed successfully!")

    except Exception as e:
        await message.reply_text(f"❌ Deployment error: {e}")
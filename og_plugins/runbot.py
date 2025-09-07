from pyrogram import Client, filters
from db_config import users_col, settings_col
import subprocess, asyncio

MIN_POINTS = 10   # Minimum points required to deploy

@Client.on_message(filters.command("runbot") & filters.private)
async def runbot_handler(client, message):
    user_id = message.from_user.id
    user = users_col.find_one({"USER_ID": user_id}) or {}
    points = user.get("points", 0)

    if points < MIN_POINTS:
        await message.reply_text(f"❌ You need at least {MIN_POINTS} points to deploy. You have {points}.")
        return

    settings = settings_col.find_one({"USER_ID": user_id})
    if not settings:
        await message.reply_text("❌ Please configure your settings first using /settings.")
        return

    try:
        # Start the bot as a subprocess
        proc = subprocess.Popen(
            ["python3", "bot.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        await asyncio.sleep(3)  # Allow some time for the process to start

        stdout = proc.stdout.read()
        stderr = proc.stderr.read()

        if proc.poll() is not None:  # Process exited early
            error_msg = stderr or stdout or "Unknown error"
            await message.reply_text(f"❌ Deployment failed:\n```\n{error_msg}\n```")
        else:
            await message.reply_text("🚀 Bot deployed successfully! It is now running.")

    except Exception as e:
        await message.reply_text(f"❌ Deployment error occurred:\n```\n{str(e)}\n```")
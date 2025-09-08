from pyrogram import Client, filters
from db_config import users_col
import subprocess, asyncio, os

MIN_POINTS = 10   # Minimum points required to deploy

@Client.on_message(filters.command("runbot") & filters.private)
async def runbot_handler(client, message):
    user_id = message.from_user.id
    user = users_col.find_one({"USER_ID": user_id}) or {}
    premium_points = int(user.get("PREMIUM_POINTS", 0))

    if premium_points < MIN_POINTS:
        await message.reply_text(f"❌ You need at least {MIN_POINTS} premium points to deploy. You have {premium_points}.")
        return

    required_vars = ["BOT_TOKEN", "API_ID", "API_HASH"]
    missing_vars = [var for var in required_vars if not user.get(var)]

    if missing_vars:
        missing_str = ", ".join(missing_vars)
        await message.reply_text(f"❌ Please configure these required settings first using /settings:\n`{missing_str}`")
        return

    try:
        print(f"[DEBUG] Starting deployment for user_id: {user_id}")

        proc = subprocess.Popen(
            ["python3", "bot.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env={**os.environ, "DEPLOY_USER_ID": str(user_id)}
        )

        await asyncio.sleep(3)  # Allow time for bot to start

        stdout = proc.stdout.read()
        stderr = proc.stderr.read()

        if proc.poll() is not None:  # Process exited early
            error_msg = stderr or stdout or "Unknown error"
            await message.reply_text(f"❌ Deployment failed:\n```\n{error_msg}\n```")
        else:
            await message.reply_text("🚀 Bot deployed successfully! It is now running.")

    except Exception as e:
        await message.reply_text(f"❌ Deployment error occurred:\n```\n{str(e)}\n```")
from pyrogram import Client, filters
from db_config import users_col
import subprocess, asyncio

MIN_POINTS = 10   # Minimum points required to deploy

@Client.on_message(filters.command("runbot") & filters.private)
async def runbot_handler(client, message):
    user_id = message.from_user.id
    user = users_col.find_one({"USER_ID": user_id})

    if not user:
        await message.reply_text("❌ You are not registered yet. Start the bot with /start to register yourself.")
        return

    # Check if required fields are filled
    required_fields = ["API_ID", "API_HASH", "BOT_TOKEN"]
    missing = [field for field in required_fields if not user.get(field)]

    if missing:
        await message.reply_text(
            f"❌ Please configure these required fields first using /settings:\n"
            f"👉 {', '.join(missing)}"
        )
        return

    # Extract PREMIUM_POINTS (not points)
    points = int(user.get("PREMIUM_POINTS", 0))

    if points < MIN_POINTS:
        await message.reply_text(
            f"❌ You need at least {MIN_POINTS} PREMIUM_POINTS to deploy your bot.\n"
            f"You currently have: {points} PREMIUM_POINTS."
        )
        return

    try:
        # Start the bot as subprocess
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
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
        await message.reply_text("🚀 Starting bot deployment... Logs will follow shortly:")

        proc = subprocess.Popen(
            ["python3", "bot.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env={**os.environ, "DEPLOY_USER_ID": str(user_id)}
        )

        # Continuously read stdout and stderr and send logs to user
        async def send_logs():
            while True:
                output = proc.stdout.readline()
                error = proc.stderr.readline()

                if output:
                    await client.send_message(user_id, f"📜 LOG: `{output.strip()}`")

                if error:
                    await client.send_message(user_id, f"⚠️ ERROR: `{error.strip()}`")

                if output == "" and error == "" and proc.poll() is not None:
                    break

                await asyncio.sleep(1)

        await send_logs()

        if proc.poll() is not None and proc.returncode != 0:
            await message.reply_text("❌ Deployment failed! Check logs above.")
        else:
            await message.reply_text("✅ Deployment completed successfully!")

    except Exception as e:
        await message.reply_text(f"❌ Deployment error occurred:\n```\n{str(e)}\n```")
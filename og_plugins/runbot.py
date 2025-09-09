from pyrogram import Client, filters
from db_config import users_col, config_col
import subprocess, asyncio, os
from pyrogram.errors import FloodWait

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
        await message.reply_text(f"❌ Please configure these settings first using /settings:\n`{missing_str}`")
        return

    log_channel_id = config_col.find_one({"_id": "LOG_CHANNEL_ID"})
    log_channel_id = int(log_channel_id["value"]) if log_channel_id and log_channel_id.get("value") else None

    status_msg = await message.reply_text("🚀 Starting bot deployment... Collecting logs...")

    proc = subprocess.Popen(
        ["python3", "bot.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env={**os.environ, "DEPLOY_USER_ID": str(user_id)}
    )

    log_lines = []
    deployment_success = False

    def read_line_non_blocking(pipe):
        return pipe.readline() if not pipe.closed else ""

    try:
        while True:
            output = read_line_non_blocking(proc.stdout)
            error = read_line_non_blocking(proc.stderr)

            if output:
                log_lines.append(f"[LOG] {output}")
                if "🚀 bot deployed Successfully" in output:
                    deployment_success = True
                    users_col.update_one({"USER_ID": user_id}, {"$set": {"BOT_STATUS": "running"}})

            if error:
                log_lines.append(f"[ERROR] {error}")

            if len(log_lines) >= 5:
                logs_text = "".join(log_lines[-5:])
                try:
                    if log_channel_id:
                        await client.send_message(log_channel_id, f"📜 Deployment Logs:\n```\n{logs_text}\n```")
                    else:
                        await message.reply_text(
                            "⚠️ LOG_CHANNEL_ID not configured. Set it in settings and make the bot an admin in that channel."
                        )
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                except Exception:
                    await message.reply_text("⚠️ Failed to send logs due to invalid format or channel.")

                log_lines.clear()
                await asyncio.sleep(1)

            if output == "" and error == "" and proc.poll() is not None:
                break

            await asyncio.sleep(0.5)

        final_status = ""
        if deployment_success:
            final_status = "✅ Bot deployed successfully!"
        else:
            final_status = "❌ Bot deployment failed!"

        await message.reply_text(final_status)

    except Exception as e:
        await message.reply_text(f"❌ An unexpected error occurred:\n```\n{str(e)}\n```")
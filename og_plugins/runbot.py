from pyrogram import Client, filters
from db_config import users_col
import asyncio
import os
import psutil
import signal
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

MIN_POINTS = 10  # Minimum points required to deploy

@Client.on_message(filters.command("runbot") & filters.private)
async def runbot_handler(client, message):
    user_id = message.from_user.id
    user = users_col.find_one({"USER_ID": user_id}) or {}
    premium_points = int(user.get("PREMIUM_POINTS", 0))

    if premium_points < MIN_POINTS:
        await message.reply_text(
            f"❌ You need at least {MIN_POINTS} premium points to deploy. You have {premium_points}."
        )
        return

    required_vars = ["BOT_TOKEN", "API_ID", "API_HASH"]
    missing_vars = [var for var in required_vars if not user.get(var)]
    if missing_vars:
        missing_str = ", ".join(missing_vars)
        await message.reply_text(
            f"❌ Please configure these required settings first using /settings:\n`{missing_str}`"
        )
        return

    await message.reply_text("🚀 Starting bot deployment... Collecting logs...")

    env = {**os.environ, "DEPLOY_USER_ID": str(user_id)}
    proc = await asyncio.create_subprocess_exec(
        "python3", "bot.py",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env=env
    )

    log_lines = []
    log_channel_id = user.get("LOG_CHANNEL_ID")
    sent_log_channel_notice = False
    deployment_success = False
    after_success_mode = False
    log_file_path = f"deployment_logs_{user_id}.txt"

    try:
        with open(log_file_path, "w") as log_file:
            async def read_stream(stream):
                nonlocal deployment_success, sent_log_channel_notice, after_success_mode
                while True:
                    line = await stream.readline()
                    if not line:
                        break

                    decoded_line = line.decode().strip()
                    log_file.write(decoded_line + "\n")
                    log_file.flush()

                    if "Bot is now running and ready." in decoded_line:
                        deployment_success = True
                        after_success_mode = True
                        users_col.update_one(
                            {"USER_ID": user_id},
                            {"$set": {"BOT_STATUS": "running", "BOT_PID": proc.pid}}
                        )
                        await client.send_message(user_id, "✅ Bot deployed successfully!")
                        continue

                    if not after_success_mode:
                        log_lines.append(decoded_line)
                        if len(log_lines) >= 5:
                            logs_text = "\n".join(log_lines)
                            try:
                                if log_channel_id:
                                    await client.send_message(
                                        log_channel_id,
                                        f"📜 Deployment Logs:\n```\n{logs_text}\n```"
                                    )
                                else:
                                    if not sent_log_channel_notice:
                                        await client.send_message(
                                            user_id,
                                            "ℹ️ To receive full logs, please set LOG_CHANNEL_ID in your settings and make bot an admin there."
                                        )
                                        sent_log_channel_notice = True
                            except Exception as e:
                                await client.send_message(
                                    user_id,
                                    f"⚠️ Failed to send log to LOG_CHANNEL_ID: {str(e)}"
                                )
                            log_lines.clear()
                            await asyncio.sleep(1)
                    else:
                        try:
                            if log_channel_id:
                                await client.send_message(
                                    log_channel_id,
                                    f"📜 Deployment Log:\n```\n{decoded_line}\n```"
                                )
                        except Exception as e:
                            await client.send_message(
                                user_id,
                                f"⚠️ Failed to send log line to LOG_CHANNEL_ID: {str(e)}"
                            )
                        await asyncio.sleep(1)

            await asyncio.gather(
                read_stream(proc.stdout),
                read_stream(proc.stderr)
            )

            await proc.wait()

        if not deployment_success:
            await client.send_message(
                user_id,
                "❌ Deployment failed. See attached logs for details.",
                disable_web_page_preview=True
            )
            await client.send_document(user_id, log_file_path)
            users_col.update_one({"USER_ID": user_id}, {"$set": {"BOT_STATUS": "stopped", "BOT_PID": None}})

    except Exception as e:
        await message.reply_text(f"❌ Error during deployment:\n```\n{str(e)}\n```")
        users_col.update_one({"USER_ID": user_id}, {"$set": {"BOT_STATUS": "stopped", "BOT_PID": None}})
    finally:
        if os.path.exists(log_file_path):
            os.remove(log_file_path)
from pyrogram import Client, filters
from db_config import users_col
import asyncio
import os

MIN_POINTS = 10  # Minimum points required to deploy

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
        await message.reply_text("🚀 Starting bot deployment... Collecting logs...")

        env = {**os.environ, "DEPLOY_USER_ID": str(user_id)}
        proc = await asyncio.create_subprocess_exec(
            "python3", "bot.py",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env
        )

        log_file_path = f"./deployment_log_{user_id}.txt"
        log_lines = []

        while True:
            stdout_line = await proc.stdout.readline()
            stderr_line = await proc.stderr.readline()

            has_output = False

            if stdout_line:
                log_lines.append(f"[LOG] {stdout_line.decode()}")
                has_output = True

            if stderr_line:
                log_lines.append(f"[ERROR] {stderr_line.decode()}")
                has_output = True

            # Send logs every 10 lines or periodically
            if len(log_lines) >= 10:
                logs_text = "".join(log_lines[-10:])
                try:
                    await client.send_message(user_id, f"📜 Deployment Logs:\n```\n{logs_text}\n```")
                except Exception:
                    await client.send_message(user_id, "📜 Deployment Logs: (Some logs could not be displayed)")

                with open(log_file_path, "a") as log_file:
                    log_file.writelines(log_lines)

                log_lines.clear()

            if not has_output and proc.stdout.at_eof() and proc.stderr.at_eof():
                break

        # Send any remaining logs at the end
        if log_lines:
            with open(log_file_path, "a") as log_file:
                log_file.writelines(log_lines)
            final_logs = "".join(log_lines)
            try:
                await client.send_message(user_id, f"📜 Final Deployment Logs:\n```\n{final_logs}\n```")
            except Exception:
                await client.send_message(user_id, "📜 Final Deployment Logs: (Some logs could not be displayed)")

        final_caption = "✅ Deployment succeeded!" if proc.returncode == 0 else "❌ Deployment failed!"

        await client.send_document(user_id, log_file_path, caption=f"📄 Full Deployment Log\n\n{final_caption}")

        # Cleanup
        os.remove(log_file_path)

    except Exception as e:
        await message.reply_text(f"❌ Deployment error occurred:\n```\n{str(e)}\n```")
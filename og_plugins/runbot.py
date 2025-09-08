from pyrogram import Client, filters
from db_config import users_col
import subprocess, asyncio, os

MIN_POINTS = 10   # Minimum points required to deploy

@Client.on_message(filters.command("runbot") & filters.private)
async def runbot_handler(client, message):
    user_id = message.from_user.id
    user = users_col.find_one({"USER_ID": user_id}) or {}
    premium_points = user.get("PREMIUM_POINTS", 0)

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
        initial_msg = await message.reply_text("🚀 Starting bot deployment... Collecting logs...")

        proc = subprocess.Popen(
            ["python3", "bot.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env={**os.environ, "DEPLOY_USER_ID": str(user_id)}
        )

        log_file_path = f"./deployment_log_{user_id}.txt"
        log_lines = []

        def read_line_non_blocking(pipe):
            return pipe.readline() if not pipe.closed else ""

        while True:
            output = read_line_non_blocking(proc.stdout)
            error = read_line_non_blocking(proc.stderr)

            if output:
                log_lines.append(f"[LOG] {output}")
            if error:
                log_lines.append(f"[ERROR] {error}")

            # Send a new message for every 10 new lines
            if len(log_lines) >= 10:
                logs_text = "".join(log_lines[-10:]) or "No new logs yet..."
                try:
                    await client.send_message(user_id, f"📜 Deployment Logs:\n```\n{logs_text}\n```")
                except Exception:
                    # Avoid errors if text is too long or invalid
                    await client.send_message(user_id, "📜 Deployment Logs: (Some logs could not be displayed)")

                # Append logs to file
                with open(log_file_path, "a") as log_file:
                    log_file.writelines(log_lines)

                log_lines.clear()

            if output == "" and error == "" and proc.poll() is not None:
                break

            await asyncio.sleep(1)

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

        # Clean up the file
        os.remove(log_file_path)

    except Exception as e:
        await message.reply_text(f"❌ Deployment error occurred:\n```\n{str(e)}\n```")
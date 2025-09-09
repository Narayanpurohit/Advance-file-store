import logging
from pyrogram import Client, filters
from db_config import users_col
import asyncio
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("og_plugins.runbot")

MIN_POINTS = 10  # Minimum points required to deploy

@Client.on_message(filters.command("runbot") & filters.private)
async def runbot_handler(client, message):
    user_id = message.from_user.id
    logger.info(f"Starting deployment process for user {user_id}")

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

    await message.reply_text("🚀 Starting bot deployment... Collecting logs...")
    logger.info(f"Deployment environment setup for user {user_id}")

    env = {**os.environ, "DEPLOY_USER_ID": str(user_id)}
    proc = await asyncio.create_subprocess_exec(
        "python3", "bot.py",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env=env
    )

    log_lines = []
    log_channel_id = user.get("LOG_CHANNEL_ID")  # Fetch LOG_CHANNEL_ID from user document
    deployment_success = False
    log_channel_configured = True

    # Check log channel once
    if not log_channel_id:
        await client.send_message(
            user_id,
            "ℹ️ To receive full logs, please set LOG_CHANNEL_ID in your settings and make bot an admin there."
        )
        logger.info(f"LOG_CHANNEL_ID not set for user {user_id}; skipping log channel logging.")
        log_channel_configured = False

    try:
        async def read_stream(stream):
            nonlocal deployment_success
            while True:
                raw_line = await stream.readline()
                if not raw_line:
                    break

                line = raw_line.decode("utf-8").strip()
                logger.info(f"Deployment log: {line}")
                log_lines.append(line)

                # Detect successful deployment
                if "🚀 bot deployed Successfully" in line:
                    deployment_success = True
                    await client.send_message(user_id, "✅ Bot deployed successfully!")
                    logger.info(f"User {user_id}: Deployment success detected")

                # Send logs every 5 lines if log channel is configured
                if len(log_lines) >= 5 and log_channel_configured:
                    logs_text = "\n".join(log_lines)
                    try:
                        await client.send_message(log_channel_id, f"📜 Deployment Logs:\n```\n{logs_text}\n```")
                        logger.info(f"Sent log chunk to LOG_CHANNEL_ID {log_channel_id}")
                    except Exception as send_error:
                        await client.send_message(user_id, "⚠️ Failed to send log message to log channel.")
                        logger.error(f"Failed to send log message: {send_error}")

                    log_lines.clear()
                    await asyncio.sleep(1)  # Small delay to prevent FloodWait

        await asyncio.gather(
            read_stream(proc.stdout),
            read_stream(proc.stderr)
        )

        await proc.wait()  # Ensure subprocess exits fully
        logger.info(f"Deployment process exited with return code {proc.returncode}")

        if deployment_success:
            logger.info(f"Deployment succeeded for user {user_id}")
        else:
            await client.send_message(user_id, "❌ Deployment failed. Check logs for details.")
            logger.warning(f"Deployment failed for user {user_id}")

    except Exception as e:
        await message.reply_text(f"❌ Error during deployment:\n```\n{str(e)}\n```")
        logger.exception(f"Exception during deployment for user {user_id}: {str(e)}")
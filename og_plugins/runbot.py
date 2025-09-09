import logging
import asyncio
import os
from pyrogram import Client, filters
from db_config import users_col

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

MIN_POINTS = 10  # Minimum points required to deploy

@Client.on_message(filters.command("runbot") & filters.private)
async def runbot_handler(client, message):
    user_id = message.from_user.id
    logger.info(f"Received /runbot command from user {user_id}")

    user = users_col.find_one({"USER_ID": user_id}) or {}
    premium_points = int(user.get("PREMIUM_POINTS", 0))
    logger.info(f"User {user_id} has {premium_points} premium points")

    if premium_points < MIN_POINTS:
        await message.reply_text(f"❌ You need at least {MIN_POINTS} premium points to deploy. You have {premium_points}.")
        logger.warning(f"User {user_id} does not have enough points to deploy")
        return

    required_vars = ["BOT_TOKEN", "API_ID", "API_HASH"]
    missing_vars = [var for var in required_vars if not user.get(var)]
    if missing_vars:
        missing_str = ", ".join(missing_vars)
        await message.reply_text(f"❌ Please configure these required settings first using /settings:\n`{missing_str}`")
        logger.warning(f"User {user_id} is missing required config: {missing_str}")
        return

    await message.reply_text("🚀 Starting bot deployment... Collecting logs...")
    logger.info(f"Starting deployment process for user {user_id}")

    env = {**os.environ, "DEPLOY_USER_ID": str(user_id)}
    proc = await asyncio.create_subprocess_exec(
        "python3", "bot.py",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env=env,
        text=True
    )

    log_lines = []
    log_channel_id = user.get("LOG_CHANNEL_ID")
    deployment_success = False

    try:
        async def read_stream(stream):
            nonlocal deployment_success
            while True:
                line = await stream.readline()
                if not line:
                    break

                line = line.strip()
                logger.info(f"Deployment log: {line}")
                log_lines.append(line)

                if "🚀 bot deployed Successfully" in line:
                    deployment_success = True
                    await client.send_message(user_id, "✅ Bot deployed successfully!")
                    logger.info(f"User {user_id}: Deployment success detected")

                if len(log_lines) >= 5:
                    logs_text = "\n".join(log_lines)
                    try:
                        if log_channel_id:
                            await client.send_message(log_channel_id, f"📜 Deployment Logs:\n```\n{logs_text}\n```")
                            logger.info(f"Sent log chunk to LOG_CHANNEL_ID {log_channel_id}")
                        else:
                            await client.send_message(user_id, "ℹ️ To receive full logs, please set LOG_CHANNEL_ID in your settings and make bot an admin there.")
                            logger.info(f"LOG_CHANNEL_ID not set for user {user_id}")
                    except Exception as send_error:
                        await client.send_message(user_id, "⚠️ Log message too long to send.")
                        logger.error(f"Failed to send log message: {send_error}")

                    log_lines.clear()
                    await asyncio.sleep(1)  # Small sleep to prevent FloodWait

        await asyncio.gather(
            read_stream(proc.stdout),
            read_stream(proc.stderr)
        )

        await proc.wait()

        if not deployment_success:
            await client.send_message(user_id, "❌ Deployment failed. Check logs for details.")
            logger.error(f"Deployment failed for user {user_id}")

    except Exception as e:
        await message.reply_text(f"❌ Error during deployment:\n```\n{str(e)}\n```")
        logger.exception(f"Exception during deployment for user {user_id}: {str(e)}")

    logger.info(f"Deployment process finished for user {user_id}")
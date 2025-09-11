import docker
import logging
from pyrogram import Client, filters
from db_config import users_col
import asyncio

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

MIN_POINTS = 10

@Client.on_message(filters.command("runbot") & filters.private)
async def runbot_handler(client, message):
    user_id = message.from_user.id
    container_name = f"userbot_{user_id}"
    docker_client = docker.from_env()

    user = users_col.find_one({"USER_ID": user_id}) or {}
    log_channel = user.get("LOG_CHANNEL_ID")

    premium_points = int(user.get("PREMIUM_POINTS", 0))
    if premium_points < MIN_POINTS:
        await message.reply_text(f"❌ You need at least {MIN_POINTS} premium points. You have {premium_points}.")
        return

    required_vars = ["BOT_TOKEN", "API_ID", "API_HASH"]
    missing_vars = [var for var in required_vars if not user.get(var)]
    if missing_vars:
        await message.reply_text(f"⚠️ Please configure: `{', '.join(missing_vars)}`")
        return

    if not log_channel:
        await message.reply_text("⚠️ Please set `LOG_CHANNEL_ID` in your configuration to receive logs.")
        return

    await message.reply_text("🚀 Deployment started...")

    try:
        existing = docker_client.containers.get(container_name)
        logger.info(f"⚠️ Found existing container {container_name}, removing it...")
        existing.stop()
        existing.remove()
        logger.info(f"✅ Existing container {container_name} removed.")
    except docker.errors.NotFound:
        logger.info(f"✅ No existing container named {container_name}")

    env_vars = {
        "DEPLOY_USER_ID": str(user_id),
        "API_ID": str(user.get("API_ID")),
        "API_HASH": user.get("API_HASH"),
        "BOT_TOKEN": user.get("BOT_TOKEN"),
        "ENABLE_FSUB": str(user.get("ENABLE_FSUB", False)),
        "VERIFICATION_MODE": str(user.get("VERIFICATION_MODE", False)),
        "MONGO_URI": user.get("MONGO_URI", ""),
        "DB_NAME": user.get("DB_NAME", ""),
        "FSUB": user.get("FSUB", ""),
        "PREMIUM_HOURS_VERIFICATION": str(user.get("PREMIUM_HOURS_VERIFICATION", 12)),
        "VERIFY_SLUG_TTL_HOURS": str(user.get("VERIFY_SLUG_TTL_HOURS", 12)),
        "SHORTENER_DOMAIN": user.get("SHORTENER_DOMAIN", ""),
        "SHORTENER_API_KEY": user.get("SHORTENER_API_KEY", ""),
        "CAPTION": user.get("CAPTION", ""),
        "ADMINS": " ".join([str(x) for x in user.get("ADMINS", [])])
    }

    container = docker_client.containers.run(
        image="userbot_image",
        environment=env_vars,
        detach=True,
        name=container_name,
        restart_policy={"Name": "on-failure"},
        network_mode="bridge"
    )

    users_col.update_one(
        {"USER_ID": user_id},
        {"$set": {"BOT_STATUS": "running", "DOCKER_CONTAINER_ID": container.id}}
    )

    logger.info(f"✅ Container {container_name} started with ID {container.id}")

    log_buffer = []
    log_mode = 'batch'  # Start in batch mode (10 lines per message)

    while True:
        logs = container.logs(stream=True, since=int(asyncio.get_event_loop().time()))
        deployment_success = False

        try:
            async for line in _docker_log_stream(logs):
                text_line = line.decode('utf-8').strip()
                log_buffer.append(text_line)

                # Detect success message
                if "Bot is now running and ready" in text_line:
                    deployment_success = True

                if log_mode == 'batch' and len(log_buffer) >= 10:
                    await client.send_message(log_channel, "```\n" + "\n".join(log_buffer) + "\n```")
                    log_buffer = []

                elif log_mode == 'single' and len(log_buffer) >= 1:
                    await client.send_message(log_channel, "```\n" + log_buffer[0] + "\n```")
                    log_buffer = log_buffer[1:]

                if deployment_success:
                    log_mode = 'single'
                    await client.send_message(message.chat.id, "✅ Bot deployed successfully!")
                    break

            if deployment_success:
                # Flush remaining logs
                if log_buffer:
                    await client.send_message(log_channel, "```\n" + "\n".join(log_buffer) + "\n```")
                break

            await asyncio.sleep(1)

        except Exception as e:
            await client.send_message(message.chat.id, f"⚠️ Error while streaming logs: {str(e)}")
            break


async def _docker_log_stream(logs):
    for log in logs:
        yield log
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



@Client.on_message(filters.command("runbot") & filters.private)
async def runbot_handler(client, message):
    user_id = message.from_user.id
    container_name = f"userbot_{user_id}"
    docker_client = docker.from_env()

    user = users_col.find_one({"USER_ID": user_id}) or {}

    premium_points = int(user.get("PREMIUM_POINTS", 0))
    files_sent = int(user.get("files_sent", 0))
    batch_messages_sent = int(user.get("batch_messages_sent", 0))
    MIN_POINTS = files_sent + batch_messages_sent
    if premium_points < MIN_POINTS:
        await message.reply_text(f"❌ You need at least {MIN_POINTS} premium points. You have {premium_points}.")
        return

    required_vars = ["BOT_TOKEN", "API_ID", "API_HASH"]
    missing_vars = [var for var in required_vars if not user.get(var)]
    if missing_vars:
        await message.reply_text(f"⚠️ Please configure: `{', '.join(missing_vars)}`")
        return

    await message.reply_text("🚀 Deployment started...")

    user = users_col.find_one({"USER_ID": user_id}) or {}
    admins_list = user.get("ADMINS", [])
    logger.info(f"ADMINS variable extracted from DB: {admins_list}")

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
        "PREMIUM_HOURS_VERIFICATION": str(user.get("PREMIUM_HOURS_VERIFICATION", "")),
        "VERIFY_SLUG_TTL_HOURS": str(user.get("VERIFY_SLUG_TTL_HOURS", "")),
        "SHORTENER_DOMAIN": user.get("SHORTENER_DOMAIN", ""),
        "SHORTENER_API_KEY": user.get("SHORTENER_API_KEY", ""),
        "CAPTION": user.get("CAPTION", ""),
        "ADMINS": user.get("ADMINS", ""),
        "AUTO_DELETE": str(user.get("AUTO_DELETE", False)),
        "AUTO_DELETE_TIME": str(user.get("AUTO_DELETE_TIME", ""))

        
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

    logs = container.logs(stream=True)
    deployment_success = False
    log_lines = []

    try:
        async for line in _docker_log_stream(logs):
            text_line = line.decode('utf-8').strip()
            log_lines.append(text_line)

            if "Bot is now running and ready" in text_line:
                deployment_success = True
                await message.reply_text("✅ Bot deployed successfully!")
                break

        if not deployment_success:
            # Send log file if deployment failed
            log_file_path = f"./logs_{user_id}.txt"
            with open(log_file_path, "w") as f:
                f.write("\n".join(log_lines))
            await message.reply_document(log_file_path, caption="❌ Deployment failed. See logs.")
    except Exception as e:
        await message.reply_text(f"⚠️ Error while streaming logs: {str(e)}")


async def _docker_log_stream(logs):
    for log in logs:
        yield log
import docker
import logging
from pyrogram import Client, filters
from db_config import users_col
import asyncio
import os

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

    # Fetch user record
    user = users_col.find_one({"USER_ID": user_id}) or {}
    premium_points = int(user.get("PREMIUM_POINTS", 0))
    files_sent = int(user.get("files_sent", 0))
    batch_messages_sent = int(user.get("batch_messages_sent", 0))
    MIN_POINTS = files_sent + batch_messages_sent + 1

    if premium_points < MIN_POINTS:
        await message.reply_text(
            f"❌ You need at least {MIN_POINTS} premium points. You have {premium_points}."
        )
        return

    # Check bot credentials in DB
    required_vars = ["BOT_TOKEN", "API_ID", "API_HASH"]
    missing_vars = [v for v in required_vars if not user.get(v)]
    if missing_vars:
        await message.reply_text(f"⚠️ Missing: `{', '.join(missing_vars)}`")
        return

    await message.reply_text("🚀 Deployment started...")

    # Stop & remove existing container if found
    try:
        existing = docker_client.containers.get(container_name)
        existing.reload()
        if existing.status == "running":
            logger.info(f"🛑 Stopping old container {container_name}...")
            existing.stop()
        existing.remove(force=True)
        logger.info(f"✅ Old container {container_name} removed.")
    except docker.errors.NotFound:
        pass
    except Exception as e:
        logger.error(f"⚠️ Error removing old container: {e}")
        await message.reply_text(f"⚠️ Error removing old container: {e}")
        return

    # Pass only essential variables
    env_vars = {
        "DEPLOY_USER_ID": str(user_id),
        "CODE2_MONGO_URI": os.getenv("CODE2_MONGO_URI"),
        "CODE2_DB_NAME": os.getenv("CODE2_DB_NAME"),
    }

    try:
        container = docker_client.containers.run(
            image="userbot_image",
            environment=env_vars,
            detach=True,
            name=container_name,
            restart_policy={"Name": "on-failure"},
            network_mode="bridge"
        )
        logger.info(f"✅ Container {container_name} started successfully.")
    except Exception as e:
        logger.error(f"❌ Failed to start container: {e}")
        await message.reply_text(f"❌ Deployment failed: {e}")
        return

    # Update DB status
    users_col.update_one(
        {"USER_ID": user_id},
        {"$set": {"BOT_STATUS": "running", "DOCKER_CONTAINER_ID": container.id}}
    )

    # Stream logs for success detection
    logs = container.logs(stream=True)
    deployment_success = False
    log_lines = []

    try:
        async for line in _docker_log_stream(logs):
            text_line = line.decode("utf-8").strip()
            log_lines.append(text_line)

            if "Bot is now running and ready" in text_line:
                deployment_success = True
                await message.reply_text("✅ Bot deployed successfully!")
                break

        if not deployment_success:
            log_path = f"./logs_{user_id}.txt"
            with open(log_path, "w") as f:
                f.write("\n".join(log_lines))
            await message.reply_document(log_path, caption="❌ Deployment failed. See logs.")
    except Exception as e:
        await message.reply_text(f"⚠️ Error streaming logs: {str(e)}")

async def _docker_log_stream(logs):
    for log in logs:
        yield log
import docker
import logging
import asyncio
import os
from datetime import datetime
from pyrogram import Client, filters
from db_config import users_col


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# ==========================
# /status COMMAND
# ==========================
@Client.on_message(filters.command("status") & filters.private)
async def status_handler(client, message):
    user_id = message.from_user.id
    container_name = f"userbot_{user_id}"
    docker_client = docker.from_env()

    try:
        container = docker_client.containers.get(container_name)
    except docker.errors.NotFound:
        await message.reply_text("❌ You don’t have any active deployment.")
        return

    container.reload()
    status = container.status
    started_at = container.attrs["State"].get("StartedAt")

    uptime = "N/A"
    if status == "running" and started_at:
        try:
            started_dt = datetime.strptime(started_at[:19], "%Y-%m-%dT%H:%M:%S")
            uptime_seconds = (datetime.utcnow() - started_dt).total_seconds()
            hours, remainder = divmod(int(uptime_seconds), 3600)
            minutes, seconds = divmod(remainder, 60)
            uptime = f"{hours}h {minutes}m {seconds}s"
        except Exception as e:
            logger.error(f"Error calculating uptime: {e}")

    # Fetch DB status for comparison
    user = users_col.find_one({"USER_ID": user_id}) or {}
    db_status = user.get("BOT_STATUS", "unknown")

    text = (
        f"📊 **Deployment Status**\n\n"
        f"🆔 **Container ID:** `{container.short_id}`\n"
        f"⚙️ **Docker Status:** `{status}`\n"
        f"💾 **DB Status:** `{db_status}`\n"
        f"⏱ **Uptime:** `{uptime}`\n"
    )

    await message.reply_text(text)


# ==========================
# /stopbot COMMAND
# ==========================
@Client.on_message(filters.command("stopbot") & filters.private)
async def stopbot_handler(client, message):
    user_id = message.from_user.id
    container_name = f"userbot_{user_id}"
    docker_client = docker.from_env()

    await message.reply_text("🛑 Stopping your deployed bot...")

    try:
        container = docker_client.containers.get(container_name)
    except docker.errors.NotFound:
        await message.reply_text("❌ You don’t have any active deployment to stop.")
        return

    try:
        # Stop the container if it's running
        container.reload()
        if container.status == "running":
            container.stop()
            await message.reply_text("✅ Bot stopped successfully.")
        else:
            await message.reply_text(f"⚠️ Bot is not running. Current status: `{container.status}`")

        # Remove the container completely
        container.remove()

        # Update DB
        users_col.update_one(
            {"USER_ID": user_id},
            {"$set": {"BOT_STATUS": "stopped", "DOCKER_CONTAINER_ID": None}}
        )

        logger.info(f"🧹 Container {container_name} removed for user {user_id}")

        await message.reply_text("🧹 Deployment fully stopped and container removed.")
    except Exception as e:
        logger.error(f"Error while stopping container for user {user_id}: {e}")
        await message.reply_text(f"❌ Failed to stop bot: `{str(e)}`")
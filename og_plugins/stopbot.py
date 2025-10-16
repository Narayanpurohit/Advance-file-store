import docker
import logging
from pyrogram import Client, filters
from db_config import users_col

logger = logging.getLogger(__name__)


@Client.on_message(filters.command("stopbot") & filters.private)
async def stopbot_handler(client, message):
    user_id = message.from_user.id
    container_name = f"userbot_{user_id}"
    docker_client = docker.from_env()

    await message.reply_text("🛑 Attempting to stop your deployed bot...")

    try:
        # Try to find the container by name
        container = docker_client.containers.get(container_name)
    except docker.errors.NotFound:
        await message.reply_text("❌ You don’t have any active deployment to stop.")
        return

    try:
        container.reload()
        status = container.status

        if status == "running":
            container.stop()
            await message.reply_text("✅ Bot stopped successfully (container preserved).")
            users_col.update_one(
                {"USER_ID": user_id},
                {"$set": {"BOT_STATUS": "stopped"}}
            )
            logger.info(f"🛑 Container {container_name} stopped for user {user_id}")
        else:
            await message.reply_text(f"⚠️ Bot is not currently running. Current status: `{status}`")

    except Exception as e:
        logger.error(f"Error while stopping container {container_name}: {e}")
        await message.reply_text(f"❌ Failed to stop bot: `{str(e)}`")
        
        
        @Client.on_message(filters.command("deletebot") & filters.private)
async def deletebot_handler(client, message):
    user_id = message.from_user.id
    container_name = f"userbot_{user_id}"
    docker_client = docker.from_env()

    try:
        container = docker_client.containers.get(container_name)
        container.reload()
        status = container.status

        # Stop if running
        if status == "running":
            await message.reply_text("🛑 Stopping your bot container...")
            container.stop()
            await asyncio.sleep(1)

        # Remove container
        container.remove()
        users_col.update_one(
            {"USER_ID": user_id},
            {"$set": {"BOT_STATUS": "deleted"}, "$unset": {"DOCKER_CONTAINER_ID": ""}}
        )
        await message.reply_text("✅ Your bot container has been deleted successfully!")

        logging.info(f"🗑️ Deleted container for user {user_id}")

    except docker.errors.NotFound:
        await message.reply_text("⚠️ No existing container found for your account.")
        logging.warning(f"⚠️ No container found for user {user_id} to delete.")
    except Exception as e:
        await message.reply_text(f"❌ Failed to delete your bot: `{str(e)}`")
        logging.error(f"❌ Error deleting container for user {user_id}: {e}")
        
        
        
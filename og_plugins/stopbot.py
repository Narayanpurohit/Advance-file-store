from pyrogram import Client, filters
from db_config import users_col
import docker

@Client.on_message(filters.command("stopbot") & filters.private)
async def stopbot_handler(client, message):
    user_id = message.from_user.id
    container_name = f"userbot_{user_id}"
    docker_client = docker.from_env()

    try:
        container = docker_client.containers.get(container_name)
        container.stop()
        container.remove()

        users_col.update_one(
            {"USER_ID": user_id},
            {"$set": {"BOT_STATUS": "stopped", "DOCKER_CONTAINER_ID": None}}
        )

        await message.reply_text("🛑 Your bot has been stopped and the container removed successfully.")

    except docker.errors.NotFound:
        await message.reply_text("⚠️ No running container found for your user.")

    except Exception as e:
        await message.reply_text(f"⚠️ Error stopping your bot:\n`{str(e)}`")
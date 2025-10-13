import docker
import logging
from pyrogram import Client, filters
from db_config import users_col

logger = logging.getLogger(__name__)

@Client.on_message(filters.command("log") & filters.private)
async def send_docker_log(client, message):
    """Send the Docker logs of the user's container as a file."""
    user_id = message.from_user.id
    container_name = f"userbot_{user_id}"
    docker_client = docker.from_env()

    try:
        # Try to get user's container
        container = docker_client.containers.get(container_name)
        logs = container.logs().decode("utf-8", errors="ignore")

        if not logs.strip():
            await message.reply_text("📭 No logs found for your bot yet.")
            return

        # Save logs to file
        log_file_path = f"./logs_{user_id}.txt"
        with open(log_file_path, "w") as f:
            f.write(logs)

        await message.reply_document(
            log_file_path,
            caption="📜 Here are your latest bot logs."
        )

    except docker.errors.NotFound:
        await message.reply_text("❌ No running container found for your account.\nUse /runbot to deploy your bot first.")
    except Exception as e:
        logger.exception("Error fetching Docker logs")
        await message.reply_text(f"⚠️ Error while fetching logs:\n`{str(e)}`")
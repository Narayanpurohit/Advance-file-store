from pyrogram import Client, filters
from db_config import users_col
import docker

@Client.on_message(filters.command("status") & filters.private)
async def status_handler(client, message):
    user_id = message.from_user.id
    container_name = f"userbot_{user_id}"
    docker_client = docker.from_env()

    user = users_col.find_one({"USER_ID": user_id}) or {}
    bot_status = user.get("BOT_STATUS", "not deployed")

    try:
        container = docker_client.containers.get(container_name)
        container_status = container.status

        await message.reply_text(
            f"📊 **Bot Status:** `{bot_status}`\n"
            f"⚙️ **Container Status:** `{container_status}`\n"
            f"🆔 **Container ID:** `{container.id}`"
        )
    except docker.errors.NotFound:
        await message.reply_text(
            f"❌ No Docker container found for your bot.\n"
            f"Database Status: `{bot_status}`"
        )
    except Exception as e:
        await message.reply_text(f"⚠️ An error occurred while checking status:\n`{str(e)}`")
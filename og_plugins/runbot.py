from pyrogram import Client, filters
from db_config import users_col
import docker
import logging
import asyncio

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

MIN_POINTS = 10  # Minimum points required to deploy

@Client.on_message(filters.command("runbot") & filters.private)
async def runbot_handler(client, message):
    user_id = message.from_user.id
    user = users_col.find_one({"USER_ID": user_id}) or {}

    premium_points = int(user.get("PREMIUM_POINTS", 0))
    if premium_points < MIN_POINTS:
        await message.reply_text(
            f"❌ You need at least {MIN_POINTS} premium points to deploy.\nYou currently have {premium_points}."
        )
        return

    required_vars = ["BOT_TOKEN", "API_ID", "API_HASH"]
    missing_vars = [var for var in required_vars if not user.get(var)]
    if missing_vars:
        await message.reply_text(
            f"⚠️ Please configure these required settings first using /settings:\n`{', '.join(missing_vars)}`"
        )
        return

    await message.reply_text("🚀 Starting deployment... This may take a few seconds.")

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

    docker_client = docker.from_env()

    try:
        # Run the container
        container = docker_client.containers.run(
            image="userbot_image",
            environment=env_vars,
            detach=True,
            name=f"userbot_{user_id}",
            restart_policy={"Name": "on-failure"}
        )

        # Save the container ID in DB
        users_col.update_one(
            {"USER_ID": user_id},
            {"$set": {"BOT_STATUS": "running", "DOCKER_CONTAINER_ID": container.id}}
        )

        await message.reply_text(
            f"✅ Your bot is now running in a Docker container.\nContainer ID:\n`{container.id}`"
        )

    except docker.errors.APIError as e:
        await message.reply_text(
            f"❌ Docker API error:\n```\n{str(e)}\n```"
        )
    except Exception as e:
        await message.reply_text(
            f"❌ Unexpected error:\n```\n{str(e)}\n```"
        )
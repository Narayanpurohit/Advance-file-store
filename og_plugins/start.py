from pyrogram import Client, filters
from db_config import add_user, user_exists
import logging

log = logging.getLogger("Start")

@Client.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    user_id = message.from_user.id
    username = message.from_user.username or "N/A"

    try:
        if not user_exists(user_id):
            add_user(user_id)
            log.info(f"New user {user_id} ({username}) added to DB.")
            text = "👋 Welcome! You’ve been added to the database.\n\n"
        else:
            log.info(f"Existing user {user_id} ({username}) accessed /start.")
            text = "👋 Welcome back!\n\n"

        text += (
            "⚙️ Use /settings to configure your bot.\n"
            "⭐ Use /premium to check your points.\n"
            "🚀 Use /runbot to deploy."
        )

        await message.reply_text(text)

    except Exception as e:
        log.exception(f"Error in /start for user {user_id}: {e}")
        await message.reply_text("⚠️ Something went wrong during start.")
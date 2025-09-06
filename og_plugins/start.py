from pyrogram import Client, filters
from db_config import add_user, user_exists

@Client.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    user_id = message.from_user.id

    if not user_exists(user_id):
        add_user(user_id)
        await message.reply_text("👋 Welcome! You’ve been added to the database.")

    await message.reply_text(
        "⚙️ This is the Clone Maker Bot.\n\n"
        "Use /settings to configure your bot.\n"
        "Use /premium to check your points.\n"
        "Use /runbot to deploy."
    )
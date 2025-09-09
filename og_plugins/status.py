from pyrogram import Client, filters
import psutil
from db_config import users_col


@Client.on_message(filters.command("status") & filters.private)
async def status_handler(client, message):
    user_id = message.from_user.id
    user = users_col.find_one({"USER_ID": user_id}) or {}
    bot_status = user.get("BOT_STATUS", "stopped")

    await message.reply_text(f"ℹ️ Bot status: **{bot_status}**.")
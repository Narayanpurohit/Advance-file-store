from pyrogram import Client, filters
from db_config import users_col

@Client.on_message(filters.command("premium") & filters.private)
async def premium_handler(client, message):
    user_id = message.from_user.id
    user = users_col.find_one({"USER_ID": user_id}) or {}

    points = user.get("points", 0)

    await message.reply_text(f"⭐ You currently have **{points} points**.")
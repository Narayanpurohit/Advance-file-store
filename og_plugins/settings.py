from pyrogram import Client, filters
from database import db

settings_col = db["user_settings"]

@Client.on_message(filters.command("settings") & filters.private)
async def settings_handler(client, message):
    user_id = message.from_user.id
    settings = settings_col.find_one({"user_id": user_id}) or {}

    text = (
        "⚙️ **Your Settings** ⚙️\n\n"
        f"BOT TOKEN: `{settings.get('BOT_TOKEN', '❌ Not set')}`\n"
        f"API ID: `{settings.get('API_ID', '❌ Not set')}`\n"
        f"API HASH: `{settings.get('API_HASH', '❌ Not set')}`\n"
        f"DB NAME: `{settings.get('DB_NAME', '❌ Not set')}`\n\n"
        "👉 Send values with `/set <key> <value>`\n"
        "Example: `/set BOT_TOKEN 123:ABC-xyz`"
    )
    await message.reply_text(text)


@Client.on_message(filters.command("set") & filters.private)
async def set_handler(client, message):
    user_id = message.from_user.id
    parts = message.text.split(" ", 2)

    if len(parts) < 3:
        await message.reply_text("❌ Usage: /set <key> <value>")
        return

    key, value = parts[1], parts[2]
    settings_col.update_one(
        {"user_id": user_id},
        {"$set": {key: value}},
        upsert=True
    )
    await message.reply_text(f"✅ `{key}` set successfully.")
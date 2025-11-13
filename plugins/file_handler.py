import random
import string
import traceback
from pyrogram import Client, filters
from bot import get_str, get_bool, get_admins
from pymongo import MongoClient


MONGO_URI = get_str("MONGO_URI")
DB_NAME = get_str("DB_NAME")
mongo_client = MongoClient(MONGO_URI)
db = mongo_client[DB_NAME]
files_col = db["files"]
stats_col = db["stats"]


def random_slug(prefix):
    """Generate unique slug with given prefix"""
    return f"{prefix}_{''.join(random.choices(string.ascii_lowercase + string.digits, k=12))}"


def human_readable_size(size_bytes):
    """Convert bytes to readable size"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"


@Client.on_message(filters.private & filters.command("link"))
async def generate_link(client, message):
    ADMINS = get_admins()
    PUBLIC_BOT = get_bool("PUBLIC_BOT", True)

    try:
        # Access control
        if not PUBLIC_BOT and message.from_user.id not in ADMINS:
            return await message.reply_text("❌ Only admins can use this bot.")

        if not message.reply_to_message:
            return await message.reply_text("⚠️ Please reply to a message (any type) with /link.")

        replied = message.reply_to_message

        # Initialize defaults
        file_id = None
        file_name = None
        file_size = 0
        caption = replied.caption or ""

        # Detect message type
        if replied.document:
            file_id = replied.document.file_id
            file_name = replied.document.file_name
            file_size = replied.document.file_size
            file_type = "doc"
        elif replied.video:
            file_id = replied.video.file_id
            file_name = replied.video.file_name
            file_size = replied.video.file_size
            file_type = "vid"
        elif replied.audio:
            file_id = replied.audio.file_id
            file_name = replied.audio.file_name
            file_size = replied.audio.file_size
            file_type = "aud"
        elif replied.photo:
            file_id = replied.photo.file_id
            file_name = "Photo"
            file_type = "one"
        elif replied.sticker:
            file_id = replied.sticker.file_id
            file_name = "Sticker"
            file_type = "one"
        elif replied.animation:
            file_id = replied.animation.file_id
            file_name = "Animation"
            file_type = "one"
        elif replied.text:
            file_name = "Text message"
            caption = replied.text
            file_type = "one"
        else:
            return await message.reply_text("❌ Unsupported message type.")

        # Generate unique slug
        slug = random_slug(file_type)
        while files_col.find_one({"slug": slug}):
            slug = random_slug(file_type)

        # Save file info to DB
        try:
            files_col.insert_one({
                "slug": slug,
                "file_id": file_id,
                "file_type": file_type,
                "file_name": file_name,
                "file_size": file_size,
                "caption": caption,
            })
        except Exception as db_err:
            return await message.reply_text(f"⚠️ Database Error:\n`{db_err}`")

        # Update stats
        try:
            stats_col.update_one({"key": "total_sent"}, {"$inc": {"count": 1}}, upsert=True)
        except Exception as db_err:
            # Don't break functionality if stats fail
            print("Stats update failed:", db_err)

        # Build link
        bot_info = await client.get_me()
        file_link = f"https://t.me/{bot_info.username}?start={slug}"

        # Build response
        reply_text = f"✅ **Link generated successfully!**\n\n"
        if file_name:
            reply_text += f"📁 **Type:** {file_type.upper()}\n"
            reply_text += f"📄 **Name:** `{file_name}`\n"
        if file_size > 0:
            reply_text += f"📦 **Size:** {human_readable_size(file_size)}\n\n"
        reply_text += f"🔗 **Link:** {file_link}"

        await message.reply_text(reply_text)

    except Exception as e:
        # Catch any unexpected error
        error_text = f"⚠️ **An unexpected error occurred.**\n\n`{e}`"
        await message.reply_text(error_text)
        # Also print full traceback to console/logs for debugging
        print("Error in /link handler:\n", traceback.format_exc())
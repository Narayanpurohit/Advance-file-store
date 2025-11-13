import random
import string
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
    return f"{prefix}_{''.join(random.choices(string.ascii_lowercase + string.digits, k=12))}"


def human_readable_size(size_bytes):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"


@Client.on_message(filters.private & filters.command("link"))
async def generate_link(client, message):
    ADMINS = get_admins()
    PUBLIC_BOT = get_bool("PUBLIC_BOT", True)

    if not PUBLIC_BOT and message.from_user.id not in ADMINS:
        return await message.reply_text("❌ Only admins can use this bot.")

    if not message.reply_to_message:
        return await message.reply_text("⚠️ Please reply to a message (file or text) with /link.")

    replied = message.reply_to_message

    # Detect content type
    if replied.document:
        file_id = replied.document.file_id
        file_name = replied.document.file_name
        file_size = replied.document.file_size
        file_type = "doc"
        caption = replied.caption or ""
    elif replied.video:
        file_id = replied.video.file_id
        file_name = replied.video.file_name
        file_size = replied.video.file_size
        file_type = "vid"
        caption = replied.caption or ""
    elif replied.audio:
        file_id = replied.audio.file_id
        file_name = replied.audio.file_name
        file_size = replied.audio.file_size
        file_type = "aud"
        caption = replied.caption or ""
    elif replied.text or replied.caption:
        file_id = None
        file_name = "Text message"
        file_size = 0
        file_type = "txt"
        caption = replied.text or replied.caption
    else:
        return await message.reply_text("❌ Please reply to a valid file or text message.")

    # Generate unique slug
    slug = random_slug(file_type)
    while files_col.find_one({"slug": slug}):
        slug = random_slug(file_type)

    files_col.insert_one({
        "slug": slug,
        "file_id": file_id,
        "file_type": file_type,
        "file_name": file_name,
        "file_size": file_size,
        "caption": caption
    })

    stats_col.update_one({"key": "total_sent"}, {"$inc": {"count": 1}}, upsert=True)

    bot_info = await client.get_me()
    file_link = f"https://t.me/{bot_info.username}?start={slug}"

    reply_text = f"✅ **Link generated successfully!**\n\n"
    if file_type != "txt":
        reply_text += (
            f"📁 **File:** `{file_name}`\n"
            f"📦 **Size:** {human_readable_size(file_size)}\n\n"
        )
    else:
        reply_text += "📝 **Text message saved**\n\n"

    reply_text += f"🔗 **Link:** {file_link}"

    await message.reply_text(reply_text)
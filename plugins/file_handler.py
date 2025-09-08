import random
import string
from pyrogram import Client, filters
from bot import MONGO_URI, CAPTION
from pymongo import MongoClient

mongo_client = MongoClient(MONGO_URI)
db = mongo_client["filestore"]
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

@Client.on_message(filters.private & (filters.document | filters.video | filters.audio))
async def save_file(client, message):
    if message.document:
        file_id = message.document.file_id
        file_name = message.document.file_name
        file_size = message.document.file_size
        file_type = "doc"
    elif message.video:
        file_id = message.video.file_id
        file_name = message.video.file_name
        file_size = message.video.file_size
        file_type = "vid"
    elif message.audio:
        file_id = message.audio.file_id
        file_name = message.audio.file_name
        file_size = message.audio.file_size
        file_type = "aud"
    else:
        return

    slug = random_slug(file_type)

    files_col.insert_one({
        "slug": slug,
        "file_id": file_id,
        "file_type": file_type,
        "file_name": file_name,
        "file_size": file_size,
        "caption": message.caption or ""
    })

    stats_col.update_one({"key": "total_sent"}, {"$inc": {"count": 1}}, upsert=True)

    bot_info = await client.get_me()
    file_link = f"https://t.me/{bot_info.username}?start={slug}"

    await message.reply_text(
        f"✅ File saved!\n\n📎 Link: {file_link}"
    )
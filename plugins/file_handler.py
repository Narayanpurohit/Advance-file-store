import string
import random
from pyrogram import Client, filters
from config import MONGO_URI
from pymongo import MongoClient
from pyrogram.types import Message
# ─── MongoDB Setup ───────────────────────────────
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["filestore"]
files_col = db["files"]
stats_col = db["stats"]

# ─── Helper: Generate Slug ───────────────────────
def generate_slug(file_type):
    chars = string.ascii_lowercase + string.digits
    random_part = ''.join(random.choices(chars, k=12))
    return f"{file_type}_{random_part}"

# ─── File Handler ────────────────────────────────
@Client.on_message(filters.private & (filters.document | filters.video | filters.audio))
async def save_file(client, message):
    # Detect file type
    caption = message.caption or ""
    if message.document:
        file_type = "doc"
        file_id = message.document.file_id
        file_name = message.document.file_name
        file_size = message.document.file_size
    elif message.video:
        file_type = "vid"
        file_id = message.video.file_id
        file_name = message.video.file_name
        file_size = message.video.file_size
    elif message.audio:
        file_type = "aud"
        file_id = message.audio.file_id
        file_name = message.audio.file_name
        file_size = message.audio.file_size
    else:
        return  # Not supported file type

    # Generate slug
    slug = generate_slug(file_type)

    # Store in MongoDB
    files_col.insert_one({
        "slug": slug,
        "file_id": file_id,
        "file_type": file_type
        "filename": file_name
        "filesize" : file_size
        "caption" : caption
    })

    # Update total counter
    stats_col.update_one(
        {"_id": "total"},
        {"$inc": {"sent_files": 1}},
        upsert=True
    )

    # Get bot username dynamically from API
    bot_info = await client.get_me()
    bot_username = bot_info.username

    # Create link
    file_link = f"https://t.me/{bot_username}?start={slug}"

    # Reply to user
    await message.reply_text(
        f"✅ File saved!\n\n📎 **Link:** {file_link}",
        disable_web_page_preview=True
    )

    print(f"[File Saved] Type: {file_type}, Slug: {slug}, User: {message.from_user.id}")
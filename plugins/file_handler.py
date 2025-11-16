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


def random_slug(prefix,db):
    return f"{prefix}_{db}_{''.join(random.choices(string.ascii_lowercase + string.digits, k=12))}"


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
    DEKOY = get_bool("DEKOY")
    BOT_USERNAME = get_str("BOT_USERNAME")
    USERNAME = "Itadori101bot" if DEKOY else BOT_USERNAME


    try:
        if not PUBLIC_BOT and message.from_user.id not in ADMINS:
            return await message.reply_text("❌ Only admins can use this bot.")

        if not message.reply_to_message:
            return await message.reply_text("⚠️ Please reply to a message with `/link`.")

        replied = message.reply_to_message

        # Defaults
        file_id = None
        file_name = None
        file_size = 0
        caption = replied.caption or ""

        # Detect the message type and assign your custom file types
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
            file_type = "pht"
        elif replied.sticker:
            file_id = replied.sticker.file_id
            file_name = "Sticker"
            file_type = "sti"
        elif replied.animation:
            file_id = replied.animation.file_id
            file_name = "Animation"
            file_type = "ani"
        elif replied.text:
            file_id = None
            file_name = "Text message"
            caption = replied.text
            file_type = "text"
        else:
            return await message.reply_text("❌ Unsupported message type.")

        # Generate unique slug
        slug = random_slug(file_type,DB_NAME)
        while files_col.find_one({"slug": slug}):
            slug = random_slug(file_type,DB_NAME)

        # Save file entry
        try:
            files_col.insert_one({
                "slug": slug,
                "file_id": file_id,
                "file_type": file_type,
                "file_name": file_name,
                "file_size": file_size,
                "caption": caption
            })
        except Exception as db_err:
            return await message.reply_text(f"⚠️ Database Error:\n`{db_err}`")

        # Update stats (safe)
        try:
            stats_col.update_one({"key": "total_sent"}, {"$inc": {"count": 1}}, upsert=True)
        except:
            pass

        # Generate file link
        #bot_info = await client.get_me()
        file_link = f"https://t.me/{USERNAME}?start={slug}"

        # Build response
        text_resp = (
            f"✅ **Link generated!**\n\n"
            f"📁 **Type:** `{file_type}`\n"
            f"📄 **Name:** `{file_name}`\n"
        )

        if file_size > 0:
            text_resp += f"📦 **Size:** {human_readable_size(file_size)}\n\n"

        text_resp += f"🔗 **Link:** {file_link}"

        await message.reply_text(text_resp)

    except Exception as e:
        await message.reply_text(f"⚠️ Unexpected Error:\n`{e}`")
        print("Error in /link:\n", traceback.format_exc())
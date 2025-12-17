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

def extract_buttons(message):
    if not message.reply_markup:
        return None

    buttons = []
    for row in message.reply_markup.inline_keyboard:
        btn_row = []
        for btn in row:
            btn_data = {"text": btn.text}

            if btn.url:
                btn_data["url"] = btn.url
            if btn.callback_data:
                btn_data["callback_data"] = btn.callback_data
            if btn.switch_inline_query:
                btn_data["switch_inline_query"] = btn.switch_inline_query
            if btn.switch_inline_query_current_chat:
                btn_data["switch_inline_query_current_chat"] = btn.switch_inline_query_current_chat

            btn_row.append(btn_data)

        buttons.append(btn_row)
        print(buttons)

    return buttons
    
    
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

        # Detect the message type
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

        # Extract inline buttons
        buttons = extract_buttons(replied)

        # Generate unique slug
        slug = random_slug(file_type, DB_NAME)
        while files_col.find_one({"slug": slug}):
            slug = random_slug(file_type, DB_NAME)
        slug2 = random_slug(file_type, DB_NAME)
        while files_col.find_one({"slug": slug}):
            slug = random_slug(file_type, DB_NAME)


        # Save file entry
        save_data = {
            "slug": slug,
            "file_id": file_id,
            "file_type": file_type,
            "file_name": file_name,
            "file_size": file_size,
            "caption": caption,
            "slug2":slug2
        }

        if buttons:
            save_data["buttons"] = buttons   # ⭐ Save inline button data

        try:
            files_col.insert_one(save_data)
        except Exception as db_err:
            return await message.reply_text(f"⚠️ Database Error:\n`{db_err}`")

        # Update stats
        try:
            stats_col.update_one({"key": "total_sent"}, {"$inc": {"count": 1}}, upsert=True)
        except:
            pass

        # Generate link
        file_link = f"https://t.me/{USERNAME}?start={slug2}"

        text_resp = (
            f"✅ **Link generated!**\n\n"
            f"📁 **slug:** `{slug}`\n"
            f"📁 **Type:** `{file_type}`\n"
            f"📄 **Name:** `{file_name}`\n"
        )

        if file_size > 0:
            text_resp += f"📦 **Size:** {human_readable_size(file_size)}\n\n"

        text_resp += f"🔗 **Link:** {file_link}"

        await message.reply_text(text_resp)
        await replied.delete()

    except Exception as e:
        await message.reply_text(f"⚠️ Unexpected Error:\n`{e}`")
        print("Error in /link:\n", traceback.format_exc())
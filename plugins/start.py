from pyrogram import Client, filters
from config import MONGO_URI, CAPTION, VERIFICATION_MODE
from pymongo import MongoClient
import datetime

mongo_client = MongoClient(MONGO_URI)
db = mongo_client["filestore"]
files_col = db["files"]
stats_col = db["stats"]
users_col = db["users"]
verify_col = db["verify"]

def human_readable_size(size_bytes):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"

@Client.on_message(filters.private & filters.command("start"))
async def start_command(client, message):
    user_id = message.from_user.id

    # Add user to DB if new
    if not users_col.find_one({"user_id": user_id}):
        users_col.insert_one({"user_id": user_id, "premium_until": None})

    # Check if slug provided
    if len(message.command) > 1:
        slug = message.command[1]

        # If slug starts with verify_
        if slug.startswith("verify_"):
            verify_data = verify_col.find_one({"slug": slug})
            if verify_data:
                premium_until = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
                users_col.update_one({"user_id": user_id}, {"$set": {"premium_until": premium_until}})
                await message.reply_text("✅ You are now premium for 8 hours!")
                verify_col.delete_one({"slug": slug})
            else:
                await message.reply_text("❌ Invalid or expired verification link.")
            return

        # Otherwise it’s a file slug
        file_data = files_col.find_one({"slug": slug})
        if not file_data:
            await message.reply_text("❌ File not found or has been removed.")
            return

        # Send file with caption
        file_id = file_data["file_id"]
        file_type = file_data["file_type"]
        file_name = file_data.get("file_name", "Unknown")
        file_size = file_data.get("file_size", 0)
        original_caption = file_data.get("caption", "")

        caption_text = CAPTION.format(
            filename=file_name,
            filesize=human_readable_size(file_size),
            filetype={"doc": "Document", "vid": "Video", "aud": "Audio"}.get(file_type, "Unknown"),
            caption=original_caption
        )

        if file_type == "doc":
            await message.reply_document(file_id, caption=caption_text)
        elif file_type == "vid":
            await message.reply_video(file_id, caption=caption_text)
        elif file_type == "aud":
            await message.reply_audio(file_id, caption=caption_text)

        stats_col.update_one({"key": "total_sent"}, {"$inc": {"count": 1}}, upsert=True)
        return

    # Default welcome
    await message.reply_text("👋 Welcome! Send me a file and I will give you a shareable link.")
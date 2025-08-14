import time
from pyrogram import Client, filters
from config import MONGO_URI, VERIFY_SLUG_TTL_HOURS,CAPTION
from pymongo import MongoClient

# ─── MongoDB Setup ───────────────────────────────
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["filestore"]
files_col = db["files"]
stats_col = db["stats"]
verify_col = db["verify_links"]
premium_col = db["premium_users"]

@Client.on_message(filters.private & filters.command("start"))
async def start_command(client, message):
    if len(message.command) > 1:
        arg = message.command[1]

        # ─── Handle verification links ─────────────
        if arg.startswith("verify_"):
            verify_data = verify_col.find_one({"slug": arg})

            if not verify_data:
                await message.reply_text("❌ This verification link is invalid or expired.")
                return

            # Check expiry
            now = time.time()
            if now > verify_data["created_at"] + (VERIFY_SLUG_TTL_HOURS * 3600):
                await message.reply_text("⌛ This verification link has expired.")
                return

            # Grant 8 hours premium
            premium_col.update_one(
                {"user_id": message.from_user.id},
                {"$set": {"expires_at": now + (8 * 3600)}},
                upsert=True
            )

            # Delete used verification link
            verify_col.delete_one({"slug": arg})

            await message.reply_text("✅ You are now a Premium user for 8 hours!")
            return

        # ─── Handle file links ─────────────────────
        file_data = files_col.find_one({"slug": arg})

        if not file_data:
            await message.reply_text("❌ File not found or has been removed.")
            return

        file_id = file_data["file_id"]
        file_type = file_data["file_type"]
        filename = file_data["filename"]
        filesize = file_data["filesize"]

        # Send file according to type
        if file_type == "doc":
            await message.reply_document(file_id , caption=CAPTION )
        elif file_type == "vid":
            await message.reply_video(file_id)
        elif file_type == "aud":
            await message.reply_audio(file_id)
        else:
            await message.reply_text("❌ Unknown file type.")
            return

        # Increment total files sent
        stats_col.update_one(
            {"_id": "total"},
            {"$inc": {"sent_files": 1}},
            upsert=True
        )
        return

    # ─── Default welcome message ──────────────────
    await message.reply_text(
        "👋 Welcome! Send me a file, and I'll give you a shareable link.\n"
        "🔗 Premium users can bypass verification."
    )
from pyrogram import Client, filters
from database import add_user, get_file, inc_sent_count, is_premium
from config import VERIFICATION_MODE
from .verification import start_verification_flow

@Client.on_message(filters.command("start"))
async def start_command(client, message):
    user_id = message.from_user.id
    add_user(user_id)

    args = message.text.split(" ", 1)
    if len(args) == 1:
        await message.reply_text("👋 Welcome! Send me a file to get a shareable link.")
        return

    slug = args[1]

    if slug.startswith("verify_"):
        await start_verification_flow(client, message, slug)
        return

    file_data = get_file(slug)
    if not file_data:
        await message.reply_text("❌ File not found.")
        return

    if VERIFICATION_MODE and not is_premium(user_id):
        await message.reply_text("⚠️ You need to verify before accessing files.")
        return

    await message.reply_document(file_data["file_id"]) if file_data["type"] == "doc" else \
        await message.reply_audio(file_data["file_id"]) if file_data["type"] == "aud" else \
        await message.reply_video(file_data["file_id"])
    
    inc_sent_count()
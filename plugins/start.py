import logging
from pyrogram import Client, filters
from config import VERIFICATION_MODE, CAPTION
from database import user_exists, add_user, get_file_by_slug, is_premium, increment_file_send_count
from verification import start_verification_flow, send_verification_link
from utils import human_readable_size

log = logging.getLogger(__name__)


@Client.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    user_id = message.from_user.id
    args = message.text.split()

    # 1. Add new user if not exists
    if not user_exists(user_id):
        add_user(user_id)
        log.info(f"New user {user_id} added to database.")

    # 2. No arguments — greet user
    if len(args) == 1:
        await message.reply_text("👋 Welcome! Send me a file to get started.")
        return

    slug = args[1]

    # 3. Verification slug
    if slug.startswith("verify_"):
        await start_verification_flow(client, message, slug)
        return

    # 4. File slug — fetch from DB
    file_data = get_file_by_slug(slug)
    if not file_data:
        await message.reply_text("❌ File not found or has been removed.")
        return

    # 5. If verification mode is ON, check premium
    if VERIFICATION_MODE and not is_premium(user_id):
        await send_verification_link(client, user_id)
        return

    # 6. Prepare caption
    file_name = file_data.get("file_name", "")
    file_size = file_data.get("file_size", 0)
    orig_caption = file_data.get("caption", "")

    caption_text = CAPTION.format(
        filename=file_name,
        filesize=human_readable_size(file_size),
        caption=orig_caption
    )

    # 7. Send file
    file_type = file_data.get("file_type")
    file_id = file_data.get("file_id")

    if file_type == "doc":
        await message.reply_document(file_id, caption=caption_text)
    elif file_type == "vid":
        await message.reply_video(file_id, caption=caption_text)
    elif file_type == "aud":
        await message.reply_audio(file_id, caption=caption_text)
    else:
        await message.reply_text("❌ Unknown file type.")

    # 8. Increment file send counter
    increment_file_send_count()
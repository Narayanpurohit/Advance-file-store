import logging
from pyrogram import Client, filters
from config import VERIFICATION_MODE, CAPTION
from database import (
    user_exists, add_user,
    get_file_by_slug, get_batch_by_slug,  # 🔹 added get_batch_by_slug
    is_premium, increment_file_send_count
)
from .verification import start_verification_flow, send_verification_link
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

    # 4. Batch slug
    if slug.startswith("batch_"):
        batch_data = get_batch_by_slug(slug)
        if not batch_data:
            await message.reply_text("❌ Batch not found or expired.")
            return

        # Check verification if required
        if VERIFICATION_MODE and not is_premium(user_id):
            await send_verification_link(client, user_id)
            return

        messages = batch_data.get("messages", [])
        if not messages:
            await message.reply_text("❌ This batch is empty or corrupted.")
            return

        sent_count = 0
        skipped = 0
        for msg in messages:
            try:
                mtype = msg.get("type")

                if mtype == "document":
                    await message.reply_document(
                        msg["file_id"],
                        caption=msg.get("caption", ""),
                        caption_entities=msg.get("caption_entities", None)
                    )
                elif mtype == "video":
                    await message.reply_video(
                        msg["file_id"],
                        caption=msg.get("caption", ""),
                        caption_entities=msg.get("caption_entities", None)
                    )
                elif mtype == "audio":
                    await message.reply_audio(
                        msg["file_id"],
                        caption=msg.get("caption", ""),
                        caption_entities=msg.get("caption_entities", None)
                    )
                elif mtype == "photo":
                    await message.reply_photo(
                        msg["file_id"],
                        caption=msg.get("caption", ""),
                        caption_entities=msg.get("caption_entities", None)
                    )
                elif mtype == "text":
                    await message.reply_text(
                        msg["text"],
                        entities=msg.get("entities", None)
                    )
                else:
                    skipped += 1
                    continue

                sent_count += 1

            except Exception as e:
                log.warning(f"Failed to send item in batch {slug}: {e}")
                skipped += 1
                continue

        await message.reply_text(
            f"✅ Batch delivered!\n\n"
            f"📤 Sent: {sent_count}\n"
            f"⚠️ Skipped: {skipped}"
        )
        return

    # 5. File slug — fetch from DB
    file_data = get_file_by_slug(slug)
    if not file_data:
        await message.reply_text("❌ File not found or has been removed.")
        return

    # 6. If verification mode is ON, check premium
    if VERIFICATION_MODE and not is_premium(user_id):
        await send_verification_link(client, user_id)
        return

    # 7. Prepare caption
    file_name = file_data.get("file_name", "")
    file_size = file_data.get("file_size", 0)
    orig_caption = file_data.get("caption", "")

    caption_text = CAPTION.format(
        filename=file_name,
        filesize=human_readable_size(file_size),
        caption=orig_caption
    )

    # 8. Send file
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

    # 9. Increment file send counter
    increment_file_send_count()
import logging
from pyrogram import Client, filters
from config import VERIFICATION_MODE, CAPTION
from database import (
    user_exists, add_user, get_file_by_slug,
    is_premium, increment_file_send_count,
    get_batch_by_slug, increment_batches_sent,
    increment_batch_messages_sent
)
from .verification import start_verification_flow, send_verification_link
from .force_sub import check_force_sub   # ✅ import ForceSub
from utils import human_readable_size

log = logging.getLogger(__name__)


@Client.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    user_id = message.from_user.id
    args = message.text.split()

    try:
        # 1. Add new user if not exists
        if not user_exists(user_id):
            add_user(user_id)
            log.info(f"👤 New user {user_id} added to database.")

        # 2. Check Force Sub (stop flow if not joined)
        ok = await check_force_sub(client, user_id, message)
        if not ok:
            log.warning(f"❌ User {user_id} has not joined required channels.")
            return

        # 3. No arguments — greet user
        if len(args) == 1:
            await message.reply_text("👋 Welcome! Send me a file to get started.")
            return

        slug = args[1]

        # 4. Verification slug
        if slug.startswith("verify_"):
            await start_verification_flow(client, message, slug)
            return

        # 5. Batch slug
        if slug.startswith("batch_"):
            batch_data = get_batch_by_slug(slug)
            if not batch_data:
                await message.reply_text("❌ Batch not found or expired.")
                return

            if VERIFICATION_MODE and not is_premium(user_id):
                await send_verification_link(client, user_id)
                return

            sent_count = 0
            for item in batch_data["messages"]:
                try:
                    await client.copy_message(
                        chat_id=message.chat.id,
                        from_chat_id=item["chat_id"],
                        message_id=item["message_id"]
                    )
                    sent_count += 1
                except Exception as e:
                    log.warning(
                        f"⚠️ Failed to send item in batch {slug} for user {user_id}: {e}"
                    )

            # ✅ Update counters after batch delivery
            if sent_count > 0:
                increment_batches_sent()
                increment_batch_messages_sent(sent_count)
                log.info(
                    f"📦 Batch {slug} delivered to user {user_id}: "
                    f"{sent_count} messages sent."
                )
            else:
                log.warning(f"⚠️ Batch {slug} delivered no messages to user {user_id}.")
            return

        # 6. File slug — fetch from DB
        file_data = get_file_by_slug(slug)
        if not file_data:
            await message.reply_text("❌ File not found or has been removed.")
            return

        # 7. If verification mode is ON, check premium
        if VERIFICATION_MODE and not is_premium(user_id):
            await send_verification_link(client, user_id)
            return

        # 8. Prepare caption
        file_name = file_data.get("file_name", "")
        file_size = file_data.get("file_size", 0)
        orig_caption = file_data.get("caption", "")

        caption_text = CAPTION.format(
            filename=file_name,
            filesize=human_readable_size(file_size),
            caption=orig_caption
        )

        # 9. Send file
        file_type = file_data.get("file_type")
        file_id = file_data.get("file_id")

        try:
            if file_type == "doc":
                await message.reply_document(file_id, caption=caption_text)
            elif file_type == "vid":
                await message.reply_video(file_id, caption=caption_text)
            elif file_type == "aud":
                await message.reply_audio(file_id, caption=caption_text)
            else:
                await message.reply_text("❌ Unknown file type.")
                log.error(f"❌ Unknown file type {file_type} for slug {slug}.")
                return
        except Exception as e:
            log.error(f"⚠️ Error sending file {slug} to user {user_id}: {e}")
            await message.reply_text("⚠️ Failed to send file. Try again later.")
            return

        # 10. Increment file send counter
        increment_file_send_count()
        log.info(f"📁 File {slug} sent to user {user_id}.")

    except Exception as e:
        log.exception(f"🔥 Error in /start handler for user {user_id}: {e}")
        await message.reply_text("⚠️ An unexpected error occurred. Please try again later.")
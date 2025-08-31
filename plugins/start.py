import logging
from pyrogram import Client, filters
from config import VERIFICATION_MODE, CAPTION, ENABLE_FSUB
from database import (
    user_exists, add_user, get_file_by_slug,
    is_premium, increment_file_send_count,
    get_batch_by_slug
)
from .verification import start_verification_flow, send_verification_link
from .force_sub import check_force_sub
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

    # 2. ForceSub check (only if enabled)
    if ENABLE_FSUB:
        ok = False
        try:
            ok = await check_force_sub(client, user_id, message)
        except Exception as e:
            log.exception(f"ForceSub check crashed for user {user_id}: {e}")
            await message.reply_text("❌ Error while checking subscription. Please try again later.")
            return

        if not ok:
            log.warning(f"User {user_id} blocked at ForceSub stage.")
            return  # user not subscribed → stop flow

    # 3. No arguments — greet user
    if len(args) == 1:
        await message.reply_text("👋 Welcome! Send me a file to get started.")
        return

    slug = args[1]

    # 4. Verification slug
    if slug.startswith("verify_"):
        try:
            await start_verification_flow(client, message, slug)
        except Exception as e:
            log.exception(f"Verification flow error for user {user_id}: {e}")
            await message.reply_text("❌ Error during verification. Please try again later.")
        return

    # 5. Batch slug
    if slug.startswith("batch_"):
        try:
            batch_data = get_batch_by_slug(slug)
            if not batch_data:
                await message.reply_text("❌ Batch not found or expired.")
                return

            if VERIFICATION_MODE and not is_premium(user_id):
                await send_verification_link(client, user_id)
                return

            for item in batch_data["messages"]:
                try:
                    await client.copy_message(
                        chat_id=message.chat.id,
                        from_chat_id=item["chat_id"],
                        message_id=item["message_id"]
                    )
                except Exception as e:
                    log.warning(f"Failed to send item in batch {slug} for user {user_id}: {e}")
        except Exception as e:
            log.exception(f"Batch handling error for user {user_id}: {e}")
            await message.reply_text("❌ Error while fetching batch. Please try again later.")
        return

    # 6. File slug — fetch from DB
    try:
        file_data = get_file_by_slug(slug)
        if not file_data:
            await message.reply_text("❌ File not found or has been removed.")
            return
    except Exception as e:
        log.exception(f"DB fetch error for slug {slug} (user {user_id}): {e}")
        await message.reply_text("❌ Error while fetching file. Please try again later.")
        return

   
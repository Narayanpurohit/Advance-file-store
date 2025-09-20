import logging
from pyrogram import Client, filters
from pyrogram.errors import FloodWait, PeerIdInvalid, UserIsBlocked
from bot import VERIFICATION_MODE, CAPTION
from database import (
    user_exists, add_user, get_file_by_slug,
    is_premium, increment_file_send_count,
    get_batch_by_slug, increment_batches_sent,
    increment_batch_messages_sent
)
from .verification import start_verification_flow, send_verification_link
from .force_sub import check_force_sub   # ✅ import ForceSub
from utils import human_readable_size
import asyncio
# Auto delete settings
AUTO_DELETE = True
AUTO_DELETE_TIME = 40  # 30 minutes (in seconds)

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
            failure_reasons = {}

            batch_sent_messages = []  # ✅ store sent messages

            for item in batch_data["messages"]:
                try:
                   sent = await client.copy_message(chat_id=message.chat.id,from_chat_id=int(item["chat_id"]),
message_id=int(item["message_id"]))
                   sent_count += 1
                   batch_sent_messages.append(sent)   # ✅ collect for auto delete
                   # ✅ Schedule auto delete for the whole batch
                                          
                except FloodWait as e:
                    failure_reasons["FloodWait"] = failure_reasons.get("FloodWait", 0) + 1
                    log.warning(f"⚠️ FloodWait {e.value}s for user {user_id} while batch {slug}")
                except PeerIdInvalid:
                    failure_reasons["PeerIdInvalid"] = failure_reasons.get("PeerIdInvalid", 0) + 1
                except UserIsBlocked:
                    failure_reasons["UserIsBlocked"] = failure_reasons.get("UserIsBlocked", 0) + 1
                except Exception as e:
                    failure_reasons[type(e).__name__] = failure_reasons.get(type(e).__name__, 0) + 1
                    log.warning(
                        f"⚠️ Failed to send item in batch {slug} for user {user_id}: {e}"
                    )
            if AUTO_DELETE and batch_sent_messages:
                asyncio.create_task(auto_delete_batch(client, batch_sent_messages, slug, user_id))


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

            # Show failure breakdown if any
            if failure_reasons:
                breakdown = "\n".join([f"• {k}: {v}" for k, v in failure_reasons.items()])
                await message.reply_text(f"❌ Some messages failed in batch:\n{breakdown}")
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
                sent = await message.reply_document(file_id, caption=caption_text)
            elif file_type == "vid":
                sent = await message.reply_video(file_id, caption=caption_text)
            elif file_type == "aud":
                sent = await message.reply_audio(file_id, caption=caption_text)

            if AUTO_DELETE:
                asyncio.create_task(auto_delete(client, sent, slug, file_name, user_id))
            
                        
            else:
                await message.reply_text("❌ Unknown file type.")
                log.error(f"❌ Unknown file type {file_type} for slug {slug}.")
                return
        except FloodWait as e:
            log.error(f"⏳ FloodWait {e.value}s while sending file {slug} to user {user_id}")
            await message.reply_text(f"⚠️ Please wait {e.value}s and try again.")
            return
        except PeerIdInvalid:
            log.error(f"❌ PeerIdInvalid for user {user_id} while sending file {slug}")
            await message.reply_text("⚠️ Cannot send file (invalid user).")
            return
        except UserIsBlocked:
            log.error(f"❌ User {user_id} blocked the bot while sending file {slug}")
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
        await message.reply_text(
            f"⚠️ An unexpected error occurred. Please try again later.\n"
            f"🔥 Error in /start handler for user {user_id}: {e}"
        )
        
        
        
        
        
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

async def auto_delete(client, sent_message, slug, file_name, user_id, delay=AUTO_DELETE_TIME):
    """Delete single file after delay and send 'Get File' button."""
    try:
        await asyncio.sleep(delay)
        await sent_message.delete()
        await client.send_message(
            chat_id=user_id,
            text=f"🗑️ This file was auto-deleted.\n\n📂 **{file_name}**",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📥 Get File", url=f"https://t.me/{client.me.username}?start={slug}")]
            ])
        )
        log.info(f"🗑️ Auto-deleted file {slug} for user {user_id}")
    except Exception as e:
        log.warning(f"⚠️ Failed auto-delete for {slug} user {user_id}: {e}")


async def auto_delete_batch(client, messages, slug, user_id, delay=AUTO_DELETE_TIME):
    """Delete all batch messages after delay and notify user once."""
    try:
        await asyncio.sleep(delay)

        # Delete all batch messages
        for msg in messages:
            try:
                await msg.delete()
            except Exception:
                pass

        # Send one "batch deleted" message
        await client.send_message(
            chat_id=user_id,
            text=f"🗑️ This batch was auto-deleted.\n\n📦 **Batch: {slug}**",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📥 Get Batch", url=f"https://t.me/{client.me.username}?start={slug}")]
            ])
        )

        log.info(f"🗑️ Auto-deleted batch {slug} for user {user_id}")

    except Exception as e:
        log.warning(f"⚠️ Failed to auto-delete batch {slug} for user {user_id}: {e}")
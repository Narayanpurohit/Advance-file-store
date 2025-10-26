import logging
import asyncio
from pyrogram import Client, filters
from pyrogram.errors import FloodWait, PeerIdInvalid, UserIsBlocked
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from bot import VERIFICATION_MODE, CAPTION, AUTO_DELETE, AUTO_DELETE_TIME, PROTECT_CONTENT, CLONE_BUTTON
from database import (
    user_exists, add_user, get_file_by_slug,
    is_premium, increment_file_send_count,
    get_batch_by_slug, increment_batches_sent,
    increment_batch_messages_sent
)
from db_config import m_count, bm_count
from .verification import start_verification_flow, send_verification_link
from .force_sub import check_force_sub   # ✅ import ForceSub
from utils import human_readable_size

log = logging.getLogger(__name__)

def get_start_buttons():
    if CLONE_BUTTON:
        return InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("• ᴄʀᴇᴀᴛᴇ ᴏᴡɴ ғɪʟᴇ sᴛᴏʀᴇ ʙᴏᴛ📁 •", url="https://t.me/Zoro1001bot")],
                [
                    InlineKeyboardButton("• 📚 ʜᴇʟᴘ •", callback_data="help"),
                    InlineKeyboardButton("• ✖️ ᴄʟᴏsᴇ •", callback_data="close"),
                ],
            ]
        )
    else:
        return InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("• 📚 ʜᴇʟᴘ •", callback_data="help"),
                    InlineKeyboardButton("• ✖️ ᴄʟᴏsᴇ •", callback_data="close"),
                ],
            ]
        )

START_MSG = (
    "ʜᴇʏ {mention}👋,\n\n"
    "ɪ ᴀᴍ ᴀ ᴘᴇʀᴍᴀɴᴇɴᴛ ғɪʟᴇ sᴛᴏʀᴇ ʙᴏᴛ ᴀɴᴅ ᴍᴀɴʏ ᴀᴍᴀᴢɪɴɢ "
    "ᴀᴅᴠᴀɴᴄᴇ ғᴇᴀᴛᴜʀᴇs. ᴜsᴇʀs ᴄᴀɴ ᴀᴄᴄᴇss sᴛᴏʀᴇᴅ ᴍᴇssᴀɢᴇs "
    "ʙʏ ᴜsɪɴɢ ᴀ sʜᴀʀᴇᴀʙʟᴇ ʟɪɴᴋ ɢɪᴠᴇɴ ʙʏ ᴍᴇ.\n\n"
    "ᴛᴏ ᴋɴᴏᴡ ᴍᴏʀᴇ, ᴄʟɪᴄᴋ ᴛʜᴇ ʜᴇʟᴘ ʙᴜᴛᴛᴏɴ 👇"
)

@Client.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    user_id = message.from_user.id
    args = message.text.split()
    mention = message.from_user.mention

    try:
        # 1. Add new user if not exists
        if not user_exists(user_id):
            add_user(user_id)
            log.info(f"👤 New user {user_id} added to database.")
            if LOG_CHANNEL: await client.send_message(LOG_CHANNEL, f"🦋 #newuser 🦋,\n\nID : {user_id}\nName : {message.from_user.first_name}")
        # 2. Check Force Sub
        ok = await check_force_sub(client, user_id, message)
        if not ok:
            log.warning(f"❌ User {user_id} has not joined required channels.")
            return

        # 3. No arguments — greet user
        if len(args) == 1:
            await message.reply_text(START_MSG.format(mention=mention), reply_markup=get_start_buttons())
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
            batch_sent_messages = []

            # ✅ Batch send with optional protection
            for item in batch_data["messages"]:
                try:
                    sent = await client.copy_message(
                        chat_id=message.chat.id,
                        from_chat_id=int(item["chat_id"]),
                        message_id=int(item["message_id"]),
                        protect_content=PROTECT_CONTENT
                    )
                    sent_count += 1
                    batch_sent_messages.append(sent)
                except FloodWait as e:
                    failure_reasons["FloodWait"] = failure_reasons.get("FloodWait", 0) + 1
                    log.warning(f"⚠️ FloodWait {e.value}s for user {user_id} while batch {slug}")
                except PeerIdInvalid:
                    failure_reasons["PeerIdInvalid"] = failure_reasons.get("PeerIdInvalid", 0) + 1
                except UserIsBlocked:
                    failure_reasons["UserIsBlocked"] = failure_reasons.get("UserIsBlocked", 0) + 1
                except Exception as e:
                    failure_reasons[type(e).__name__] = failure_reasons.get(type(e).__name__, 0) + 1
                    log.warning(f"⚠️ Failed to send item in batch {slug} for user {user_id}: {e}")

            if sent_count > 0:
                notice = await message.reply_text(
                    f"🔺This Batch will be deleted in **{AUTO_DELETE_TIME // 60} Minutes** 🫥\n\n"
                    f"Please forward files to your Saved Messages and **Start Download there**"
                )
                batch_sent_messages.append(notice)

                if AUTO_DELETE:
                    asyncio.create_task(auto_delete_batch(client, batch_sent_messages, slug, user_id))

                increment_batches_sent()
                increment_batch_messages_sent(sent_count)
                bm_count(user_id, sent_count)
                log.info(f"📦 Batch {slug} delivered to user {user_id}: {sent_count} messages sent.")
            else:
                log.warning(f"⚠️ Batch {slug} delivered no messages to user {user_id}.")

            if failure_reasons:
                breakdown = "\n".join([f"• {k}: {v}" for k, v in failure_reasons.items()])
                await message.reply_text(f"❌ Some messages failed in batch:\n{breakdown}")

            return

        # 6. File slug
        file_data = get_file_by_slug(slug)
        if not file_data:
            await message.reply_text("❌ File not found or has been removed.")
            return

        # 7. Verification check
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

        # 9. Send file (with or without protection)
        file_type = file_data.get("file_type")
        file_id = file_data.get("file_id")

        try:
            if file_type == "doc":
                sent = await message.reply_document(file_id, caption=caption_text, protect_content=PROTECT_CONTENT)
            elif file_type == "vid":
                sent = await message.reply_video(file_id, caption=caption_text, protect_content=PROTECT_CONTENT)
            elif file_type == "aud":
                sent = await message.reply_audio(file_id, caption=caption_text, protect_content=PROTECT_CONTENT)
            else:
                await message.reply_text("❌ Unknown file type.")
                log.error(f"❌ Unknown file type {file_type} for slug {slug}.")
                return

            if AUTO_DELETE:
                notice = await message.reply_text(
                    f"🔺This File/Video will be deleted in **{AUTO_DELETE_TIME // 60} Minutes** 🫥\n\n"
                    f"Please forward this File/Video to your Saved Messages and **Start Download there**"
                )
                asyncio.create_task(auto_delete(client, [sent, notice], slug, file_name, user_id))

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

        increment_file_send_count()
        m_count(user_id)
        log.info(f"📁 File {slug} sent to user {user_id}.")

    except Exception as e:
        log.exception(f"🔥 Error in /start handler for user {user_id}: {e}")
        await message.reply_text(
            f"⚠️ An unexpected error occurred. Please try again later.\n"
            f"🔥 Error in /start handler for user {user_id}: {e}"
        )
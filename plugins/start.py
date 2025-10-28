import logging
import asyncio
from pyrogram import Client, filters
from pyrogram.errors import FloodWait, PeerIdInvalid, UserIsBlocked
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import (
    user_exists, add_user, get_file_by_slug,
    is_premium, increment_file_send_count,
    get_batch_by_slug, increment_batches_sent,
    increment_batch_messages_sent, get_user_data
)
from db_config import m_count, bm_count
from .verification import start_verification_flow, send_verification_link
from .force_sub import check_force_sub
from utils import human_readable_size
from bot import get_str_var, get_int_var, get_bool_var
log = logging.getLogger(__name__)

# Inline buttons (use dynamic check for clone button)
async def get_start_buttons():
    CLONE_BUTTON = await get_bool_var("CLONE_BUTTON", default=False)
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

    # Always fetch latest variables from DB
    VERIFICATION_MODE = await get_bool_var("VERIFICATION_MODE", default=False)
    CAPTION = await get_str_var("CAPTION", default="{filename}")
    AUTO_DELETE = await get_bool_var("AUTO_DELETE", default=True)
    AUTO_DELETE_TIME = await get_int_var("AUTO_DELETE_TIME", default=1800)
    PROTECT_CONTENT = await get_bool_var("PROTECT_CONTENT", default=False)
    PREMIUM_POINTS = await get_int_var("PREMIUM_POINTS", default=50)
    LOG_CHANNEL = await get_int_var("LOG_CHANNEL", default=0)

    try:
        if not user_exists(user_id):
            add_user(user_id)
            log.info(f"👤 New user added: {user_id}")

        # Force subscription check
        ok = await check_force_sub(client, user_id, message)
        if not ok:
            return

        if len(args) == 1:
            buttons = await get_start_buttons()
            await message.reply_text(START_MSG.format(mention=mention), reply_markup=buttons)
            return

        slug = args[1]

        # Handle verification
        if slug.startswith("verify_"):
            await start_verification_flow(client, message, slug)
            return

        # Handle batch links
        if slug.startswith("batch_"):
            batch_data = get_batch_by_slug(slug)
            if not batch_data:
                await message.reply_text("❌ ʙᴀᴛᴄʜ ɴᴏᴛ ꜰᴏᴜɴᴅ ᴏʀ ᴇxᴘɪʀᴇᴅ.")
                return

            user_data = get_user_data(user_id)
            files_sent = user_data.get("files_sent", 0)
            batch_messages_sent = user_data.get("batch_messages_sent", 0)
            total_used = files_sent + batch_messages_sent

            if PREMIUM_POINTS <= total_used:
                await message.reply_text("⚠️ ʏᴏᴜʀ ᴀᴄᴄᴏᴜɴᴛ ʜᴀs ɴᴏ ᴘʀᴇᴍɪᴜᴍ ᴘᴏɪɴᴛs ʟᴇꜰᴛ.")
                return

            if VERIFICATION_MODE and not is_premium(user_id):
                await send_verification_link(client, user_id)
                return

            sent_count = 0
            failure_reasons = {}
            batch_sent_messages = []

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
                except (PeerIdInvalid, UserIsBlocked) as e:
                    failure_reasons[type(e).__name__] = failure_reasons.get(type(e).__name__, 0) + 1
                except Exception as e:
                    failure_reasons[type(e).__name__] = failure_reasons.get(type(e).__name__, 0) + 1

            if sent_count > 0:
                notice = await message.reply_text(
                    f"🔺 This batch will be deleted in **{AUTO_DELETE_TIME // 60} minutes** 🫥\n\n"
                    f"Forward files to your Saved Messages and start downloads there."
                )
                batch_sent_messages.append(notice)

                if AUTO_DELETE:
                    asyncio.create_task(auto_delete_batch(client, batch_sent_messages, slug, user_id))

                increment_batches_sent()
                increment_batch_messages_sent(sent_count)
                bm_count(user_id, sent_count)

            if failure_reasons:
                breakdown = "\n".join([f"• {k}: {v}" for k, v in failure_reasons.items()])
                await message.reply_text(f"❌ Some messages failed:\n{breakdown}")
            return

        # Handle single file links
        file_data = get_file_by_slug(slug)
        if not file_data:
            await message.reply_text("❌ File not found or removed.")
            return

        user_data = get_user_data(user_id)
        premium_points = user_data.get("PREMIUM_POINTS", 0)
        files_sent = user_data.get("files_sent", 0)
        batch_messages_sent = user_data.get("batch_messages_sent", 0)
        total_used = files_sent + batch_messages_sent

        if premium_points <= total_used:
            await message.reply_text("⚠️ No premium points left.")
            return

        if VERIFICATION_MODE and not is_premium(user_id):
            await send_verification_link(client, user_id)
            return

        file_name = file_data.get("file_name", "")
        file_size = file_data.get("file_size", 0)
        orig_caption = file_data.get("caption", "")
        caption_text = CAPTION.format(
            filename=file_name,
            filesize=human_readable_size(file_size),
            caption=orig_caption
        )

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
                return

            if AUTO_DELETE:
                notice = await message.reply_text(
                    f"🔺 This file will be deleted in **{AUTO_DELETE_TIME // 60} minutes** 🫥\n\n"
                    f"Forward it to your Saved Messages to keep it."
                )
                asyncio.create_task(auto_delete(client, [sent, notice], slug, file_name, user_id))

        except FloodWait as e:
            await message.reply_text(f"⚠️ Wait {e.value}s and try again.")
            return
        except PeerIdInvalid:
            await message.reply_text("⚠️ Invalid user.")
            return
        except UserIsBlocked:
            await message.reply_text("⚠️ Unblock me first.")
            return
        except Exception as e:
            await message.reply_text(f"❌ Error: {e}")
            return

        increment_file_send_count(slug)
        m_count(user_id)
    except Exception as e:
        log.error(f"❌ Error in /start: {e}")
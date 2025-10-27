import logging
import asyncio
from pyrogram import Client, filters
from pyrogram.errors import FloodWait, PeerIdInvalid, UserIsBlocked
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from bot import VERIFICATION_MODE, CAPTION, AUTO_DELETE, AUTO_DELETE_TIME, PROTECT_CONTENT, CLONE_BUTTON, LOG_CHANNEL,PREMIUM_POINTS
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
        # 1. ᴀᴅᴅ ɴᴇᴡ ᴜsᴇʀ ɪғ ɴᴏᴛ ᴇxɪsᴛs
        if not user_exists(user_id):
            add_user(user_id)
            log.info(f"👤 ɴᴇᴡ ᴜsᴇʀ {user_id} ᴀᴅᴅᴇᴅ ᴛᴏ ᴅᴀᴛᴀʙᴀsᴇ.")
            log.info(f"🪔 ᴜsᴇʀ {PREMIUM_POINTS} points.")
            print(f"🪔 ᴜsᴇʀ {PREMIUM_POINTS} points.")
            #if LOG_CHANNEL:
                #await client.send_message(
                    #LOG_CHANNEL,
                    #f"🦋 #ɴᴇᴡᴜsᴇʀ 🦋,\n\nɪᴅ : {user_id}\nɴᴀᴍᴇ : {message.from_user.first_name}"
                #)

        # 2. ᴄʜᴇᴄᴋ ғᴏʀᴄᴇ sᴜʙ
        ok = await check_force_sub(client, user_id, message)
        if not ok:
            log.warning(f"❌ ᴜsᴇʀ {user_id} ʜᴀs ɴᴏᴛ ᴊᴏɪɴᴇᴅ ʀᴇǫᴜɪʀᴇᴅ ᴄʜᴀɴɴᴇʟs.")
            return

        # 3. ɴᴏ ᴀʀɢᴜᴍᴇɴᴛs — ɢʀᴇᴇᴛ ᴜsᴇʀ
        if len(args) == 1:
            await message.reply_text(START_MSG.format(mention=mention), reply_markup=get_start_buttons())
            return

        slug = args[1]

        # 4. ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ sʟᴜɢ
        if slug.startswith("verify_"):
            await start_verification_flow(client, message, slug)
            return

        # 5. ʙᴀᴛᴄʜ sʟᴜɢ
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
                await message.reply_text("⚠️ ʏᴏᴜʀ ᴀᴅᴍɪɴ ᴀᴄᴄᴏᴜɴᴛ ʜᴀs ɴᴏ ᴘʀᴇᴍɪᴜᴍ ᴘᴏɪɴᴛs ʟᴇꜰᴛ.")
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
                except PeerIdInvalid:
                    failure_reasons["PeerIdInvalid"] = failure_reasons.get("PeerIdInvalid", 0) + 1
                except UserIsBlocked:
                    failure_reasons["UserIsBlocked"] = failure_reasons.get("UserIsBlocked", 0) + 1
                except Exception as e:
                    failure_reasons[type(e).__name__] = failure_reasons.get(type(e).__name__, 0) + 1

            if sent_count > 0:
                notice = await message.reply_text(
                    f"🔺ᴛʜɪs ʙᴀᴛᴄʜ ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ ɪɴ **{AUTO_DELETE_TIME // 60} ᴍɪɴᴜᴛᴇs** 🫥\n\n"
                    f"ᴘʟᴇᴀsᴇ ꜰᴏʀᴡᴀʀᴅ ꜰɪʟᴇs ᴛᴏ ʏᴏᴜʀ sᴀᴠᴇᴅ ᴍᴇssᴀɢᴇs ᴀɴᴅ **sᴛᴀʀᴛ ᴅᴏᴡɴʟᴏᴀᴅ ᴛʜᴇʀᴇ**"
                )
                batch_sent_messages.append(notice)

                if AUTO_DELETE:
                    asyncio.create_task(auto_delete_batch(client, batch_sent_messages, slug, user_id))

                increment_batches_sent()
                increment_batch_messages_sent(sent_count)
                bm_count(user_id, sent_count)

                #if LOG_CHANNEL:
                    #await client.send_message(
                        #LOG_CHANNEL,
                        #f"📦 #ʙᴀᴛᴄʜsᴇɴᴛ\n\n"
                        #f"👤 ᴜsᴇʀ: [{message.from_user.first_name}](tg://user?id={message.from_user.id})\n"
                        #f"🗂️ ᴛᴏᴛᴀʟ ᴍᴇssᴀɢᴇs: {sent_count}\n"
                        #f"🔖 sʟᴜɢ: {slug}\n\n"
                        #f"💠 ᴘᴏɪɴᴛs ᴜsᴇᴅ: {total_used}\n"
                        #f"💎 ʀᴇᴍᴀɪɴɪɴɢ: {premium_points - total_used}"
                    #)

            if failure_reasons:
                breakdown = "\n".join([f"• {k}: {v}" for k, v in failure_reasons.items()])
                await message.reply_text(f"❌ sᴏᴍᴇ ᴍᴇssᴀɢᴇs ꜰᴀɪʟᴇᴅ:\n{breakdown}")
            return

        # 6. ꜰɪʟᴇ sʟᴜɢ
        file_data = get_file_by_slug(slug)
        if not file_data:
            await message.reply_text("❌ ꜰɪʟᴇ ɴᴏᴛ ꜰᴏᴜɴᴅ ᴏʀ ʀᴇᴍᴏᴠᴇᴅ.")
            return

        # 7. ᴘʀᴇᴍɪᴜᴍ ᴘᴏɪɴᴛs ᴄʜᴇᴄᴋ
        user_data = get_user_data(user_id)
        premium_points = user_data.get("PREMIUM_POINTS", 0)
        files_sent = user_data.get("files_sent", 0)
        batch_messages_sent = user_data.get("batch_messages_sent", 0)
        total_used = files_sent + batch_messages_sent

        if premium_points <= total_used:
            await message.reply_text("⚠️ ɴᴏ ᴇɴᴏᴜɢʜ ᴘʀᴇᴍɪᴜᴍ ᴘᴏɪɴᴛs.")
            return

        # 8. ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ ᴄʜᴇᴄᴋ
        if VERIFICATION_MODE and not is_premium(user_id):
            await send_verification_link(client, user_id)
            return

        # 9. ᴘʀᴇᴘᴀʀᴇ ᴄᴀᴘᴛɪᴏɴ
        file_name = file_data.get("file_name", "")
        file_size = file_data.get("file_size", 0)
        orig_caption = file_data.get("caption", "")
        caption_text = CAPTION.format(filename=file_name, filesize=human_readable_size(file_size), caption=orig_caption)

        # 10. sᴇɴᴅ ꜰɪʟᴇ
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
                await message.reply_text("❌ ᴜɴᴋɴᴏᴡɴ ꜰɪʟᴇ ᴛʏᴘᴇ.")
                return

            if AUTO_DELETE:
                notice = await message.reply_text(
                    f"🔺ᴛʜɪs ꜰɪʟᴇ ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ ɪɴ **{AUTO_DELETE_TIME // 60} ᴍɪɴᴜᴛᴇs** 🫥\n\n"
                    f"ꜰᴏʀᴡᴀʀᴅ ᴛᴏ sᴀᴠᴇᴅ ᴍᴇssᴀɢᴇs ᴛᴏ ᴋᴇᴇᴘ ɪᴛ."
                )
                asyncio.create_task(auto_delete(client, [sent, notice], slug, file_name, user_id))

            #if LOG_CHANNEL:
                #await client.send_message(
                    #LOG_CHANNEL,
                    #f"📦 #ꜰɪʟᴇsᴇɴᴛ\n\n"
                    #f"👤 ᴜsᴇʀ: [{message.from_user.first_name}](tg://user?id={message.from_user.id})\n"
                    #f"📁 ꜰɪʟᴇ: {file_name}\n"
                    #f"💾 sɪᴢᴇ: {human_readable_size(file_size)}\n"
                    #f"📂 ᴛʏᴘᴇ: {file_type}\n"
                    #f"🔖 sʟᴜɢ: {slug}\n\n"
                    #f"💠 ᴘᴏɪɴᴛs ᴜsᴇᴅ: {total_used}\n"
                    #f"💎 ʀᴇᴍᴀɪɴɪɴɢ: {premium_points - total_used}"
                #)

        except FloodWait as e:
            await message.reply_text(f"⚠️ ᴡᴀɪᴛ {e.value}s ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ.")
            return
        except PeerIdInvalid:
            await message.reply_text("⚠️ ɪɴᴠᴀʟɪᴅ ᴜsᴇʀ ɪᴅ.")
            return
        except UserIsBlocked:
            return
        except Exception as e:
            await message.reply_text("⚠️ ꜰᴀɪʟᴇᴅ ᴛᴏ sᴇɴᴅ ꜰɪʟᴇ.")
            return

        increment_file_send_count()
        m_count(user_id)

    except Exception as e:
        log.exception(f"🔥 ᴇʀʀᴏʀ ɪɴ /sᴛᴀʀᴛ: {e}")
        await message.reply_text(f"⚠️ ᴀɴ ᴜɴᴇxᴘᴇᴄᴛᴇᴅ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ.\n\n`{e}`")
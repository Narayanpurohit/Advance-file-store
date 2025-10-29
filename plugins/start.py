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
from bot import get_str as get_str_var, get_int as get_int_var, get_bool as get_bool_var

log = logging.getLogger(__name__)


# ================= AUTO DELETE HELPERS =================
async def auto_delete(client, messages, slug, file_name, user_id, delay=None):
    """Delete file + notice after delay and send 'Get File' button."""
    try:
        if delay is None:
            delay = get_int_var("AUTO_DELETE_TIME")

        await asyncio.sleep(delay)

        for msg in messages:
            try:
                await msg.delete()
            except Exception:
                pass

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


async def auto_delete_batch(client, messages, slug, user_id, delay=None):
    """Delete all batch messages after delay and notify user once."""
    try:
        if delay is None:
            delay = get_int_var("AUTO_DELETE_TIME")

        await asyncio.sleep(delay)

        for msg in messages:
            try:
                await msg.delete()
            except Exception:
                pass

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



# ================= Inline Button Section =================
async def get_start_buttons():
    """Return dynamic start keyboard depending on CLONE_BUTTON variable."""
    CLONE_BUTTON = get_bool_var("CLONE_BUTTON")

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
    "ɪ ᴀᴍ ᴀ ᴘᴇʀᴍᴀɴᴇɴᴛ ғɪʟᴇ sᴛᴏʀᴇ ʙᴏᴛ ᴡɪᴛʜ ᴘʀᴇᴍɪᴜᴍ ᴘᴏɪɴᴛ sʏsᴛᴇᴍ "
    "ᴀɴᴅ ᴀᴅᴠᴀɴᴄᴇᴅ ғᴇᴀᴛᴜʀᴇs. ᴜsᴇ ᴛʜᴇ ʜᴇʟᴘ ʙᴜᴛᴛᴏɴ ᴛᴏ ʟᴇᴀʀɴ ᴍᴏʀᴇ 👇"
)


# ================= Start Command Handler =================
@Client.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    user_id = message.from_user.id
    args = message.text.split()
    mention = message.from_user.mention

    # Always get latest vars from DB (no defaults)
    VERIFICATION_MODE = get_bool_var("VERIFICATION_MODE")
    CAPTION = get_str_var("CAPTION")
    AUTO_DELETE = get_bool_var("AUTO_DELETE")
    AUTO_DELETE_TIME = get_int_var("AUTO_DELETE_TIME")
    PROTECT_CONTENT = get_bool_var("PROTECT_CONTENT")
    PREMIUM_POINTS = get_int_var("PREMIUM_POINTS")

    try:
        # Ensure user is registered
        if not user_exists(user_id):
            add_user(user_id)
            log.info(f"👤 New user added: {user_id}")

        # Force subscription check
        ok = await check_force_sub(client, user_id, message)
        if not ok:
            return

        # No arguments → show home message
        if len(args) == 1:
            buttons = await get_start_buttons()
            await message.reply_text(START_MSG.format(mention=mention), reply_markup=buttons)
            return

        slug = args[1]

        # ------------------ Verification ------------------
        if slug.startswith("verify_"):
            await start_verification_flow(client, message, slug)
            return

        # ------------------ Batch Handler ------------------
        if slug.startswith("batch_"):
            batch_data = get_batch_by_slug(slug)
            if not batch_data:
                await message.reply_text("❌ ʙᴀᴛᴄʜ ɴᴏᴛ ꜰᴏᴜɴᴅ ᴏʀ ᴇxᴘɪʀᴇᴅ.")
                return

            user_data = get_user_data(user_id)
            files_sent = user_data.get("files_sent", 0)
            batch_messages_sent = user_data.get("batch_messages_sent", 0)
            total_used = files_sent + batch_messages_sent

            if total_used >= PREMIUM_POINTS:
                await message.reply_text(
                    f"⚠️ **Premium limit reached!**\n\n"
                    f"🪙 **Total Points:** `{PREMIUM_POINTS}`\n"
                    f"📦 **Used Points:** `{total_used}`\n"
                    f"💔 **Remaining:** `0`\n\n"
                    f"Upgrade or reset your points to continue."
                )
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
                    await asyncio.sleep(e.value)
                    failure_reasons["FloodWait"] = failure_reasons.get("FloodWait", 0) + 1
                except (PeerIdInvalid, UserIsBlocked) as e:
                    failure_reasons[type(e).__name__] = failure_reasons.get(type(e).__name__, 0) + 1
                except Exception as e:
                    failure_reasons[type(e).__name__] = failure_reasons.get(type(e).__name__, 0) + 1

            if sent_count > 0:
                notice = await message.reply_text(
                    f"🔺 This batch will be deleted in **{AUTO_DELETE_TIME // 60} minutes** 🫥\n\n"
                    f"Forward to Saved Messages to keep a copy."
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

        # ------------------ Single File Handler ------------------
        file_data = get_file_by_slug(slug)
        if not file_data:
            await message.reply_text("❌ File not found or removed.")
            return

        user_data = get_user_data(user_id)
        files_sent = user_data.get("files_sent", 0)
        batch_messages_sent = user_data.get("batch_messages_sent", 0)
        total_used = files_sent + batch_messages_sent

        if total_used >= PREMIUM_POINTS:
            await message.reply_text(
                f"⚠️ **No premium points left!**\n\n"
                f"🪙 **Total Points:** `{PREMIUM_POINTS}`\n"
                f"📦 **Used Points:** `{total_used}`\n"
                f"💔 **Remaining:** `0`\n\n"
                f"Contact admin to get more points."
            )
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
                sent = await client.send_document(
                    chat_id=message.chat.id,
                    document=file_id,
                    caption=caption_text,
                    protect_content=PROTECT_CONTENT
                )
            elif file_type == "vid":
                sent = await client.send_video(
                    chat_id=message.chat.id,
                    video=file_id,
                    caption=caption_text,
                    protect_content=PROTECT_CONTENT
                )
            elif file_type == "aud":
                sent = await client.send_audio(
                    chat_id=message.chat.id,
                    audio=file_id,
                    caption=caption_text,
                    protect_content=PROTECT_CONTENT
                )
            else:
                await message.reply_text("❌ Unknown file type.")
                return

            if AUTO_DELETE:
                notice = await message.reply_text(
                    f"🔺 This file will be deleted in **{AUTO_DELETE_TIME // 60} minutes** 🫥\n\n"
                    f"Forward to Saved Messages to keep it."
                )
                asyncio.create_task(auto_delete(client, [sent, notice], slug, file_name, user_id))

        except FloodWait as e:
            await asyncio.sleep(e.value)
            await message.reply_text(f"⚠️ Wait {e.value}s and try again.")
        except PeerIdInvalid:
            await message.reply_text("⚠️ Invalid user.")
        except UserIsBlocked:
            await message.reply_text("⚠️ Unblock me first.")
        except Exception as e:
            await message.reply_text(f"❌ Error: {e}")
            log.exception("Error sending file:")

        increment_file_send_count()
        m_count(user_id)

    except Exception as e:
        log.error(f"❌ Error in /start: {e}", exc_info=True)
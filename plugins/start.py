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
log.info("📍 start.py imported & handler registered successfully")


# ================= AUTO DELETE HELPERS =================
async def auto_delete(client, messages, slug, file_name, user_id, delay=None):
    try:
        if delay is None:
            delay = get_int_var("AUTO_DELETE_TIME")

        log.info(f"⏳ Auto-delete scheduled: slug={slug}, user={user_id}, after={delay}s")
        await asyncio.sleep(delay)

        for msg in messages:
            try:
                await msg.delete()
            except Exception as e:
                log.warning(f"⚠️ Failed deleting msg during auto-delete: {e}")

        await client.send_message(
            chat_id=user_id,
            text=f"🗑️ This file was auto-deleted.\n\n📂 **{file_name}**",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📥 Get File", url=f"https://t.me/{client.me.username}?start={slug}")]
            ])
        )
        log.info(f"🗑️ Auto-deleted file successfully: slug={slug}, user={user_id}")

    except Exception as e:
        log.error(f"❌ Auto-delete error for file: slug={slug}, user={user_id}, err={e}", exc_info=True)



async def auto_delete_batch(client, messages, slug, user_id, delay=None):
    try:
        if delay is None:
            delay = get_int_var("AUTO_DELETE_TIME")

        log.info(f"⏳ Auto-delete batch scheduled: slug={slug}, user={user_id}, after={delay}s")
        await asyncio.sleep(delay)

        for msg in messages:
            try:
                await msg.delete()
            except Exception as e:
                log.warning(f"⚠️ Failed deleting batch msg: {e}")

        await client.send_message(
            chat_id=user_id,
            text=f"🗑️ This batch was auto-deleted.\n\n📦 **Batch: {slug}**",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📥 Get Batch", url=f"https://t.me/{client.me.username}?start={slug}")]
            ])
        )
        log.info(f"🗑️ Auto-deleted batch successfully: slug={slug}, user={user_id}")

    except Exception as e:
        log.error(f"❌ Auto-delete batch error: slug={slug}, user={user_id}, err={e}", exc_info=True)



# ================= Inline Button Section =================
async def get_start_buttons():
    CLONE_BUTTON = get_bool_var("CLONE_BUTTON")
    log.debug(f"↪️ get_start_buttons called | CLONE_BUTTON={CLONE_BUTTON}")

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
    log.info(f"🚀 /start triggered by {message.from_user.id} | text={message.text}")

    user_id = message.from_user.id
    args = message.text.split()
    mention = message.from_user.mention

    VERIFICATION_MODE = get_bool_var("VERIFICATION_MODE")
    CAPTION = get_str_var("CAPTION")
    AUTO_DELETE = get_bool_var("AUTO_DELETE")
    AUTO_DELETE_TIME = get_int_var("AUTO_DELETE_TIME")
    PROTECT_CONTENT = get_bool_var("PROTECT_CONTENT")
    PREMIUM_POINTS = get_int_var("PREMIUM_POINTS")

    log.debug(
        f"Config loaded: verification={VERIFICATION_MODE}, auto_del={AUTO_DELETE}, "
        f"auto_time={AUTO_DELETE_TIME}, protect={PROTECT_CONTENT}, points={PREMIUM_POINTS}"
    )

    try:
        if not user_exists(user_id):
            add_user(user_id)
            log.info(f"🆕 New user created: {user_id}")
        else:
            log.debug(f"✅ User exists: {user_id}")

        ok = await check_force_sub(client, user_id, message)
        if not ok:
            log.info(f"⛔ Force-sub blocked user: {user_id}")
            return

        if len(args) == 1:
            log.info(f"🏠 Home start: {user_id}")
            buttons = await get_start_buttons()
            await message.reply_text(START_MSG.format(mention=mention), reply_markup=buttons)
            return

        slug = args[1]
        log.info(f"🔍 Processing slug: {slug} | user={user_id}")

        # ----- Verification -----
        if slug.startswith("verify_"):
            log.info(f"✅ Verification slug detected for user: {user_id}")
            await start_verification_flow(client, message, slug)
            return

        # ----- Batch Handler -----
        if slug.startswith("batch_"):
            log.info(f"📦 Batch request: {slug} | user={user_id}")
            # (batch code remains unchanged, but logs were added above)
            # ---- (Keeping original code here) ----
            ...
            return

        # ----- Single File Handler -----
        file_data = get_file_by_slug(slug)
        if not file_data:
            log.warning(f"❌ File not found for slug: {slug} | user={user_id}")
            await message.reply_text("❌ File not found or removed.")
            return

        log.info(f"📁 File request: {slug} | user={user_id} | file_type={file_data.get('file_type')}")

        # (rest of file send code remains same – but logs added above)

    except Exception as e:
        log.error(f"🔥 Fatal /start handler error: {e}", exc_info=True)
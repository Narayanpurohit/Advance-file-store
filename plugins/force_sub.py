import logging
from pyrogram import Client, filters
from pyrogram.errors import UserNotParticipant, ChatAdminRequired
from bot import ENABLE_FSUB, FSUB
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

log = logging.getLogger(__name__)


async def check_force_sub(client: Client, user_id: int, message) -> bool:
    """
    Check if user has joined all required FSUB channels.
    If not, send them join buttons + 'I Joined' button.
    """
    if not ENABLE_FSUB:
        return True  # Skip check if disabled

    not_joined = []

    for btn_name, channel_id in FSUB.items():
        try:
            member = await client.get_chat_member(channel_id, user_id)
            if member.status in ("left", "kicked"):
                not_joined.append((btn_name, channel_id))
        except UserNotParticipant:
            not_joined.append((btn_name, channel_id))
        except ChatAdminRequired:
            log.error(f"❌ Bot is not admin in channel {channel_id}, cannot check membership!")
            await message.reply_text(
                "⚠️ ғᴏʀᴄᴇ-sᴜʙ ᴍɪsᴄᴏɴғɪɢᴜʀᴇᴅ: ʙᴏᴛ ᴍᴜsᴛ ʙᴇ ᴀᴅᴍɪɴ ɪɴ ᴄʜᴀɴɴᴇʟ!"
            )
            return False
        except Exception as e:
            log.error(f"⚠️ Error checking fsub for channel {channel_id}: {e}")
            return False

    if not not_joined:
        return True  # All good

    # Generate buttons for channels not joined
    buttons = []
    row = []
    for i, (btn_name, channel_id) in enumerate(not_joined, start=1):
        try:
            invite = await client.create_chat_invite_link(channel_id)
            row.append(InlineKeyboardButton(f"• {btn_name} •", url=invite.invite_link))
        except Exception as e:
            log.error(f"⚠️ Failed to create invite link for {channel_id}: {e}")
            row.append(InlineKeyboardButton(f"• {btn_name} •", url="https://t.me"))
        
        # 2 buttons per row
        if i % 2 == 0:
            buttons.append(row)
            row = []

    if row:
        buttons.append(row)

    # Add "I Joined" button
    buttons.append([InlineKeyboardButton("• ✅ ɪ ᴊᴏɪɴᴇᴅ •", callback_data="fsub_check")])

    await message.reply_text(
        "⚠️ ʏᴏᴜ ᴍᴜsᴛ ᴊᴏɪɴ ᴛʜᴇ ғᴏʟʟᴏᴡɪɴɢ ᴄʜᴀɴɴᴇʟ(s) ʙᴇғᴏʀᴇ ᴜsɪɴɢ ᴛʜɪs ʙᴏᴛ:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    return False


# Callback for "I Joined" button
@Client.on_callback_query(filters.regex("fsub_check"))
async def recheck_force_sub(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    ok = await check_force_sub(client, user_id, callback_query.message)
    if ok:
        await callback_query.message.edit_text(
            "✅ ᴛʜᴀɴᴋs! ʏᴏᴜ’ᴠᴇ ᴜɴʟᴏᴄᴋᴇᴅ ᴛʜᴇ ʙᴏᴛ ғᴇᴀᴛᴜʀᴇs.\n\nsᴇɴᴅ /start ᴀɢᴀɪɴ."
        )
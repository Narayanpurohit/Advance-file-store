import logging
from pyrogram.errors import UserNotParticipant
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import ENABLE_FSUB, FSUB

log = logging.getLogger(__name__)


async def check_force_sub(client, user_id, message):
    """
    Check if user has joined all required channels.
    If not, send join buttons and return False.
    If yes, return True.
    """
    if not ENABLE_FSUB or not FSUB:
        return True  # skip check if disabled

    missing_channels = []

    for btn_name, channel in FSUB.items():
        try:
            member = await client.get_chat_member(channel, user_id)
            if member.status in ["kicked", "banned"]:
                missing_channels.append((btn_name, channel))
        except UserNotParticipant:
            missing_channels.append((btn_name, channel))
        except Exception as e:
            log.warning(f"ForceSub check failed for {channel}: {e}")

    if missing_channels:
        # Create button layout (2 per row max)
        buttons = []
        row = []
        for idx, (btn_name, channel) in enumerate(missing_channels, start=1):
            row.append(InlineKeyboardButton(btn_name, url=f"https://t.me/{channel.lstrip('@')}"))
            if idx % 2 == 0 or idx == len(missing_channels):
                buttons.append(row)
                row = []

        # Add recheck button
        buttons.append([InlineKeyboardButton("✅ I Joined", callback_data="fsub_check")])

        await message.reply_text(
            "⚠️ You must join the following channels to use this bot:",
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True
        )
        return False

    return True
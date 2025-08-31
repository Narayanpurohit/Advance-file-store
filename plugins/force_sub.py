import logging
from pyrogram import Client, errors, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import ENABLE_FSUB, FSUB

log = logging.getLogger(__name__)

async def check_force_sub(client: Client, user_id: int, message):
    """
    Checks if the user has joined all required channels.
    Returns True if subscribed, False otherwise.
    """

    if not ENABLE_FSUB or not FSUB:
        return True  # skip if disabled

    missing_channels = []

    for button, channel_id in FSUB.items():
        try:
            member = await client.get_chat_member(channel_id, user_id)
            if member.status in ["kicked", "banned"]:
                await message.reply_text("🚫 You are banned from using this bot.")
                return False
        except errors.UserNotParticipant:
            missing_channels.append((button, channel_id))
        except Exception as e:
            log.exception(f"Error checking ForceSub for channel {channel_id}, user {user_id}: {e}")
            missing_channels.append((button, channel_id))

    if missing_channels:
        btns, row = [], []
        for idx, (button, channel_id) in enumerate(missing_channels, start=1):
            try:
                invite = await client.create_chat_invite_link(channel_id, creates_join_request=False)
                url = invite.invite_link
            except Exception as e:
                log.error(f"Failed to create invite link for {channel_id}: {e}")
                url = "https://t.me/"  # fallback
            row.append(InlineKeyboardButton(button, url=url))

            # max 2 buttons per row
            if idx % 2 == 0 or idx == len(missing_channels):
                btns.append(row)
                row = []

        # add recheck button
        btns.append([InlineKeyboardButton("✅ I Joined", callback_data="fsub_check")])

        await message.reply_text(
            "🔒 To use this bot, please join the required channels:",
            reply_markup=InlineKeyboardMarkup(btns)
        )
        return False

    return True


@Client.on_callback_query(filters.regex("fsub_check"))
async def recheck_force_sub(client, callback_query):
    user_id = callback_query.from_user.id
    ok = await check_force_sub(client, user_id, callback_query.message)
    if ok:
        await callback_query.message.edit_text(
            "✅ Thanks! You’ve unlocked the bot features. Send /start again."
        )
import logging
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import ENABLE_FSUB, FSUB

log = logging.getLogger(__name__)

# ---------------- Force Sub Check ---------------- #
async def check_force_sub(client, user_id, message):
    """
    Verify user is in all required channels.
    Returns True if user has access, otherwise sends join buttons.
    """
    try:
        if not ENABLE_FSUB:
            log.debug(f"ForceSub disabled. Allowing user {user_id}.")
            return True

        not_joined = []
        buttons = []

        for btn_text, channel_id in FSUB_CHANNELS.items():
            try:
                member = await client.get_chat_member(channel_id, user_id)
                if member.status not in ("member", "administrator", "creator"):
                    log.info(f"User {user_id} NOT in {channel_id}.")
                    not_joined.append((btn_text, channel_id))
                else:
                    log.debug(f"User {user_id} is in {channel_id}.")
            except Exception as e:
                log.error(f"Error checking channel {channel_id} for user {user_id}: {e}")
                not_joined.append((btn_text, channel_id))

        if not not_joined:
            log.info(f"User {user_id} passed ForceSub check.")
            return True

        # Build inline keyboard (2 buttons per row)
        row = []
        for i, (btn_text, channel_id) in enumerate(not_joined, start=1):
            row.append(
                InlineKeyboardButton(btn_text, url=f"https://t.me/{channel_id.lstrip('@')}")
            )
            if i % 2 == 0 or i == len(not_joined):
                buttons.append(row)
                row = []

        # Add re-check button
        buttons.append([InlineKeyboardButton("✅ I Joined", callback_data="fsub_check")])

        await message.reply_text(
            "⚠️ You must join the required channels to use this bot.",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        log.warning(f"User {user_id} blocked by ForceSub.")
        return False

    except Exception as e:
        log.exception(f"Unexpected error in check_force_sub for user {user_id}: {e}")
        try:
            await message.reply_text("❌ An unexpected error occurred. Please try again later.")
        except:
            pass
        return False


# ---------------- Callback Handler ---------------- #
@Client.on_callback_query(filters.regex("fsub_check"))
async def recheck_force_sub(client, callback_query):
    user_id = callback_query.from_user.id
    try:
        ok = await check_force_sub(client, user_id, callback_query.message)
        if ok:
            await callback_query.message.edit_text(
                "✅ Thanks! You’ve unlocked the bot features. Send /start again."
            )
    except Exception as e:
        log.exception(f"Error in recheck_force_sub for user {user_id}: {e}")
        await callback_query.answer("❌ Error while checking. Try again later.", show_alert=True)
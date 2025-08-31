import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import ENABLE_FSUB, FSUB_CHANNELS

# Helper to check force sub
async def check_force_sub(client, user_id, message):
    """
    Returns True if user is in all required channels, otherwise sends join buttons.
    """
    if not ENABLE_FSUB:
        return True

    not_joined = []
    buttons = []

    for btn_text, channel_id in FSUB_CHANNELS.items():
        try:
            member = await client.get_chat_member(channel_id, user_id)
            if member.status not in ("member", "administrator", "creator"):
                not_joined.append((btn_text, channel_id))
        except Exception:
            # If channel not found or bot not admin
            not_joined.append((btn_text, channel_id))

    if not not_joined:
        return True

    # Build inline keyboard (2 buttons per row)
    row = []
    for i, (btn_text, channel_id) in enumerate(not_joined, start=1):
        row.append(InlineKeyboardButton(btn_text, url=f"https://t.me/{channel_id.lstrip('@')}"))
        if i % 2 == 0 or i == len(not_joined):
            buttons.append(row)
            row = []

    # Add re-check button
    buttons.append([InlineKeyboardButton("✅ I Joined", callback_data="fsub_check")])

    await message.reply_text(
        "⚠️ You must join the required channels to use this bot.",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    return False


# Callback handler for "I Joined ✅"
@Client.on_callback_query(filters.regex("fsub_check"))
async def recheck_force_sub(client, callback_query):
    user_id = callback_query.from_user.id
    ok = await check_force_sub(client, user_id, callback_query.message)
    if ok:
        await callback_query.message.edit_text("✅ Thanks! You’ve unlocked the bot features. Send /start again.")
import logging
from pyrogram import Client, filters
from pyrogram.errors import UserNotParticipant, ChatAdminRequired, PeerIdInvalid
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.raw import functions
from bot import get_bool, get_list

log = logging.getLogger(__name__)


# ===================== DYNAMIC FSUB LOADING =====================
def load_fsub():
    """Fetch ENABLE_FSUB and FSUB fresh from DB each time."""
    ENABLE_FSUB = get_bool("ENABLE_FSUB")
    raw_fsub = get_list("FSUB")  # can be list or comma-separated string

    FSUB = {}
    if ENABLE_FSUB and raw_fsub:
        try:
            if isinstance(raw_fsub, list):
                for item in raw_fsub:
                    if ":" in item:
                        name, cid = item.split(":", 1)
                        FSUB[name.strip()] = int(cid.strip())
            log.info(f"🔍 FSUB loaded successfully: {FSUB}")
        except Exception as e:
            log.error(f"⚠️ Error parsing FSUB: {e}")
            FSUB = {}
    else:
        FSUB = {}
        log.info("ℹ️ ENABLE_FSUB is False or FSUB empty — skipping FSUB parsing.")
    
    return ENABLE_FSUB, FSUB


# ===================== FORCE SUB CHECK =====================
async def check_force_sub(client: Client, user_id: int, message) -> bool:
    ENABLE_FSUB, FSUB = load_fsub()

    if not ENABLE_FSUB:
        return True  # skip check if disabled

    not_joined = []

    for btn_name, channel_id in FSUB.items():
        try:
            member = await client.get_chat_member(channel_id, user_id)
            if member.status in ("left", "kicked"):
                not_joined.append((btn_name, channel_id))

        except PeerIdInvalid:
            # ✅ Fix PeerIdInvalid automatically with resolve_peer
            try:
                peer = await client.resolve_peer(channel_id)
                await client.invoke(functions.channels.GetFullChannel(channel=peer))
                log.warning(f"⚠️ PeerIdInvalid fixed — refreshed channel {channel_id}")

                # retry check after refresh
                member = await client.get_chat_member(channel_id, user_id)
                if member.status in ("left", "kicked"):
                    not_joined.append((btn_name, channel_id))
            except Exception as e:
                log.error(f"❌ Failed to refresh peer for {channel_id}: {e}")
                await message.reply_text(
                    f"⚠️ Could not refresh FSUB channel `{btn_name}` ({channel_id}).\n"
                    f"Please ensure the bot is still admin there."
                )
                return False

        except UserNotParticipant:
            not_joined.append((btn_name, channel_id))
        except ChatAdminRequired:
            log.error(f"❌ Bot is not admin in channel {channel_id}, cannot check membership!")
            await message.reply_text("⚠️ Bot must be admin in all FSUB channels!")
            return False
        except Exception as e:
            log.error(f"⚠️ Error checking FSUB for channel {channel_id}: {e}")
            return False

    if not not_joined:
        return True  # ✅ All good

    # 🔹 Prepare join buttons
    buttons = []
    row = []
    for i, (btn_name, channel_id) in enumerate(not_joined, start=1):
        try:
            invite = await client.create_chat_invite_link(channel_id)
            row.append(InlineKeyboardButton(f"• {btn_name} •", url=invite.invite_link))
        except Exception as e:
            log.error(f"⚠️ Failed to create invite link for {channel_id}: {e}")
            row.append(InlineKeyboardButton(f"• {btn_name} •", url="https://t.me"))

        if i % 2 == 0:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton("• ✅ I Joined •", callback_data="fsub_check")])

    await message.reply_text(
        "⚠️ You must join the following channel(s) before using this bot:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    return False


# ===================== CALLBACK =====================
@Client.on_callback_query(filters.regex("fsub_check"))
async def recheck_force_sub(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    ok = await check_force_sub(client, user_id, callback_query.message)
    if ok:
        await callback_query.message.edit_text(
            "✅ Thanks! You’ve unlocked the bot features.\n\nSend /start again."
        )
import logging
from pyrogram import Client, filters
from pyrogram.errors import UserNotParticipant, ChatAdminRequired, PeerIdInvalid, FloodWait
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.raw import functions
import asyncio
from bot import get_bool, get_list

log = logging.getLogger(__name__)


# ===================== DYNAMIC FSUB LOADING =====================
def load_fsub():
    ENABLE_FSUB = get_bool("ENABLE_FSUB")
    raw_fsub = get_list("FSUB")

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


# ===================== SAFE CHANNEL RESOLVE =====================
async def safe_resolve_channel(client: Client, channel_id: int):
    """Ensure the bot session knows this channel peer."""
    try:
        peer = await client.resolve_peer(channel_id)
        await client.invoke(functions.channels.GetFullChannel(channel=peer))
        log.info(f"✅ Resolved channel peer successfully: {channel_id}")
        return True
    except PeerIdInvalid:
        log.warning(f"⚠️ PeerIdInvalid for {channel_id}, trying import...")
        try:
            await client.invoke(functions.channels.GetChannels(id=[channel_id]))
            log.info(f"✅ Imported channel peer successfully: {channel_id}")
            return True
        except Exception as e:
            log.error(f"❌ Failed to import peer for channel {channel_id}: {e}")
            return False
    except FloodWait as e:
        log.warning(f"⏳ FloodWait while resolving {channel_id}, sleeping {e.value}s...")
        await asyncio.sleep(e.value)
        return await safe_resolve_channel(client, channel_id)
    except Exception as e:
        log.error(f"❌ Unexpected error resolving peer {channel_id}: {e}")
        return False


# ===================== FORCE SUB CHECK =====================
async def check_force_sub(client: Client, user_id: int, message) -> bool:
    ENABLE_FSUB, FSUB = load_fsub()

    if not ENABLE_FSUB:
        return True  # skip if disabled

    not_joined = []

    for btn_name, channel_id in FSUB.items():
        try:
            member = await client.get_chat_member(channel_id, user_id)
            if member.status in ("left", "kicked"):
                not_joined.append((btn_name, channel_id))

        except PeerIdInvalid:
            log.warning(f"⚠️ PeerIdInvalid while checking {channel_id}, resolving...")
            ok = await safe_resolve_channel(client, channel_id)
            if not ok:
                await message.reply_text(
                    f"⚠️ Could not access channel `{btn_name}` ({channel_id}).\n"
                    f"Please re-add the bot as admin in that channel."
                )
                return False
            # retry check
            try:
                member = await client.get_chat_member(channel_id, user_id)
                if member.status in ("left", "kicked"):
                    not_joined.append((btn_name, channel_id))
            except Exception as e:
                log.error(f"❌ Still failed after resolving {channel_id}: {e}")
                return False

        except UserNotParticipant:
            not_joined.append((btn_name, channel_id))
        except ChatAdminRequired:
            await message.reply_text("⚠️ Bot must be admin in all FSUB channels!")
            log.error(f"❌ Bot not admin in {channel_id}")
            return False
        except Exception as e:
            log.error(f"⚠️ Error checking FSUB for channel {channel_id}: {e}")
            return False

    if not not_joined:
        return True  # all joined

    # 🔹 Generate buttons
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
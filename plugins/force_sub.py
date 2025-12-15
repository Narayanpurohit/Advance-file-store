import logging
import asyncio
from pyrogram import Client, filters
from pyrogram.errors import (
    UserNotParticipant,
    ChatAdminRequired,
    PeerIdInvalid,
    FloodWait
)
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)
from pyrogram.raw import functions
from bot import get_bool, get_list

log = logging.getLogger(__name__)

# ===================== FSUB LOADER =====================
def load_fsub():
    ENABLE_FSUB = get_bool("ENABLE_FSUB")
    raw_fsub = get_list("FSUB")

    FSUB = {}
    if ENABLE_FSUB and raw_fsub:
        try:
            for item in raw_fsub:
                if ":" in item:
                    name, cid = item.split(":", 1)
                    FSUB[name.strip()] = int(cid.strip())
            log.info(f"🔍 FSUB loaded: {FSUB}")
        except Exception as e:
            log.error(f"⚠️ FSUB parse error: {e}")
            FSUB = {}
    return ENABLE_FSUB, FSUB


# ===================== RFSUB LOADER =====================
def load_rfsub():
    raw_rfsub = get_list("RFSUB")

    RFSUB = {}
    if raw_rfsub:
        try:
            for item in raw_rfsub:
                if ":" in item:
                    name, cid = item.split(":", 1)
                    RFSUB[name.strip()] = int(cid.strip())
            log.info(f"🔍 RFSUB loaded: {RFSUB}")
        except Exception as e:
            log.error(f"⚠️ RFSUB parse error: {e}")
            RFSUB = {}
    return RFSUB


# ===================== SAFE CHANNEL RESOLVE =====================
async def safe_resolve_channel(client: Client, channel_id: int):
    try:
        peer = await client.resolve_peer(channel_id)
        await client.invoke(functions.channels.GetFullChannel(channel=peer))
        return True
    except PeerIdInvalid:
        try:
            await client.invoke(functions.channels.GetChannels(id=[channel_id]))
            return True
        except Exception as e:
            log.error(f"❌ Cannot resolve channel {channel_id}: {e}")
            return False
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await safe_resolve_channel(client, channel_id)
    except Exception as e:
        log.error(f"❌ Resolve error {channel_id}: {e}")
        return False


# ===================== FORCE SUB CHECK =====================
async def check_force_sub(client: Client, user_id: int, message) -> bool:
    ENABLE_FSUB, FSUB = load_fsub()
    RFSUB = load_rfsub()

    if not ENABLE_FSUB:
        return True

    not_joined = []
    not_requested = []

    # -------- FSUB (JOIN REQUIRED) --------
    for btn_name, channel_id in FSUB.items():
        try:
            member = await client.get_chat_member(channel_id, user_id)
            if member.status in ("left", "kicked"):
                not_joined.append((btn_name, channel_id))

        except UserNotParticipant:
            not_joined.append((btn_name, channel_id))

        except PeerIdInvalid:
            ok = await safe_resolve_channel(client, channel_id)
            if not ok:
                return False

        except ChatAdminRequired:
            await message.reply_text("⚠️ Bot must be admin in all FSUB channels!")
            return False

        except Exception as e:
            log.error(f"⚠️ FSUB error {channel_id}: {e}")
            return False

    # -------- RFSUB (REQUEST REQUIRED) --------
    for btn_name, channel_id in RFSUB.items():
        try:
            member = await client.get_chat_member(channel_id, user_id)

            # ✅ Join request sent (pending approval)
            if getattr(member, "is_pending", False):
                continue

            # ❌ Not joined and no request
            if member.status in ("left", "kicked"):
                not_requested.append((btn_name, channel_id))

        except UserNotParticipant:
            not_requested.append((btn_name, channel_id))

        except PeerIdInvalid:
            ok = await safe_resolve_channel(client, channel_id)
            if not ok:
                return False

        except ChatAdminRequired:
            await message.reply_text("⚠️ Bot must be admin in all RFSUB channels!")
            return False

        except Exception as e:
            log.error(f"⚠️ RFSUB error {channel_id}: {e}")
            return False

    # -------- PASSED --------
    if not not_joined and not not_requested:
        return True

    # ===================== BUTTONS =====================
    buttons = []
    row = []

    # FSUB buttons
    for i, (btn_name, channel_id) in enumerate(not_joined, start=1):
        try:
            invite = await client.create_chat_invite_link(channel_id)
            link = invite.invite_link
        except Exception:
            link = "https://t.me"

        row.append(InlineKeyboardButton(f"• {btn_name} •", url=link))
        if i % 2 == 0:
            buttons.append(row)
            row = []

    if row:
        buttons.append(row)

    # RFSUB buttons (request)
    for btn_name, channel_id in not_requested:
        try:
            invite = await client.create_chat_invite_link(
                channel_id,
                creates_join_request=True
            )
            link = invite.invite_link
        except Exception:
            link = "https://t.me"

        buttons.append([
            InlineKeyboardButton(
                f"• Request {btn_name} •",
                url=link
            )
        ])

    buttons.append([
        InlineKeyboardButton("• ✅ I Joined •", callback_data="fsub_check")
    ])

    await message.reply_text(
        "⚠️ You must join or send join request to continue:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    return False


# ===================== CALLBACK =====================
@Client.on_callback_query(filters.regex("^fsub_check$"))
async def recheck_force_sub(client: Client, callback_query: CallbackQuery):
    await callback_query.answer("Checking...")
    user_id = callback_query.from_user.id

    ok = await check_force_sub(
        client,
        user_id,
        callback_query.message
    )

    if ok:
        await callback_query.message.edit_text(
            "✅ Access granted!\n\nSend /start again."
        )
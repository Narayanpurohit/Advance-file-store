import datetime
from bot import get_int,get_str
from database import create_verification_slug, use_verification_slug, add_premium_hours
from .shortener import shorten_url
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ===================== VARIABLE GETTERS =====================
PREMIUM_HOURS_VERIFICATION = get_int("PREMIUM_HOURS_VERIFICATION")
VERIFY_SLUG_TTL_HOURS = get_int("VERIFY_SLUG_TTL_HOURS")
HTW = get_str_var("HTW")


def get_htw_keyboard():
    if HTW:
        return InlineKeyboardMarkup(
            [[InlineKeyboardButton("📥 How to DL", url=HTW)]]
        )
    return None

# ===================== HANDLE VERIFICATION =====================
async def start_verification_flow(client, message, slug):
    try:
        record = use_verification_slug(slug)  # Returns full doc or None
    except Exception as e:
        await message.reply_text(f"⚠️ ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ᴇʀʀᴏʀ:\n`{e}`")
        return

    if not record:
        # Handle old timestamp-based slugs with a dot (backward compatibility)
        if slug.startswith("verify_") and "." in slug:
            await message.reply_text("❌ ᴛʜɪꜱ ᴏʟᴅ ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ʟɪɴᴋ ʜᴀꜱ ᴇxᴘɪʀᴇᴅ.\nᴘʟᴇᴀꜱᴇ ʀᴇǫᴜᴇꜱᴛ ᴀ ɴᴇᴡ ᴏɴᴇ.")
        else:
            await message.reply_text("❌ ɪɴᴠᴀʟɪᴅ ᴏʀ ᴇxᴘɪʀᴇᴅ ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ʟɪɴᴋ.")
        return

    # Check if slug belongs to this user
    if record.get("user_id") != message.from_user.id:
        await message.reply_text("⚠️ ᴛʜɪꜱ ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ʟɪɴᴋ ɪꜱ ɴᴏᴛ ꜰᴏʀ ʏᴏᴜʀ ᴀᴄᴄᴏᴜɴᴛ.")
        return

    # Give premium hours
    try:
        add_premium_hours(message.from_user.id, PREMIUM_HOURS_VERIFICATION)
        await message.reply_text(
            f"✅ ᴠᴇʀɪꜰɪᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ!\n\n⏰ ʏᴏᴜ ɴᴏᴡ ʜᴀᴠᴇ **{PREMIUM_HOURS_VERIFICATION} ʜᴏᴜʀꜱ** ᴏꜰ ᴘʀᴇᴍɪᴜᴍ ᴀᴄᴄᴇꜱꜱ."
        )
    except Exception as e:
        await message.reply_text(f"⚠️ ꜰᴀɪʟᴇᴅ ᴛᴏ ᴀᴘᴘʟʏ ᴘʀᴇᴍɪᴜᴍ:\n`{e}`")


# ===================== CREATE + SEND LINK =====================
async def send_verification_link(client, user_id):
    try:
        slug = create_verification_slug(user_id, VERIFY_SLUG_TTL_HOURS)
        bot_link = f"https://t.me/{client.me.username}?start={slug}"

        # Pass bot link through shortener
        short_link, err = shorten_url(bot_link)

        if err:
            await client.send_message(
                user_id,
                f"❌ ᴄᴏᴜʟᴅ ɴᴏᴛ ɢᴇɴᴇʀᴀᴛᴇ ꜱʜᴏʀᴛ ʟɪɴᴋ:\n`{err}`\n\n"
                f"👉 ᴜꜱᴇ ᴛʜɪꜱ ᴏʀɪɢɪɴᴀʟ ʟɪɴᴋ ɪɴꜱᴛᴇᴀᴅ:\n{bot_link}"
            )
        else:
            await client.send_message(
    user_id,
    f"⚠️ ᴘʟᴇᴀꜱᴇ ᴠᴇʀɪꜰʏ ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ:\n\n{short_link}",
    reply_markup=get_htw_keyboard()
)

    except Exception as e:
        await client.send_message(user_id, f"❌ ᴄᴏᴜʟᴅ ɴᴏᴛ ɢᴇɴᴇʀᴀᴛᴇ ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ʟɪɴᴋ:\n`{e}`")
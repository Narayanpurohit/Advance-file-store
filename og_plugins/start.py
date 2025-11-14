import logging
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
from db_config import add_user, user_exists
from config import CODE2_LOG_CHANNEL

log = logging.getLogger("Start")
SUPPORT_CHAT = "https://t.me/jn_family"

# ---------------- KEYBOARDS ----------------
def get_start_keyboard():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🖍️ Help", callback_data="help_menu"),
                InlineKeyboardButton("✨ Features", callback_data="features_menu")
            ],
            [
                InlineKeyboardButton("💬 Support Chat", url=SUPPORT_CHAT)
            ]
        ]
    )

def get_back_keyboard():
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("⬅️ Back", callback_data="start_menu")]]
    )

# ---------------- MESSAGES (styled fonts kept) ----------------
START_TEXT = (
    "ʜᴇʏ {mention} 👋\n\n"
    "ɪ ᴀᴍ ᴀ ᴘᴇʀᴍᴇɴᴀɴᴛ ғɪʟᴇ sᴛᴏʀᴇ ᴄʟᴏɴᴇ ᴍᴀᴋᴇʀ ᴡɪᴛʜ ᴀᴍᴀᴢɪɴɢ ᴀᴅᴠᴀɴᴄᴇ ғᴇᴀᴛᴜʀᴇs\n\n"
    "ᴛᴏ ᴋɴᴏᴡ ᴍᴏʀᴇ, ᴜsᴇ ᴛʜᴇ ʙᴜᴛᴛᴏɴs ʙᴇʟᴏᴡ 👇"
)

HELP_TEXT = (
    "🖍️ ʜᴇʟᴘ ᴍᴇɴᴜ\n\n"
    "✨ ᴛʜɪs ɪs ᴀ ᴘᴇʀᴍᴀɴᴇɴᴛ ғɪʟᴇ sᴛᴏʀᴇ ᴄʟᴏɴᴇ ᴍᴀᴋᴇʀ ʙᴏᴛ ✨\n\n"
    "🛠️ ʜᴏᴡ ᴛᴏ ᴄʀᴇᴀᴛᴇ ʏᴏᴜʀ ʙᴏᴛ:\n\n"
    "1️⃣ ᴄʜᴇᴄᴋ ᴀɴᴅ ʙᴜʏ ᴇɴᴏᴜɢʜ ᴘᴏɪɴᴛs ᴛᴏ ᴅᴇᴘʟᴏʏ ᴠɪᴀ /Points\n"
    "2️⃣ ɢᴏ ᴛᴏ sᴇᴛᴛɪɴɢs ᴀɴᴅ ᴀᴅᴅ ʏᴏᴜʀ ʙᴏᴛ ᴛᴏᴋᴇɴ\n"
    "3️⃣ sᴇɴᴅ /ʀᴜɴʙᴏᴛ ᴄᴏᴍᴍᴀɴᴅ\n"
    "4️⃣ ᴡᴀɴᴛ ᴛᴏ ᴄʜᴀɴɢᴇ ᴀɴʏᴛʜɪɴɢ? ᴇᴅɪᴛ ɪɴ sᴇᴛᴛɪɴɢs ᴀɴᴅ ʀᴇ-ᴜsᴇ /ʀᴜɴʙᴏᴛ\n"
)

FEATURES_TEXT = (
    "**✨ ғᴇᴀᴛᴜʀᴇs ᴍᴇɴᴜ ✨**\n\n"
    "🚀 ᴄʟᴏɴᴇ ᴍᴀᴋᴇʀ ʙᴏᴛ ʟᴇᴛs ʏᴏᴜ ᴄʀᴇᴀᴛᴇ ʏᴏᴜʀ ᴏᴡɴ ғɪʟᴇ sᴛᴏʀᴇ ʙᴏᴛ ɪɴ ᴊᴜsᴛ ᴀ ғᴇᴡ ᴛᴀᴘs — ɴᴏ ᴄᴏᴅɪɴɢ, ɴᴏ ʜᴏsᴛɪɴɢ 💫\n\n"
    "**💎 ᴘᴀʏ ᴏɴʟʏ ғᴏʀ ᴡʜᴀᴛ ʏᴏᴜ ᴜsᴇ**\n"
    "ᴘᴏɪɴᴛs ᴀʀᴇ ᴏɴʟʏ ᴜsᴇᴅ ᴡʜᴇɴ ʏᴏᴜʀ ʙᴏᴛ sᴇɴᴅ ғɪʟᴇs – ᴀʟʟ ᴏᴛʜᴇʀ ᴛᴏᴏʟs ᴀʀᴇ **ғʀᴇᴇ** 🎁\n\n"
    "**⚙️ ᴋᴇʏ ғᴇᴀᴛᴜʀᴇs**\n"
    "• 1 ᴛᴀᴘ ʙᴏᴛ ᴄʀᴇᴀᴛɪᴏɴ 🪄\n"
    "• ғᴜʟʟʏ ᴄᴜsᴛᴏᴍɪᴢᴀʙʟᴇ sᴇᴛᴛɪɴɢs ⚙️\n"
    "• ғᴏʀᴄᴇ sᴜʙ & ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ ᴍᴏᴅᴇs\n"
    "• ғʀᴇᴇ ʙʀᴏᴀᴅᴄᴀsᴛs & sʏsᴛᴇᴍ ᴍᴇssᴀɢᴇs 🆓\n"
    "• ʀᴇᴀʟ-ᴛɪᴍᴇ sᴛᴀᴛs 📊\n"
    "• ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇ, ᴄᴀᴘᴛɪᴏɴs, ᴀɴᴅ ᴍᴏʀᴇ ✨\n\n"
    "💬 sɪᴍᴘʟᴇ. ғᴀɪʀ. ᴘᴏᴡᴇʀғᴜʟ.\n"
    "ᴄʀᴇᴀᴛᴇ ʏᴏᴜʀ ʙᴏᴛ ɴᴏᴡ ᴀɴᴅ ᴘᴀʏ ᴏɴʟʏ ғᴏʀ ᴡʜᴀᴛ ʏᴏᴜ ᴜsᴇ 🚀"
)

# ---------------- HANDLERS ----------------
@Client.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    user_id = message.from_user.id
    username = message.from_user.username or "N/A"

    # Add user to DB if not exists (preserve original behavior)
    try:
        if not user_exists(user_id):
            add_user(user_id)
            log.info(f"New user {user_id} ({username}) added to DB.")
            text = f"👋 Welcome! You’ve been added to the database.\n\n{START_TEXT.format(mention=f'[{message.from_user.first_name}](tg://user?id={user_id})')}"
            if CODE2_LOG_CHANNEL: await client.send_message(CODE2_LOG_CHANNEL, f"🦋 #newuser 🦋,\n\nID : {user_id}\nName : {message.from_user.first_name}")
        else:
            log.info(f"Existing user {user_id} ({username}) accessed /start.")
            text = START_TEXT.format(mention=f'[{message.from_user.first_name}](tg://user?id={user_id})')
    except Exception as e:
        log.exception(f"Error in /start for user {user_id}: {e}")
        text = "⚠️ Something went wrong during start. Please try again later."

    await message.reply_text(
        text,
        reply_markup=get_start_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )

# Help menu callback
@Client.on_callback_query(filters.regex(r"^help_menu$"))
async def help_menu(client, cq):
    try:
        await cq.answer()  # acknowledge callback
        await cq.message.edit_text(
            HELP_TEXT,
            reply_markup=get_back_keyboard(),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )
    except Exception as e:
        log.exception("Error opening help menu: %s", e)
        # safe fallback
        await cq.answer("An error occurred.", show_alert=True)

# Features menu callback
@Client.on_callback_query(filters.regex(r"^features_menu$"))
async def features_menu(client, cq):
    try:
        await cq.answer()
        await cq.message.edit_text(
            FEATURES_TEXT,
            reply_markup=get_back_keyboard(),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )
    except Exception as e:
        log.exception("Error opening features menu: %s", e)
        await cq.answer("An error occurred.", show_alert=True)

# Back to start menu callback
@Client.on_callback_query(filters.regex(r"^start_menu$"))
async def start_menu(client, cq):
    try:
        await cq.answer()
        mention = f'[{cq.from_user.first_name}](tg://user?id={cq.from_user.id})'
        await cq.message.edit_text(
            START_TEXT.format(mention=mention),
            reply_markup=get_start_keyboard(),
            parse_mode=ParseMode.MARKDOWN,
        )
    except Exception as e:
        log.exception("Error returning to start menu: %s", e)
        await cq.answer("An error occurred.", show_alert=True)
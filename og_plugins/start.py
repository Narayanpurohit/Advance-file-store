from pyrogram import Client, filters
from db_config import add_user, user_exists
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging

log = logging.getLogger("Start")

@Client.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    user_id = message.from_user.id
    username = message.from_user.username or "N/A"

    # Add user to DB if not exists
    try:
        if not user_exists(user_id):
            add_user(user_id)
            log.info(f"New user {user_id} ({username}) added to DB.")
        else:
            log.info(f"Existing user {user_id} ({username}) accessed /start.")
    except Exception as e:
        log.exception(f"Error adding/checking user {user_id}: {e}")

    # Welcome message
    text = f"""
ʜᴇʏ {message.from_user.mention} 👋,

ɪ ᴀᴍ ᴀ ᴘᴇʀᴍᴀɴᴇɴᴛ ғɪʟᴇ sᴛᴏʀᴇ ᴄʟᴏɴᴇ ᴍᴀᴋᴇʀ ᴡɪᴛʜ ᴀᴍᴀᴢɪɴɢ ᴀᴅᴠᴀɴᴄᴇ ғᴇᴀᴛᴜʀᴇs.

ᴛᴏ ᴋɴᴏᴡ ᴍᴏʀᴇ, ᴜsᴇ ᴛʜᴇ ʙᴜᴛᴛᴏɴs ʙᴇʟᴏᴡ 👇
"""

    # Inline keyboard
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🖍️ Help", callback_data="help_menu")],
            [InlineKeyboardButton("✨ Features", callback_data="features_menu")],
            [InlineKeyboardButton("💬 Support Chat", url="https://t.me/jn_family")]
        ]
    )

    await message.reply_text(text, reply_markup=keyboard)

# ===============================
# Callback for Help Menu
# ===============================
@Client.on_callback_query(filters.regex(r"help_menu"))
async def help_menu(client, cq):
    help_text = """
🖍️ ʜᴇʟᴘ ᴍᴇɴᴜ

✨ ᴛʜɪs ɪs ᴀ ᴘᴇʀᴍᴀɴᴇɴᴛ ғɪʟᴇ sᴛᴏʀᴇ ᴄʟᴏɴᴇ ᴍᴀᴋᴇʀ ʙᴏᴛ ✨

🛠️ ʜᴏᴡ ᴛᴏ ᴄʀᴇᴀᴛᴇ ʏᴏᴜʀ ʙᴏᴛ:

1️⃣  ᴄʜᴇᴄᴋ ᴀɴᴅ ʙᴜʏ ᴇɴᴏᴜɢʜ ᴘᴏɪɴᴛs ᴛᴏ ᴅᴇᴘʟᴏʏ ᴠɪᴀ /ᴘᴏɪɴᴛs  
2️⃣  ɢᴏ ᴛᴏ sᴇᴛᴛɪɴɢs ᴀɴᴅ ᴀᴅᴅ ʏᴏᴜʀ ʙᴏᴛ ᴛᴏᴋᴇɴ  
3️⃣  sᴇɴᴅ /ʀᴜɴʙᴏᴛ ᴄᴏᴍᴍᴀɴᴅ  
4️⃣  ᴡᴀɴᴛ ᴛᴏ ᴄʜᴀɴɢᴇ ᴀɴʏᴛʜɪɴɢ? ᴇᴅɪᴛ ɪɴ sᴇᴛᴛɪɴɢs ᴀɴᴅ ʀᴇ-ᴜsᴇ /ʀᴜɴʙᴏᴛ
"""
    back_keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("⬅️ Back", callback_data="start_menu")]]
    )
    await cq.message.edit_text(help_text, reply_markup=back_keyboard, disable_web_page_preview=True)

# ===============================
# Callback for Features Menu
# ===============================
@Client.on_callback_query(filters.regex(r"features_menu"))
async def features_menu(client, cq):
    features_text = """
📝 ғᴇᴀᴛᴜʀᴇs ᴏғ ᴍʏ ᴘᴇʀᴍᴀɴᴇɴᴛ ғɪʟᴇ sᴛᴏʀᴇ ᴄʟᴏɴᴇ:

✨ ᴜsᴇʀs ᴘᴀʏ ᴏɴʟʏ ғᴏʀ ᴡʜᴀᴛ ᴛʜᴇʏ ᴜsᴇ (sᴇɴᴅ ғɪʟᴇs)  
🎯 ᴏᴛʜᴇʀ ᴄᴏᴍᴍᴀɴᴅs ᴀʀᴇ ғʀᴇᴇ:
   - /ʀᴜɴʙᴏᴛ
   - /sᴇᴛᴛɪɴɢs
   - /ʙʀᴏᴀᴅᴄᴀsᴛ  
🛡️ ᴘʀᴇᴍɪᴜᴍ ᴘᴏɪɴᴛs ᴄʜᴀʀɢᴇ ᴜsᴇʀs ғᴏʀ ғɪʟᴇ ᴜsᴀɢᴇ  
"""
    back_keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("⬅️ Back", callback_data="start_menu")]]
    )
    await cq.message.edit_text(features_text, reply_markup=back_keyboard, disable_web_page_preview=True)

# ===============================
# Callback to return to Start Menu
# ===============================
@Client.on_callback_query(filters.regex(r"start_menu"))
async def start_menu(client, cq):
    user = cq.from_user
    text = f"""
ʜᴇʏ {user.mention} 👋,

ɪ ᴀᴍ ᴀ ᴘᴇʀᴍᴀɴᴇɴᴛ ғɪʟᴇ sᴛᴏʀᴇ ᴄʟᴏɴᴇ ᴍᴀᴋᴇʀ ᴡɪᴛʜ ᴀᴍᴀᴢɪɴɢ ᴀᴅᴠᴀɴᴄᴇ ғᴇᴀᴛᴜʀᴇs.

ᴛᴏ ᴋɴᴏᴡ ᴍᴏʀᴇ, ᴜsᴇ ᴛʜᴇ ʙᴜᴛᴛᴏɴs ʙᴇʟᴏᴡ 👇
"""
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🖍️ Help", callback_data="help_menu")],
            [InlineKeyboardButton("✨ Features", callback_data="features_menu")],
            [InlineKeyboardButton("💬 Support Chat", url="https://t.me/jn_family")]
        ]
    )
    await cq.message.edit_text(text, reply_markup=keyboard)
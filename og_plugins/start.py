from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ============================
# /start COMMAND
# ============================
@Client.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    mention = message.from_user.mention
    start_text = f"""
ʜᴇʏ {mention}👋,

ɪ ᴀᴍ ᴀ ᴘᴇʀᴍᴇɴᴀɴᴛ ғɪʟᴇ sᴛᴏʀᴇ ᴄʟᴏɴᴇ ᴍᴀᴋᴇʀ ᴡɪᴛʜ ᴀᴍᴀᴢɪɴɢ ᴀᴅᴠᴀɴᴄᴇ ғᴇᴀᴛᴜʀᴇs

ᴛᴏ ᴋɴᴏᴡ ᴍᴏʀᴇ ᴄʟɪᴄᴋ ʜᴇʟᴘ ᴏʀ ғᴇᴀᴛᴜʀᴇs
"""
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🖍️ Help", callback_data="help_menu"),
                InlineKeyboardButton("✨ Features", callback_data="features_menu")
            ],
            [
                InlineKeyboardButton("💬 Support Chat", url="https://t.me/jn_family")
            ]
        ]
    )

    await message.reply_text(start_text, reply_markup=keyboard, parse_mode="HTML")

# ============================
# Help Menu Callback
# ============================
@Client.on_callback_query(filters.regex(r"help_menu"))
async def help_menu(client, cq):
    help_text = """
🖍️ <b>ʜᴇʟᴘ ᴍᴇɴᴜ</b>

✨ <b>ᴛʜɪs ɪs ᴀ ᴘᴇʀᴍᴀɴᴇɴᴛ ғɪʟᴇ sᴛᴏʀᴇ ᴄʟᴏɴᴇ ᴍᴀᴋᴇʀ ʙᴏᴛ</b> ✨

🛠️ <b>ʜᴏᴡ ᴛᴏ ᴄʀᴇᴀᴛᴇ ʏᴏᴜʀ ʙᴏᴛ</b>:

1️⃣ ᴄʜᴇᴄᴋ ᴀɴᴅ ʙᴜʏ ᴇɴᴏᴜɢʜ ᴘᴏɪɴᴛs ᴛᴏ ᴅᴇᴘʟᴏʏ via /points  
2️⃣ ɢᴏ ᴛᴏ sᴇᴛᴛɪɴɢs ᴀɴᴅ ᴀᴅᴅ ʏᴏᴜʀ ʙᴏᴛ ᴛᴏᴋᴇɴ  
3️⃣ sᴇɴᴅ /runbot ᴄᴏᴍᴍᴀɴᴅ  
4️⃣ ᴡᴀɴᴛ ᴛᴏ ᴄʜᴀɴɢᴇ ᴀɴʏᴛʜɪɴɢ, ᴇᴅɪᴛ ɪɴ sᴇᴛᴛɪɴɢs ᴀɴᴅ ʀᴇ-ᴜsᴇ /runbot
"""
    back_keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("⬅️ Back", callback_data="start_menu")]]
    )

    await cq.message.edit_text(help_text, reply_markup=back_keyboard, parse_mode="HTML")

# ============================
# Features Menu Callback
# ============================
@Client.on_callback_query(filters.regex(r"features_menu"))
async def features_menu(client, cq):
    features_text = """
✨ <b>ғᴇᴀᴛᴜʀᴇs ᴍᴇɴᴜ</b> ✨

🚀 <b>ᴄʟᴏɴᴇ ᴍᴀᴋᴇʀ ʙᴏᴛ</b> ʟᴇᴛs ʏᴏᴜ ᴄʀᴇᴀᴛᴇ ʏᴏᴜʀ ᴏᴡɴ ғɪʟᴇ sᴛᴏʀᴇ ʙᴏᴛ ɪɴ ᴊᴜsᴛ ᴀ ғᴇᴡ ᴛᴀᴘs — ɴᴏ ᴄᴏᴅɪɴɢ, ɴᴏ ʜᴏsᴛɪɴɢ 💫

💎 <b>ᴘᴀʏ ᴏɴʟʏ ғᴏʀ ᴡʜᴀᴛ ʏᴏᴜ ᴜsᴇ</b>
ᴘᴏɪɴᴛs ᴀʀᴇ ᴏɴʟʏ ᴜsᴇᴅ ᴡʜᴇɴ ʏᴏᴜ sᴇɴᴅ ᴏʀ sᴛᴏʀᴇ ғɪʟᴇs – ᴀʟʟ ᴏᴛʜᴇʀ ᴛᴏᴏʟs ᶠʳᵉᴇ 🎁

⚙️ <b>ᴋᴇʏ ғᴇᴀᴛᴜʀᴇs</b>
• 1ᴛᴀᴘ ʙᴏᴛ ᴄʀᴇᴀᴛɪᴏɴ 🪄
• ғᴜʟʟʏ ᴄᴜsᴛᴏᴍɪᴢᴀʙʟᴇ sᴇᴛᴛɪɴɢs ⚙️
• ғᴏʀᴄᴇ sᴜʙ & ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ ᴍᴏᴅᴇs 
• ғʀᴇᴇ ʙʀᴏᴀᴅᴄᴀsᴛs & sʏsᴛᴇᴍ ᴍᴇssᴀɢᴇs 🆓
• ʀᴇᴀʟ-ᴛɪᴍᴇ sᴛᴀᴛs 📊
• ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇ, ᴄᴀᴘᴛɪᴏɴs, ᴀɴᴅ ᴍᴏʀᴇ ✨

💬 <b>sɪᴍᴘʟᴇ. ғᴀɪʀ. ᴘᴏᴡᴇʀғᴜʟ.</b>
ᴄʀᴇᴀᴛᴇ ʏᴏᴜʀ ʙᴏᴛ ɴᴏᴡ ᴀɴᴅ ᴘᴀʏ ᴏɴʟʏ ғᴏʀ ᴡʜᴀᴛ ʏᴏᴜ ᵘˢᵉ 🚀
"""
    back_keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("⬅️ Back", callback_data="start_menu")]]
    )
    await cq.message.edit_text(features_text, reply_markup=back_keyboard, parse_mode="HTML")

# ============================
# Back to Start Menu Callback
# ============================
@Client.on_callback_query(filters.regex(r"start_menu"))
async def back_to_start(client, cq):
    mention = cq.from_user.mention
    start_text = f"""
ʜᴇʏ {mention}👋,

ɪ ᴀᴍ ᴀ ᴘᴇʀᴍᴇɴᴀɴᴛ ғɪʟᴇ sᴛᴏʀᴇ ᴄʟᴏɴᴇ ᴍᴀᴋᴇʀ ᴡɪᴛʜ ᴀᴍᴀᴢɪɴɢ ᴀᴅᴠᴀɴᴄᴇ ғᴇᴀᴛᴜʀᴇs

ᴛᴏ ᴋɴᴏᴡ ᴍᴏʀᴇ ᴄʟɪᴄᴋ ʜᴇʟᴘ ᴏʀ ғᴇᴀᴛᴜʀᴇs
"""
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🖍️ Help", callback_data="help_menu"),
                InlineKeyboardButton("✨ Features", callback_data="features_menu")
            ],
            [
                InlineKeyboardButton("💬 Support Chat", url="https://t.me/jn_family")
            ]
        ]
    )
    await cq.message.edit_text(start_text, reply_markup=keyboard, parse_mode="HTML")
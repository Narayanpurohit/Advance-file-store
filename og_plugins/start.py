from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode

SUPPORT_CHAT = "https://t.me/jn_family"

# ---------------- KEYBOARDS ----------------
def get_start_keyboard():
    buttons = [
        [
            InlineKeyboardButton("🖍️ Help", callback_data="help"),
            InlineKeyboardButton("✨ Features", callback_data="features")
        ],
        [
            InlineKeyboardButton("💬 Support Chat", url=SUPPORT_CHAT)
        ]
    ]
    return InlineKeyboardMarkup(buttons)

def get_back_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Back", callback_data="back_to_start")]
    ])

# ---------------- MESSAGES ----------------
START_TEXT = "ʜᴇʏ {mention}👋,\n\nɪ ᴀᴍ ᴀ ᴘᴇʀᴍᴇɴᴀɴᴛ ғɪʟᴇ sᴛᴏʀᴇ ᴄʟᴏɴᴇ ᴍᴀᴋᴇʀ ᴡɪᴛʜ ᴀᴍᴀᴢɪɴɢ ᴀᴅᴠᴀɴᴄᴇ ғᴇᴀᴛᴜʀᴇs\n\nᴛᴏ ᴋɴᴏᴡ ᴍᴏʀᴇ ᴄʟɪᴄᴋ *Help* ʙᴜᴛᴛᴏɴ."

HELP_TEXT = """**🖍️ ʜᴇʟᴘ ᴍᴇɴᴜ**

✨ ᴛʜɪs ɪs ᴀ ᴘᴇʀᴍᴀɴᴇɴᴛ ғɪʟᴇ sᴛᴏʀᴇ ᴄʟᴏɴᴇ ᴍᴀᴋᴇʀ ʙᴏᴛ ✨

**🛠️ ʜᴏᴡ ᴛᴏ ᴄʀᴇᴀᴛᴇ ʏᴏᴜʀ ʙᴏᴛ:**

1️⃣ ᴄʜᴇᴄᴋ ᴀɴᴅ ʙᴜʏ ᴇɴᴏᴜɢʜ ᴘᴏɪɴᴛs ᴛᴏ ᴅᴇᴘʟᴏʏ ᴠɪᴀ /points  

2️⃣ ɢᴏ ᴛᴏ sᴇᴛᴛɪɴɢs ᴀɴᴅ ᴀᴅᴅ ʏᴏᴜʀ ʙᴏᴛ ᴛᴏᴋᴇɴ  

3️⃣ sᴇɴᴅ /Runbot ᴄᴏᴍᴍᴀɴᴅ  

♻️ ᴡᴀɴᴛ **ᴛᴏ ᴄʜᴀɴɢᴇ ᴀɴʏᴛʜɪɴɢ**, ᴇᴅɪᴛ ɪɴ sᴇᴛᴛɪɴɢs ᴀɴᴅ ʀᴇ-ᴜsᴇ /runbot ᴄᴏᴍᴍᴀɴᴅ
"""

FEATURES_TEXT = """**✨ ғᴇᴀᴛᴜʀᴇs ᴍᴇɴᴜ ✨**

🚀 ᴄʟᴏɴᴇ ᴍᴀᴋᴇʀ ʙᴏᴛ ʟᴇᴛs ʏᴏᴜ ᴄʀᴇᴀᴛᴇ ʏᴏᴜʀ ᴏᴡɴ ғɪʟᴇ sᴛᴏʀᴇ ʙᴏᴛ ɪɴ ᴊᴜsᴛ ᴀ ғᴇᴡ ᴛᴀᴘs — ɴᴏ ᴄᴏᴅɪɴɢ, ɴᴏ ʜᴏsᴛɪɴɢ 💫

**💎 ᴘᴀʏ ᴏɴʟʏ ғᴏʀ ᴡʜᴀᴛ ʏᴏᴜ ᴜsᴇ**
ᴘᴏɪɴᴛs ᴀʀᴇ ᴏɴʟʏ ᴜsᴇᴅ ᴡʜᴇɴ ʏᴏᴜʀ ʙᴏᴛ sᴇɴᴅ ғɪʟᴇs – ᴀʟʟ ᴏᴛʜᴇʀ ᴛᴏᴏʟs ᴀʀᴇ **ғʀᴇᴇ** 🎁

**⚙️ ᴋᴇʏ ғᴇᴀᴛᴜʀᴇs**
• 1 ᴛᴀᴘ ʙᴏᴛ ᴄʀᴇᴀᴛɪᴏɴ 🪄
• ғᴜʟʟʏ ᴄᴜsᴛᴏᴍɪᴢᴀʙʟᴇ sᴇᴛᴛɪɴɢs ⚙️
• ғᴏʀᴄᴇ sᴜʙ & ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ ᴍᴏᴅᴇs 
• ғʀᴇᴇ ʙʀᴏᴀᴅᴄᴀsᴛs & sʏsᴛᴇᴍ ᴍᴇssᴀɢᴇs 🆓
• ʀᴇᴀʟ-ᴛɪᴍᴇ sᴛᴀᴛs 📊
• ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇ, ᴄᴀᴘᴛɪᴏɴs, ᴀɴᴅ ᴍᴏʀᴇ ✨

💬 sɪᴍᴘʟᴇ. ғᴀɪʀ. ᴘᴏᴡᴇʀғᴜʟ.
ᴄʀᴇᴀᴛᴇ ʏᴏᴜʀ ʙᴏᴛ ɴᴏᴡ ᴀɴᴅ ᴘᴀʏ ᴏɴʟʏ ғᴏʀ ᴡʜᴀᴛ ʏᴏᴜ ᴜsᴇ 🚀
"""

# ---------------- HANDLERS ----------------
@Client.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    mention = f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"
    await message.reply_text(
        START_TEXT.format(mention=mention),
        reply_markup=get_start_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )

@Client.on_callback_query(filters.regex(r"^help$"))
async def help_cb(client, cq):
    await cq.message.edit_text(
        HELP_TEXT,
        reply_markup=get_back_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )

@Client.on_callback_query(filters.regex(r"^features$"))
async def features_cb(client, cq):
    await cq.message.edit_text(
        FEATURES_TEXT,
        reply_markup=get_back_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )

@Client.on_callback_query(filters.regex(r"^back_to_start$"))
async def back_cb(client, cq):
    mention = f"[{cq.from_user.first_name}](tg://user?id={cq.from_user.id})"
    await cq.message.edit_text(
        START_TEXT.format(mention=mention),
        reply_markup=get_start_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )
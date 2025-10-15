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

HELP_TEXT = """*🖍️ Help Menu*

✨ This is a permanent file store clone maker bot ✨

🛠️ How to create your bot:
1️⃣ Check and buy enough points to deploy via /points  
2️⃣ Go to settings and add your bot token  
3️⃣ Send /runbot command  
4️⃣ Want to change anything? Edit in settings and re-use /runbot command
"""

FEATURES_TEXT = """*✨ Features Menu ✨*

🚀 Clone Maker Bot lets you create your own file store bot in just a few taps — no coding, no hosting 💫

💎 *Pay only for what you use*  
Points are only used when you send or store files – all other tools are free 🎁

⚙️ *Key Features*
• 1-tap bot creation 🪄
• Fully customizable settings ⚙️
• Force sub & verification modes 
• Free broadcasts & system messages 🆓
• Real-time stats 📊
• Auto-delete, captions, and more ✨

💬 Simple. Fair. Powerful.  
Create your bot now and pay only for what you *use* 🚀
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
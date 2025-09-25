import logging
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
from pyromod.listen import Client as ListenClient  # pyromod integration
from db_config import users_col

# ---------------- LOGGING ----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"
)
log = logging.getLogger("Settings")

# ---------------- VARIABLES ----------------
BOOLEAN_VARS = ["ENABLE_FSUB", "VERIFICATION_MODE", "AUTO_DELETE"]
INT_VARS = ["PREMIUM_HOURS_VERIFICATION", "AUTO_DELETE_TIME"]

VARIABLE_INFO = {
    "BOT_TOKEN": {"name": "ʙᴏᴛ ᴛᴏᴋᴇɴ", "help": "ᴛʜᴇ ᴛᴏᴋᴇɴ ʏᴏᴜ ɢᴇᴛ ғʀᴏᴍ @ʙᴏᴛғᴀᴛʜᴇʀ."},
    "MONGO_URI": {"name": "ᴍᴏɴɢᴏᴅʙ ᴜʀɪ", "help": "ᴄᴏɴɴᴇᴄᴛɪᴏɴ sᴛʀɪɴɢ ғᴏʀ ᴍᴏɴɢᴏᴅʙ."},
    "ADMINS": {"name": "ᴀᴅᴍɪɴ ᴜsᴇʀs", "help": "ᴜsᴇʀ ɪᴅs ᴏғ ᴀᴅᴍɪɴs."},
    "FSUB": {"name": "ғᴏʀᴄᴇ sᴜʙ ᴄʜᴀɴɴᴇʟ", "help": "ᴜsᴇʀɴᴀᴍᴇ/ɪᴅ ᴏғ ᴄʜᴀɴɴᴇʟ ғᴏʀ ғsᴜʙ."},
    "PREMIUM_HOURS_VERIFICATION": {"name": "ᴘʀᴇᴍɪᴜᴍ ʜᴏᴜʀ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ", "help": "ʜᴏᴜʀs ᴜsᴇʀ sᴛᴀʏs ᴠᴇʀɪғɪᴇᴅ."},
    "SHORTENER_DOMAIN": {"name": "sʜᴏʀᴛᴇɴᴇʀ ᴅᴏᴍᴀɪɴ", "help": "ᴅᴏᴍᴀɪɴ ғᴏʀ ʟɪɴᴋ sʜᴏʀᴛᴇɴᴇʀ."},
    "SHORTENER_API_KEY": {"name": "sʜᴏʀᴛᴇɴᴇʀ ᴀᴘɪ ᴋᴇʏ", "help": "ᴀᴘɪ ᴋᴇʏ ғᴏʀ ʏᴏᴜʀ sʜᴏʀᴛᴇɴᴇʀ."},
    "CAPTION": {"name": "ғɪʟᴇ ᴄᴀᴘᴛɪᴏɴ", "help": "ᴅᴇғᴀᴜʟᴛ ᴄᴀᴘᴛɪᴏɴ ғᴏʀ ғɪʟᴇs."},
    "AUTO_DELETE_TIME": {"name": "ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴛɪᴍᴇ", "help": "ᴛɪᴍᴇ (sᴇᴄᴏɴᴅs) ғᴏʀ ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇ."},
    "ENABLE_FSUB": {"name": "ᴇɴᴀʙʟᴇ ғᴏʀᴄᴇ sᴜʙ", "help": "ᴛᴏɢɢʟᴇ ғᴏʀᴄᴇ-sᴜʙ."},
    "VERIFICATION_MODE": {"name": "ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ ᴍᴏᴅᴇ", "help": "ᴛᴏɢɢʟᴇ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ sʏsᴛᴇᴍ."},
    "AUTO_DELETE": {"name": "ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ", "help": "ᴛᴏɢɢʟᴇ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ғᴇᴀᴛᴜʀᴇ."}
}

# ---------------- GROUPS ----------------
GROUPS = {
    "☉ ʀᴇQᴜɪʀᴇᴅ sᴇᴛᴛɪɴɢs": ["BOT_TOKEN", "MONGO_URI"],
    "⍟ ᴀᴅᴍɪɴs": ["ADMINS"],
    "⊛ ғᴏʀᴄᴇ sᴜʙ": ["ENABLE_FSUB", "FSUB"],
    "⊘ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ": [],  # submenu handled separately
    "⌬ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ": ["AUTO_DELETE", "AUTO_DELETE_TIME"],
    "○ ᴄᴀᴘᴛɪᴏɴ": ["CAPTION"]
}

VERIFICATION_SUB = [
    "VERIFICATION_MODE",
    "PREMIUM_HOURS_VERIFICATION",
    "SHORTENER_DOMAIN",
    "SHORTENER_API_KEY"
]

# ---------------- KEYBOARDS ----------------
def get_group_keyboard():
    buttons = [[InlineKeyboardButton(group, callback_data=f"group:{group}")] for group in GROUPS.keys()]
    buttons.append([InlineKeyboardButton("⊗ ᴄʟᴏsᴇ", callback_data="close")])
    return InlineKeyboardMarkup(buttons)

def get_variable_keyboard(group_name: str):
    if group_name == "⊘ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ":
        buttons = [[InlineKeyboardButton(f"• {VARIABLE_INFO[var]['name']} •", callback_data=f"setting:{group_name}:{var}")]
                   for var in VERIFICATION_SUB]
    else:
        buttons = [[InlineKeyboardButton(f"• {VARIABLE_INFO[var]['name']} •", callback_data=f"setting:{group_name}:{var}")]
                   for var in GROUPS[group_name]]
    buttons.append([InlineKeyboardButton("⊖ ʙᴀᴄᴋ", callback_data="back_to_groups"),
                    InlineKeyboardButton("⊗ ᴄʟᴏsᴇ", callback_data="close")])
    return InlineKeyboardMarkup(buttons)

def get_setting_keyboard(group_name: str, var_name: str, is_boolean=False):
    buttons = [[InlineKeyboardButton("✧ ᴛᴏɢɢʟᴇ", callback_data=f"toggle:{group_name}:{var_name}")]] if is_boolean else \
              [[InlineKeyboardButton("✎ ᴇᴅɪᴛ", callback_data=f"edit:{group_name}:{var_name}")]]
    buttons.append([InlineKeyboardButton("⊖ ʙᴀᴄᴋ", callback_data=f"back_to_group:{group_name}"),
                    InlineKeyboardButton("⊗ ᴄʟᴏsᴇ", callback_data="close")])
    return InlineKeyboardMarkup(buttons)

def get_edit_keyboard(group_name: str, var_name: str):
    return InlineKeyboardMarkup([[InlineKeyboardButton("⊖ ʙᴀᴄᴋ", callback_data=f"back_to_setting:{group_name}:{var_name}")]])

# ---------------- HANDLERS ----------------
@Client.on_message(filters.command("settings") & filters.private)
async def settings_handler(client, message):
    await message.reply_text("⚙️ <b>ʙᴏᴛ sᴇᴛᴛɪɴɢs</b>\n\nsᴇʟᴇᴄᴛ ᴀ ᴄᴀᴛᴇɢᴏʀʏ:", 
                             reply_markup=get_group_keyboard(), parse_mode=ParseMode.HTML)

@Client.on_callback_query(filters.regex(r"^group:(.+)"))
async def open_group(client, cq):
    group_name = cq.data.split(":", 1)[1]
    await cq.message.edit_text(f"📂 <b>{group_name}</b>\n\nsᴇʟᴇᴄᴛ ᴀ ᴠᴀʀɪᴀʙʟᴇ:",
                               reply_markup=get_variable_keyboard(group_name), parse_mode=ParseMode.HTML)

@Client.on_callback_query(filters.regex(r"^setting:(.+?):(.+)"))
async def open_setting(client, cq):
    group_name, var_name = cq.data.split(":", 2)[1:]
    user = users_col.find_one({"USER_ID": cq.from_user.id}) or {}
    current_value = user.get(var_name, "ɴᴏᴛ sᴇᴛ")
    var_info = VARIABLE_INFO.get(var_name, {"name": var_name, "help": ""})
    text = f"<b>{var_info['name']}</b>\n\n<b>ᴄᴜʀʀᴇɴᴛ:</b>\n<code>{current_value}</code>\n\n{var_info['help']}"
    await cq.message.edit_text(text, reply_markup=get_setting_keyboard(group_name, var_name, var_name in BOOLEAN_VARS),
                               parse_mode=ParseMode.HTML, disable_web_page_preview=True)

@Client.on_callback_query(filters.regex(r"^toggle:(.+?):(.+)"))
async def toggle_setting(client, cq):
    group_name, var_name = cq.data.split(":", 2)[1:]
    user_id = cq.from_user.id
    user = users_col.find_one({"USER_ID": user_id}) or {}
    new_value = not bool(user.get(var_name, False))
    users_col.update_one({"USER_ID": user_id}, {"$set": {var_name: new_value}})
    await open_setting(client, cq)

@Client.on_callback_query(filters.regex(r"^edit:(.+?):(.+)"))
async def edit_setting(client, cq):
    group_name, var_name = cq.data.split(":", 2)[1:]
    var_info = VARIABLE_INFO.get(var_name, {"name": var_name, "help": ""})
    await cq.message.edit_text(
        f"✎ Send new value for <b>{var_info['name']}</b>.\n\n{var_info['help']}\n\n⏳ 120s timeout.",
        reply_markup=get_edit_keyboard(group_name, var_name),
        parse_mode=ParseMode.HTML
    )
    try:
        response = await client.listen(cq.message.chat.id, timeout=120)
        new_value = int(response.text.strip()) if var_name in INT_VARS else response.text.strip()
        users_col.update_one({"USER_ID": cq.from_user.id}, {"$set": {var_name: new_value}})
        await cq.message.reply_text(f"✅ {var_info['name']} updated: <code>{new_value}</code>", parse_mode=ParseMode.HTML)
    except asyncio.TimeoutError:
        await cq.message.reply_text("⏳ Edit timed out.")
    await open_setting(client, cq)

# ---------------- BACK & CLOSE ----------------
@Client.on_callback_query(filters.regex(r"^back_to_groups$"))
async def back_to_groups(client, cq): await settings_handler(client, cq.message)

@Client.on_callback_query(filters.regex(r"^back_to_group:(.+)"))
async def back_to_group(client, cq): await open_group(client, cq)

@Client.on_callback_query(filters.regex(r"^back_to_setting:(.+?):(.+)"))
async def back_to_setting(client, cq): await open_setting(client, cq)

@Client.on_callback_query(filters.regex(r"^close$"))
async def close_menu(client, cq): await cq.message.delete()
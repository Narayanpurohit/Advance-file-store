import logging
from pyromod import listen  # ✅ important!
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
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
STRING_VARS = ["BOT_TOKEN", "MONGO_URI", "SHORTENER_DOMAIN", "SHORTENER_API_KEY", "CAPTION", "FSUB"]

VARIABLE_INFO = {
    "BOT_TOKEN": {"name": "ʙᴏᴛ ᴛᴏᴋᴇɴ", "help": "ᴛʜᴇ ᴛᴏᴋᴇɴ ʏᴏᴜ ɢᴇᴛ ғʀᴏᴍ @ʙᴏᴛғᴀᴛʜᴇʀ."},
    "MONGO_URI": {"name": "ᴍᴏɴɢᴏᴅʙ ᴜʀɪ", "help": "ᴄᴏɴɴᴇᴄᴛɪᴏɴ sᴛʀɪɴɢ ғᴏʀ ʏᴏᴜʀ ᴍᴏɴɢᴏᴅʙ ᴅᴀᴛᴀʙᴀsᴇ."},
    "AUTO_DELETE_TIME": {"name": "ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴛɪᴍᴇ", "help": "ᴛɪᴍᴇ ɪɴ sᴇᴄᴏɴᴅs ᴀғᴛᴇʀ ᴡʜɪᴄʜ ғɪʟᴇs ᴀʀᴇ ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇᴅ."},
    "PREMIUM_HOURS_VERIFICATION": {"name": "ᴘʀᴇᴍɪᴜᴍ ʜᴏᴜʀ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ", "help": "ɴᴜᴍʙᴇʀ ᴏғ ʜᴏᴜʀs ᴀ ᴠᴇʀɪғɪᴇᴅ ᴜsᴇʀ sᴛᴀʏs ᴠᴇʀɪғɪᴇᴅ."},
    "SHORTENER_DOMAIN": {"name": "sʜᴏʀᴛᴇɴᴇʀ ᴅᴏᴍᴀɪɴ", "help": "ᴛʜᴇ ᴅᴏᴍᴀɪɴ ᴜsᴇᴅ ғᴏʀ ʏᴏᴜʀ ʟɪɴᴋ sʜᴏʀᴛᴇɴᴇʀ."},
    "SHORTENER_API_KEY": {"name": "sʜᴏʀᴛᴇɴᴇʀ ᴀᴘɪ ᴋᴇʏ", "help": "ᴀᴘɪ ᴋᴇʏ ғᴏʀ ʏᴏᴜʀ sʜᴏʀᴛᴇɴᴇʀ."},
    "CAPTION": {"name": "ғɪʟᴇ ᴄᴀᴘᴛɪᴏɴ", "help": "ᴅᴇғᴀᴜʟᴛ ᴄᴀᴘᴛɪᴏɴ ᴛᴇxᴛ ғᴏʀ ғɪʟᴇs sᴇɴᴛ ʙʏ ᴛʜᴇ ʙᴏᴛ."},
    "ENABLE_FSUB": {"name": "ᴇɴᴀʙʟᴇ ғᴏʀᴄᴇ sᴜʙ", "help": "sᴇᴛ ᴛʀᴜᴇ ᴛᴏ ᴇɴᴀʙʟᴇ ғᴏʀᴄᴇ sᴜʙsᴄʀɪʙᴇ."},
    "VERIFICATION_MODE": {"name": "ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ ᴍᴏᴅᴇ", "help": "sᴇᴛ ᴛʀᴜᴇ ᴛᴏ ᴇɴᴀʙʟᴇ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ."},
    "AUTO_DELETE": {"name": "ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ", "help": "sᴇᴛ ᴛʀᴜᴇ ᴛᴏ ᴇɴᴀʙʟᴇ ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇ."},
}

GROUPS = {
    "☉ ʀᴇQᴜɪʀᴇᴅ sᴇᴛᴛɪɴɢs": ["BOT_TOKEN", "MONGO_URI"],
    "⍟ ᴀᴅᴍɪɴs": ["ADMINS"],
    "⊛ ғᴏʀᴄᴇ sᴜʙ": ["ENABLE_FSUB", "FSUB"],
    "⊘ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ": ["VERIFICATION_MODE"],  # submenu
    "⌬ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ": ["AUTO_DELETE", "AUTO_DELETE_TIME"],
    "○ ᴄᴀᴘᴛɪᴏɴ": ["CAPTION"]
}

VERIFICATION_SUB = ["VERIFICATION_MODE", "PREMIUM_HOURS_VERIFICATION", "SHORTENER_DOMAIN", "SHORTENER_API_KEY"]

# ---------------- KEYBOARDS ----------------
def get_group_keyboard():
    buttons = [[InlineKeyboardButton(g, callback_data=f"group:{g}")] for g in GROUPS.keys()]
    buttons.append([InlineKeyboardButton("⊗ ᴄʟᴏsᴇ", callback_data="close")])
    return InlineKeyboardMarkup(buttons)

def get_variable_keyboard(group_name: str):
    if group_name == "⊘ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ":
        buttons = [[InlineKeyboardButton(f"• {VARIABLE_INFO[var]['name']} •", callback_data=f"setting:verification:{var}")] for var in VERIFICATION_SUB]
    else:
        buttons = [[InlineKeyboardButton(f"• {VARIABLE_INFO[var]['name']} •", callback_data=f"setting:{group_name}:{var}")] for var in GROUPS[group_name]]
    buttons.append([
        InlineKeyboardButton("⊖ ʙᴀᴄᴋ", callback_data="back_to_groups"),
        InlineKeyboardButton("⊗ ᴄʟᴏsᴇ", callback_data="close")
    ])
    return InlineKeyboardMarkup(buttons)

def get_setting_keyboard(group_name: str, var_name: str, is_boolean=False):
    buttons = [[InlineKeyboardButton("✧ ᴛᴏɢɢʟᴇ", callback_data=f"toggle:{group_name}:{var_name}")] if is_boolean else
               [InlineKeyboardButton("✎ ᴇᴅɪᴛ", callback_data=f"edit:{group_name}:{var_name}")]]
    buttons.append([
        InlineKeyboardButton("⊖ ʙᴀᴄᴋ", callback_data=f"back_to_group:{group_name}"),
        InlineKeyboardButton("⊗ ᴄʟᴏsᴇ", callback_data="close")
    ])
    return InlineKeyboardMarkup(buttons)

def get_edit_keyboard(group_name: str, var_name: str):
    return InlineKeyboardMarkup([[InlineKeyboardButton("⊖ ʙᴀᴄᴋ", callback_data=f"back_to_setting:{group_name}:{var_name}")]])

# ---------------- HANDLERS ----------------
@listen.Client.on_message(filters.command("settings") & filters.private)
async def settings_handler(client, message):
    user_id = message.from_user.id
    if users_col.find_one({"USER_ID": user_id}) is None:
        users_col.insert_one({"USER_ID": user_id})  # create default if missing
    log.info(f"User {user_id} opened settings.")
    text = "⚙️ <b>ʙᴏᴛ sᴇᴛᴛɪɴɢs</b>\n\nsᴇʟᴇᴄᴛ ᴀ ᴄᴀᴛᴇɢᴏʀʏ ᴛᴏ ᴄᴏɴғɪɢᴜʀᴇ:"
    await message.reply_text(text, reply_markup=get_group_keyboard(), parse_mode=ParseMode.HTML)

# ---------------- CALLBACKS ----------------
@listen.Client.on_callback_query(filters.regex(r"^group:(.+)"))
async def open_group(client, callback_query):
    group_name = callback_query.data.split(":", 1)[1]
    text = f"📂 <b>{group_name}</b>\n\nsᴇʟᴇᴄᴛ ᴀ ᴠᴀʀɪᴀʙʟᴇ ᴛᴏ ᴄᴏɴғɪɢᴜʀᴇ:"
    await callback_query.message.edit_text(text, reply_markup=get_variable_keyboard(group_name), parse_mode=ParseMode.HTML)

@listen.Client.on_callback_query(filters.regex(r"^setting:(.+?):(.+)"))
async def open_setting(client, callback_query):
    group_name, var_name = callback_query.data.split(":", 2)[1:]
    user = users_col.find_one({"USER_ID": callback_query.from_user.id}) or {}
    current_value = user.get(var_name, "ɴᴏᴛ sᴇᴛ")
    var_info = VARIABLE_INFO.get(var_name, {"name": var_name, "help": ""})
    text = f"<b>{var_info['name']}</b>\n\n<b>ᴄᴜʀʀᴇɴᴛ ᴠᴀʟᴜᴇ:</b>\n<code>{current_value}</code>\n\n{var_info['help']}"
    keyboard = get_setting_keyboard(group_name, var_name, var_name in BOOLEAN_VARS)
    await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML, disable_web_page_preview=True)

@listen.Client.on_callback_query(filters.regex(r"^toggle:(.+?):(.+)"))
async def toggle_setting(client, callback_query):
    group_name, var_name = callback_query.data.split(":", 2)[1:]
    user_id = callback_query.from_user.id
    user = users_col.find_one({"USER_ID": user_id}) or {}
    new_value = not bool(user.get(var_name, False))
    users_col.update_one({"USER_ID": user_id}, {"$set": {var_name: new_value}})
    log.info(f"Toggled {var_name} for {user_id}: {new_value}")
    await open_setting(client, callback_query)

@listen.Client.on_callback_query(filters.regex(r"^edit:(.+?):(.+)"))
async def edit_setting(client, callback_query):
    group_name, var_name = callback_query.data.split(":", 2)[1:]
    var_info = VARIABLE_INFO.get(var_name, {"name": var_name, "help": ""})
    await callback_query.message.edit_text(
        f"✎ sᴇɴᴅ ᴀ ɴᴇᴡ ᴠᴀʟᴜᴇ ғᴏʀ <b>{var_info['name']}</b>.\n\n{var_info['help']}\n\n⏳ ʏᴏᴜ ʜᴀᴠᴇ 120 sᴇᴄᴏɴᴅs.",
        reply_markup=get_edit_keyboard(group_name, var_name),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True
    )
    try:
        response = await client.listen(callback_query.message.chat.id, timeout=120)
        new_value = response.text.strip()
        if var_name in INT_VARS:
            new_value = int(new_value)
        users_col.update_one({"USER_ID": callback_query.from_user.id}, {"$set": {var_name: new_value}})
        log.info(f"Updated {var_name} for {callback_query.from_user.id}: {new_value}")
        await callback_query.message.reply_text(f"✅ {var_info['name']} ᴜᴘᴅᴀᴛᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ.")
    except asyncio.TimeoutError:
        await callback_query.message.reply_text("⌛ Timeout. Operation canceled.")
    await open_setting(client, callback_query)

# ---------------- BACK & CLOSE ----------------
@listen.Client.on_callback_query(filters.regex(r"^back_to_groups$"))
async def back_to_groups(client, callback_query):
    await settings_handler(client, callback_query.message)

@listen.Client.on_callback_query(filters.regex(r"^back_to_group:(.+)"))
async def back_to_group(client, callback_query):
    await open_group(client, callback_query)

@listen.Client.on_callback_query(filters.regex(r"^back_to_setting:(.+?):(.+)"))
async def back_to_setting(client, callback_query):
    await open_setting(client, callback_query)

@listen.Client.on_callback_query(filters.regex(r"^close$"))
async def close_menu(client, callback_query):
    await callback_query.message.delete()
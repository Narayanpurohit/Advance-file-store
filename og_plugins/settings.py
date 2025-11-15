import logging
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
import pyromod.listen  # enable client.listen
from db_config import users_col

# ---------------- LOGGING ----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"
)
log = logging.getLogger("Settings")

# ---------------- VARIABLES ----------------
BOOLEAN_VARS = ["ENABLE_FSUB", "VERIFICATION_MODE", "AUTO_DELETE", "PROTECT_CONTENT", "CLONE_BUTTON", "PUBLIC_BOT"]
INT_VARS = ["PREMIUM_HOURS_VERIFICATION", "AUTO_DELETE_TIME", "LOG_CHANNEL"]

VARIABLE_INFO = {
    "BOT_TOKEN": {"name": "ʙᴏᴛ ᴛᴏᴋᴇɴ", "help": "ᴛʜᴇ ᴛᴏᴋᴇɴ ʏᴏᴜ ɢᴇᴛ ғʀᴏᴍ @ʙᴏᴛғᴀᴛʜᴇʀ."},
    "DB_NAME": {"name": "Data code", "help": "ᴛʜɪs ɪs ᴜɴɪǫᴜᴇ ᴄᴏᴅᴇ ᴛʜᴀᴛ sᴛᴏʀᴇs ʏᴏᴜʀ ʟɪɴᴋs ᴀɴᴅ ᴜsᴇʀ ᴅᴀᴛᴀ ɪꜰ ʏᴏᴜ ᴄʜᴀɴɢᴇ ᴀᴄᴏᴜɴᴛ sᴇᴛ ᴛʜɪs ᴄᴏᴅᴇ."},
    "ADMINS": {"name": "ᴀᴅᴍɪɴ ᴜsᴇʀs", "help": "ᴜsᴇʀ ɪᴅs ᴏғ ᴀᴅᴍɪɴs sᴇᴘᴀʀᴀᴛᴇ ᴛʜᴇᴍ ᴡɪᴛʜ ,"},
    "FSUB": {"name": "ғᴏʀᴄᴇ sᴜʙ ᴄʜᴀɴɴᴇʟ", "help": "ɪᴅ ᴏғ ᴄʜᴀɴɴᴇʟ ғᴏʀ ғsᴜʙ ɪɴ ᴛʜɪs ғᴏʀᴍᴀᴛ. \n\nʙᴜᴛᴛᴏɴ ɴᴀᴍᴇ 1 : ɪᴅ1 , ʙᴜᴛᴛᴏɴ ɴᴀᴍᴇ 2 : ɪᴅ2 , ʙᴜᴛᴛᴏɴ ɴᴀᴍᴇ 3 : ɪᴅ3"},
    "PREMIUM_HOURS_VERIFICATION": {"name": "ʜᴏᴜʀs ᴜsᴇʀ ɢᴇᴛ ᴘʀᴇᴍɪᴜᴍ ᴀғᴛᴇʀ ᴠᴇʀɪғɪᴇᴅ.", "help": "ʜᴏᴜʀs ᴜsᴇʀ sᴛᴀʏs ᴠᴇʀɪғɪᴇᴅ."},
    "SHORTENER_DOMAIN": {"name": "sʜᴏʀᴛᴇɴᴇʀ ᴅᴏᴍᴀɪɴ", "help": "ᴏɴʟʏ ᴅᴏᴍᴀɪɴ ғᴏʀ ʟɪɴᴋ sʜᴏʀᴛᴇɴᴇʀ. ʟɪᴋᴇ ᴛʜɪs ᴅᴏᴍᴀɪɴ.ᴄᴏᴍ"},
    "SHORTENER_API_KEY": {"name": "sʜᴏʀᴛᴇɴᴇʀ ᴀᴘɪ ᴋᴇʏ", "help": "ᴀᴘɪ ᴋᴇʏ ғᴏʀ ʏᴏᴜʀ sʜᴏʀᴛᴇɴᴇʀ."},
    "CAPTION": {"name": "ғɪʟᴇ ᴄᴀᴘᴛɪᴏɴ", "help": "ʏᴏᴜ ᴄᴀɴ ᴜsᴇ ᴛʜɪs ғᴏʀᴍᴀᴛs ᴀs ᴄᴀᴘᴛɪᴏɴ\n`{filename}`\n`{filesize}`\n`{caption}`"},
    "AUTO_DELETE_TIME": {"name": "ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴛɪᴍᴇ", "help": "ᴛɪᴍᴇ ɪɴ (sᴇᴄᴏɴᴅs) ғᴏʀ ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇ."},
    "ENABLE_FSUB": {"name": "ᴇɴᴀʙʟᴇ ғᴏʀᴄᴇ sᴜʙ", "help": "ᴄʜᴀɴɢᴇ ғᴏʀᴄᴇ-sᴜʙ ᴍᴏᴅᴇ"},
    "VERIFICATION_MODE": {"name": "ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ ᴍᴏᴅᴇ", "help": "ᴄʜᴀɴɢᴇ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ ᴍᴏᴅᴇ."},
    "AUTO_DELETE": {"name": "ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ", "help": "ᴄʜᴀɴɢᴇ ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇ ᴍᴏᴅᴇ."},
    "LOG_CHANNEL": {"name": "ʟᴏɢ ᴄʜᴀɴɴᴇʟ", "help": "ꜱᴇᴛ ʟᴏɢ ᴄʜᴀɴɴᴇʟ ɪᴅ ᴀɴᴅ ᴍᴀᴋᴇ ꜱᴜʀᴇ ʙᴏᴛ ɪꜱ ᴀᴅᴍɪɴ ᴏɴ ᴄʜᴀɴɴᴇʟ."},
    "PROTECT_CONTENT": {"name": "ᴘʀᴏᴛᴇᴄᴛ ᴄᴏɴᴛᴇɴᴛ", "help": "ʀᴇꜱᴛʀɪᴄᴛ ᴜꜱᴇʀ ꜰʀᴏᴍ ꜱᴀᴠɪɴɢ ᴄᴏɴᴛᴇɴᴛ."},
    "CLONE_BUTTON": {"name": "ᴄʟᴏɴᴇ ʙᴜᴛᴛᴏɴ", "help": "ꜱʜᴏᴡ ᴄʀᴇᴀᴛᴇ ᴄʟᴏɴᴇ ʙᴜᴛᴛᴏɴ ᴏɴ ʏᴏᴜʀ ʙᴏᴛ."},
    "PUBLIC_BOT": {"name": "ᴘᴜʙʟɪᴄ ʙᴏᴛ", "help": "ᴇᴠᴇʀʏᴏɴᴇ ᴄᴀɴ ᴜꜱᴇ ʙᴏᴛ."}
    "DEKOY": {"name": "DEKOY", "help": "ENABLE ʙᴏᴛ."}

    
    
    
    
}

# ---------------- GROUPS ----------------
GROUP_KEYS = {
    "☉ ʀᴇQᴜɪʀᴇᴅ sᴇᴛᴛɪɴɢs": "required",
    "⍟ ᴀᴅᴍɪɴs": "admins",
    "⊛ ғᴏʀᴄᴇ sᴜʙ": "fsub",
    "⊘ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ": "verification",
    "⌬ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ": "autodelete",
    "○ ᴄᴀᴘᴛɪᴏɴ": "caption",
    "• ᴏᴛʜᴇʀ ꜱᴇᴛᴛɪɴɢꜱ": "other"
}

GROUPS = {
    "☉ ʀᴇQᴜɪʀᴇᴅ sᴇᴛᴛɪɴɢs": ["BOT_TOKEN","DB_NAME"],
    "⍟ ᴀᴅᴍɪɴs": ["ADMINS"],
    "⊛ ғᴏʀᴄᴇ sᴜʙ": ["ENABLE_FSUB", "FSUB"],
    "⊘ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ": [],  # submenu handled separately
    "⌬ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ": ["DEKOY","AUTO_DELETE", "AUTO_DELETE_TIME"],
    "○ ᴄᴀᴘᴛɪᴏɴ": ["CAPTION"],
    "• ᴏᴛʜᴇʀ ꜱᴇᴛᴛɪɴɢꜱ":["PROTECT_CONTENT", "CLONE_BUTTON", "PUBLIC_BOT", "LOG_CHANNEL"]
    
}

VERIFICATION_SUB = [
    "VERIFICATION_MODE",
    "PREMIUM_HOURS_VERIFICATION",
    "SHORTENER_DOMAIN",
    "SHORTENER_API_KEY"
]

# ---------------- KEYBOARDS ----------------
def get_group_keyboard():
    buttons = [
        [InlineKeyboardButton(group, callback_data=f"group:{GROUP_KEYS[group]}")]
        for group in GROUPS.keys()
    ]
    buttons.append([InlineKeyboardButton("⊗ ᴄʟᴏsᴇ", callback_data="close")])
    return InlineKeyboardMarkup(buttons)

def get_variable_keyboard(group_key: str):
    group_name = next(name for name, key in GROUP_KEYS.items() if key == group_key)
    if group_name == "⊘ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ":
        buttons = [[InlineKeyboardButton(f"• {VARIABLE_INFO[var]['name']} •",
                   callback_data=f"setting:{group_key}:{var}")] for var in VERIFICATION_SUB]
    else:
        buttons = [[InlineKeyboardButton(f"• {VARIABLE_INFO[var]['name']} •",
                   callback_data=f"setting:{group_key}:{var}")] for var in GROUPS[group_name]]
    buttons.append([
        InlineKeyboardButton("⊖ ʙᴀᴄᴋ", callback_data="back_to_groups"),
        InlineKeyboardButton("⊗ ᴄʟᴏsᴇ", callback_data="close")
    ])
    return InlineKeyboardMarkup(buttons)

def get_setting_keyboard(group_key: str, var_name: str, is_boolean=False):
    if is_boolean:
        buttons = [[InlineKeyboardButton("✧ ᴏɴ/ᴏғғ", callback_data=f"toggle:{group_key}:{var_name}")]]
    else:
        buttons = [[InlineKeyboardButton("✎ ᴇᴅɪᴛ", callback_data=f"edit:{group_key}:{var_name}")]]
    buttons.append([
        InlineKeyboardButton("⊖ ʙᴀᴄᴋ", callback_data=f"back_to_group:{group_key}"),
        InlineKeyboardButton("⊗ ᴄʟᴏsᴇ", callback_data="close")
    ])
    return InlineKeyboardMarkup(buttons)

def get_edit_keyboard(group_key: str, var_name: str):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⊖ ʙᴀᴄᴋ", callback_data=f"back_to_setting:{group_key}:{var_name}")]
    ])

# ---------------- ACTIVE LISTENERS ----------------
active_edit_listeners = {}

# ---------------- HANDLERS ----------------
@Client.on_message(filters.command("settings") & filters.private)
async def settings_handler(client, message):
    await message.reply_text(
        "⚙️ <b>ʙᴏᴛ sᴇᴛᴛɪɴɢs</b>\n\nsᴇʟᴇᴄᴛ ᴀ ᴄᴀᴛᴇɢᴏʀʏ:",
        reply_markup=get_group_keyboard(),
        parse_mode=ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^group:(.+)"))
async def open_group(client, cq):
    group_key = cq.data.split(":", 1)[1]
    group_name = next(name for name, key in GROUP_KEYS.items() if key == group_key)
    await cq.message.edit_text(
        f"📂 <b>{group_name}</b>\n\nsᴇʟᴇᴄᴛ ᴀ ᴠᴀʀɪᴀʙʟᴇ:",
        reply_markup=get_variable_keyboard(group_key),
        parse_mode=ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^setting:(.+?):(.+)"))
async def open_setting(client, cq):
    group_key, var_name = cq.data.split(":", 2)[1:]
    user = users_col.find_one({"USER_ID": cq.from_user.id}) or {}
    current_value = user.get(var_name, "ɴᴏᴛ sᴇᴛ")
    var_info = VARIABLE_INFO.get(var_name, {"name": var_name, "help": ""})
    text = f"<b>{var_info['name']}</b>\n\n<b>ᴄᴜʀʀᴇɴᴛ:</b>\n<code>{current_value}</code>\n\n{var_info['help']}"
    await cq.message.edit_text(
        text,
        reply_markup=get_setting_keyboard(group_key, var_name, var_name in BOOLEAN_VARS),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True
    )

@Client.on_callback_query(filters.regex(r"^toggle:(.+?):(.+)"))
async def toggle_setting(client, cq):
    group_key, var_name = cq.data.split(":", 2)[1:]
    user_id = cq.from_user.id
    user = users_col.find_one({"USER_ID": user_id}) or {}
    new_value = not bool(user.get(var_name, False))
    users_col.update_one({"USER_ID": user_id}, {"$set": {var_name: new_value}})
    await open_setting(client, cq)

@Client.on_callback_query(filters.regex(r"^edit:(.+?):(.+)"))
async def edit_setting(client, cq):
    group_key, var_name = cq.data.split(":", 2)[1:]
    var_info = VARIABLE_INFO.get(var_name, {"name": var_name, "help": ""})

    await cq.message.edit_text(
        f"✎ Send new value for <b>{var_info['name']}</b>.\n\n{var_info['help']}\n\n⏳ 120s timeout.",
        reply_markup=get_edit_keyboard(group_key, var_name),
        parse_mode=ParseMode.HTML
    )

    # Cancel previous listener if exists
    if cq.message.chat.id in active_edit_listeners:
        active_edit_listeners[cq.message.chat.id].cancel()

    # Start new listener
    task = asyncio.create_task(client.listen(cq.message.chat.id, timeout=120))
    active_edit_listeners[cq.message.chat.id] = task

    try:
        response = await task
        new_value = int(response.text.strip()) if var_name in INT_VARS else response.text.strip()
        users_col.update_one({"USER_ID": cq.from_user.id}, {"$set": {var_name: new_value}})
        await cq.message.reply_text(
            f"✅ {var_info['name']} updated: <code>{new_value}</code>",
            parse_mode=ParseMode.HTML
        )
    except asyncio.TimeoutError:
        await cq.message.reply_text("⏳ Edit timed out.", parse_mode=ParseMode.HTML)
    except asyncio.CancelledError:
        pass  # cancelled by back/close
    finally:
        active_edit_listeners.pop(cq.message.chat.id, None)

    await open_setting(client, cq)

# ---------------- BACK & CLOSE ----------------
@Client.on_callback_query(filters.regex(r"^back_to_groups$"))
async def back_to_groups(client, cq):
    # cancel active listener
    listener = active_edit_listeners.pop(cq.message.chat.id, None)
    if listener:
        listener.cancel()
    await cq.message.edit_text(
        "⚙️ <b>ʙᴏᴛ sᴇᴛᴛɪɴɢs</b>\n\nsᴇʟᴇᴄᴛ ᴀ ᴄᴀᴛᴇɢᴏʀʏ:",
        reply_markup=get_group_keyboard(),
        parse_mode=ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^back_to_group:(.+)"))
async def back_to_group(client, cq):
    listener = active_edit_listeners.pop(cq.message.chat.id, None)
    if listener:
        listener.cancel()
    group_key = cq.data.split(":", 1)[1]
    group_name = next(k for k, v in GROUP_KEYS.items() if v == group_key)
    await cq.message.edit_text(
        f"📂 <b>{group_name}</b>\n\nsᴇʟᴇᴄᴛ ᴀ ᴠᴀʀɪᴀʙʟᴇ:",
        reply_markup=get_variable_keyboard(group_key),
        parse_mode=ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^back_to_setting:(.+?):(.+)"))
async def back_to_setting(client, cq):
    listener = active_edit_listeners.pop(cq.message.chat.id, None)
    if listener:
        listener.cancel()
    group_key, var_name = cq.data.split(":", 2)[1:]
    user = users_col.find_one({"USER_ID": cq.from_user.id}) or {}
    current_value = user.get(var_name, "ɴᴏᴛ sᴇᴛ")
    var_info = VARIABLE_INFO.get(var_name, {"name": var_name, "help": ""})
    text = f"<b>{var_info['name']}</b>\n\n<b>ᴄᴜʀʀᴇɴᴛ:</b>\n<code>{current_value}</code>\n\n{var_info['help']}"
    await cq.message.edit_text(
        text,
        reply_markup=get_setting_keyboard(group_key, var_name, var_name in BOOLEAN_VARS),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True
    )

@Client.on_callback_query(filters.regex(r"^close$"))
async def close_menu(client, cq):
    listener = active_edit_listeners.pop(cq.message.chat.id, None)
    if listener:
        listener.cancel()
    await cq.message.delete()
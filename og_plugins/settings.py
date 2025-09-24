import logging
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from db_config import users_col
from pyrogram.enums import ParseMode

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
    "BOT_TOKEN": {
        "name": "ʙᴏᴛ ᴛᴏᴋᴇɴ",
        "help": "ᴛʜᴇ ᴛᴏᴋᴇɴ ʏᴏᴜ ɢᴇᴛ ғʀᴏᴍ @ʙᴏᴛғᴀᴛʜᴇʀ ᴛᴏ ʀᴜɴ ʏᴏᴜʀ ʙᴏᴛ."
    },
    "MONGO_URI": {
        "name": "ᴍᴏɴɢᴏᴅʙ ᴜʀɪ",
        "help": 'ᴄᴏɴɴᴇᴄᴛɪᴏɴ sᴛʀɪɴɢ ғᴏʀ ʏᴏᴜʀ ᴍᴏɴɢᴏᴅʙ ᴅᴀᴛᴀʙᴀsᴇ.\n\nᴄʟɪᴄᴋ ʜᴇʀᴇ ғᴏʀ <a href="https://youtu.be/4d-07F-Z2dc?si=_8OIuEJoL5oT1kQr">ᴛᴜᴛᴏʀɪᴀʟ ʟɪɴᴋ</a>.'
    },
    "ADMINS": {
        "name": "ᴀᴅᴍɪɴ ᴜsᴇʀs",
        "help": "ᴜsᴇʀ ɪᴅs ᴏғ ᴀᴅᴍɪɴs ᴡʜᴏ ᴄᴀɴ ᴄᴏɴᴛʀᴏʟ ᴛʜᴇ ʙᴏᴛ.\nᴇxᴀᴍᴘʟᴇ: 123456789,987654321"
    },
    "FSUB": {
        "name": "ғᴏʀᴄᴇ sᴜʙᴄʀɪʙᴇ ᴄʜᴀɴɴᴇʟ",
        "help": "ᴜsᴇʀɴᴀᴍᴇ ᴏʀ ᴄʜᴀɴɴᴇʟ ɪᴅ ᴜsᴇʀs ᴍᴜsᴛ ᴊᴏɪɴ ʙᴇғᴏʀᴇ ᴜsɪɴɢ ᴛʜᴇ ʙᴏᴛ.\nᴇxᴀᴍᴘʟᴇ: @ᴍʏᴄʜᴀɴɴᴇʟ ᴏʀ -1001234567890"
    },
    "PREMIUM_HOURS_VERIFICATION": {
        "name": "ᴘʀᴇᴍɪᴜᴍ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ ʜᴏᴜʀs",
        "help": "ɴᴜᴍʙᴇʀ ᴏғ ʜᴏᴜʀs ᴀ ᴠᴇʀɪғɪᴇᴅ ᴜsᴇʀ sᴛᴀʏs ᴠᴇʀɪғɪᴇᴅ.\nᴇxᴀᴍᴘʟᴇ: 12"
    },
    "SHORTENER_DOMAIN": {
        "name": "sʜᴏʀᴛᴇɴᴇʀ ᴅᴏᴍᴀɪɴ",
        "help": "ᴛʜᴇ ᴅᴏᴍᴀɪɴ ᴜsᴇᴅ ғᴏʀ ʏᴏᴜʀ ʟɪɴᴋ sʜᴏʀᴛᴇɴᴇʀ.\nᴇxᴀᴍᴘʟᴇ: sʜᴏʀᴛ.ᴇxᴀᴍᴘʟᴇ.ᴄᴏᴍ"
    },
    "SHORTENER_API_KEY": {
        "name": "sʜᴏʀᴛᴇɴᴇʀ ᴀᴘɪ ᴋᴇʏ",
        "help": "ᴀᴘɪ ᴋᴇʏ ғᴏʀ ʏᴏᴜʀ sʜᴏʀᴛᴇɴᴇʀ sᴇʀᴠɪᴄᴇ."
    },
    "CAPTION": {
        "name": "ғɪʟᴇ ᴄᴀᴘᴛɪᴏɴ",
        "help": "ᴅᴇғᴀᴜʟᴛ ᴄᴀᴘᴛɪᴏɴ ᴛᴇxᴛ ғᴏʀ ғɪʟᴇs sᴇɴᴛ ʙʏ ᴛʜᴇ ʙᴏᴛ."
    },
    "AUTO_DELETE_TIME": {
        "name": "ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴛɪᴍᴇ",
        "help": "ᴛɪᴍᴇ (ɪɴ sᴇᴄᴏɴᴅs) ᴀғᴛᴇʀ ᴡʜɪᴄʜ ғɪʟᴇs ᴀʀᴇ ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇᴅ.\nᴇxᴀᴍᴘʟᴇ: 1800"
    },
    "ENABLE_FSUB": {
        "name": "ᴇɴᴀʙʟᴇ ғᴏʀᴄᴇ sᴜʙsᴄʀɪʙᴇ",
        "help": "sᴇᴛ ᴛᴏ ᴛʀᴜᴇ ᴛᴏ ᴇɴᴀʙʟᴇ ғᴏʀᴄᴇ-sᴜʙsᴄʀɪʙᴇ ғᴇᴀᴛᴜʀᴇ."
    },
    "VERIFICATION_MODE": {
        "name": "ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ ᴍᴏᴅᴇ",
        "help": "sᴇᴛ ᴛᴏ ᴛʀᴜᴇ ᴛᴏ ᴇɴᴀʙʟᴇ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ sʏsᴛᴇᴍ."
    },
    "AUTO_DELETE": {
        "name": "ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ",
        "help": "sᴇᴛ ᴛᴏ ᴛʀᴜᴇ ᴛᴏ ᴇɴᴀʙʟᴇ ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛɪɴɢ ᴏғ ғɪʟᴇs ᴀғᴛᴇʀ sᴇᴛ ᴛɪᴍᴇ."
    }
}

# ---------------- GROUPS ----------------
GROUPS = {
    "☉ ʀᴇQᴜɪʀᴇᴅ sᴇᴛᴛɪɴɢs": ["BOT_TOKEN", "MONGO_URI"],
    "⍟ ᴀᴅᴍɪɴs": ["ADMINS"],
    "⊛ ғᴏʀᴄᴇ sᴜʙ": ["ENABLE_FSUB", "FSUB"],
    "⊘ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ": ["VERIFICATION_MODE", "PREMIUM_HOURS_VERIFICATION", "SHORTENER_DOMAIN", "SHORTENER_API_KEY"],
    "⌬ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ": ["AUTO_DELETE", "AUTO_DELETE_TIME"],
    "○ ᴄᴀᴘᴛɪᴏɴ": ["CAPTION"]
}

# ---------------- KEYBOARDS ----------------
def get_group_keyboard():
    buttons = []
    for group in GROUPS.keys():
        buttons.append([InlineKeyboardButton(group, callback_data=f"group:{group}")])
    buttons.append([InlineKeyboardButton("⊗ ᴄʟᴏsᴇ", callback_data="close")])
    return InlineKeyboardMarkup(buttons)

def get_variable_keyboard(group_name: str):
    buttons = []
    for var in GROUPS[group_name]:
        label = VARIABLE_INFO.get(var, {}).get("name", var)
        buttons.append([InlineKeyboardButton(f"• {label} •", callback_data=f"setting:{group_name}:{var}")])
    buttons.append([
        InlineKeyboardButton("⊖ ʙᴀᴄᴋ", callback_data="back_to_groups"),
        InlineKeyboardButton("⊗ ᴄʟᴏsᴇ", callback_data="close")
    ])
    return InlineKeyboardMarkup(buttons)

def get_setting_keyboard(group_name: str, var_name: str, is_boolean=False):
    buttons = []
    if is_boolean:
        buttons.append([InlineKeyboardButton("✧ ᴛᴏɢɢʟᴇ", callback_data=f"toggle:{group_name}:{var_name}")])
    else:
        buttons.append([InlineKeyboardButton("✎ ᴇᴅɪᴛ", callback_data=f"edit:{group_name}:{var_name}")])
    buttons.append([
        InlineKeyboardButton("⊖ ʙᴀᴄᴋ", callback_data=f"back_to_group:{group_name}"),
        InlineKeyboardButton("⊗ ᴄʟᴏsᴇ", callback_data="close")
    ])
    return InlineKeyboardMarkup(buttons)

def get_edit_keyboard(group_name: str, var_name: str):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⊖ ʙᴀᴄᴋ", callback_data=f"back_to_setting:{group_name}:{var_name}")]
    ])

# ---------------- HANDLERS ----------------
@Client.on_message(filters.command("settings") & filters.private)
async def settings_handler(client, message):
    user_id = message.from_user.id
    log.info(f"User {user_id} opened settings.")
    text = "⚙️ <b>ʙᴏᴛ sᴇᴛᴛɪɴɢs</b>\n\nsᴇʟᴇᴄᴛ ᴀ ᴄᴀᴛᴇɢᴏʀʏ ᴛᴏ ᴄᴏɴғɪɢᴜʀᴇ:"
    await message.reply_text(text, reply_markup=get_group_keyboard(), parse_mode=ParseMode.HTML)

@Client.on_callback_query(filters.regex(r"^group:(.+)"))
async def open_group(client, callback_query):
    group_name = callback_query.data.split(":", 1)[1]
    text = f"📂 <b>{group_name}</b>\n\nsᴇʟᴇᴄᴛ ᴀ ᴠᴀʀɪᴀʙʟᴇ ᴛᴏ ᴄᴏɴғɪɢᴜʀᴇ:"
    await callback_query.message.edit_text(
        text,
        reply_markup=get_variable_keyboard(group_name),
        parse_mode=ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^setting:(.+?):(.+)"))
async def open_setting(client, callback_query):
    group_name, var_name = callback_query.data.split(":", 2)[1:]
    user = users_col.find_one({"USER_ID": callback_query.from_user.id}) or {}
    current_value = user.get(var_name, "ɴᴏᴛ sᴇᴛ")

    var_info = VARIABLE_INFO.get(var_name, {"name": var_name, "help": ""})
    text = (
        f"<b>{var_info['name']}</b>\n\n"
        f"<b>ᴄᴜʀʀᴇɴᴛ ᴠᴀʟᴜᴇ:</b>\n<code>{current_value}</code>\n\n"
        f"{var_info['help']}"
    )

    keyboard = get_setting_keyboard(group_name, var_name, var_name in BOOLEAN_VARS)
    await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML, disable_web_page_preview=True)

@Client.on_callback_query(filters.regex(r"^toggle:(.+?):(.+)"))
async def toggle_setting(client, callback_query):
    group_name, var_name = callback_query.data.split(":", 2)[1:]
    user_id = callback_query.from_user.id
    user = users_col.find_one({"USER_ID": user_id}) or {}
    current_value = bool(user.get(var_name, False))
    new_value = not current_value
    users_col.update_one({"USER_ID": user_id}, {"$set": {var_name: new_value}})
    log.info(f"Toggled {var_name} for {user_id}: {current_value} → {new_value}")
    await open_setting(client, callback_query)

@Client.on_callback_query(filters.regex(r"^edit:(.+?):(.+)"))
async def edit_setting(client, callback_query):
    group_name, var_name = callback_query.data.split(":", 2)[1:]
    var_info = VARIABLE_INFO.get(var_name, {"name": var_name, "help": ""})

    await callback_query.message.edit_text(
        f"✎ sᴇɴᴅ ᴀ ɴᴇᴡ ᴠᴀʟᴜᴇ ғᴏʀ <b>{var_info['name']}</b>.\n\n"
        f"{var_info['help']}\n\n"
        "⏳ ʏᴏᴜ ʜᴀᴠᴇ 120 sᴇᴄᴏɴᴅs.",
        reply_markup=get_edit_keyboard(group_name, var_name),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True
    )

    while True:
        try:
            response = await client.listen(callback_query.message.chat.id, timeout=120)
        except asyncio.TimeoutError:
            await open_setting(client, callback_query)
            return

        if response.text and response.text.startswith("/"):
            continue

        new_value = response.text.strip()

        if var_name in INT_VARS:
            if not new_value.isdigit():
                await callback_query.message.reply_text("❌ ᴘʟᴇᴀsᴇ sᴇɴᴅ ᴀ ᴠᴀʟɪᴅ ɪɴᴛᴇɢᴇʀ.")
                continue
            new_value = int(new_value)

        users_col.update_one({"USER_ID": callback_query.from_user.id}, {"$set": {var_name: new_value}})
        log.info(f"Updated {var_name} for {callback_query.from_user.id}: {new_value}")
        await callback_query.message.reply_text(f"✅ {var_info['name']} ᴜᴘᴅᴀᴛᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ.")
        await open_setting(client, callback_query)
        return

# ---------------- BACK & CLOSE ----------------
@Client.on_callback_query(filters.regex(r"^back_to_groups$"))
async def back_to_groups(client, callback_query):
    await callback_query.message.edit_text(
        "⚙️ <b>ʙᴏᴛ sᴇᴛᴛɪɴɢs</b>\n\nsᴇʟᴇᴄᴛ ᴀ ᴄᴀᴛᴇɢᴏʀʏ ᴛᴏ ᴄᴏɴғɪɢᴜʀᴇ:",
        reply_markup=get_group_keyboard(),
        parse_mode=ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^back_to_group:(.+)"))
async def back_to_group(client, callback_query):
    await open_group(client, callback_query)

@Client.on_callback_query(filters.regex(r"^back_to_setting:(.+?):(.+)"))
async def back_to_setting(client, callback_query):
    await open_setting(client, callback_query)

@Client.on_callback_query(filters.regex(r"^close$"))
async def close_menu(client, callback_query):
    await callback_query.message.delete()